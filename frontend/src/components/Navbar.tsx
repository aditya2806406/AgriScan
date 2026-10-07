import { NavLink } from 'react-router-dom'

const links = [
  { to: '/', label: 'Home' },
  { to: '/scan', label: 'Scan' },
  { to: '/stores', label: 'Stores' },
  { to: '/about', label: 'About' },
]

export default function Navbar() {
  return (
    <nav className="sticky top-0 z-10 bg-forest/95 backdrop-blur border-b border-white/10">
      <div className="container-shell flex items-center justify-between py-4">
        <div className="font-display text-xl font-semibold flex items-center gap-2">
          <svg viewBox="0 0 24 24" width="22" height="22" fill="none">
            <path d="M4 20C4 12 9 4 20 4C20 15 12 20 4 20Z" fill="#7FA37A" />
            <path d="M4 20C10 16 14 12 18 6" stroke="#1E3626" strokeWidth="1.2" />
          </svg>
          AgriScan
        </div>
        <div className="flex gap-1">
          {links.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              className={({ isActive }) =>
                `px-4 py-2 rounded-md text-sm transition-colors ${
                  isActive ? 'bg-gold text-forest font-medium' : 'text-cream-dim hover:text-cream hover:bg-white/5'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}
