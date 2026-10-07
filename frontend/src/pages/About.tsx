import Reveal from '../components/Reveal'

export default function About() {
  return (
    <div className="container-shell max-w-2xl mx-auto py-16">
      <Reveal delay={0.1}>
        <h2 className="font-display text-3xl mb-5">Methodology</h2>
        <p className="text-cream-dim leading-relaxed mb-4">
          AgriScan is an AI-assisted crop disease screening and decision-support system.
          The current model is trained/evaluated using PlantVillage.
        </p>
      </Reveal>

      <Reveal delay={0.2}>
        <h4 className="font-display text-lg mt-7 mb-2">Explainability</h4>
        <p className="text-cream-dim leading-relaxed mb-4">
          Every diagnosis is paired with a Grad-CAM heatmap, showing exactly which region of the
          leaf drove the model's decision — so the result is legible, not a black box.
        </p>
      </Reveal>

      <Reveal delay={0.3}>
        <h4 className="font-display text-lg mt-7 mb-2">Known limitations</h4>
        <div className="bg-forest-2/60 backdrop-blur-md border-l-[3px] border-gold rounded-r-lg p-5 text-sm text-cream-dim leading-relaxed">
          PlantVillage contains controlled image conditions. Real-world field images can differ due to:
          <ul className="list-disc pl-5 mt-2 mb-2">
            <li>lighting</li>
            <li>background</li>
            <li>camera quality</li>
            <li>disease stage</li>
            <li>crop variety</li>
            <li>environmental conditions</li>
            <li>multiple simultaneous diseases</li>
          </ul>
          Therefore benchmark performance does not guarantee equivalent field performance.
          <br /><br />
          <strong>Important Note:</strong> Results should be treated as decision support rather than a guaranteed diagnosis. 
          Treatment decisions should be verified using qualified agricultural professionals and locally applicable agricultural guidance.
        </div>
      </Reveal>
    </div>
  )
}

