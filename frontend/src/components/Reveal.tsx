import { ReactNode } from 'react'
import { motion } from 'framer-motion'

interface RevealProps {
  children: ReactNode
  delay?: number
  direction?: 'up' | 'left' | 'right'
  className?: string
}

export default function Reveal({
  children,
  delay = 0,
  direction = 'up',
  className = '',
}: RevealProps) {
  let initial = {}
  
  if (direction === 'up') {
    initial = { opacity: 0, y: 40, rotateX: -8 }
  } else if (direction === 'left') {
    initial = { opacity: 0, x: -50, rotateY: 12 }
  } else if (direction === 'right') {
    initial = { opacity: 0, x: 50, rotateY: -12 }
  }

  return (
    <div style={{ perspective: 1000 }} className={className}>
      <motion.div
        initial={initial}
        whileInView={{ opacity: 1, x: 0, y: 0, rotateX: 0, rotateY: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{
          duration: 0.75,
          delay,
          ease: [0.19, 1, 0.22, 1], // easeOutExpo-like curve
        }}
      >
        {children}
      </motion.div>
    </div>
  )
}
