import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { faceService } from '../../services'
import { useFaceStore } from '../../store'
import { Toast, Button, Alert, LoadingSpinner, Skeleton } from '../ui'
import { CheckCircle, Camera } from 'lucide-react'

export const FaceEnrollment = () => {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [hasPermission, setHasPermission] = useState(false)
  const { enrollmentProgress, setEnrollmentProgress, setEnrollmentError, resetEnrollment } = useFaceStore()
  const [isCapturing, setIsCapturing] = useState(false)
  const [enrollmentStatus, setEnrollmentStatus] = useState('idle') // idle, in_progress, completed

  useEffect(() => {
    startEnrollment()
    requestCameraPermission()
  }, [])

  const startEnrollment = async () => {
    try {
      const response = await faceService.startEnrollment()
      Toast.info(`Enrollment started. Capture ${response.images_required} images.`)
    } catch (error) {
      Toast.error('Failed to start enrollment')
      setEnrollmentError(error.message)
    }
  }

  const requestCameraPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'user', width: { ideal: 640 }, height: { ideal: 480 } },
      })
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        setHasPermission(true)
      }
    } catch (error) {
      Toast.error('Camera permission denied')
      setEnrollmentError('Camera access required')
    }
  }

  const captureImage = async () => {
    if (!videoRef.current || !canvasRef.current) return

    setIsCapturing(true)
    try {
      const context = canvasRef.current.getContext('2d')
      canvasRef.current.width = videoRef.current.videoWidth
      canvasRef.current.height = videoRef.current.videoHeight
      context.drawImage(videoRef.current, 0, 0)
      const imageData = canvasRef.current.toDataURL('image/jpeg')

      const response = await faceService.captureEnrollmentImage(imageData)
      setEnrollmentProgress(response.progress.images_captured)

      Toast.success(response.message)

      if (response.progress.enrollment_complete) {
        setEnrollmentStatus('completed')
        await completeEnrollment()
      }
    } catch (error) {
      Toast.error('Image capture failed')
    } finally {
      setIsCapturing(false)
    }
  }

  const completeEnrollment = async () => {
    try {
      const response = await faceService.completeEnrollment()
      Toast.success('Face enrollment completed successfully!')
      setEnrollmentStatus('completed')
    } catch (error) {
      Toast.error('Enrollment completion failed')
      setEnrollmentError(error.message)
    }
  }

  if (!hasPermission) {
    return (
      <Alert
        variant="error"
        title="Camera Access Required"
        message="Please enable camera access for face enrollment"
        dismissible={false}
      />
    )
  }

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold mb-2">Face Enrollment</h1>
        <p className="text-gray-600 dark:text-gray-400">
          Capture face images for biometric authentication
        </p>
      </motion.div>

      <div className="glassmorphism rounded-lg p-6 space-y-4">
        <div className="relative bg-black rounded-lg overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className="w-full aspect-video object-cover"
          />
          <div className="absolute inset-0 border-4 border-blue-500 opacity-50" />
        </div>
        <canvas ref={canvasRef} className="hidden" />

        <div className="space-y-2">
          <div className="flex justify-between text-sm">
            <span>Progress</span>
            <span>{enrollmentProgress} / 15</span>
          </div>
          <div className="w-full h-3 bg-gray-300 dark:bg-gray-700 rounded-full overflow-hidden">
            <motion.div
              animate={{ width: `${(enrollmentProgress / 15) * 100}%` }}
              transition={{ duration: 0.5 }}
              className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
            />
          </div>
        </div>

        <Button
          onClick={captureImage}
          disabled={isCapturing || enrollmentStatus === 'completed'}
          className="w-full"
        >
          <Camera size={20} />
          {isCapturing ? 'Capturing...' : 'Capture Image'}
        </Button>

        {enrollmentStatus === 'completed' && (
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            className="flex items-center justify-center gap-2 text-green-500"
          >
            <CheckCircle size={24} />
            <span>Enrollment Completed!</span>
          </motion.div>
        )}
      </div>

      <div className="glassmorphism rounded-lg p-4 space-y-3">
        <h3 className="font-semibold">Tips for Better Results:</h3>
        <ul className="space-y-2 text-sm text-gray-700 dark:text-gray-300">
          <li>✓ Ensure good lighting on your face</li>
          <li>✓ Capture face from different angles</li>
          <li>✓ Avoid shadows and glare</li>
          <li>✓ Keep your face centered in frame</li>
          <li>✓ Natural expressions work best</li>
        </ul>
      </div>
    </div>
  )
}

export default FaceEnrollment
