import { useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap, useMapEvents } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'
import L from 'leaflet'
import Reveal from '../components/Reveal'
import { getNearbyStores, Store } from '../api/client'

// Fix for default marker icon in Vite/Leaflet
import icon from 'leaflet/dist/images/marker-icon.png'
import iconShadow from 'leaflet/dist/images/marker-shadow.png'
import iconRetina from 'leaflet/dist/images/marker-icon-2x.png'

const DefaultIcon = L.icon({
  iconUrl: icon,
  iconRetinaUrl: iconRetina,
  shadowUrl: iconShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28],
  shadowSize: [41, 41]
})
L.Marker.prototype.options.icon = DefaultIcon

const SelectedIcon = L.divIcon({
  html: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="#ef4444" stroke="#7f1d1d" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="width:32px;height:32px;margin-left:-16px;margin-top:-32px;"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>`,
  className: '',
  iconSize: [0, 0],
  iconAnchor: [0, 0],
})

function ChangeView({ center, zoom }: { center: [number, number]; zoom: number }) {
  const map = useMap()
  map.setView(center, zoom)
  return null
}

function MapClickHandler({ onLocationSelect }: { onLocationSelect: (latlng: [number, number]) => void }) {
  useMapEvents({
    click(e) {
      onLocationSelect([e.latlng.lat, e.latlng.lng])
    },
  })
  return null
}

export default function StoreLocator() {
  const [selectionMode, setSelectionMode] = useState<'prompt' | 'my_location' | 'manual'>('prompt')
  
  // Confirmed search center
  const [location, setLocation] = useState<[number, number] | null>(null)
  
  // Temporary selected center for manual mode
  const [selectedLocation, setSelectedLocation] = useState<[number, number] | null>(null)
  
  const [radius, setRadius] = useState<number>(5000)
  const [stores, setStores] = useState<Store[]>([])
  
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [permissionState, setPermissionState] = useState<'prompt' | 'granted' | 'denied'>('prompt')

  const fetchStores = async (lat: number, lng: number, rad: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getNearbyStores(lat, lng, rad)
      setStores(data.stores)
    } catch (err: any) {
      setError(err.message || "Nearby store data is temporarily unavailable.")
    } finally {
      setLoading(false)
    }
  }

  const handleUseLocation = () => {
    if (!navigator.geolocation) {
      setError("Geolocation is not supported by your browser.")
      return
    }

    setSelectionMode('my_location')
    setLoading(true)
    setError(null)

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setPermissionState('granted')
        const { latitude, longitude } = position.coords
        setLocation([latitude, longitude])
        fetchStores(latitude, longitude, radius)
      },
      (err) => {
        setLoading(false)
        setPermissionState('denied')
        if (err.code === err.PERMISSION_DENIED) {
          setError("Location access was denied. Allow location access to find nearby stores.")
        } else {
          setError("Unable to retrieve your location.")
        }
      }
    )
  }

  const handleManualSelectionStart = () => {
    setSelectionMode('manual')
    setError(null)
  }

  const handleSearchHere = () => {
    if (selectedLocation) {
      setLocation(selectedLocation)
      fetchStores(selectedLocation[0], selectedLocation[1], radius)
    }
  }

  const handleRadiusChange = (newRadius: number) => {
    setRadius(newRadius)
    // Only search if we already have a confirmed location
    if (location) {
      fetchStores(location[0], location[1], newRadius)
    }
  }

  const handleStoreClick = (storeLat: number, storeLon: number) => {
    // Optional cleanly synced marker-focus function could be added here
    // For now, map relies on user interaction
  }

  // India default center for manual map selection if location is empty
  const defaultCenter: [number, number] = [20.5937, 78.9629]
  const defaultZoom = 5
  
  // The center to pass to the MapContainer based on current state
  const currentCenter = location || selectedLocation || defaultCenter
  const mapZoom = location || selectedLocation ? (radius === 5000 ? 13 : radius === 10000 ? 12 : 11) : defaultZoom

  return (
    <div className="container-shell py-16">
      <Reveal delay={0.1}>
        <h2 className="font-display text-3xl mb-2">Nearby input stores</h2>
        <p className="text-cream-dim mb-6">
          Find agricultural stores near you. Store information is sourced from OpenStreetMap and may be incomplete or outdated.
        </p>
      </Reveal>

      <Reveal delay={0.2} direction="up">
        {selectionMode === 'prompt' && !loading && !error && (
          <div className="bg-forest-2/60 backdrop-blur-md border border-white/10 rounded-lg p-8 text-center mb-6">
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button
                onClick={handleUseLocation}
                className="bg-gold text-forest font-semibold py-3 px-6 rounded-full hover:bg-white transition-colors"
              >
                Use My Location
              </button>
              <button
                onClick={handleManualSelectionStart}
                className="bg-forest border border-gold text-gold font-semibold py-3 px-6 rounded-full hover:bg-gold hover:text-forest transition-colors"
              >
                Select Location on Map
              </button>
            </div>
          </div>
        )}

        {loading && (
          <div className="bg-forest-2/60 backdrop-blur-md border border-white/10 rounded-lg p-8 text-center mb-6 animate-pulse">
            <p className="text-cream">Finding nearby agricultural stores...</p>
          </div>
        )}

        {error && (
          <div className="bg-red-900/40 border border-red-500/50 rounded-lg p-6 text-center mb-6">
            <p className="text-red-200 mb-4">{error}</p>
            <button
              onClick={() => {
                setError(null)
                setSelectionMode('prompt')
                setPermissionState('prompt')
              }}
              className="bg-white/10 text-white font-semibold py-2 px-6 rounded hover:bg-white/20 transition-colors"
            >
              Try Again
            </button>
          </div>
        )}

        {/* Show map if we have a confirmed location, OR if we are in manual mode (even if no selection yet) */}
        {(location || selectionMode === 'manual') && !error && (
          <div className="mb-6 rounded-lg overflow-hidden border border-white/10 relative z-0 flex flex-col">
            <div className="h-80 w-full relative">
              <MapContainer
                center={currentCenter}
                zoom={mapZoom}
                style={{ height: '100%', width: '100%', backgroundColor: '#1a2e22' }}
              >
                <ChangeView center={currentCenter} zoom={mapZoom} />
                {selectionMode === 'manual' && <MapClickHandler onLocationSelect={setSelectedLocation} />}
                
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                
                {/* Confirmed Location Marker (Only if not using a distinct selected marker overriding it) */}
                {location && (!selectedLocation || location !== selectedLocation) && (
                  <Marker position={location} icon={SelectedIcon}>
                    <Popup>Search Center</Popup>
                  </Marker>
                )}

                {/* Temporary Selected Location Marker */}
                {selectedLocation && (
                  <Marker position={selectedLocation} icon={SelectedIcon}>
                    <Popup>Selected search location</Popup>
                  </Marker>
                )}

                {/* Store Markers */}
                {stores.map((store) => (
                  <Marker key={store.id} position={[store.latitude, store.longitude]}>
                    <Popup>
                      <div className="flex flex-col min-w-[200px] text-gray-800">
                        <div className="font-semibold text-base leading-tight mb-1">{store.name}</div>
                        <div className="text-xs text-gray-500 mb-2">{store.category}</div>
                        
                        <div className="text-xs text-blue-600 font-medium mb-2">
                          📍 {store.distance_meters >= 1000 
                            ? `${(store.distance_meters / 1000).toFixed(1)} km away` 
                            : `${store.distance_meters} m away`}
                        </div>
                        
                        {store.address && (
                          <div className="text-xs mb-2">
                            <span className="font-semibold text-gray-700">📌 Address</span><br/>
                            {store.address}
                          </div>
                        )}
                        
                        {store.phone && (
                          <div className="text-xs mb-1">
                            📞 {store.phone}
                          </div>
                        )}
                        
                        {store.opening_hours && (
                          <div className="text-xs mb-2">
                            🕒 {store.opening_hours}
                          </div>
                        )}

                        <div className="mt-2 pt-2 border-t border-gray-200 flex flex-wrap gap-1.5">
                          {location && (
                            <a
                              href={`https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=${location[0]}%2C${location[1]}%3B${store.latitude}%2C${store.longitude}`}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[11px] bg-blue-50 text-blue-700 px-2 py-1 rounded border border-blue-200 no-underline hover:bg-blue-100"
                            >
                              Directions
                            </a>
                          )}
                          {store.phone && (
                            <a
                              href={`tel:${store.phone}`}
                              className="text-[11px] bg-gray-50 text-gray-700 px-2 py-1 rounded border border-gray-200 no-underline hover:bg-gray-100"
                            >
                              Call
                            </a>
                          )}
                          {store.website && (
                            <a
                              href={store.website}
                              target="_blank"
                              rel="noreferrer"
                              className="text-[11px] bg-gray-50 text-gray-700 px-2 py-1 rounded border border-gray-200 no-underline hover:bg-gray-100"
                            >
                              Website
                            </a>
                          )}
                        </div>
                      </div>
                    </Popup>
                  </Marker>
                ))}
              </MapContainer>
            </div>
            
            {/* Search Controls for Manual Mode */}
            {selectionMode === 'manual' && selectedLocation && !loading && (
              <div className="bg-forest-2 p-4 flex justify-between items-center border-t border-white/10">
                <div className="text-sm text-cream-dim">
                  Selected search location
                </div>
                <button
                  onClick={handleSearchHere}
                  className="bg-gold text-forest font-semibold py-2 px-4 rounded hover:bg-white transition-colors"
                >
                  Search Stores Here
                </button>
              </div>
            )}
            
            {selectionMode === 'manual' && !selectedLocation && !loading && (
              <div className="bg-forest-2 p-4 text-center text-cream-dim border-t border-white/10">
                Click anywhere on the map to select a location
              </div>
            )}
          </div>
        )}
      </Reveal>

      {(location || selectionMode === 'manual') && !error && (
        <Reveal delay={0.3} direction="up">
          <div className="flex justify-center gap-4 mb-8">
            <button
              onClick={() => handleRadiusChange(5000)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                radius === 5000 ? 'bg-gold text-forest' : 'bg-forest-2/60 text-cream hover:bg-forest-2'
              }`}
            >
              5 km
            </button>
            <button
              onClick={() => handleRadiusChange(10000)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                radius === 10000 ? 'bg-gold text-forest' : 'bg-forest-2/60 text-cream hover:bg-forest-2'
              }`}
            >
              10 km
            </button>
            <button
              onClick={() => handleRadiusChange(25000)}
              className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
                radius === 25000 ? 'bg-gold text-forest' : 'bg-forest-2/60 text-cream hover:bg-forest-2'
              }`}
            >
              25 km
            </button>
          </div>

          {!loading && location && stores.length === 0 && (
            <div className="text-center text-cream-dim py-8">
              No agricultural stores were found within {radius / 1000} km of this location. Search a larger area.
            </div>
          )}

          <div className="grid md:grid-cols-2 gap-4">
            {stores.map((store, i) => (
              <Reveal key={store.id} delay={0.1 + (i % 5) * 0.1} direction="up">
                <div 
                  className="bg-forest-2/60 backdrop-blur-md border border-white/10 rounded-lg p-5 flex flex-col h-full cursor-pointer hover:border-gold/30 transition-colors"
                  onClick={() => handleStoreClick(store.latitude, store.longitude)}
                >
                  <div className="font-semibold text-lg mb-1">{store.name}</div>
                  <div className="text-sm text-gold mb-3">
                    {store.distance_meters >= 1000 
                      ? `${(store.distance_meters / 1000).toFixed(1)} km away` 
                      : `${store.distance_meters} m away`} 
                    <span className="text-cream-dim ml-2">— {store.category}</span>
                  </div>
                  
                  {store.address && (
                    <div className="text-sm text-cream mb-2 opacity-90">
                      📍 {store.address}
                    </div>
                  )}
                  {store.opening_hours && (
                    <div className="text-sm text-cream mb-2 opacity-80">
                      🕒 {store.opening_hours}
                    </div>
                  )}

                  <div className="mt-auto pt-4 flex flex-wrap gap-2">
                    {location && (
                      <a
                        href={`https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=${location[0]}%2C${location[1]}%3B${store.latitude}%2C${store.longitude}`}
                        target="_blank"
                        rel="noreferrer"
                        className="bg-white/10 hover:bg-white/20 text-xs px-3 py-1.5 rounded transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Directions
                      </a>
                    )}
                    {store.phone && (
                      <a
                        href={`tel:${store.phone}`}
                        className="bg-white/10 hover:bg-white/20 text-xs px-3 py-1.5 rounded transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Call
                      </a>
                    )}
                    {store.website && (
                      <a
                        href={store.website}
                        target="_blank"
                        rel="noreferrer"
                        className="bg-white/10 hover:bg-white/20 text-xs px-3 py-1.5 rounded transition-colors"
                        onClick={(e) => e.stopPropagation()}
                      >
                        Website
                      </a>
                    )}
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </Reveal>
      )}
    </div>
  )
}
