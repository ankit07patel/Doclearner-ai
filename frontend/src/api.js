import axios from 'axios'

const API = axios.create({
  baseURL: 'http://127.0.0.1:8000'
})

// Automatically attach token to every request
API.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const register = (email, password) =>
  API.post('/register', { email, password })

export const login = (email, password) =>
  API.post('/login', { email, password })

export const getMe = () =>
  API.get('/me')

export const uploadPDF = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return API.post('/upload', formData)
}

export const getDocuments = () =>
  API.get('/documents')

export const chat = (doc_id, question, session_id = null) =>
  API.post('/chat', { doc_id, question, session_id })