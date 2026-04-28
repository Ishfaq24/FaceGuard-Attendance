import { useState } from 'react'
import { faceService } from '../services'
import { useFaceStore } from '../store'
import { Toast } from '../components/ui'

export const useFace = () => {
  const { enrollmentProgress, setEnrollmentProgress, setEnrollmentError } = useFaceStore()
  const [isLoading, setIsLoading] = useState(false)
  const [enrollmentStep, setEnrollmentStep] = useState('idle') // idle, capturing, processing, completed

  const startEnrollment = async () => {
    setIsLoading(true)
    try {
      const response = await faceService.startEnrollment()
      setEnrollmentStep('capturing')
      Toast.info(`Capture ${response.images_required} images`)
      return response
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to start enrollment'
      setEnrollmentError(message)
      Toast.error(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const captureImage = async (imageData) => {
    setIsLoading(true)
    try {
      setEnrollmentStep('processing')
      const response = await faceService.captureEnrollmentImage(imageData)
      setEnrollmentProgress(response.progress.images_captured)
      Toast.success('Image captured successfully')
      return response
    } catch (err) {
      const message = err.response?.data?.detail || 'Image capture failed'
      setEnrollmentError(message)
      Toast.error(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const completeEnrollment = async () => {
    setIsLoading(true)
    try {
      const response = await faceService.completeEnrollment()
      setEnrollmentStep('completed')
      Toast.success('Face enrollment completed!')
      return response
    } catch (err) {
      const message = err.response?.data?.detail || 'Enrollment completion failed'
      setEnrollmentError(message)
      Toast.error(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  const verifyFace = async (imageData) => {
    setIsLoading(true)
    try {
      const response = await faceService.verifyFace(imageData)
      return response
    } catch (err) {
      const message = err.response?.data?.detail || 'Face verification failed'
      setEnrollmentError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }

  return {
    enrollmentProgress,
    enrollmentStep,
    isLoading,
    startEnrollment,
    captureImage,
    completeEnrollment,
    verifyFace,
  }
}

export default useFace
