import { create } from 'zustand'

export const useAuthStore = create((set) => ({
  user: null,
  token: localStorage.getItem('access_token') || null,
  isLoading: false,
  error: null,

  setUser: (user) => set({ user }),
  setToken: (token) => {
    if (token) {
      localStorage.setItem('access_token', token)
    } else {
      localStorage.removeItem('access_token')
    }
    set({ token })
  },
  setLoading: (isLoading) => set({ isLoading }),
  setError: (error) => set({ error }),

  login: async (user, token) => {
    set({ user, token, error: null })
    localStorage.setItem('access_token', token)
  },

  logout: () => {
    set({ user: null, token: null, error: null })
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  },
}))

export const useAttendanceStore = create((set) => ({
  sessions: [],
  currentSession: null,
  attendanceHistory: [],
  fraudLogs: [],
  isLoading: false,

  setSessions: (sessions) => set({ sessions }),
  setCurrentSession: (session) => set({ currentSession: session }),
  setAttendanceHistory: (history) => set({ attendanceHistory: history }),
  setFraudLogs: (logs) => set({ fraudLogs: logs }),
  setLoading: (isLoading) => set({ isLoading }),
}))

export const useFaceStore = create((set) => ({
  enrollmentStatus: null,
  enrollmentProgress: 0,
  isFaceEnrolled: false,
  isEnrolling: false,
  enrollmentError: null,

  setEnrollmentStatus: (status) => set({ enrollmentStatus: status }),
  setEnrollmentProgress: (progress) => set({ enrollmentProgress: progress }),
  setIsFaceEnrolled: (enrolled) => set({ isFaceEnrolled: enrolled }),
  setIsEnrolling: (enrolling) => set({ isEnrolling: enrolling }),
  setEnrollmentError: (error) => set({ enrollmentError: error }),

  resetEnrollment: () => set({
    enrollmentProgress: 0,
    isEnrolling: false,
    enrollmentError: null,
  }),
}))

export const useThemeStore = create((set) => ({
  isDarkMode: localStorage.getItem('darkMode') === 'true',
  toggleDarkMode: () => set((state) => {
    const newDarkMode = !state.isDarkMode
    localStorage.setItem('darkMode', newDarkMode)
    return { isDarkMode: newDarkMode }
  }),
}))
