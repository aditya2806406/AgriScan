import { useState, useRef } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { diagnoseLeaf } from '../api/client'
import { useDiagnosis } from '../api/DiagnosisContext'
import Reveal from '../components/Reveal'

export default function Scan() {
  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const { setResult, setLeafPreviewUrl } = useDiagnosis()

  function handleFileSelect(selected: File | null) {
    setError(null)
    setFile(selected)
  }

  async function handleSubmit() {
    if (!file) return
    setLoading(true)
    setError(null)
    try {
      const result = await diagnoseLeaf(file)
      setResult(result)
      setLeafPreviewUrl(URL.createObjectURL(file))
      navigate('/result')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong diagnosing this leaf.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container-shell max-w-xl mx-auto py-16 text-center">
      <Reveal direction="up" delay={0.1}>
        <h2 className="font-display text-3xl mb-2">Scan a leaf</h2>
        <p className="text-cream-dim mb-8">Upload a clear, well-lit photo of the affected leaf.</p>
      </Reveal>

      <Reveal direction="up" delay={0.2}>
        <div
          onClick={() => inputRef.current?.click()}
          className="border border-dashed border-white/20 rounded-xl bg-forest-2/60 backdrop-blur-md py-14 px-6 cursor-pointer hover:border-white/35 transition-colors"
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={(e) => handleFileSelect(e.target.files?.[0] ?? null)}
          />
          {file ? (
            <>
              <div className="text-base mb-1">{file.name}</div>
              <div className="text-sm text-cream-dim">Ready to diagnose — click submit below</div>
            </>
          ) : (
            <>
              <div className="text-base mb-1">Click to choose a photo</div>
              <div className="text-sm text-cream-dim">JPEG, PNG, or WebP</div>
            </>
          )}
        </div>
      </Reveal>

      <Reveal direction="up" delay={0.25}>
        <p className="mt-4 text-sm text-cream-dim">
          AgriScan currently supports 38 crop/disease classes from the PlantVillage dataset.
        </p>
        <p className="mt-1 text-sm">
          <Link to="/supported-crops" className="text-gold underline hover:text-gold/80 transition-colors">
            View supported crops
          </Link>
        </p>
      </Reveal>

      {error && (
        <Reveal delay={0.3}>
          <div className="mt-4 text-sm text-brick bg-brick/10 border border-brick/30 rounded-md py-3 px-4">
            {error}
          </div>
        </Reveal>
      )}

      <Reveal delay={0.4}>
        <button
          onClick={handleSubmit}
          disabled={!file || loading}
          className="mt-6 w-full bg-gold text-forest font-semibold py-3.5 rounded-md disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {loading ? 'Diagnosing…' : 'Diagnose this leaf'}
        </button>
      </Reveal>
    </div>
  )
}
