import React from 'react';
import { render, screen, fireEvent, waitFor } from '../test-utils';
import InventoryView from '../../pages/InventoryView';
import { mockInventory, mockMerchants, mockFetchResponse } from '../test-utils';

describe('InventoryView Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders inventory view with title', () => {
    render(<InventoryView />);
    
    expect(screen.getByText(/Inventory Management/i)).toBeInTheDocument();
    expect(screen.getByText(/Real-time Stock Levels/i)).toBeInTheDocument();
  });

  test('displays merchant inventory list', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/Downtown Deli/i)).toBeInTheDocument();
      expect(screen.getByText(/Uptown Market/i)).toBeInTheDocument();
    });
  });

  test('shows inventory items for each merchant', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/Item 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Item 2/i)).toBeInTheDocument();
      expect(screen.getByText(/Product A/i)).toBeInTheDocument();
      expect(screen.getByText(/Product B/i)).toBeInTheDocument();
    });
  });

  test('displays stock levels and thresholds', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/15/i)).toBeInTheDocument(); // Item 1 quantity
      expect(screen.getByText(/8/i)).toBeInTheDocument();  // Item 2 quantity
      expect(screen.getByText(/10/i)).toBeInTheDocument(); // Threshold
      expect(screen.getByText(/50/i)).toBeInTheDocument(); // Product A quantity
    });
  });

  test('shows low stock alerts', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/Low Stock Alert/i)).toBeInTheDocument();
      expect(screen.getByText(/Item 2/i)).toBeInTheDocument();
      expect(screen.getByText(/8\/10/i)).toBeInTheDocument();
    });
  });

  test('displays item prices', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/\$5.99/i)).toBeInTheDocument();
      expect(screen.getByText(/\$12.99/i)).toBeInTheDocument();
      expect(screen.getByText(/\$8.99/i)).toBeInTheDocument();
      expect(screen.getByText(/\$15.99/i)).toBeInTheDocument();
    });
  });

  test('handles inventory updates', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const updateButton = screen.getByText(/Update/i);
      fireEvent.click(updateButton);
      
      expect(screen.getByText(/Updating inventory/i)).toBeInTheDocument();
    });
  });

  test('shows inventory history', async () => {
    const mockHistory = [
      {
        timestamp: '2024-01-01T12:00:00Z',
        action: 'restock',
        item_name: 'Item 1',
        quantity_change: 10,
        new_quantity: 15
      },
      {
        timestamp: '2024-01-01T11:00:00Z',
        action: 'sale',
        item_name: 'Item 2',
        quantity_change: -2,
        new_quantity: 8
      }
    ];
    
    mockFetchResponse('/api/v1/inventory/merchant_001/history', mockHistory);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const historyButton = screen.getByText(/History/i);
      fireEvent.click(historyButton);
      
      expect(screen.getByText(/restock/i)).toBeInTheDocument();
      expect(screen.getByText(/sale/i)).toBeInTheDocument();
      expect(screen.getByText(/+10/i)).toBeInTheDocument();
      expect(screen.getByText(/-2/i)).toBeInTheDocument();
    });
  });

  test('displays last updated timestamps', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/Last Updated/i)).toBeInTheDocument();
      expect(screen.getByText(/12:00 PM/i)).toBeInTheDocument();
      expect(screen.getByText(/11:45 AM/i)).toBeInTheDocument();
    });
  });

  test('handles inventory filtering', () => {
    render(<InventoryView />);
    
    const filterInput = screen.getByPlaceholderText(/Filter items/i);
    fireEvent.change(filterInput, { target: { value: 'Item 1' } });
    
    expect(filterInput).toHaveValue('Item 1');
  });

  test('shows inventory analytics', async () => {
    const mockAnalytics = {
      total_items: 150,
      low_stock_items: 5,
      out_of_stock_items: 2,
      average_turnover_rate: 0.15,
      total_value: 12500.50
    };
    
    mockFetchResponse('/api/v1/inventory/analytics', mockAnalytics);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const analyticsButton = screen.getByText(/Analytics/i);
      fireEvent.click(analyticsButton);
      
      expect(screen.getByText(/Total Items/i)).toBeInTheDocument();
      expect(screen.getByText(/150/i)).toBeInTheDocument();
      expect(screen.getByText(/Low Stock/i)).toBeInTheDocument();
      expect(screen.getByText(/5/i)).toBeInTheDocument();
      expect(screen.getByText(/\$12,500/i)).toBeInTheDocument();
    });
  });

  test('handles restock requests', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const restockButton = screen.getByText(/Request Restock/i);
      fireEvent.click(restockButton);
      
      expect(screen.getByText(/Restock Request/i)).toBeInTheDocument();
      expect(screen.getByText(/Quantity/i)).toBeInTheDocument();
    });
  });

  test('displays inventory categories', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const categoryFilter = screen.getByLabelText(/Category/i);
      fireEvent.click(categoryFilter);
      
      expect(screen.getByText(/All Categories/i)).toBeInTheDocument();
      expect(screen.getByText(/Food/i)).toBeInTheDocument();
      expect(screen.getByText(/Beverages/i)).toBeInTheDocument();
    });
  });

  test('shows inventory trends', async () => {
    const mockTrends = [
      { date: '2024-01-01', quantity: 15, sales: 5 },
      { date: '2024-01-02', quantity: 12, sales: 8 },
      { date: '2024-01-03', quantity: 8, sales: 4 }
    ];
    
    mockFetchResponse('/api/v1/inventory/trends', mockTrends);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const trendsButton = screen.getByText(/Trends/i);
      fireEvent.click(trendsButton);
      
      expect(screen.getByText(/Inventory Trends/i)).toBeInTheDocument();
      expect(screen.getByText(/Sales/i)).toBeInTheDocument();
    });
  });

  test('handles bulk operations', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const selectAllCheckbox = screen.getByLabelText(/Select all/i);
      fireEvent.click(selectAllCheckbox);
      
      const bulkUpdateButton = screen.getByText(/Bulk Update/i);
      fireEvent.click(bulkUpdateButton);
      
      expect(screen.getByText(/Bulk Operations/i)).toBeInTheDocument();
    });
  });

  test('displays inventory alerts', async () => {
    const mockAlerts = [
      {
        id: 'alert_001',
        type: 'low_stock',
        message: 'Item 2 is running low',
        severity: 'warning',
        timestamp: new Date().toISOString()
      },
      {
        id: 'alert_002',
        type: 'expiry',
        message: 'Item 3 expires soon',
        severity: 'critical',
        timestamp: new Date().toISOString()
      }
    ];
    
    mockFetchResponse('/api/v1/inventory/alerts', mockAlerts);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/Item 2 is running low/i)).toBeInTheDocument();
      expect(screen.getByText(/Item 3 expires soon/i)).toBeInTheDocument();
    });
  });

  test('shows inventory value calculations', async () => {
    mockFetchResponse('/api/v1/inventory', mockInventory);
    mockFetchResponse('/api/v1/merchants', mockMerchants);
    
    render(<InventoryView />);
    
    await waitFor(() => {
      const valueButton = screen.getByText(/Total Value/i);
      fireEvent.click(valueButton);
      
      expect(screen.getByText(/Inventory Value/i)).toBeInTheDocument();
      expect(screen.getByText(/\$89.85/i)).toBeInTheDocument(); // Item 1: 15 * 5.99
    });
  });

  test('handles export functionality', () => {
    render(<InventoryView />);
    
    const exportButton = screen.getByText(/Export/i);
    fireEvent.click(exportButton);
    
    expect(screen.getByText(/Export Options/i)).toBeInTheDocument();
    expect(screen.getByText(/CSV/i)).toBeInTheDocument();
    expect(screen.getByText(/PDF/i)).toBeInTheDocument();
  });

  test('displays real-time updates from WebSocket', async () => {
    render(<InventoryView />);
    
    // Simulate WebSocket inventory update
    const mockInventoryUpdate = {
      type: 'inventory_update',
      data: {
        merchant_id: 'merchant_001',
        item_name: 'Item 1',
        new_quantity: 12,
        timestamp: new Date().toISOString()
      }
    };
    
    const event = new CustomEvent('websocket_message', { detail: mockInventoryUpdate });
    window.dispatchEvent(event);
    
    await waitFor(() => {
      expect(screen.getByText(/12/i)).toBeInTheDocument();
    });
  });

  test('handles error states gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
    
    render(<InventoryView />);
    
    await waitFor(() => {
      expect(screen.getByText(/Error loading inventory/i)).toBeInTheDocument();
    });
  });

  test('shows loading state', () => {
    render(<InventoryView />);
    
    expect(screen.getByText(/Loading inventory/i)).toBeInTheDocument();
  });

  test('handles responsive design', () => {
    render(<InventoryView />);
    
    const gridContainer = screen.getByTestId('inventory-grid');
    expect(gridContainer).toHaveClass('grid');
    expect(gridContainer).toHaveClass('md:grid-cols-2');
    expect(gridContainer).toHaveClass('lg:grid-cols-3');
  });

  test('displays refresh controls', () => {
    render(<InventoryView />);
    
    const refreshButton = screen.getByLabelText(/refresh inventory/i);
    fireEvent.click(refreshButton);
    
    expect(screen.getByText(/Refreshing/i)).toBeInTheDocument();
  });

  test('shows inventory search', () => {
    render(<InventoryView />);
    
    const searchInput = screen.getByPlaceholderText(/Search inventory/i);
    fireEvent.change(searchInput, { target: { value: 'Item 1' } });
    
    expect(searchInput).toHaveValue('Item 1');
  });
}); 