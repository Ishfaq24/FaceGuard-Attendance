import { useState, useEffect } from 'react'
import { attendanceService } from '../services'
import { Toast } from '../components/ui'

export const useAttendance = () => {
  const [sessions, setSessions] = useState([])
  const [history, setHistory] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchSessions = async () => {
    setIsLoading(true)
    try {
      const response = await attendanceService.getAttendanceHistory()
      setSessions(response)
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to fetch sessions'
      setError(message)
    } finally {
      setIsLoading(false)
    }
  }

  const markAttendance = async (sessionId, imageData, location) => {
    setIsLoading(true)
    try {
      const response = await attendanceService.markAttendance({
        session_id: sessionId,
        image_base64: imageData,
        user_latitude: location.latitude,
        user_longitude: location.longitude,
      })
      Toast.success('Attendance marked successfully!')
      return response
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to mark attendance'
      setError(message)
      Toast.error(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return {
    sessions,
    history,
    isLoading,
    error,
    fetchSessions,
    markAttendance,
  }
}

export default useAttendance
