import { useState } from 'react'
import Login from './Login'
import Dashboard from './Dashboard'
import Chat from './Chat'

export default function App() {
  const [page, setPage] = useState(
    localStorage.getItem('token') ? 'dashboard' : 'login'
  )
  const [selectedDoc, setSelectedDoc] = useState(null)

  const handleLogin = () => {
    setPage('dashboard')
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    setPage('login')
  }

  const handleSelectDoc = (doc) => {
    setSelectedDoc(doc)
    setPage('chat')
  }

  const handleBack = () => {
    setPage('dashboard')
    setSelectedDoc(null)
  }

  if (page === 'login') return <Login onLogin={handleLogin} />
  if (page === 'chat') return <Chat doc={selectedDoc} onBack={handleBack} />
  return <Dashboard onSelectDoc={handleSelectDoc} onLogout={handleLogout} />
}