import { Outlet } from 'react-router-dom'
import { useAuthStore } from '../store'
import { useState } from 'react'
import { LogOut, Menu, X } from 'lucide-react'

export default function MainLayout() {
  const { user, logout } = useAuthStore()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  const handleLogout = () => {
    logout()
    window.location.href = '/auth/login'
  }

  return (
    <div className="min-h-screen bg-light dark:bg-dark text-dark dark:text-light">
      {/* Header */}
      <header className="glassmorphism border-b border-white/20 sticky top-0 z-40">
        <div className="flex items-center justify-between px-6 py-4">
          <h1 className="text-2xl font-bold">FaceGuard</h1>
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="md:hidden">
            {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
      </header>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'w-64' : 'w-0'} transition-all duration-300 md:w-64 glassmorphism border-r border-white/20 p-6 space-y-4`}>
          <div className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            {user?.full_name} ({user?.role})
          </div>
          <nav className="space-y-2">
            <a href={`/${user?.role}/dashboard`} className="block px-4 py-2 rounded-lg hover:bg-white/10">Dashboard</a>
            {user?.role === 'student' && (
              <>
                <a href="/student/enroll" className="block px-4 py-2 rounded-lg hover:bg-white/10">Face Enrollment</a>
                <a href="/student/attendance" className="block px-4 py-2 rounded-lg hover:bg-white/10">Mark Attendance</a>
              </>
            )}
          </nav>
          <button onClick={handleLogout} className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-white">
            <LogOut size={18} />
            Logout
          </button>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
