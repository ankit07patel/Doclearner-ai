import { useState, useEffect } from 'react'
import { getDocuments, uploadPDF } from './api'

export default function Dashboard({ onSelectDoc, onLogout }) {
  const [documents, setDocuments] = useState([])
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      const res = await getDocuments()
      setDocuments(res.data.documents)
    } catch (err) {
      console.error(err)
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return
    setUploading(true)
    setMessage('')
    try {
      await uploadPDF(file)
      setMessage('PDF uploaded successfully!')
      fetchDocuments()
    } catch (err) {
      setMessage('Upload failed. Try again.')
    }
    setUploading(false)
  }

  return (
    <div className="min-h-screen bg-gray-950 text-white">
      {/* Header */}
      <div className="bg-gray-900 px-6 py-4 flex justify-between items-center border-b border-gray-800">
        <h1 className="text-xl font-bold text-white">Doclearner AI</h1>
        <button
          onClick={onLogout}
          className="text-gray-400 hover:text-white transition"
        >
          Logout
        </button>
      </div>

      <div className="max-w-4xl mx-auto px-6 py-8">
        {/* Upload Section */}
        <div className="bg-gray-900 rounded-2xl p-6 mb-8 border border-gray-800">
          <h2 className="text-lg font-semibold mb-4">Upload a PDF</h2>
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-700 rounded-xl cursor-pointer hover:border-blue-500 transition">
            <span className="text-gray-400">
              {uploading ? 'Uploading...' : 'Click to upload PDF'}
            </span>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              onChange={handleUpload}
              disabled={uploading}
            />
          </label>
          {message && (
            <p className="text-green-400 mt-3 text-sm">{message}</p>
          )}
        </div>

        {/* Documents List */}
        <h2 className="text-lg font-semibold mb-4">Your Documents</h2>
        {documents.length === 0 ? (
          <p className="text-gray-500">No documents yet. Upload a PDF to get started.</p>
        ) : (
          <div className="grid gap-4">
            {documents.map((doc) => (
              <div
                key={doc.doc_id}
                className="bg-gray-900 border border-gray-800 rounded-xl p-5 flex justify-between items-center hover:border-blue-500 transition cursor-pointer"
                onClick={() => onSelectDoc(doc)}
              >
                <div>
                  <p className="font-medium text-white">{doc.filename}</p>
                  <p className="text-gray-500 text-sm">{doc.chunk_count} chunks • {doc.created_at?.slice(0, 10)}</p>
                </div>
                <button className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm transition">
                  Chat
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}