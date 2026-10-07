import { createContext, useContext, useState, ReactNode } from 'react'
import { DiagnosisResult } from '../api/client'

interface DiagnosisContextValue {
  result: DiagnosisResult | null
  setResult: (r: DiagnosisResult | null) => void
  leafPreviewUrl: string | null
  setLeafPreviewUrl: (url: string | null) => void
}

const DiagnosisContext = createContext<DiagnosisContextValue | undefined>(undefined)

export function DiagnosisProvider({ children }: { children: ReactNode }) {
  const [result, setResult] = useState<DiagnosisResult | null>(null)
  const [leafPreviewUrl, setLeafPreviewUrl] = useState<string | null>(null)

  return (
    <DiagnosisContext.Provider value={{ result, setResult, leafPreviewUrl, setLeafPreviewUrl }}>
      {children}
    </DiagnosisContext.Provider>
  )
}

export function useDiagnosis() {
  const ctx = useContext(DiagnosisContext)
  if (!ctx) throw new Error('useDiagnosis must be used within a DiagnosisProvider')
  return ctx
}
