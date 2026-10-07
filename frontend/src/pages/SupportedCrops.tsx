import { useEffect, useState } from 'react'
import { getSupportedClasses } from '../api/client'
import { parseClassName } from '../utils/parseClassName'
import Reveal from '../components/Reveal'

export default function SupportedCrops() {
  const [classes, setClasses] = useState<string[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getSupportedClasses()
      .then(res => setClasses(res.classes))
      .catch(err => console.error("Failed to load supported classes", err))
      .finally(() => setLoading(false))
  }, [])

  // Group classes by crop
  const grouped = classes.reduce((acc, cls) => {
    const { crop, condition } = parseClassName(cls)
    if (!acc[crop]) acc[crop] = []
    acc[crop].push(condition)
    return acc
  }, {} as Record<string, string[]>)

  return (
    <div className="container-shell py-16">
      <Reveal direction="up">
        <h2 className="font-display text-3xl mb-2 text-center">Supported Crops</h2>
        <p className="text-cream-dim text-center mb-10 max-w-2xl mx-auto">
          AgriScan's AI model is trained on the PlantVillage dataset and can recognize the following conditions across 14 crops.
        </p>
      </Reveal>

      {loading ? (
        <div className="text-center text-cream-dim">Loading supported crops...</div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Object.entries(grouped).sort(([a], [b]) => a.localeCompare(b)).map(([crop, conditions], idx) => (
            <Reveal key={crop} direction="up" delay={0.1 + idx * 0.05}>
              <div className="bg-forest-2/60 backdrop-blur-md border border-white/10 rounded-lg p-5">
                <h3 className="font-display text-xl text-gold mb-3 border-b border-white/10 pb-2">{crop}</h3>
                <ul className="list-disc pl-5 text-sm text-cream-dim space-y-1">
                  {conditions.sort().map((cond, i) => (
                    <li key={i}>{cond}</li>
                  ))}
                </ul>
              </div>
            </Reveal>
          ))}
        </div>
      )}
    </div>
  )
}
