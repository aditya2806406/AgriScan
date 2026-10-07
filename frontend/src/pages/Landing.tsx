import { Link } from 'react-router-dom'
import Reveal from '../components/Reveal'

export default function Landing() {
  return (
    <div className="container-shell">
      <div className="grid md:grid-cols-[1.1fr_0.9fr] gap-12 items-center py-20">
        <Reveal direction="left" delay={0.1}>
          <h1 className="font-display font-semibold text-4xl md:text-5xl leading-tight max-w-[14ch] mb-5">
            Know what's on your leaf before it spreads.
          </h1>
          <p className="text-cream-dim text-lg leading-relaxed max-w-[46ch] mb-7">
            Photograph a crop leaf and get an instant diagnosis, a visual explanation of what the
            model saw, and clear treatment steps — organic or chemical.
          </p>
          <div className="flex gap-3">
            <Link to="/scan" className="bg-gold text-forest px-6 py-3 rounded-md font-semibold text-sm">
              Scan a leaf
            </Link>
            <Link to="/about" className="border border-white/15 px-6 py-3 rounded-md text-sm">
              How it works
            </Link>
          </div>
        </Reveal>
        <Reveal direction="right" delay={0.2} className="flex justify-center">
          <svg width="220" height="220" viewBox="0 0 220 220" fill="none">
            <path d="M110 30C160 30 190 70 190 120C190 170 150 195 110 195C70 195 30 170 30 120C30 70 60 30 110 30Z" fill="#2B4A33" stroke="#7FA37A" strokeWidth="2" />
            <path d="M110 45V185" stroke="#7FA37A" strokeWidth="1.5" opacity="0.6" />
            <circle cx="95" cy="105" r="7" fill="#A6503E" opacity="0.85" />
            <circle cx="130" cy="140" r="5" fill="#A6503E" opacity="0.7" />
            <circle cx="105" cy="150" r="4" fill="#A6503E" opacity="0.6" />
          </svg>
        </Reveal>
      </div>

      <div className="grid md:grid-cols-3 gap-px bg-white/10 border border-white/10 rounded-lg overflow-hidden mb-20">
        <Reveal delay={0.3} className="bg-forest-2/60 backdrop-blur-md p-6 h-full">
          <div className="font-mono text-2xl">38</div>
          <div className="text-sm text-cream-dim mt-1">crop-disease classes across 14 species</div>
        </Reveal>
        <Reveal delay={0.4} className="bg-forest-2/60 backdrop-blur-md p-6 h-full">
          <div className="font-mono text-2xl">Grad-CAM</div>
          <div className="text-sm text-cream-dim mt-1">shows exactly what the model looked at</div>
        </Reveal>
        <Reveal delay={0.5} className="bg-forest-2/60 backdrop-blur-md p-6 h-full">
          <div className="font-mono text-2xl">2 models</div>
          <div className="text-sm text-cream-dim mt-1">baseline vs. tuned, compared honestly</div>
        </Reveal>
      </div>
    </div>
  )
}
