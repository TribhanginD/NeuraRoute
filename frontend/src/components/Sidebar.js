import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Play,
  Users,
  Truck,
  Package,
  MessageSquare,
  Settings,
  X,
  Activity,
  Zap,
  AlertTriangle,
  CheckCircle,
} from 'lucide-react';

import { useSystemStore } from '../stores/systemStore';
import { supabaseService } from '../services/supabaseService.ts';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Agents', href: '/agents', icon: Users },
  { name: 'Fleet', href: '/fleet', icon: Truck },
  { name: 'Inventory', href: '/inventory', icon: Package },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
];

const Sidebar = ({ open, setOpen }) => {
  const location = useLocation();
  const { systemStatus, agentStatus, getSystemHealth, getActiveAgentsCount } = useSystemStore();

  const isHealthy = getSystemHealth();
  const activeAgents = getActiveAgentsCount();

  const getStatusIcon = () => {
    if (isHealthy) {
      return <CheckCircle className="h-4 w-4 text-success-500" />;
    }
    return <AlertTriangle className="h-4 w-4 text-error-500" />;
  };

  const getStatusText = () => {
    if (isHealthy) {
      return 'System Healthy';
    }
    return 'System Issues';
  };

  return (
    <>
      {/* Mobile backdrop */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 lg:hidden"
            onClick={() => setOpen(false)}
          >
            <div className="fixed inset-0 bg-gray-600 bg-opacity-75" />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <AnimatePresence>
        <motion.div
          initial={{ x: -300 }}
          animate={{ x: 0 }}
          exit={{ x: -300 }}
          transition={{ type: 'tween', duration: 0.3 }}
          className={`fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-lg transform lg:translate-x-0 lg:static lg:inset-0 ${
            open ? 'translate-x-0' : '-translate-x-full'
          }`}
        >
          <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between h-16 px-6 border-b border-gray-200">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <Zap className="h-5 w-5 text-white" />
                  </div>
                </div>
                <div className="ml-3">
                  <h1 className="text-lg font-semibold text-gray-900">NeuraRoute</h1>
                  <p className="text-xs text-gray-500">AI Logistics</p>
                </div>
              </div>
              
              {/* Close button for mobile */}
              <button
                type="button"
                className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
                onClick={() => setOpen(false)}
              >
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* System Status */}
            <div className="px-6 py-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getStatusIcon()}
                  <span className="text-sm font-medium text-gray-900">
                    {getStatusText()}
                  </span>
                </div>
                <div className="flex items-center space-x-1">
                  <Activity className="h-4 w-4 text-gray-400" />
                  <span className="text-sm text-gray-500">{activeAgents} running</span>
                </div>
              </div>
              
              {/* Service Status */}
              <div className="mt-3 space-y-1">
                {Object.entries(systemStatus.services)
                  .filter(([service]) => service !== 'database')
                  .map(([service, status]) => (
                    <div key={service} className="flex items-center justify-between text-xs">
                      <span className="text-gray-600 capitalize">{service.replace('_', ' ')}</span>
                      <div className={`w-2 h-2 rounded-full ${
                        status === 'healthy' ? 'bg-success-500' : 'bg-error-500'
                      }`} />
                    </div>
                  ))}
              </div>
            </div>

            {/* Navigation */}
            <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`sidebar-item ${
                      isActive ? 'sidebar-item-active' : 'sidebar-item-inactive'
                    }`}
                    onClick={() => setOpen(false)}
                  >
                    <item.icon className="mr-3 h-5 w-5" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-gray-200">
              <Link
                to="/settings"
                className="sidebar-item sidebar-item-inactive"
                onClick={() => setOpen(false)}
              >
                <Settings className="mr-3 h-5 w-5" />
                Settings
              </Link>
              
              <div className="mt-4 text-xs text-gray-500">
                <p>Version 1.0.0</p>
                <p className="mt-1">© 2024 NeuraRoute</p>
              </div>
            </div>
          </div>
        </motion.div>
      </AnimatePresence>
    </>
  );
};

export default Sidebar; 