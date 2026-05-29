import React, { useEffect } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import EmailTable from "./components/EmailTable";
import EmailDetails from "./components/EmailDetails";
import CalendarPage from "./components/CalendarPage";
import { Layout, Badge, Space } from "antd";

const { Header, Content, Footer } = Layout;

const NavLink: React.FC<{ to: string; label: string }> = ({ to, label }) => {
  const location = useLocation();
  const active = location.pathname === to || (to !== "/" && location.pathname.startsWith(to));
  return (
    <Link
      to={to}
      style={{
        color: active ? "#ffffff" : "#94a3b8",
        fontWeight: active ? 700 : 500,
        fontSize: 14,
        textDecoration: "none",
        padding: "6px 14px",
        borderRadius: 8,
        background: active ? "#1e293b" : "transparent",
        border: active ? "1px solid #334155" : "1px solid transparent",
        transition: "all 0.15s",
      }}
    >
      {label}
    </Link>
  );
};

const App: React.FC = () => {
  // Inject premium typography dynamically
  useEffect(() => {
    const link = document.createElement("link");
    link.href = "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap";
    link.rel = "stylesheet";
    document.head.appendChild(link);

    // Apply global font settings
    document.body.style.fontFamily = "'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif";
    document.body.style.backgroundColor = "#f6f8fa";
    document.body.style.margin = "0";
    document.body.style.setProperty("-webkit-font-smoothing", "antialiased");
  }, []);

  return (
    <BrowserRouter>
      <Layout style={{ minHeight: "100vh", background: "#f6f8fa" }}>
        {/* Modern Custom Premium Header Shell */}
        <Header style={{ 
          background: "#0f172a", // Sleek dark slate
          color: "white", 
          display: "flex", 
          justifyContent: "space-between", 
          alignItems: "center",
          padding: "0 24px",
          height: "64px",
          boxShadow: "0 4px 20px rgba(0, 0, 0, 0.08)",
          position: "sticky",
          top: 0,
          zIndex: 100,
          borderBottom: "1px solid #1e293b"
        }}>
          {/* Logo with Dynamic Lightning Symbol */}
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <div style={{
              background: "linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%)",
              width: "36px",
              height: "36px",
              borderRadius: "10px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 12px rgba(59, 130, 246, 0.5)",
              fontSize: "18px"
            }}>
              ⚡
            </div>
            <span style={{ 
              color: "white", 
              fontSize: "20px", 
              fontWeight: 800, 
              letterSpacing: "0.5px",
              background: "linear-gradient(to right, #ffffff, #94a3b8)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent"
            }}>
              HERMES <span style={{ fontWeight: 400, color: "#94a3b8", fontSize: "16px" }}>AI</span>
            </span>
          </Link>

          {/* Nav links */}
          <Space size={4} align="center">
            <NavLink to="/" label="📧 Pipeline" />
            <NavLink to="/calendar" label="📅 Calendar" />
          </Space>

          {/* Connection Status & Pipeline Meta info */}
          <Space size={16} align="center">
            <div style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              background: "#1e293b",
              padding: "6px 14px",
              borderRadius: "20px",
              border: "1px solid #334155",
              fontSize: "12px",
              fontWeight: 500,
              color: "#cbd5e1"
            }}>
              <Badge status="processing" color="#10b981" />
              <span>PIPELINE ENGINE ONLINE</span>
            </div>
            <span style={{ fontSize: "11px", color: "#64748b", fontWeight: 500 }}>
              v1.2.0 (Local API)
            </span>
          </Space>
        </Header>

        {/* Content Container with dynamic spacing */}
        <Content style={{ 
          padding: "32px 24px",
          maxWidth: "1440px",
          width: "100%",
          margin: "0 auto",
          flex: 1
        }}>
          <Routes>
            <Route path="/" element={<EmailTable />} />
            <Route path="/email/:id" element={<EmailDetails />} />
            <Route path="/calendar" element={<CalendarPage />} />
          </Routes>
        </Content>

        {/* Premium footer with subtle branding */}
        <Footer style={{ 
          textAlign: "center", 
          background: "transparent", 
          color: "#94a3b8", 
          fontSize: "13px",
          padding: "24px 0 32px",
          fontWeight: 500
        }}>
          Hermes Email Intelligence Pipeline &copy; {new Date().getFullYear()} &bull; Advanced Agentic Decision Engine
        </Footer>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
