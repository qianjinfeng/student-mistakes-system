import { Routes, Route } from 'react-router-dom'
import Dashboard from './pages/Dashboard'
import UploadMistake from './pages/UploadMistake'
import ReviewSession from './pages/ReviewSession'
import Achievements from './pages/Achievements'
import Header from './components/Header'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<UploadMistake />} />
          <Route path="/review" element={<ReviewSession />} />
          <Route path="/achievements" element={<Achievements />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
