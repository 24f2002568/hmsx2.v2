import { defineStore } from 'pinia'
import axios from 'axios'

export const API = '/api'

axios.interceptors.request.use(config => {
  const token = localStorage.getItem('hms_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

axios.interceptors.response.use(
  res => res,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('hms_token')
      localStorage.removeItem('hms_user')
      window.location.hash = '#/login'
    }
    return Promise.reject(err)
  }
)

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('hms_user') || 'null'),
    token: localStorage.getItem('hms_token') || null,
    loading: false,
    error: null
  }),
  getters: {
    isLoggedIn: (s) => !!s.token,
    isAdmin:    (s) => s.user?.role === 'admin',
    isDoctor:   (s) => s.user?.role === 'doctor',
    isPatient:  (s) => s.user?.role === 'patient',
    role:       (s) => s.user?.role || null,
  },
  actions: {
    async login(username, password) {
      this.loading = true
      this.error = null
      try {
        const { data } = await axios.post(`${API}/auth/login`, { username, password })
        this.token = data.token
        this.user  = data.user
        localStorage.setItem('hms_token', data.token)
        localStorage.setItem('hms_user',  JSON.stringify(data.user))
        return data.user
      } catch (e) {
        this.error = e.response?.data?.error || 'Login failed'
        throw this.error
      } finally {
        this.loading = false
      }
    },
    async register(payload) {
      this.loading = true
      this.error = null
      try {
        await axios.post(`${API}/auth/register`, payload)
        return true
      } catch (e) {
        this.error = e.response?.data?.error || 'Registration failed'
        throw this.error
      } finally {
        this.loading = false
      }
    },
    logout() {
      this.token = null
      this.user  = null
      localStorage.removeItem('hms_token')
      localStorage.removeItem('hms_user')
    }
  }
})

export { axios }