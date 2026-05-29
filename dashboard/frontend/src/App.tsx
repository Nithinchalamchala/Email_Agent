import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Link, useLocation } from "react-router-dom";
import EmailTable from "./components/EmailTable";
import EmailDetails from "./components/EmailDetails";
import CalendarPage from "./components/CalendarPage";
import { Layout, Avatar, Button, message as antMessage, Tooltip, Space } from "antd";
import {
  CheckCircleFilled,
  SyncOutlined,
  MailOutlined,
  UserOutlined,
  LogoutOutlined,
  CloudDownloadOutlined,
} from "@ant-design/icons";
import { useMsal, useIsAuthenticated } from "@azure/msal-react";
import { graphScopes } from "./auth/msalConfig";
import { fetchSyncStatus, triggerEmailFetch } from "./api";

const { Header, Content, Footer } = Layout;

interface SyncStatus {
  last_sync: string | null;
  ai_status: string;
  connected_account: string;
  user_email: string;
}

const timeAgo = (dateStr: string | null): string => {
  if (!dateStr) return "Never synced";
  try {
    const mins = Math.floor((Date.now() - new Date(dateStr).getTime()) / 60_000);
    if (mins < 1)   return "Just now";
    if (mins === 1) return "1 min ago";
    if (mins < 60)  return `${mins} mins ago`;
    const hrs = Math.floor(mins / 60);
    return hrs < 24 ? `${hrs}h ago` : "Over a day ago";
  } catch { return "Unknown"; }
};

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
  const { instance, accounts } = useMsal();
  const isAuthenticated         = useIsAuthenticated();
  const [syncStatus, setSyncStatus] = useState<SyncStatus | null>(null);
  const [fetching, setFetching]     = useState(false);

  useEffect(() => {
    document.body.style.fontFamily =
      "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif";
    document.body.style.margin = "0";

    const link = document.createElement("link");
    link.href = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap";
    link.rel  = "stylesheet";
    document.head.appendChild(link);

    const load = () => fetchSyncStatus().then(setSyncStatus).catch(() => {});
    load();
    const interval = setInterval(load, 60_000);
    return () => clearInterval(interval);
  }, []);

  // ── MSAL helpers ────────────────────────────────────────────────────────
  const handleSignIn = () => {
    instance.loginRedirect({ scopes: graphScopes }).catch(console.error);
  };

  const handleSignOut = () => {
    instance.logoutRedirect().catch(console.error);
  };

  const getGraphToken = async (): Promise<string> => {
    const account = accounts[0];
    if (!account) throw new Error("Not signed in to Microsoft");
    try {
      const result = await instance.acquireTokenSilent({ scopes: graphScopes, account });
      return result.accessToken;
    } catch {
      instance.loginRedirect({ scopes: graphScopes });
      throw new Error("Redirecting to sign in…");
    }
  };

  // ── Fetch emails via Graph token from browser ────────────────────────────
  const handleFetchEmails = async () => {
    setFetching(true);
    try {
      const token   = await getGraphToken();
      const result  = await triggerEmailFetch(token);
      if (result.processed > 0) {
        antMessage.success(`${result.processed} new email${result.processed > 1 ? "s" : ""} fetched. Click Refresh to view.`);
      } else {
        antMessage.info("No new unread emails found.");
      }
      // Refresh sync status
      fetchSyncStatus().then(setSyncStatus).catch(() => {});
    } catch (err: any) {
      antMessage.error(err.message ?? "Failed to fetch emails.");
    } finally {
      setFetching(false);
    }
  };

  // ── Derive display info ──────────────────────────────────────────────────
  const msalEmail   = accounts[0]?.username ?? "";
  const msalName    = accounts[0]?.name     ?? "";
  const displayName = msalEmail.includes("@") ? msalEmail.split("@")[0] : msalName || "Account";
  const initial     = displayName.charAt(0).toUpperCase();

  return (
    <BrowserRouter>
      <Layout style={{ minHeight: "100vh", background: "#f1f5f9" }}>

        {/* ── Header ────────────────────────────────────────────────────── */}
        <Header style={{
          background:    "#0f172a",
          display:       "flex",
          alignItems:    "center",
          justifyContent: "space-between",
          padding:       "0 24px",
          height:        56,
          position:      "sticky",
          top:           0,
          zIndex:        200,
          borderBottom:  "1px solid #1e293b",
          boxShadow:     "0 1px 3px rgba(0,0,0,0.3)",
        }}>

          {/* Left — wordmark */}
          <Link to="/" style={{ display: "flex", alignItems: "center", gap: 10, textDecoration: "none" }}>
            <div style={{
              width: 30, height: 30, borderRadius: 7,
              background: "#2563eb", flexShrink: 0,
              display: "flex", alignItems: "center", justifyContent: "center",
              fontWeight: 700, fontSize: 15, color: "#fff", letterSpacing: -0.5,
            }}>H</div>
            <span style={{ color: "#f8fafc", fontSize: 15, fontWeight: 700, letterSpacing: 0.5 }}>Hermes</span>
            <span style={{ color: "#475569", fontSize: 13 }}>Email Intelligence</span>
          </Link>

          {/* Nav links */}
          <Space size={4} align="center">
            <NavLink to="/" label="📧 Pipeline" />
            <NavLink to="/calendar" label="📅 Calendar" />
          </Space>

          {/* Right — status + auth */}
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>

            {/* AI status */}
            <div style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "4px 12px", borderRadius: 6,
              background: "#0f2a1a", border: "1px solid #14532d",
              fontSize: 12, fontWeight: 500, color: "#4ade80",
            }}>
              <CheckCircleFilled style={{ fontSize: 11 }} />
              AI Engine Online
            </div>

            {/* Sync time */}
            <Tooltip title={`Last processed: ${syncStatus?.last_sync ?? "No data"}`}>
              <div style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "4px 12px", borderRadius: 6,
                background: "#1e293b", border: "1px solid #334155",
                fontSize: 12, color: "#94a3b8", cursor: "default",
              }}>
                <SyncOutlined style={{ fontSize: 11 }} />
                {timeAgo(syncStatus?.last_sync ?? null)}
              </div>
            </Tooltip>

            {isAuthenticated ? (
              <>
                {/* Connected indicator */}
                <div style={{
                  display: "flex", alignItems: "center", gap: 6,
                  padding: "4px 12px", borderRadius: 6,
                  background: "#0c1f3f", border: "1px solid #1e3a5f",
                  fontSize: 12, fontWeight: 500, color: "#60a5fa",
                }}>
                  <MailOutlined style={{ fontSize: 11 }} />
                  Outlook
                </div>

                {/* Fetch emails button */}
                <Button
                  size="small"
                  icon={<CloudDownloadOutlined />}
                  loading={fetching}
                  onClick={handleFetchEmails}
                  style={{
                    borderRadius: 6, fontWeight: 500, fontSize: 12,
                    background: "#1e3a5f", border: "1px solid #2563eb",
                    color: "#93c5fd",
                  }}
                >
                  Fetch Emails
                </Button>

                {/* Divider */}
                <div style={{ width: 1, height: 28, background: "#1e293b" }} />

                {/* Profile */}
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Avatar size={28} style={{ background: "#2563eb", fontSize: 12, fontWeight: 600, flexShrink: 0 }}>
                    {initial}
                  </Avatar>
                  <div style={{ lineHeight: 1.35 }}>
                    <div style={{ color: "#f1f5f9", fontSize: 12, fontWeight: 600 }}>{displayName}</div>
                    <div style={{ color: "#475569", fontSize: 11 }}>{msalEmail}</div>
                  </div>
                </div>

                {/* Sign out */}
                <Tooltip title="Sign out from Microsoft">
                  <Button
                    size="small"
                    icon={<LogoutOutlined />}
                    onClick={handleSignOut}
                    style={{
                      borderRadius: 6, background: "transparent",
                      border: "1px solid #334155", color: "#64748b",
                    }}
                  />
                </Tooltip>
              </>
            ) : (
              <>
                {/* Sign in button */}
                <Button
                  size="small"
                  icon={<UserOutlined />}
                  onClick={handleSignIn}
                  style={{
                    borderRadius: 6, fontWeight: 600, fontSize: 12,
                    background: "#2563eb", border: "none", color: "#fff",
                  }}
                >
                  Sign in with Microsoft
                </Button>
                <span style={{ color: "#475569", fontSize: 11 }}>
                  Required to fetch emails from Outlook
                </span>
              </>
            )}
          </div>
        </Header>

        {/* ── Content ───────────────────────────────────────────────────── */}
        <Content style={{ padding: "28px 24px", maxWidth: 1400, width: "100%", margin: "0 auto", flex: 1 }}>
          <Routes>
            <Route path="/"          element={<EmailTable />} />
            <Route path="/email/:id" element={<EmailDetails />} />
            <Route path="/calendar" element={<CalendarPage />} />
          </Routes>
        </Content>

        {/* ── Footer ────────────────────────────────────────────────────── */}
        <Footer style={{
          textAlign: "center", background: "transparent",
          color: "#94a3b8", fontSize: 12, padding: "16px 0 24px",
          borderTop: "1px solid #e2e8f0",
        }}>
          Hermes Email Intelligence &copy; {new Date().getFullYear()}
        </Footer>
      </Layout>
    </BrowserRouter>
  );
};

export default App;
