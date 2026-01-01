import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DataTable } from './DataTable';


// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = value.toString();
    }),
    clear: vi.fn(() => {
      store = {};
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
  };
})();
Object.defineProperty(window, 'localStorage', { value: localStorageMock });

describe('DataTable', () => {
  const mockDataSource = [
    { key: '1', name: 'User 1', age: 30 },
    { key: '2', name: 'User 2', age: 25 },
  ];

  const mockColumns = [
    { title: 'Name', dataIndex: 'name', key: 'name', sorter: true },
    { title: 'Age', dataIndex: 'age', key: 'age' },
  ];

  const defaultProps = {
    columns: mockColumns,
    dataSource: mockDataSource,
    storageKey: 'test_table',
    loading: false,
  };

  beforeEach(() => {
    localStorageMock.clear();
    vi.clearAllMocks();
  });

  it('renders columns and data correctly', () => {
    render(<DataTable {...defaultProps} />);
    
    expect(screen.getByText('User 1')).toBeInTheDocument();
    expect(screen.getByText('User 2')).toBeInTheDocument();
    expect(screen.getByText('Name')).toBeInTheDocument();
    expect(screen.getByText('Age')).toBeInTheDocument();
  });

  it('persists changes to localStorage', async () => {
    render(<DataTable {...defaultProps} />);
    
    // Simulate Sort (click column header)
    const nameHeader = screen.getByText('Name');
    fireEvent.click(nameHeader);

    await waitFor(() => {
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'table_pref_test_table',
        expect.stringContaining('"sortOrder":{"columnKey":"name","order":"ascend"}')
      );
    });
  });

  it('loads state from localStorage', () => {
    const savedState = {
       pagination: { pageSize: 20 },
       sortOrder: { columnKey: 'name', order: 'descend' }
    };
    localStorageMock.getItem.mockReturnValue(JSON.stringify(savedState));

    render(<DataTable {...defaultProps} />);
    
    // Check if sort class exists or aria-sort (AntD specifics)
    // AntD uses aria-sort="descending" or similar on th
    const nameHeader = screen.getByText('Name').closest('th');
    expect(nameHeader).toHaveAttribute('aria-sort', 'descending');
  });
});
