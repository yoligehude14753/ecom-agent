import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  Search,
  FileText,
  Star,
  Eye,
  Megaphone,
  Zap,
  Menu,
  X,
} from 'lucide-react'
import { useState } from 'react'
import { cn } from '@/lib/utils'

const navItems = [
  { to: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
  { to: '/research', icon: Search, label: 'Product Research' },
  { to: '/listing', icon: FileText, label: 'Listing Generator' },
  { to: '/reviews', icon: Star, label: 'Review Analyzer' },
  { to: '/monitor', icon: Eye, label: 'Competitor Monitor' },
  { to: '/ads', icon: Megaphone, label: 'Ad Optimizer' },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  return (
    <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
      {/* Sidebar */}
      <aside
        className={cn(
          'flex flex-col transition-all duration-300 bg-slate-900 border-r border-slate-800',
          sidebarOpen ? 'w-60' : 'w-16',
        )}
      >
        {/* Logo */}
        <div className="flex items-center gap-3 px-4 py-5 border-b border-slate-800">
          <div className="flex-shrink-0 w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          {sidebarOpen && (
            <span className="font-bold text-lg tracking-tight text-white">EcomAgent</span>
          )}
          <button
            onClick={() => setSidebarOpen(v => !v)}
            className="ml-auto text-slate-400 hover:text-white"
          >
            {sidebarOpen ? <X className="w-4 h-4" /> : <Menu className="w-4 h-4" />}
          </button>
        </div>

        {/* Nav items */}
        <nav className="flex-1 py-4 space-y-1 px-2">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                cn(
                  'flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-400 hover:text-white hover:bg-slate-800',
                )
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {sidebarOpen && <span>{label}</span>}
            </NavLink>
          ))}
        </nav>

        {/* Version */}
        {sidebarOpen && (
          <div className="px-4 py-3 border-t border-slate-800 text-xs text-slate-500">
            v1.0.0 · Open Source
          </div>
        )}
      </aside>

      {/* Main content */}
      <main className="flex-1 overflow-auto bg-slate-950">
        <Outlet />
      </main>
    </div>
  )
}
