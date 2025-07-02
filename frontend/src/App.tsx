import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import './App.css';

// Components
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import AgentMonitor from './pages/AgentMonitor';
import FleetMap from './pages/FleetMap';
import InventoryView from './pages/InventoryView';
import MerchantChat from './pages/MerchantChat';
import SimulationControl from './pages/SimulationControl';
import AgenticAI from './pages/AgenticAI';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="flex h-screen bg-gray-50">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/agents" element={<AgentMonitor />} />
              <Route path="/agentic" element={<AgenticAI />} />
              <Route path="/fleet" element={<FleetMap />} />
              <Route path="/inventory" element={<InventoryView />} />
              <Route path="/chat" element={<MerchantChat />} />
              <Route path="/simulation" element={<SimulationControl />} />
            </Routes>
          </main>
        </div>
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
          }}
        />
      </Router>
    </QueryClientProvider>
  );
}

export default App; 