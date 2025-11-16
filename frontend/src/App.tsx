import React, { useEffect } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useQuery } from 'react-query'

import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import AgenticDashboard from './pages/AgenticDashboard'
import FleetMap from './pages/FleetMap'
import InventoryView from './pages/InventoryView'
import { useSystemStore } from './stores/systemStore'
import { useWebSocket } from './hooks/useWebSocket'
import { agenticApi } from './services/agenticApi'

const App: React.FC = () => {
  const { setSystemStatus } = useSystemStore()
  const wsUrl = process.env.REACT_APP_WS_URL
  const { data: wsData } = useWebSocket(wsUrl)

  const { data: systemStats } = useQuery(['system-stats'], () => agenticApi.getSystemStats(), {
    refetchInterval: 30_000,
    retry: 1,
  })

  useEffect(() => {
    if (systemStats) {
      setSystemStatus({ status: 'healthy', services: systemStats, timestamp: new Date().toISOString() })
    }
  }, [systemStats, setSystemStatus])

  useEffect(() => {
    if (!wsData) return
    if (wsData.type === 'status_update') {
      setSystemStatus(wsData.payload)
    }
  }, [wsData, setSystemStatus])

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/agentic" element={<AgenticDashboard />} />
          <Route path="/fleet" element={<FleetMap />} />
          <Route path="/inventory" element={<InventoryView />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
