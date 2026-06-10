import axios from 'axios'
import { getToken, logout } from './auth'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

api.interceptors.request.use(
  config => {
    const token = getToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      logout()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const authAPI = {
  login: (data) => api.post('/auth/login', data, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  }),
  register: (data) => api.post('/auth/register', data),
  getMe: () => api.get('/auth/me')
}

export const dataAPI = {
  list: (params) => api.get('/data', { params }),
  get: (id) => api.get(`/data/${id}`),
  create: (data) => api.post('/data', data),
  update: (id, data) => api.put(`/data/${id}`, data),
  delete: (id) => api.delete(`/data/${id}`),
  import: (formData) => api.post('/data/import', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  export: (params) => api.get('/data/export', { params, responseType: 'blob' }),
  categories: () => api.get('/data/categories'),
  summary: (params) => api.get('/data/summary', { params })
}

export const reportAPI = {
  templates: () => api.get('/reports/templates'),
  getTemplate: (id) => api.get(`/reports/templates/${id}`),
  createTemplate: (data) => api.post('/reports/templates', data),
  updateTemplate: (id, data) => api.put(`/reports/templates/${id}`, data),
  deleteTemplate: (id) => api.delete(`/reports/templates/${id}`),
  generate: (data) => api.post('/reports/generate', data),
  export: (data) => api.post('/reports/export', data, { responseType: 'blob' })
}

export const userAPI = {
  list: (params) => api.get('/users', { params }),
  get: (id) => api.get(`/users/${id}`),
  create: (data) => api.post('/users', data),
  update: (id, data) => api.put(`/users/${id}`, data),
  delete: (id) => api.delete(`/users/${id}`)
}
