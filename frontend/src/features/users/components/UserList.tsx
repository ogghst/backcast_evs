import { useEffect, useState } from 'react';
import { Button, Space, Tag, App } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useUserStore } from '@/stores/useUserStore';
import { DataTable } from '@/components/DataTable';
import { User, UserRole, CreateUserPayload } from '@/types/user';
import { UserModal } from './UserModal';

export const UserList = () => {
  const { users, loading, fetchUsers, deleteUser } = useUserStore();
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const { message, modal } = App.useApp();

  useEffect(() => {
    fetchUsers();
  }, [fetchUsers]);

  const handleDelete = async (id: string) => {
    modal.confirm({
      title: 'Are you sure you want to delete this user?',
      content: 'This action cannot be undone.',
      okText: 'Yes, Delete',
      okType: 'danger',
      onOk: async () => {
        await deleteUser(id);
        message.success('User deleted successfully');
      },
    });
  };

  const columns = [
    {
      title: 'Full Name',
      dataIndex: 'full_name',
      key: 'full_name',
      sorter: (a: User, b: User) => a.full_name.localeCompare(b.full_name),
    },
    {
      title: 'Email',
      dataIndex: 'email',
      key: 'email',
    },
    {
      title: 'Role',
      dataIndex: 'role',
      key: 'role',
      render: (role: UserRole) => <Tag color="blue">{role.toUpperCase()}</Tag>,
    },
    {
      title: 'Status',
      dataIndex: 'is_active',
      key: 'is_active',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'red'}>{active ? 'Active' : 'Inactive'}</Tag>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: unknown, record: User) => (
        <Space>
          <Button 
            icon={<EditOutlined />} 
            onClick={() => {
              setSelectedUser(record);
              setModalOpen(true);
            }}
          />
          <Button 
            danger 
            icon={<DeleteOutlined />} 
            onClick={() => handleDelete(record.id)} 
          />
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 16, display: 'flex', justifyContent: 'space-between' }}>
        <h2>User Management</h2>
        <Button 
          type="primary" 
          icon={<PlusOutlined />} 
          onClick={() => {
            setSelectedUser(null);
            setModalOpen(true);
          }}
        >
          Add User
        </Button>
      </div>

      <DataTable
        columns={columns}
        dataSource={users}
        loading={loading}
        rowKey="id"
        storageKey="users_table"
      />

      <UserModal
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={async (values) => {
          if (selectedUser) {
            await useUserStore.getState().updateUser(selectedUser.id, values);
            message.success('User updated successfully');
          } else {
            // Determine create payload (UserModal handles validation)
             await useUserStore.getState().createUser(values as CreateUserPayload); 
             // Note: values needs casting or precise type guard if strictly typed between Create/Update
             // CreateUserPayload vs UpdateUserPayload
             message.success('User created successfully');
          }
          setModalOpen(false);
        }}
        confirmLoading={loading}
        initialValues={selectedUser}
      />
    </div>
  );
};
