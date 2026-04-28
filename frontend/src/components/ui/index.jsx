import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle, CheckCircle, Info, AlertTriangle, X } from 'lucide-react'
import toast from 'react-hot-toast'

export const Toast = {
  success: (message, duration = 3000) => {
    toast.custom((t) => (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="glassmorphism rounded-lg p-4 flex items-center gap-3 max-w-md"
      >
        <CheckCircle className="text-green-500" size={24} />
        <span>{message}</span>
      </motion.div>
    ), { duration })
  },

  error: (message, duration = 4000) => {
    toast.custom((t) => (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="glassmorphism rounded-lg p-4 flex items-center gap-3 max-w-md border border-red-500/50"
      >
        <AlertCircle className="text-red-500" size={24} />
        <span>{message}</span>
      </motion.div>
    ), { duration })
  },

  info: (message, duration = 3000) => {
    toast.custom((t) => (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="glassmorphism rounded-lg p-4 flex items-center gap-3 max-w-md"
      >
        <Info className="text-blue-500" size={24} />
        <span>{message}</span>
      </motion.div>
    ), { duration })
  },

  warning: (message, duration = 3000) => {
    toast.custom((t) => (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: 20 }}
        className="glassmorphism rounded-lg p-4 flex items-center gap-3 max-w-md border border-yellow-500/50"
      >
        <AlertTriangle className="text-yellow-500" size={24} />
        <span>{message}</span>
      </motion.div>
    ), { duration })
  },
}

export const Button = ({ variant = 'primary', size = 'md', children, ...props }) => {
  const baseClasses = 'font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2'
  
  const variantClasses = {
    primary: 'bg-blue-600 hover:bg-blue-700 text-white',
    secondary: 'bg-purple-600 hover:bg-purple-700 text-white',
    outline: 'border-2 border-blue-600 text-blue-600 hover:bg-blue-50 dark:hover:bg-blue-900/20',
    danger: 'bg-red-600 hover:bg-red-700 text-white',
    ghost: 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300',
  }

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2.5 text-base',
    lg: 'px-6 py-3 text-lg',
  }

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      {...props}
    >
      {children}
    </button>
  )
}

export const Input = ({ label, error, ...props }) => {
  return (
    <div className="flex flex-col gap-2">
      {label && <label className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>}
      <input
        className={`px-4 py-2 rounded-lg border-2 bg-white dark:bg-gray-800 transition-colors ${
          error 
            ? 'border-red-500 focus:border-red-600' 
            : 'border-gray-300 dark:border-gray-600 focus:border-blue-500'
        } focus:outline-none`}
        {...props}
      />
      {error && <span className="text-sm text-red-500">{error}</span>}
    </div>
  )
}

export const Card = ({ children, className = '' }) => {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`glassmorphism rounded-xl p-6 ${className}`}
    >
      {children}
    </motion.div>
  )
}

export const LoadingSpinner = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'w-6 h-6',
    md: 'w-12 h-12',
    lg: 'w-16 h-16',
  }

  return (
    <motion.div
      animate={{ rotate: 360 }}
      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
      className={`${sizeClasses[size]} border-4 border-gray-300 dark:border-gray-600 border-t-blue-600 rounded-full`}
    />
  )
}

export const Skeleton = ({ width = 'w-full', height = 'h-6', className = '' }) => {
  return (
    <motion.div
      animate={{ opacity: [0.5, 1, 0.5] }}
      transition={{ duration: 2, repeat: Infinity }}
      className={`${width} ${height} bg-gray-300 dark:bg-gray-700 rounded ${className}`}
    />
  )
}

export const Alert = ({ variant = 'info', title, message, dismissible = true, onDismiss }) => {
  const variantClasses = {
    info: 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-700',
    success: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-700',
    warning: 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-700',
    error: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-700',
  }

  const textClasses = {
    info: 'text-blue-800 dark:text-blue-200',
    success: 'text-green-800 dark:text-green-200',
    warning: 'text-yellow-800 dark:text-yellow-200',
    error: 'text-red-800 dark:text-red-200',
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className={`border-2 rounded-lg p-4 ${variantClasses[variant]} ${textClasses[variant]}`}
    >
      <div className="flex justify-between items-start gap-3">
        <div>
          {title && <h3 className="font-semibold mb-1">{title}</h3>}
          {message && <p className="text-sm">{message}</p>}
        </div>
        {dismissible && (
          <button onClick={onDismiss} className="hover:opacity-70">
            <X size={20} />
          </button>
        )}
      </div>
    </motion.div>
  )
}
