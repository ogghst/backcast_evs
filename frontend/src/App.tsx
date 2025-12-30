import React from 'react';
import { Button, Typography } from 'antd';

const { Title } = Typography;

const App: React.FC = () => {
  return (
    <div style={{ padding: '20px' }}>
      <Title level={1}>Project Management Dashboard</Title>
      <Button type="primary">Get Started</Button>
    </div>
  );
};

export default App;
