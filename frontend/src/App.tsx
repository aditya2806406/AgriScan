import { BrowserRouter, Routes, Route } from 'react-router-dom'
import React, { Suspense } from 'react'
import Navbar from './components/Navbar'
import Landing from './pages/Landing'
import Scan from './pages/Scan'
import Result from './pages/Result'
import StoreLocator from './pages/StoreLocator'
import About from './pages/About'
import { DiagnosisProvider } from './api/DiagnosisContext'

import SupportedCrops from './pages/SupportedCrops'

const CinematicBackground = React.lazy(() => import('./components/CinematicBackground'))

export default function App() {
  return (
    <DiagnosisProvider>
      <BrowserRouter>
        <Suspense fallback={null}>
          <CinematicBackground />
        </Suspense>
        <Navbar />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/result" element={<Result />} />
          <Route path="/stores" element={<StoreLocator />} />
          <Route path="/about" element={<About />} />
          <Route path="/supported-crops" element={<SupportedCrops />} />
        </Routes>
      </BrowserRouter>
    </DiagnosisProvider>
  )
}
