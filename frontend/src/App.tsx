import { BrowserRouter, Route, Routes } from 'react-router-dom'
import NavBar from './components/NavBar'
import { AuthProvider } from './contexts/AuthContext'
import DataEntry from './pages/DataEntry'
import Dashboard from './pages/Dashboard'
import Explorer from './pages/Explorer'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <div className="flex flex-col h-full">
          <NavBar />
          <main className="flex flex-1 overflow-hidden">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/explorer" element={<Explorer />} />
              <Route path="/data-entry" element={<DataEntry />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AuthProvider>
  )
}
