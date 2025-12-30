import React from "react";
import { Typography } from "antd";

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  return (
    <div>
      <Title level={2}>Welcome to EVCS</Title>
      <Paragraph>
        This is the dashboard for the Entity Version Control System.
      </Paragraph>
    </div>
  );
};

export default Home;
