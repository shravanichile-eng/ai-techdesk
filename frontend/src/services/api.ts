import axios, { AxiosInstance } from 'axios'
import { LoginRequest, LoginResponse } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authService = {
  login: async (credentials: LoginRequest): Promise<LoginResponse> => {
    const response = await api.post('/api/auth/login', credentials)
    return response.data
  },

  register: async (data: any): Promise<any> => {
    const response = await api.post('/api/auth/register', data)
    return response.data
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me')
    return response.data
  },

  logout: async () => {
    await api.post('/api/auth/logout')
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
  },
}

export default api
