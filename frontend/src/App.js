import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { motion, AnimatePresence } from 'framer-motion';

import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import SimulationControl from './components/SimulationControl';
import AgentMonitor from './components/AgentMonitor';
import FleetMap from './components/FleetMap';
import InventoryView from './components/InventoryView';
import MerchantChat from './components/MerchantChat';

import { useWebSocket } from './hooks/useWebSocket';
import { useSystemStore } from './stores/systemStore';
import { supabaseService } from './services/supabaseService.ts';

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const { setSystemStatus, setAgentStatus } = useSystemStore();
  
  // WebSocket connection for real-time updates
  const { data: wsData } = useWebSocket();
  
  // Fetch system health from Supabase
  const { data: healthData, isLoading: healthLoading } = useQuery(
    'health',
    () => supabaseService.getSystemHealth(),
    {
      refetchInterval: 30000, // 30 seconds
      retry: 3,
    }
  );
  
  // Update system status from WebSocket data
  useEffect(() => {
    if (wsData) {
      if (wsData.type === 'system_status') {
        setSystemStatus(wsData.data);
      } else if (wsData.type === 'update') {
        setAgentStatus(wsData.data.agent_status);
      }
    }
  }, [wsData, setSystemStatus, setAgentStatus]);
  
  // Update system status from health check
  useEffect(() => {
    if (healthData) {
      setSystemStatus(healthData);
    }
  }, [healthData, setSystemStatus]);
  
  const pageVariants = {
    initial: {
      opacity: 0,
      x: -20,
    },
    in: {
      opacity: 1,
      x: 0,
    },
    out: {
      opacity: 0,
      x: 20,
    },
  };
  
  const pageTransition = {
    type: 'tween',
    ease: 'anticipate',
    duration: 0.3,
  };
  
  return (
    <div className="h-screen flex bg-gray-50">
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} setOpen={setSidebarOpen} />
      
      {/* Main content */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Top navigation */}
        <div className="bg-white shadow-sm border-b border-gray-200">
          <div className="flex items-center justify-between px-4 sm:px-6 lg:px-8 h-16">
            <div className="flex items-center">
              <button
                type="button"
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-primary-500"
                onClick={() => setSidebarOpen(true)}
              >
                <span className="sr-only">Open sidebar</span>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              
              <div className="ml-4 lg:ml-0">
                <h1 className="text-xl font-semibold text-gray-900">NeuraRoute</h1>
                <p className="text-sm text-gray-500">AI-Native Logistics System</p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Page content */}
        <div className="flex-1 overflow-auto min-h-0">
          <AnimatePresence mode="wait">
            <Routes>
              <Route
                path="/"
                element={
                  <motion.div
                    key="dashboard"
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <Dashboard />
                  </motion.div>
                }
              />
              <Route
                path="/simulation"
                element={
                  <motion.div
                    key="simulation"
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <SimulationControl />
                  </motion.div>
                }
              />
              <Route
                path="/agents"
                element={
                  <motion.div
                    key="agents"
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <AgentMonitor />
                  </motion.div>
                }
              />
              <Route
                path="/fleet"
                element={
                  <motion.div
                    key="fleet"
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <FleetMap />
                  </motion.div>
                }
              />
              <Route
                path="/inventory"
                element={
                  <motion.div
                    key="inventory"
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <InventoryView />
                  </motion.div>
                }
              />
              <Route
                path="/chat"
                element={
                  <motion.div
                    key="chat"
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={pageTransition}
                  >
                    <MerchantChat />
                  </motion.div>
                }
              />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

export default App; 