import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store'
import { authService } from '../../services'
import { Button, Input, Alert, Toast, LoadingSpinner } from '../../components/ui'
import { motion } from 'framer-motion'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [formData, setFormData] = useState({ email: '', password: '' })

  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsLoading(true)
    setError(null)

    try {
      const response = await authService.login(formData.email, formData.password)
      await login(response.user, response.access_token)
      Toast.success('Login successful!')
      navigate(`/${response.user.role}/dashboard`)
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed'
      setError(message)
      Toast.error(message)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glassmorphism rounded-2xl p-8 max-w-md w-full"
      >
        <h1 className="text-4xl font-bold text-center mb-2">FaceGuard</h1>
        <p className="text-center text-gray-600 dark:text-gray-400 mb-8">Smart Attendance Management</p>

        {error && <Alert variant="error" title="Error" message={error} className="mb-4" />}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Email"
            type="email"
            placeholder="your@email.com"
            value={formData.email}
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
            required
            disabled={isLoading}
          />

          <Input
            label="Password"
            type="password"
            placeholder="••••••••"
            value={formData.password}
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
            required
            disabled={isLoading}
          />

          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? <LoadingSpinner size="sm" /> : 'Login'}
          </Button>
        </form>

        <p className="text-center text-sm mt-6 text-gray-600 dark:text-gray-400">
          Don't have an account? <a href="/auth/signup" className="text-blue-500 hover:underline">Sign up</a>
        </p>
      </motion.div>
    </div>
  )
}
