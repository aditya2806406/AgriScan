import { Treatment } from '../api/client'

export default function TreatmentCard({ treatment }: { treatment: Treatment }) {
  return (
    <div className="mt-2 text-sm text-cream-dim leading-relaxed">
      {treatment.symptoms.length > 0 && (
        <>
          <h4 className="font-display text-gold text-base mt-5 mb-2">Symptoms</h4>
          <ul className="list-disc pl-5 space-y-1">
            {treatment.symptoms.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </>
      )}

      {treatment.organic_management.length > 0 && (
        <>
          <h4 className="font-display text-gold text-base mt-5 mb-2">Organic Management</h4>
          <ul className="list-disc pl-5 space-y-1">
            {treatment.organic_management.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </>
      )}

      {treatment.chemical_management.length > 0 && (
        <>
          <h4 className="font-display text-gold text-base mt-5 mb-2">Chemical Management</h4>
          <ul className="list-disc pl-5 space-y-1">
            {treatment.chemical_management.map((m, i) => <li key={i}>{m}</li>)}
          </ul>
        </>
      )}

      {treatment.prevention.length > 0 && (
        <>
          <h4 className="font-display text-gold text-base mt-5 mb-2">Prevention</h4>
          <ul className="list-disc pl-5 space-y-1">
            {treatment.prevention.map((tip, i) => <li key={i}>{tip}</li>)}
          </ul>
        </>
      )}

      {treatment.caution && (
        <div className="mt-5 p-3 border border-brick/30 bg-brick/10 rounded-md">
          <strong className="text-brick block mb-1">Caution:</strong>
          {treatment.caution}
        </div>
      )}

      {treatment.sources.length > 0 && (
        <div className="mt-5 text-xs opacity-70">
          <strong>Sources:</strong> {treatment.sources.join(', ')}
        </div>
      )}
    </div>
  )
}
