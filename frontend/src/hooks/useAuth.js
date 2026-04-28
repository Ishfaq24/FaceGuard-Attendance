import { useEffect, useState } from 'react'
import { useAuthStore } from '../store'
import { authService, Toast } from '../services'

export const useAuth = () => {
  const { user, token, login, logout, setError } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)

  const signin = async (email, password) => {
    setIsLoading(true)
    try {
      const response = await authService.login(email, password)
      await login(response.user, response.access_token)
      return response
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed'
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const signup = async (userData) => {
    setIsLoading(true)
    try {
      return await authService.signup(userData)
    } catch (err) {
      const message = err.response?.data?.detail || 'Signup failed'
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const signout = async () => {
    try {
      await authService.logout()
    } finally {
      logout()
    }
  }

  const refreshToken = async () => {
    try {
      const response = await authService.refreshToken()
      await login(user, response.access_token)
    } catch (err) {
      logout()
    }
  }

  return {
    user,
    token,
    isLoading,
    signin,
    signup,
    signout,
    refreshToken,
    isAuthenticated: !!token,
  }
}

export default useAuth
