import json
import math
import urllib.request
import urllib.error
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["stores"])

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter"
]
USER_AGENT = "AgriScan/0.1 (Student/Demo Project)"

class Location(BaseModel):
    latitude: float
    longitude: float

class Store(BaseModel):
    id: str
    name: str
    category: str
    address: Optional[str]
    latitude: float
    longitude: float
    distance_meters: float
    phone: Optional[str]
    website: Optional[str]
    opening_hours: Optional[str]
    source: str = "OpenStreetMap"

class NearbyStoresResponse(BaseModel):
    location: Location
    radius_meters: int
    stores: List[Store]

def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  # radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c

def build_overpass_query(lat: float, lng: float, radius: int) -> str:
    # We query node and way for shop=agrarian and shop=garden_centre
    return f"""
    [out:json];
    (
      node["shop"="agrarian"](around:{radius},{lat},{lng});
      node["shop"="garden_centre"](around:{radius},{lat},{lng});
      way["shop"="agrarian"](around:{radius},{lat},{lng});
      way["shop"="garden_centre"](around:{radius},{lat},{lng});
    );
    out center;
    """

def format_address(tags: dict) -> Optional[str]:
    parts = []
    if "addr:housenumber" in tags and "addr:street" in tags:
        parts.append(f"{tags['addr:housenumber']} {tags['addr:street']}")
    elif "addr:street" in tags:
        parts.append(tags["addr:street"])
    
    if "addr:city" in tags:
        parts.append(tags["addr:city"])
        
    if parts:
        return ", ".join(parts)
    return None

@router.get("/stores/nearby", response_model=NearbyStoresResponse)
def get_nearby_stores(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius: int = Query(5000, description="Search radius in meters")
):
    if radius not in [5000, 10000, 25000]:
        raise HTTPException(status_code=400, detail="Invalid radius. Allowed values are 5000, 10000, 25000.")
        
    query = build_overpass_query(lat, lng, radius)
    data = query.encode("utf-8")
    
    result = None
    last_error = None
    
    for url in OVERPASS_URLS:
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("User-Agent", USER_AGENT)
        req.add_header("Content-Type", "application/x-www-form-urlencoded")
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode("utf-8"))
                break # Success
        except urllib.error.URLError as e:
            last_error = e
            continue
        except Exception as e:
            last_error = e
            continue
            
    if result is None:
        if isinstance(last_error, urllib.error.URLError):
            raise HTTPException(status_code=503, detail="Nearby store data is temporarily unavailable.")
        else:
            raise HTTPException(status_code=500, detail="Internal server error while fetching store data.")
        
    elements = result.get("elements", [])
    
    parsed_stores = []
    for el in elements:
        tags = el.get("tags", {})
        
        # Only include elements with a name, or fall back to generic name if we want to be generous
        # It's better to show them even if unnamed, we can just say "Agricultural supply store"
        el_type = el.get("type", "node")
        el_id = el.get("id")
        osm_id = f"osm-{el_type}-{el_id}"
        
        # Coordinates
        if el_type == "node":
            store_lat = el.get("lat")
            store_lon = el.get("lon")
        else:
            center = el.get("center", {})
            store_lat = center.get("lat")
            store_lon = center.get("lon")
            
        if store_lat is None or store_lon is None:
            continue
            
        distance = haversine(lat, lng, store_lat, store_lon)
        
        shop_type = tags.get("shop", "")
        if shop_type == "agrarian":
            category = "Agricultural supply"
        elif shop_type == "garden_centre":
            category = "Garden center"
        else:
            category = "Agricultural supply"
            
        name = tags.get("name") or category
            
        store = Store(
            id=osm_id,
            name=name,
            category=category,
            address=format_address(tags),
            latitude=store_lat,
            longitude=store_lon,
            distance_meters=round(distance, 1),
            phone=tags.get("phone") or tags.get("contact:phone"),
            website=tags.get("website") or tags.get("contact:website"),
            opening_hours=tags.get("opening_hours")
        )
        parsed_stores.append(store)
        
    # Sort by distance
    parsed_stores.sort(key=lambda s: s.distance_meters)
    
    return NearbyStoresResponse(
        location=Location(latitude=lat, longitude=lng),
        radius_meters=radius,
        stores=parsed_stores
    )
