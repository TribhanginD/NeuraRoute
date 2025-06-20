import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard';
import SimulationControl from './components/SimulationControl';
import AgentMonitor from './components/AgentMonitor';
import FleetMap from './components/FleetMap';
import InventoryView from './components/InventoryView';
import MerchantChat from './components/MerchantChat';
import Sidebar from './components/Sidebar';

function App() {
  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        <Sidebar />
        <div className="flex-1 flex flex-col overflow-hidden">
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/simulation" element={<SimulationControl />} />
              <Route path="/agents" element={<AgentMonitor />} />
              <Route path="/fleet" element={<FleetMap />} />
              <Route path="/inventory" element={<InventoryView />} />
              <Route path="/chat" element={<MerchantChat />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  );
}

export default App; 