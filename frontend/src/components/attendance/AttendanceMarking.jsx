import { useState, useRef, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Camera, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { attendanceService } from '../../services'
import { Toast, Button, Alert, LoadingSpinner } from '../ui'

const WebcamCapture = ({ onCapture, isCapturing }) => {
  const videoRef = useRef(null)
  const canvasRef = useRef(null)
  const [hasPermission, setHasPermission] = useState(false)

  useEffect(() => {
    requestCameraPermission()
  }, [])

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
      setHasPermission(false)
    }
  }

  const captureImage = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d')
      canvasRef.current.width = videoRef.current.videoWidth
      canvasRef.current.height = videoRef.current.videoHeight
      context.drawImage(videoRef.current, 0, 0)
      const imageData = canvasRef.current.toDataURL('image/jpeg')
      onCapture(imageData)
    }
  }

  if (!hasPermission) {
    return (
      <Alert
        variant="error"
        title="Camera Access Required"
        message="Please enable camera access to mark attendance"
        dismissible={false}
      />
    )
  }

  return (
    <div className="space-y-4">
      <div className="relative bg-black rounded-lg overflow-hidden">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full aspect-video object-cover"
        />
        <div className="absolute inset-0 border-2 border-blue-500 opacity-50" />
      </div>
      <canvas ref={canvasRef} className="hidden" />
      <Button
        onClick={captureImage}
        disabled={isCapturing}
        className="w-full"
      >
        <Camera size={20} />
        {isCapturing ? 'Processing...' : 'Capture Image'}
      </Button>
    </div>
  )
}

export const AttendanceMarking = ({ sessionId, studentId }) => {
  const [step, setStep] = useState('capture') // capture, processing, result
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [location, setLocation] = useState(null)

  useEffect(() => {
    getStudentLocation()
  }, [])

  const getStudentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
          })
        },
        () => {
          Toast.warning('Could not get location. Geofence verification may fail.')
        }
      )
    }
  }

  const handleCapture = async (imageData) => {
    if (!location) {
      Toast.error('Location not available. Please try again.')
      return
    }

    setIsLoading(true)
    setStep('processing')
    setError(null)

    try {
      const response = await attendanceService.markAttendance({
        session_id: sessionId,
        image_base64: imageData,
        user_latitude: location.latitude,
        user_longitude: location.longitude,
        challenge_response: imageData, // For liveness detection
      })

      setResult(response)
      setStep('result')

      if (!response.is_flagged) {
        Toast.success('Attendance marked successfully!')
      } else {
        Toast.warning(`Attendance marked but flagged: ${response.flag_reason}`)
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to mark attendance')
      Toast.error('Attendance marking failed')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="max-w-md mx-auto p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="space-y-6"
      >
        {step === 'capture' && (
          <>
            <h2 className="text-2xl font-bold text-center">Mark Attendance</h2>
            <WebcamCapture onCapture={handleCapture} isCapturing={isLoading} />
          </>
        )}

        {step === 'processing' && (
          <div className="flex flex-col items-center justify-center py-12 gap-4">
            <LoadingSpinner size="lg" />
            <p className="text-lg font-semibold">Processing Face Verification...</p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Please wait while we verify your face</p>
          </div>
        )}

        {step === 'result' && result && (
          <div className="space-y-4">
            <Alert
              variant={result.is_flagged ? 'warning' : 'success'}
              title={result.is_flagged ? 'Flagged for Review' : 'Success'}
              message={result.message}
              dismissible={false}
            />

            <div className="glassmorphism rounded-lg p-4 space-y-2">
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Face Confidence:</span>
                <span className="font-semibold">{(result.face_confidence * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Liveness Score:</span>
                <span className="font-semibold">{(result.liveness_score * 100).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Geofence Verified:</span>
                <span className={result.geofence_verified ? 'text-green-500 font-semibold' : 'text-red-500 font-semibold'}>
                  {result.geofence_verified ? 'Yes' : 'No'}
                </span>
              </div>
            </div>

            <Button onClick={() => window.location.reload()} className="w-full">
              Mark Again
            </Button>
          </div>
        )}

        {error && <Alert variant="error" title="Error" message={error} />}
      </motion.div>
    </div>
  )
}

export default AttendanceMarking
