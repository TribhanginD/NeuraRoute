import React, { useState, useEffect } from 'react';
import { Play, Pause, Square, RotateCcw, Settings } from 'lucide-react';
import { supabaseService } from '../services/supabaseService.ts';

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
      const status = await supabaseService.getSimulationStatus();
      setSimulationStatus(status);
    } catch (error) {
      console.error('Error fetching simulation status:', error);
    }
  };

  const controlSimulation = async (action) => {
    try {
      const result = await supabaseService.simulationAction(action);
      if (result.ok) {
        fetchSimulationStatus();
      }
    } catch (error) {
      console.error(`Error ${action} simulation:`, error);
    }
  };

  const setSimulationSpeed = async (newSpeed) => {
    try {
      const speed = await supabaseService.getSimulationSpeed();
      const response = await supabaseService.setSimulationSpeed(newSpeed);
      if (response.ok) {
        setSpeed(newSpeed);
        fetchSimulationStatus();
      }
    } catch (error) {
      console.error('Error setting simulation speed:', error);
    }
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Simulation Control</h1>
        <p className="text-gray-600 mt-2">Manage the AI-Native Logistics Simulation</p>
      </div>

      {/* Simulation Status */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Simulation Status</h2>
        {simulationStatus && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-sm text-gray-600">Status</p>
              <p className={`text-lg font-semibold ${
                simulationStatus.is_running ? 'text-green-600' : 'text-red-600'
              }`}>
                {simulationStatus.is_running ? 'Running' : 'Stopped'}
              </p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Tick Count</p>
              <p className="text-lg font-semibold text-gray-900">{simulationStatus.tick_count}</p>
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-600">Current Time</p>
              <p className="text-lg font-semibold text-gray-900">
                {new Date(simulationStatus.current_time).toLocaleString()}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Control Panel */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Control Panel</h2>
        <div className="flex flex-wrap gap-4 items-center">
          <button
            onClick={() => controlSimulation('start')}
            disabled={simulationStatus?.is_running}
            className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Play className="h-4 w-4 mr-2" />
            Start
          </button>
          
          <button
            onClick={() => controlSimulation('pause')}
            disabled={!simulationStatus?.is_running}
            className="flex items-center px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Pause className="h-4 w-4 mr-2" />
            Pause
          </button>
          
          <button
            onClick={() => controlSimulation('stop')}
            disabled={!simulationStatus?.is_running}
            className="flex items-center px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Square className="h-4 w-4 mr-2" />
            Stop
          </button>
          
          <button
            onClick={() => controlSimulation('reset')}
            className="flex items-center px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700"
          >
            <RotateCcw className="h-4 w-4 mr-2" />
            Reset
          </button>
        </div>
      </div>

      {/* Speed Control */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Speed Control</h2>
        <div className="flex items-center space-x-4">
          <label className="text-sm text-gray-600">Speed Multiplier:</label>
          <input
            type="range"
            min="0.1"
            max="10"
            step="0.1"
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            onMouseUp={() => setSimulationSpeed(speed)}
            onKeyUp={() => setSimulationSpeed(speed)}
            className="w-32"
          />
          <span className="text-sm font-medium text-gray-900">{speed}x</span>
          <button
            onClick={() => setSimulationSpeed(speed)}
            className="flex items-center px-3 py-1 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
          >
            <Settings className="h-3 w-3 mr-1" />
            Apply
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Adjust simulation speed from 0.1x (slow) to 10x (fast)
        </p>
      </div>

      {/* Simulation Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Active Agents</span>
              <span className="text-sm font-medium text-gray-900">
                {simulationStatus?.agents_active || 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Events Processed</span>
              <span className="text-sm font-medium text-gray-900">
                {simulationStatus?.events_processed || 0}
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