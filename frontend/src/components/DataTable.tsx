import React, { useState } from 'react';
import { Table, TableProps } from 'antd';
import { ColumnsType, TablePaginationConfig } from 'antd/es/table';
import { FilterValue } from 'antd/es/table/interface';

interface DataTableProps<T> extends Omit<TableProps<T>, 'columns'> {
  columns: ColumnsType<T>;
  storageKey: string;
  onRefresh?: () => void;
}

interface TableState {
  pagination: TablePaginationConfig;
  filters: Record<string, FilterValue | null>;
  sortOrder?: {
    columnKey: React.Key;
    order: 'ascend' | 'descend';
  };
}

export const DataTable = <T extends object>({
  columns: initialColumns,
  storageKey,
  dataSource,
  loading,
  onChange,
  pagination,
  ...props
}: DataTableProps<T>) => {
  // Load initial state from localStorage
  const getSavedState = (): Partial<TableState> => {
    try {
      const saved = localStorage.getItem(`table_pref_${storageKey}`);
      return saved ? JSON.parse(saved) : {};
    } catch {
      return {};
    }
  };

  const [savedState, setSavedState] = useState<Partial<TableState>>(getSavedState());

  // Merge saved sort order into columns
  const columns = initialColumns.map((col) => {
    if (savedState.sortOrder && col.key === savedState.sortOrder.columnKey) {
      return {
        ...col,
        defaultSortOrder: savedState.sortOrder.order,
      };
    }
    return col;
  });

  const handleTableChange: TableProps<T>['onChange'] = (
    newPagination,
    newFilters,
    newSorter,
    extra
  ) => {
    // Handle single sorter for now
    const sorter = Array.isArray(newSorter) ? newSorter[0] : newSorter;
    
    // Save preferences
    const newState: TableState = {
      pagination: {
        pageSize: newPagination.pageSize,
      },
      filters: newFilters,
      sortOrder: sorter.column && sorter.order ? {
        columnKey: sorter.columnKey as React.Key,
        order: sorter.order,
      } : undefined
    };

    localStorage.setItem(`table_pref_${storageKey}`, JSON.stringify(newState));
    setSavedState(newState);

    // Propagate event
    if (onChange) {
      onChange(newPagination, newFilters, newSorter, extra);
    }
  };

  return (
    <Table
      {...props}
      columns={columns}
      dataSource={dataSource}
      loading={loading}
      onChange={handleTableChange}
      pagination={{
        ...pagination,
        defaultPageSize: savedState.pagination?.pageSize || 10,
        showSizeChanger: true,
      }}
    />
  );
};
