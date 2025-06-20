import React, { useState, useEffect, useRef } from 'react';
import { MessageSquare, Send, User, Bot, Clock } from 'lucide-react';

const MerchantChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Mock initial messages
  useEffect(() => {
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: 'Hello! I\'m your AI logistics assistant. How can I help you today?',
        timestamp: new Date(Date.now() - 60000)
      },
      {
        id: 2,
        type: 'user',
        content: 'I need to check the status of my recent order #12345',
        timestamp: new Date(Date.now() - 45000)
      },
      {
        id: 3,
        type: 'bot',
        content: 'I\'ll check that for you. Order #12345 is currently in transit and expected to be delivered by 3:00 PM today. Your delivery vehicle is 15 minutes away.',
        timestamp: new Date(Date.now() - 30000)
      }
    ]);
  }, []);

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    const userMessage = {
      id: messages.length + 1,
      type: 'user',
      content: inputMessage,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsTyping(true);

    // Simulate AI response
    setTimeout(() => {
      const botResponse = {
        id: messages.length + 2,
        type: 'bot',
        content: generateBotResponse(inputMessage),
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botResponse]);
      setIsTyping(false);
    }, 2000);
  };

  const generateBotResponse = (userMessage) => {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('order') && lowerMessage.includes('status')) {
      return 'I can help you check your order status. Please provide your order number or I can show you all your recent orders.';
    } else if (lowerMessage.includes('delivery') || lowerMessage.includes('shipping')) {
      return 'I can track your delivery in real-time. Would you like me to show you the current location of your delivery vehicle?';
    } else if (lowerMessage.includes('inventory') || lowerMessage.includes('stock')) {
      return 'I can check inventory levels for any SKU. What product would you like me to look up?';
    } else if (lowerMessage.includes('pricing') || lowerMessage.includes('cost')) {
      return 'I can help you with pricing information and dynamic pricing recommendations based on current market conditions.';
    } else if (lowerMessage.includes('restock') || lowerMessage.includes('reorder')) {
      return 'I can analyze your inventory and provide restock recommendations. Would you like me to run an analysis?';
    } else {
      return 'I\'m here to help with your logistics needs. I can assist with order tracking, inventory management, delivery status, pricing, and restock recommendations. What would you like to know?';
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="p-6">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Merchant Chat</h1>
        <p className="text-gray-600 mt-2">AI-powered logistics assistant for merchants</p>
      </div>

      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg">
          {/* Chat Header */}
          <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
            <div className="flex items-center">
              <Bot className="h-6 w-6 mr-3" />
              <div>
                <h2 className="text-lg font-semibold">AI Logistics Assistant</h2>
                <p className="text-sm text-blue-100">Powered by NeuraRoute AI</p>
              </div>
            </div>
          </div>

          {/* Messages */}
          <div className="h-96 overflow-y-auto p-6 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`flex max-w-xs lg:max-w-md ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                  <div className={`flex-shrink-0 h-8 w-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'
                  }`}>
                    {message.type === 'user' ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                  </div>
                  <div className={`ml-3 ${message.type === 'user' ? 'mr-3' : ''}`}>
                    <div className={`rounded-lg px-4 py-2 ${
                      message.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="text-sm">{message.content}</p>
                    </div>
                    <div className={`mt-1 text-xs text-gray-500 flex items-center ${
                      message.type === 'user' ? 'justify-end' : 'justify-start'
                    }`}>
                      <Clock className="h-3 w-3 mr-1" />
                      {formatTime(message.timestamp)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
            
            {isTyping && (
              <div className="flex justify-start">
                <div className="flex max-w-xs lg:max-w-md">
                  <div className="flex-shrink-0 h-8 w-8 rounded-full bg-gray-200 text-gray-600 flex items-center justify-center">
                    <Bot className="h-4 w-4" />
                  </div>
                  <div className="ml-3">
                    <div className="bg-gray-100 rounded-lg px-4 py-2">
                      <div className="flex space-x-1">
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="px-6 py-4 border-t border-gray-200">
            <div className="flex space-x-4">
              <div className="flex-1">
                <textarea
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message here..."
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                  rows="2"
                />
              </div>
              <button
                onClick={sendMessage}
                disabled={!inputMessage.trim() || isTyping}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => setInputMessage('Check order status')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
            >
              <div className="font-medium text-gray-900">Order Status</div>
              <div className="text-sm text-gray-600">Track your orders</div>
            </button>
            <button
              onClick={() => setInputMessage('Check inventory levels')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
            >
              <div className="font-medium text-gray-900">Inventory</div>
              <div className="text-sm text-gray-600">Check stock levels</div>
            </button>
            <button
              onClick={() => setInputMessage('Delivery tracking')}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 text-left"
            >
              <div className="font-medium text-gray-900">Delivery</div>
              <div className="text-sm text-gray-600">Track deliveries</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MerchantChat; 