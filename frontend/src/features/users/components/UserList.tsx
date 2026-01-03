import { App, Button, Card, Space, Table, Tag } from "antd";
import { DeleteOutlined, EditOutlined, PlusOutlined } from "@ant-design/icons";
import { useEffect, useState } from "react";
import { CreateUserPayload, User } from "@/types/user";
import { UserModal } from "./UserModal";
import { useUserStore } from "@/stores/useUserStore";
import type { ColumnType } from "antd/es/table";

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
      title: "Are you sure you want to delete this user?",
      content: "This action cannot be undone.",
      okText: "Yes, Delete",
      okType: "danger",
      onOk: async () => {
        await deleteUser(id);
        message.success("User deleted successfully");
        fetchUsers();
      },
    });
  };

  const columns: ColumnType<User>[] = [
    {
      title: "Full Name",
      dataIndex: "full_name",
      key: "full_name",
      sorter: (a: User, b: User) => a.full_name.localeCompare(b.full_name),
    },
    {
      title: "Email",
      dataIndex: "email",
      key: "email",
    },
    {
      title: "Role",
      dataIndex: "role",
      key: "role",
      render: (role: string) => <Tag color="blue">{role.toUpperCase()}</Tag>,
    },
    {
      title: "Department",
      dataIndex: "department",
      key: "department",
    },
    {
      title: "Status",
      dataIndex: "is_active",
      key: "is_active",
      render: (isActive: boolean) => (
        <Tag color={isActive ? "green" : "red"}>
          {isActive ? "Active" : "Inactive"}
        </Tag>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_, record) => (
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
      <Card
        title="User Management"
        extra={
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
        }
        style={{ marginBottom: 16 }}
      >
        <Table<User>
          columns={columns}
          dataSource={users}
          loading={loading}
          rowKey="id"
          pagination={{
            pageSize: 10,
            showSizeChanger: true,
          }}
        />
      </Card>

      <UserModal
        open={modalOpen}
        onCancel={() => setModalOpen(false)}
        onOk={async (values) => {
          if (selectedUser) {
            await useUserStore.getState().updateUser(selectedUser.id, values);
            message.success("User updated successfully");
          } else {
            // Determine create payload (UserModal handles validation)
            await useUserStore
              .getState()
              .createUser(values as CreateUserPayload);
            message.success("User created successfully");
          }
          setModalOpen(false);
          fetchUsers();
        }}
        confirmLoading={loading}
        initialValues={selectedUser}
      />
    </div>
  );
};
