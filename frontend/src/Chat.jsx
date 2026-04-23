import { useState, useEffect, useRef } from 'react'
import { chat } from './api'
import axios from 'axios'

export default function Chat({ doc, onBack }) {
  const [question, setQuestion] = useState('')
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const bottomRef = useRef(null)

  useEffect(() => {
    loadHistory()
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadHistory = async () => {
    try {
      const token = localStorage.getItem('token')
      const res = await axios.get(
        `http://127.0.0.1:8000/chat/history/${doc.doc_id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      )
      const history = res.data.history.map(h => ([
        { role: 'user', content: h.question },
        { role: 'ai', content: h.answer }
      ])).flat()
      setMessages(history)
    } catch (err) {
      console.error(err)
    }
  }

  const handleChat = async () => {
    if (!question.trim()) return
    const userMessage = question
    setQuestion('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const res = await chat(doc.doc_id, userMessage, sessionId)
      setSessionId(res.data.session_id)
      setMessages(prev => [...prev, { role: 'ai', content: res.data.answer }])
    } catch (err) {
      setMessages(prev => [...prev, { role: 'ai', content: 'Something went wrong. Try again.' }])
    }
    setLoading(false)
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleChat()
    }
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white flex flex-col">
      {/* Header */}
      <div className="bg-gray-900 px-6 py-4 flex items-center gap-4 border-b border-gray-800">
        <button
          onClick={onBack}
          className="text-gray-400 hover:text-white transition"
        >
          ← Back
        </button>
        <div>
          <h1 className="font-semibold text-white">{doc.filename}</h1>
          <p className="text-gray-500 text-sm">{doc.chunk_count} chunks</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6 max-w-3xl mx-auto w-full">
        {messages.length === 0 && (
          <div className="text-center text-gray-600 mt-20">
            <p className="text-4xl mb-4">📄</p>
            <p className="text-lg">Ask anything about this document</p>
          </div>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`mb-4 flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-2xl px-4 py-3 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-800 text-gray-200'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start mb-4">
            <div className="bg-gray-800 px-4 py-3 rounded-2xl text-gray-400 text-sm">
              Thinking...
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="bg-gray-900 border-t border-gray-800 px-6 py-4">
        <div className="max-w-3xl mx-auto flex gap-3">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about this document..."
            rows={1}
            className="flex-1 bg-gray-800 text-white px-4 py-3 rounded-xl outline-none focus:ring-2 focus:ring-blue-500 resize-none"
          />
          <button
            onClick={handleChat}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl font-semibold transition"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  )
}