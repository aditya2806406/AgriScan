import { Navigate, Link } from 'react-router-dom'
import { useDiagnosis } from '../api/DiagnosisContext'
import TreatmentCard from '../components/TreatmentCard'
import Reveal from '../components/Reveal'
import { parseClassName } from '../utils/parseClassName'
import { generateReport } from '../api/client'
import { useState } from 'react'

export default function Result() {
  const { result, leafPreviewUrl } = useDiagnosis()
  const [isGeneratingReport, setIsGeneratingReport] = useState(false)
  const [reportError, setReportError] = useState<string | null>(null)

  const handleDownloadReport = async () => {
    if (!result || !result.scan_id || isGeneratingReport) return
    setIsGeneratingReport(true)
    setReportError(null)
    try {
      await generateReport(result)
    } catch (err: any) {
      setReportError('Unable to generate the report. Please try again.')
    } finally {
      setIsGeneratingReport(false)
    }
  }

  // If someone lands here directly without having scanned anything, send them back.
  if (!result) {
    return <Navigate to="/scan" replace />
  }

  if (result.prediction_status === 'image_quality_failed') {
    return (
      <div className="container-shell py-16">
        <Reveal direction="up">
          <div className="bg-brick/10 border border-brick/30 rounded-lg p-7 max-w-2xl mx-auto text-center">
            <h3 className="font-display text-2xl text-brick mb-4">Image Quality Issue</h3>
            <p className="text-cream-dim mb-4">
              We couldn't analyze the image for the following reasons:
            </p>
            <ul className="text-sm text-left inline-block mb-6 list-disc pl-5 text-cream-dim">
              {result.image_quality?.issues.map((issue, idx) => (
                <li key={idx} className="mb-1">{issue}</li>
              ))}
            </ul>
            <div className="mt-4">
              <Link to="/scan" className="btn-primary inline-block">Upload a New Image</Link>
            </div>
          </div>
        </Reveal>
      </div>
    )
  }

  const confidencePct = result.confidence ? Math.round(result.confidence * 100) : 0
  const parsedClass = result.disease ? parseClassName(result.disease) : null

  return (
    <div className="container-shell py-16">
      {result.prediction_status === 'low_confidence' && (
        <Reveal direction="up" delay={0.05}>
          <div className="mb-6 bg-brick/10 border border-brick/30 rounded-lg p-5">
            <h4 className="font-display text-xl text-brick mb-2">Low-confidence prediction</h4>
            <p className="text-sm text-cream-dim">
              This image may belong to a crop or disease outside AgriScan's currently supported dataset. 
              Upload a clear image of a supported crop for a more reliable diagnosis.
            </p>
          </div>
        </Reveal>
      )}

      <div className="grid md:grid-cols-2 gap-10">
        <Reveal direction="left" delay={0.1}>
          <div className="bg-forest-2/60 backdrop-blur-md border border-white/10 rounded-lg p-5">
          {result.gradcam && (
            <img
              src={import.meta.env.VITE_API_BASE_URL ? `${import.meta.env.VITE_API_BASE_URL}${result.gradcam}` : `http://localhost:8000${result.gradcam}`}
              alt="Leaf with Grad-CAM heatmap overlay"
              className="rounded-md w-full"
            />
          )}
          <div className="font-mono text-xs text-cream-dim mt-3">
            The highlighted regions show areas that influenced the model's prediction. This visualization explains model attention and does not guarantee that the diagnosis is correct.
          </div>
        </div>
        </Reveal>

        <Reveal direction="right" delay={0.2}>
          <div className="bg-forest-2/60 backdrop-blur-md border border-white/10 rounded-lg p-7">
          <div className="font-mono text-xs text-cream-dim">
            {result.prediction_status === 'low_confidence' ? 'POSSIBLE MATCH' : 'DIAGNOSIS'}
          </div>
          {parsedClass && (
            <h3 className="font-display text-2xl mt-1 mb-3">
              {parsedClass.crop} <span className="opacity-60">—</span> {parsedClass.condition}
            </h3>
          )}

          <div className="flex items-center gap-3 mb-2">
            <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
              <div className="h-full bg-brick rounded-full" style={{ width: `${confidencePct}%` }} />
            </div>
            <div className="font-mono text-sm">Model confidence: {confidencePct}%</div>
          </div>

          {result.predictions && result.predictions.length > 0 && (
            <div className="mt-4 mb-6">
              <div className="font-mono text-xs text-cream-dim mb-2">
                {result.prediction_status === 'low_confidence' ? 'POSSIBLE MATCHES' : 'TOP PREDICTIONS'}
              </div>
              <div className="flex flex-col gap-2">
                {result.predictions.map((p, idx) => {
                  const pParsed = parseClassName(p.disease)
                  return (
                    <div key={idx} className="flex justify-between text-sm">
                      <span>{pParsed.crop} - {pParsed.condition}</span>
                      <span className="font-mono opacity-80">{Math.round(p.confidence)}%</span>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {result.prediction_status === 'low_confidence' ? (
            <div className="mt-6 p-4 border border-white/10 rounded-lg bg-black/20 text-sm text-cream-dim">
              Treatment recommendations are withheld because the diagnosis confidence is low.
            </div>
          ) : (
            result.treatment && <TreatmentCard treatment={result.treatment} />
          )}

          {reportError && (
            <div className="mt-4 text-sm text-brick bg-brick/10 p-3 rounded border border-brick/30">
              {reportError}
            </div>
          )}

          {result.scan_id && (
            <div className="mt-6 text-right">
              <button
                onClick={handleDownloadReport}
                disabled={isGeneratingReport}
                className="bg-gold text-forest font-semibold py-2 px-6 rounded hover:bg-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isGeneratingReport ? 'Generating Report...' : 'Download Report'}
              </button>
            </div>
          )}
          </div>
        </Reveal>
      </div>

      {leafPreviewUrl && (
        <Reveal delay={0.3}>
          <p className="text-xs text-cream-dim mt-6 font-mono">Original upload preserved for this session only.</p>
        </Reveal>
      )}
    </div>
  )
}
