
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export interface Treatment {
  disease: string
  symptoms: string[]
  organic_management: string[]
  chemical_management: string[]
  prevention: string[]
  caution: string
  sources: string[]
}

export interface ImageQuality {
  acceptable: boolean
  issues: string[]
}

export interface DiagnosisResult {
  filename: string
  image_quality: ImageQuality
  prediction_status: string
  disease?: string
  display_name?: string
  confidence?: number
  predictions?: { disease: string; confidence: number }[]
  gradcam?: string
  is_low_confidence: boolean
  treatment?: Treatment
  scan_id?: number
}

export interface ScanHistoryItem {
  id: number
  disease?: string
  confidence?: number
  prediction_status: string
  created_at: string
}

export async function diagnoseLeaf(file: File): Promise<DiagnosisResult> {
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`${API_BASE}/api/predict`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Diagnosis request failed (${response.status})`)
  }

  return response.json()
}

export async function getScanHistory(limit = 20): Promise<ScanHistoryItem[]> {
  const response = await fetch(`${API_BASE}/api/history?limit=${limit}`)

  if (!response.ok) {
    throw new Error(`Failed to load scan history (${response.status})`)
  }

  return response.json()
}

export async function getSupportedClasses(): Promise<{ classes: string[] }> {
  const response = await fetch(`${API_BASE}/api/supported-classes`)

  if (!response.ok) {
    throw new Error(`Failed to load supported classes (${response.status})`)
  }

  return response.json()
}

export interface StoreLocation {
  latitude: number
  longitude: number
}

export interface Store {
  id: string
  name: string
  category: string
  address?: string
  latitude: number
  longitude: number
  distance_meters: number
  phone?: string
  website?: string
  opening_hours?: string
  source: string
}

export interface NearbyStoresResponse {
  location: StoreLocation
  radius_meters: number
  stores: Store[]
}

interface OverpassElement {
  type: string
  id: number
  lat?: number
  lon?: number
  center?: {
    lat: number
    lon: number
  }
  tags?: Record<string, string>
}

interface OverpassResponse {
  elements?: OverpassElement[]
}

const OVERPASS_ENDPOINTS = [
  'https://overpass-api.de/api/interpreter',
  'https://lz4.overpass-api.de/api/interpreter',
  'https://z.overpass-api.de/api/interpreter',
]

function haversineDistance(
  lat1: number,
  lng1: number,
  lat2: number,
  lng2: number
): number {
  const toRadians = (degrees: number) => degrees * Math.PI / 180
  const dLat = toRadians(lat2 - lat1)
  const dLng = toRadians(lng2 - lng1)

  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLng / 2) ** 2

  const safeA = Math.max(0, Math.min(1, a))

  return 6371000 * 2 * Math.atan2(
    Math.sqrt(safeA),
    Math.sqrt(1 - safeA)
  )
}

function buildStoreQuery(lat: number, lng: number, radius: number): string {
  return `
    [out:json][timeout:15];
    (
      node["shop"="agrarian"](around:${radius},${lat},${lng});
      node["shop"="garden_centre"](around:${radius},${lat},${lng});
      way["shop"="agrarian"](around:${radius},${lat},${lng});
      way["shop"="garden_centre"](around:${radius},${lat},${lng});
      relation["shop"="agrarian"](around:${radius},${lat},${lng});
      relation["shop"="garden_centre"](around:${radius},${lat},${lng});
    );
    out center;
  `
}

function parseOverpassStores(
  elements: OverpassElement[],
  lat: number,
  lng: number,
  radius: number
): Store[] {
  const stores: Store[] = []
  const seenIds = new Set<string>()

  for (const element of elements) {
    const tags = element.tags || {}
    const latitude = element.lat ?? element.center?.lat
    const longitude = element.lon ?? element.center?.lon

    if (latitude == null || longitude == null) continue

    const shopType = tags.shop

    if (shopType !== 'agrarian' && shopType !== 'garden_centre') {
      continue
    }

    const distance = haversineDistance(lat, lng, latitude, longitude)

    if (distance > radius) continue

    const id = `osm-${element.type}-${element.id}`

    if (seenIds.has(id)) continue
    seenIds.add(id)

    const category =
      shopType === 'garden_centre'
        ? 'Garden center'
        : 'Agricultural supply'

    const address = [
      tags['addr:housenumber'],
      tags['addr:street'],
      tags['addr:city'] || tags['addr:town']
    ].filter(Boolean).join(', ')

    stores.push({
      id,
      name: tags.name || category,
      category,
      address: address || undefined,
      latitude,
      longitude,
      distance_meters: Math.round(distance * 10) / 10,
      phone: tags.phone || tags['contact:phone'],
      website: tags.website || tags['contact:website'],
      opening_hours: tags.opening_hours,
      source: 'OpenStreetMap',
    })
  }

  return stores.sort((a, b) => a.distance_meters - b.distance_meters)
}

export async function getNearbyStores(
  lat: number,
  lng: number,
  radius: number
): Promise<NearbyStoresResponse> {
  if (![-90, 90].every((bound) => Number.isFinite(bound))) {
    throw new Error('Invalid coordinates.')
  }

  if (
    !Number.isFinite(lat) ||
    !Number.isFinite(lng) ||
    lat < -90 ||
    lat > 90 ||
    lng < -180 ||
    lng > 180
  ) {
    throw new Error('Invalid location coordinates.')
  }

  if (![5000, 10000, 25000].includes(radius)) {
    throw new Error('Invalid search radius.')
  }

  const query = buildStoreQuery(lat, lng, radius)
  let lastError = 'No Overpass server responded.'

  for (const endpoint of OVERPASS_ENDPOINTS) {
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json',
        },
        body: new URLSearchParams({ data: query }).toString(),
      })

      if (!response.ok) {
        lastError = `Overpass returned HTTP ${response.status}.`
        continue
      }

      const data = await response.json() as OverpassResponse

      if (!Array.isArray(data.elements)) {
        lastError = 'Overpass returned an invalid response.'
        continue
      }

      return {
        location: {
          latitude: lat,
          longitude: lng,
        },
        radius_meters: radius,
        stores: parseOverpassStores(data.elements, lat, lng, radius),
      }
    } catch (error) {
      lastError = error instanceof Error
        ? error.message
        : 'Unknown network error.'
    }
  }

  throw new Error(
    `Unable to load nearby stores. Please try again later. ${lastError}`
  )
}

export async function generateReport(result: DiagnosisResult): Promise<void> {
  if (!result.scan_id) {
    throw new Error('Cannot generate report: missing scan ID.')
  }

  const payload = {
    scan_id: result.scan_id,
    predictions: result.predictions || [],
    gradcam_url: result.gradcam || null,
  }

  const response = await fetch(`${API_BASE}/api/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error(`Failed to generate report (${response.status})`)
  }

  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)

  const disposition = response.headers.get('Content-Disposition')
  let filename = `AgriScan_Report_${new Date().toISOString().split('T')[0]}.pdf`

  if (disposition && disposition.includes('filename="')) {
    const matches = /filename="([^"]+)"/.exec(disposition)

    if (matches?.[1]) {
      filename = matches[1]
    }
  }

  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  window.URL.revokeObjectURL(url)
}
