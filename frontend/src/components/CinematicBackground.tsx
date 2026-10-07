import { useEffect, useRef } from 'react'
import * as THREE from 'three'

// Helper to create a soft radial gradient sprite texture
function createParticleTexture() {
  const size = 128
  const canvas = document.createElement('canvas')
  canvas.width = size
  canvas.height = size
  const ctx = canvas.getContext('2d')
  if (!ctx) return null

  const centerX = size / 2
  const centerY = size / 2
  const gradient = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, size / 2)
  gradient.addColorStop(0, 'rgba(255, 255, 255, 1)')
  gradient.addColorStop(0.2, 'rgba(255, 255, 255, 0.8)')
  gradient.addColorStop(0.5, 'rgba(255, 255, 255, 0.2)')
  gradient.addColorStop(1, 'rgba(0, 0, 0, 0)')

  ctx.fillStyle = gradient
  ctx.fillRect(0, 0, size, size)

  const texture = new THREE.CanvasTexture(canvas)
  return texture
}

export default function CinematicBackground() {
  const mountRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Check prefers-reduced-motion
    const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches

    if (!mountRef.current) return

    // Setup Scene, Camera, Renderer
    const scene = new THREE.Scene()
    scene.fog = new THREE.FogExp2('#1E3626', 0.035)

    const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000)
    camera.position.z = 12

    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true })
    renderer.setSize(window.innerWidth, window.innerHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    mountRef.current.appendChild(renderer.domElement)

    // Setup Particle Texture
    const particleTexture = createParticleTexture() || undefined

    const createParticleLayer = (count: number, colorHex: string, size: number) => {
      const geometry = new THREE.BufferGeometry()
      const positions = new Float32Array(count * 3)
      for (let i = 0; i < count * 3; i++) {
        // distribute within a box
        positions[i] = (Math.random() - 0.5) * 40
      }
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))

      const material = new THREE.PointsMaterial({
        color: new THREE.Color(colorHex),
        size,
        map: particleTexture,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
      })

      const points = new THREE.Points(geometry, material)
      scene.add(points)
      return points
    }

    // Create 3 layers of particles
    // Far layer (180 particles, slowest): sage green — #7FA37A
    const farLayer = createParticleLayer(180, '#7FA37A', 0.5)
    // Mid layer (120 particles): gold — #C9963B
    const midLayer = createParticleLayer(120, '#C9963B', 1.0)
    // Near layer (60 particles, fastest, largest): brick/rust — #A6503E
    const nearLayer = createParticleLayer(60, '#A6503E', 1.8)

    // Leaf planes: forest green — #2B4A33, opacity 0.25
    const leaves: THREE.Mesh[] = []
    const leafGeometry = new THREE.PlaneGeometry(3, 4)
    const leafMaterial = new THREE.MeshBasicMaterial({
      color: new THREE.Color('#2B4A33'),
      transparent: true,
      opacity: 0.25,
      side: THREE.DoubleSide,
      depthWrite: false,
    })

    for (let i = 0; i < 6; i++) {
      const leaf = new THREE.Mesh(leafGeometry, leafMaterial)
      leaf.position.set(
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 20,
        (Math.random() - 0.5) * 15 - 5 // mostly behind camera base 12, so -12.5 to +2.5
      )
      leaf.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, Math.random() * Math.PI)
      
      // Add custom userData for animation speeds
      leaf.userData = {
        rotSpeedX: (Math.random() - 0.5) * 0.005,
        rotSpeedY: (Math.random() - 0.5) * 0.005,
        rotSpeedZ: (Math.random() - 0.5) * 0.005,
      }
      scene.add(leaf)
      leaves.push(leaf)
    }

    let currentScrollY = window.scrollY
    let targetScrollY = window.scrollY
    let animationFrameId: number

    const onScroll = () => {
      targetScrollY = window.scrollY
    }

    const onResize = () => {
      camera.aspect = window.innerWidth / window.innerHeight
      camera.updateProjectionMatrix()
      renderer.setSize(window.innerWidth, window.innerHeight)
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    window.addEventListener('resize', onResize)

    const clock = new THREE.Clock()

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate)

      const elapsed = clock.getElapsedTime()

      // If reduced motion, we don't animate the scene time, 
      // but we still want to render to ensure it shows up.
      if (!prefersReducedMotion) {
        // Rotate layers
        farLayer.rotation.y = elapsed * 0.02
        farLayer.rotation.x = elapsed * 0.01

        midLayer.rotation.y = elapsed * 0.03
        midLayer.rotation.z = elapsed * 0.015

        nearLayer.rotation.y = elapsed * 0.05
        nearLayer.rotation.x = elapsed * 0.025

        // Rotate leaves
        leaves.forEach((leaf) => {
          leaf.rotation.x += leaf.userData.rotSpeedX
          leaf.rotation.y += leaf.userData.rotSpeedY
          leaf.rotation.z += leaf.userData.rotSpeedZ
        })
      }

      // Smooth scroll (lerp factor 0.06)
      currentScrollY += (targetScrollY - currentScrollY) * 0.06

      // Camera scroll math
      camera.position.z = 12 - currentScrollY * 0.004
      camera.position.y = -currentScrollY * 0.002
      camera.rotation.y = Math.sin(elapsed * 0.15) * 0.05 + currentScrollY * 0.0002

      renderer.render(scene, camera)
    }

    animate()

    // Cleanup
    return () => {
      cancelAnimationFrame(animationFrameId)
      window.removeEventListener('scroll', onScroll)
      window.removeEventListener('resize', onResize)

      // Dispose geometries & materials
      farLayer.geometry.dispose()
      ;(farLayer.material as THREE.Material).dispose()
      
      midLayer.geometry.dispose()
      ;(midLayer.material as THREE.Material).dispose()
      
      nearLayer.geometry.dispose()
      ;(nearLayer.material as THREE.Material).dispose()

      leafGeometry.dispose()
      leafMaterial.dispose()

      if (particleTexture) particleTexture.dispose()

      renderer.dispose()
      mountRef.current?.removeChild(renderer.domElement)
    }
  }, [])

  return (
    <div
      ref={mountRef}
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: -10,
        pointerEvents: 'none',
      }}
    />
  )
}
