import api from './api'

export const authService = {
  signup: async (data) => {
    const response = await api.post('/auth/signup', data)
    return response.data
  },

  login: async (email, password) => {
    const response = await api.post('/auth/login', { email, password })
    return response.data
  },

  logout: async () => {
    await api.post('/auth/logout')
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me')
    return response.data
  },

  changePassword: async (currentPassword, newPassword) => {
    const response = await api.post('/auth/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
    return response.data
  },

  refreshToken: async (refreshToken) => {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },
}

export const faceService = {
  startEnrollment: async () => {
    const response = await api.post('/face/enroll/start')
    return response.data
  },

  captureEnrollmentImage: async (imageBase64) => {
    const response = await api.post('/face/enroll/capture', {
      image_base64: imageBase64,
    })
    return response.data
  },

  completeEnrollment: async () => {
    const response = await api.post('/face/enroll/complete')
    return response.data
  },

  verifyFace: async (imageBase64, studentId = null) => {
    const response = await api.post('/face/verify', {
      image_base64: imageBase64,
    }, {
      params: studentId ? { student_id: studentId } : {},
    })
    return response.data
  },

  getEnrollmentStatus: async () => {
    const response = await api.get('/face/enrollment-status')
    return response.data
  },
}

export const attendanceService = {
  createSession: async (data) => {
    const response = await api.post('/attendance/sessions', data)
    return response.data
  },

  startSession: async (sessionId) => {
    const response = await api.post(`/attendance/sessions/${sessionId}/start`)
    return response.data
  },

  endSession: async (sessionId) => {
    const response = await api.post(`/attendance/sessions/${sessionId}/end`)
    return response.data
  },

  markAttendance: async (data) => {
    const response = await api.post('/attendance/mark', data)
    return response.data
  },

  getAttendanceHistory: async () => {
    const response = await api.get('/attendance/history')
    return response.data
  },

  getSessionRecords: async (sessionId) => {
    const response = await api.get(`/attendance/sessions/${sessionId}/records`)
    return response.data
  },

  getFraudLogs: async (unresolvedOnly = true) => {
    const response = await api.get('/attendance/fraud-logs', {
      params: { unresolved_only: unresolvedOnly },
    })
    return response.data
  },
}

export const adminService = {
  createDepartment: async (data) => {
    const response = await api.post('/admin/departments', data)
    return response.data
  },

  listDepartments: async () => {
    const response = await api.get('/admin/departments')
    return response.data
  },

  createClass: async (data) => {
    const response = await api.post('/admin/classes', data)
    return response.data
  },

  listClasses: async (departmentId = null) => {
    const response = await api.get('/admin/classes', {
      params: departmentId ? { department_id: departmentId } : {},
    })
    return response.data
  },

  createSubject: async (data) => {
    const response = await api.post('/admin/subjects', data)
    return response.data
  },

  createGeofence: async (data) => {
    const response = await api.post('/admin/geofence', data)
    return response.data
  },

  getAttendanceAnalytics: async (classId = null, days = 30) => {
    const response = await api.get('/admin/analytics/attendance', {
      params: {
        class_id: classId,
        days,
      },
    })
    return response.data
  },

  getFraudAnalytics: async (days = 90) => {
    const response = await api.get('/admin/analytics/fraud', {
      params: { days },
    })
    return response.data
  },

  listUsers: async (role = null) => {
    const response = await api.get('/admin/users', {
      params: role ? { role } : {},
    })
    return response.data
  },

  deactivateUser: async (userId) => {
    const response = await api.post(`/admin/users/${userId}/deactivate`)
    return response.data
  },

  activateUser: async (userId) => {
    const response = await api.post(`/admin/users/${userId}/activate`)
    return response.data
  },
}
