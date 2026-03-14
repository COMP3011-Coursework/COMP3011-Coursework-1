import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

const links = [
  { to: '/', label: 'Dashboard' },
  { to: '/explorer', label: 'Explorer' },
  { to: '/data-entry', label: 'Data Entry' },
]

export default function NavBar() {
  const location = useLocation()
  const { username, logout } = useAuth()

  return (
    <nav className="bg-gray-900 text-white h-14 flex items-center px-4 gap-6 shrink-0">
      <span className="font-bold text-sm tracking-wide whitespace-nowrap">
        🌍 Food Price Monitor
      </span>
      <div className="flex gap-4 flex-1">
        {links.map(({ to, label }) => (
          <Link
            key={to}
            to={to}
            className={`text-sm px-2 py-1 rounded transition-colors ${
              location.pathname === to
                ? 'bg-white text-gray-900 font-semibold'
                : 'text-gray-300 hover:text-white'
            }`}
          >
            {label}
          </Link>
        ))}
      </div>
      {username && (
        <div className="flex items-center gap-3 text-sm">
          <span className="text-gray-400">{username}</span>
          <button
            onClick={logout}
            className="text-gray-300 hover:text-white transition-colors"
          >
            Log out
          </button>
        </div>
      )}
    </nav>
  )
}
