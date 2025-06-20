import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  Home, 
  Play, 
  Cpu, 
  Map, 
  Package, 
  MessageSquare,
  Settings
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/', icon: Home, label: 'Dashboard' },
    { path: '/simulation', icon: Play, label: 'Simulation' },
    { path: '/agents', icon: Cpu, label: 'Agents' },
    { path: '/fleet', icon: Map, label: 'Fleet Map' },
    { path: '/inventory', icon: Package, label: 'Inventory' },
    { path: '/chat', icon: MessageSquare, label: 'Merchant Chat' },
  ];

  return (
    <div className="w-64 bg-white shadow-lg">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-gray-900">NeuraRoute</h1>
        <p className="text-sm text-gray-600 mt-1">AI-Native Logistics</p>
      </div>
      
      <nav className="mt-6">
        <div className="px-3">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center px-3 py-2 text-sm font-medium rounded-md mb-1 transition-colors ${
                  isActive
                    ? 'bg-primary-100 text-primary-700 border-r-2 border-primary-500'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`
              }
            >
              <item.icon className="mr-3 h-5 w-5" />
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>
      
      <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200">
        <NavLink
          to="/settings"
          className="flex items-center px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 rounded-md"
        >
          <Settings className="mr-3 h-5 w-5" />
          Settings
        </NavLink>
      </div>
    </div>
  );
};

export default Sidebar; 