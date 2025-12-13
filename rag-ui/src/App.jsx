import React, { useState } from 'react'
import axios from 'axios'

const API_URL = 'http://localhost:8000'

function App() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState('')
  const [file, setFile] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [documentUploaded, setDocumentUploaded] = useState(false)

  const handleFileUpload = async (e) => {
    const selectedFile = e.target.files[0]
    if (!selectedFile) return

    setFile(selectedFile)
    setIsLoading(true)

    const formData = new FormData()
    formData.append('file', selectedFile)

    try {
      const response = await axios.post(`${API_URL}/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      setDocumentUploaded(true)
      setMessages([...messages, { 
        role: 'system', 
        content: `✅ Document "${selectedFile.name}" uploaded successfully! You can now ask questions about it.` 
      }])
    } catch (error) {
      console.error('Upload error:', error)
      setMessages([...messages, { 
        role: 'system', 
        content: `❌ Error uploading file: ${error.response?.data?.detail || error.message}` 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!input.trim()) return

    if (!documentUploaded) {
      setMessages([...messages, { 
        role: 'system', 
        content: '⚠️ Please upload a document first before asking questions.' 
      }])
      return
    }

    const userMessage = { role: 'user', content: input }
    setMessages([...messages, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_URL}/ask`, {
        question: input
      })

      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.answer 
      }])
    } catch (error) {
      console.error('Question error:', error)
      setMessages(prev => [...prev, { 
        role: 'system', 
        content: `❌ Error: ${error.response?.data?.detail || error.message}` 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      {/* Header */}
      <header className="bg-gray-800 p-4 border-b border-gray-700">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <h1 className="text-2xl font-bold">RAG Mini</h1>
          {documentUploaded && (
            <span className="text-sm bg-green-600 px-3 py-1 rounded-full">
              📄 Document loaded
            </span>
          )}
        </div>
      </header>

      {/* Chat Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <h2 className="text-3xl font-bold mb-4">Welcome to RAG Mini! 👋</h2>
              <p className="text-gray-400 mb-2">Upload a document and ask questions about it</p>
              <p className="text-gray-500 text-sm">Start by uploading a PDF or text file</p>
            </div>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg ${
                msg.role === 'user' 
                  ? 'bg-blue-600 ml-auto max-w-2xl' 
                  : msg.role === 'assistant'
                  ? 'bg-gray-700 max-w-3xl'
                  : 'bg-gray-800 max-w-2xl text-center mx-auto'
              }`}
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex items-center gap-2 text-gray-400">
            <div className="animate-spin h-5 w-5 border-2 border-blue-500 border-t-transparent rounded-full"></div>
            <span>Processing...</span>
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="bg-gray-800 p-4 border-t border-gray-700">
        <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
          <div className="flex gap-2">
            <input
              type="file"
              onChange={handleFileUpload}
              className="hidden"
              id="file-upload"
              accept=".pdf,.txt"
              disabled={isLoading}
            />
            <label
              htmlFor="file-upload"
              className={`px-4 py-2 bg-gray-700 rounded-lg cursor-pointer hover:bg-gray-600 transition ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              📎
            </label>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask a question..."
              disabled={isLoading}
              className="flex-1 px-4 py-2 bg-gray-700 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-2 bg-blue-600 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
          {file && !documentUploaded && (
            <p className="text-sm text-gray-400 mt-2">
              Uploading: {file.name}...
            </p>
          )}
        </form>
      </div>
    </div>
  )
}

export default App