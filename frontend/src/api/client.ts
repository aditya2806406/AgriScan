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
  prediction_status: string // "high_confidence" | "low_confidence" | "image_quality_failed"
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

export async function getNearbyStores(lat: number, lng: number, radius: number): Promise<NearbyStoresResponse> {
  const response = await fetch(`${API_BASE}/api/stores/nearby?lat=${lat}&lng=${lng}&radius=${radius}`)
  if (!response.ok) {
    const body = await response.json().catch(() => ({}))
    throw new Error(body.detail || `Failed to fetch nearby stores (${response.status})`)
  }
  return response.json()
}

export async function generateReport(result: DiagnosisResult): Promise<void> {
  if (!result.scan_id) {
    throw new Error("Cannot generate report: missing scan ID.")
  }

  const payload = {
    scan_id: result.scan_id,
    predictions: result.predictions || [],
    gradcam_url: result.gradcam || null
  }

  const response = await fetch(`${API_BASE}/api/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })

  if (!response.ok) {
    throw new Error(`Failed to generate report (${response.status})`)
  }

  // Create a blob and trigger download
  const blob = await response.blob()
  const url = window.URL.createObjectURL(blob)
  
  // Extract filename from header if possible
  const disposition = response.headers.get('Content-Disposition')
  let filename = `AgriScan_Report_${new Date().toISOString().split('T')[0]}.pdf`
  if (disposition && disposition.includes('filename="')) {
    const matches = /filename="([^"]+)"/.exec(disposition)
    if (matches != null && matches[1]) {
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
