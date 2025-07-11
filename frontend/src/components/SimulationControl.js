import React, { useState, useEffect } from 'react';
import { Play, Pause, Square, RotateCcw, Settings } from 'lucide-react';
import { agenticWebSocket } from '../services/agenticWebSocket.ts';

const SimulationControl = () => {
  const [simulationStatus, setSimulationStatus] = useState(null);
  const [speed, setSpeed] = useState(1.0);

  useEffect(() => {
    fetchSimulationStatus();
    const interval = setInterval(fetchSimulationStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchSimulationStatus = async () => {
    try {
      const status = await agenticWebSocket.getSimulationStatus();
      setSimulationStatus(status);
    } catch (error) {
      console.error('Error fetching simulation status:', error);
    }
  };

  const controlSimulation = async (action) => {
    try {
      if (action === 'start') {
        await agenticWebSocket.startAgents();
      } else if (action === 'stop') {
        await agenticWebSocket.stopAgents();
      }
      fetchSimulationStatus();
    } catch (error) {
      console.error(`Error ${action} simulation:`, error);
    }
  };

  const setSimulationSpeed = async (newSpeed) => {
    try {
      setSpeed(newSpeed);
      fetchSimulationStatus();
    } catch (error) {
      console.error('Error setting simulation speed:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Simulation Control</h1>
        <p className="text-gray-600 mt-2">Control and monitor the AI agent simulation</p>
      </div>

      {/* Control Panel */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-gray-900">Agent Control</h2>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <label className="text-sm font-medium text-gray-700">Speed:</label>
              <select
                value={speed}
                onChange={(e) => setSimulationSpeed(parseFloat(e.target.value))}
                className="border border-gray-300 rounded-md px-3 py-1 text-sm"
              >
                <option value={0.5}>0.5x</option>
                <option value={1.0}>1.0x</option>
                <option value={2.0}>2.0x</option>
                <option value={5.0}>5.0x</option>
              </select>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-4">
          <button
            onClick={() => controlSimulation('start')}
            className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors duration-200"
          >
            <Play className="h-5 w-5" />
            <span>Start Agents</span>
          </button>
          <button
            onClick={() => controlSimulation('stop')}
            className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors duration-200"
          >
            <Square className="h-5 w-5" />
            <span>Stop Agents</span>
          </button>
          <button
            onClick={() => controlSimulation('restart')}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors duration-200"
          >
            <RotateCcw className="h-5 w-5" />
            <span>Restart</span>
          </button>
        </div>
      </div>

      {/* Status Display */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Status</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Agents Running</span>
              <span className="text-sm font-medium text-gray-900">
                {simulationStatus?.agents_running ? 'Yes' : 'No'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Total Agents</span>
              <span className="text-sm font-medium text-gray-900">
                {simulationStatus?.total_agents || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">System Health</span>
              <span className="text-sm font-medium text-green-600">Healthy</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="space-y-2">
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
              Generate Test Data
            </button>
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
              Export Simulation Logs
            </button>
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
              View Agent Status
            </button>
            <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded">
              System Diagnostics
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimulationControl; 