
import json
import math
import urllib.request
import urllib.error
from urllib.parse import urlencode

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(tags=["stores"])

OVERPASS_URLS = [
    "https://overpass-api.de/api/interpreter",
    "https://lz4.overpass-api.de/api/interpreter",
    "https://z.overpass-api.de/api/interpreter",
]

USER_AGENT = "AgriScan/0.1 (Student/Demo Project)"
REQUEST_TIMEOUT = 20


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
    earth_radius = 6371000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    a = max(0.0, min(1.0, a))
    return earth_radius * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def build_overpass_query(lat: float, lng: float, radius: int) -> str:
    return f"""
    [out:json][timeout:15];
    (
      node["shop"="agrarian"](around:{radius},{lat},{lng});
      node["shop"="garden_centre"](around:{radius},{lat},{lng});
      way["shop"="agrarian"](around:{radius},{lat},{lng});
      way["shop"="garden_centre"](around:{radius},{lat},{lng});
      relation["shop"="agrarian"](around:{radius},{lat},{lng});
      relation["shop"="garden_centre"](around:{radius},{lat},{lng});
    );
    out center;
    """


def format_address(tags: dict) -> Optional[str]:
    parts = []

    house_number = tags.get("addr:housenumber")
    street = tags.get("addr:street")

    if house_number and street:
        parts.append(f"{house_number} {street}")
    elif street:
        parts.append(street)

    city = tags.get("addr:city") or tags.get("addr:town")
    if city:
        parts.append(city)

    return ", ".join(parts) if parts else None


@router.get("/stores/nearby", response_model=NearbyStoresResponse)
def get_nearby_stores(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lng: float = Query(..., ge=-180, le=180, description="Longitude"),
    radius: int = Query(5000, description="Search radius in meters"),
):
    if radius not in (5000, 10000, 25000):
        raise HTTPException(
            status_code=400,
            detail="Invalid radius. Allowed values are 5000, 10000, 25000.",
        )

    query = build_overpass_query(lat, lng, radius)
    data = urlencode({"data": query}).encode("utf-8")
    result = None
    errors = []

    for url in OVERPASS_URLS:
        req = urllib.request.Request(
            url,
            data=data,
            method="POST",
            headers={
                "User-Agent": USER_AGENT,
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(
                req, timeout=REQUEST_TIMEOUT
            ) as response:
                result = json.loads(response.read().decode("utf-8"))

            if not isinstance(result, dict) or not isinstance(
                result.get("elements", []), list
            ):
                errors.append(f"{url}: Invalid response format")
                result = None
                continue

            break

        except urllib.error.HTTPError as exc:
            errors.append(f"{url}: HTTP {exc.code}")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            errors.append(f"{url}: {type(exc).__name__}")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            errors.append(f"{url}: Invalid JSON ({type(exc).__name__})")

    if result is None:
        # Keep details in server logs; don't expose upstream errors to clients.
        print("Overpass request failed: " + "; ".join(errors))
        raise HTTPException(
            status_code=503,
            detail="Nearby store data is temporarily unavailable. Please try again.",
        )

    parsed_stores = []
    seen_ids = set()

    for element in result.get("elements", []):
        tags = element.get("tags") or {}
        element_type = element.get("type", "node")
        element_id = element.get("id")

        if element_id is None:
            continue

        store_id = f"osm-{element_type}-{element_id}"

        if store_id in seen_ids:
            continue

        if element_type == "node":
            store_lat = element.get("lat")
            store_lon = element.get("lon")
        else:
            center = element.get("center") or {}
            store_lat = center.get("lat")
            store_lon = center.get("lon")

        if store_lat is None or store_lon is None:
            continue

        try:
            store_lat = float(store_lat)
            store_lon = float(store_lon)
        except (TypeError, ValueError):
            continue

        if not (-90 <= store_lat <= 90 and -180 <= store_lon <= 180):
            continue

        distance = haversine(lat, lng, store_lat, store_lon)

        # Avoid returning elements outside the requested radius.
        if distance > radius:
            continue

        shop_type = tags.get("shop", "")

        if shop_type == "garden_centre":
            category = "Garden center"
        else:
            category = "Agricultural supply"

        store = Store(
            id=store_id,
            name=tags.get("name") or category,
            category=category,
            address=format_address(tags),
            latitude=store_lat,
            longitude=store_lon,
            distance_meters=round(distance, 1),
            phone=tags.get("phone") or tags.get("contact:phone"),
            website=tags.get("website") or tags.get("contact:website"),
            opening_hours=tags.get("opening_hours"),
        )

        parsed_stores.append(store)
        seen_ids.add(store_id)

    parsed_stores.sort(key=lambda store: store.distance_meters)

    return NearbyStoresResponse(
        location=Location(latitude=lat, longitude=lng),
        radius_meters=radius,
        stores=parsed_stores,
    )
