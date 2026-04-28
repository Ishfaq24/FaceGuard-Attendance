import { Navigate } from 'react-router-dom'
import { useAuthStore } from '../store'

export const ProtectedRoute = ({ children, requiredRoles = [] }) => {
  const { user, token } = useAuthStore()

  if (!token || !user) {
    return <Navigate to="/auth/login" replace />
  }

  if (requiredRoles.length > 0 && !requiredRoles.includes(user.role)) {
    return <Navigate to="/" replace />
  }

  return children
}

export default ProtectedRoute
