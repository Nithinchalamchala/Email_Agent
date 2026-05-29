import React, { useEffect, useState, useCallback, useRef } from "react";
import { Typography, Row, Col, Input, Select, Space, Avatar, Spin, Button } from "antd";
import {
  CalendarOutlined,
  ClockCircleOutlined,
  FieldTimeOutlined,
  MailOutlined,
  StarOutlined,
  RobotOutlined,
  EditOutlined,
  InboxOutlined,
  ReloadOutlined,
  PaperClipOutlined,
  FlagFilled,
} from "@ant-design/icons";
import { useNavigate } from "react-router-dom";
import { fetchBatch, fetchStats, markEmailRead } from "../api";

const { Title, Text } = Typography;
const { Option }      = Select;

// ── Design tokens ──────────────────────────────────────────────────────────────

const C = {
  primary:   "#2563eb",
  primaryBg: "#eff6ff",
  text1:     "#0f172a",
  text2:     "#475569",
  text3:     "#94a3b8",
  border:    "#e2e8f0",
  bgCard:    "#ffffff",
  bgPage:    "#f1f5f9",
  unreadBg:  "#f0f9ff",
  unreadBdr: "#2563eb",
  high:      "#dc2626",
  highBg:    "#fef2f2",
  medium:    "#d97706",
  mediumBg:  "#fffbeb",
  low:       "#16a34a",
  lowBg:     "#f0fdf4",
};

const PAGE_SIZE = 25;

// ── Filter definitions ─────────────────────────────────────────────────────────

const FILTERS = [
  { key: "7days",          label: "Last 7 Days",  icon: <CalendarOutlined /> },
  { key: "today",          label: "Today",         icon: <ClockCircleOutlined /> },
  { key: "yesterday",      label: "Yesterday",     icon: <FieldTimeOutlined /> },
  { key: "unread",         label: "Unread",        icon: <MailOutlined /> },
  { key: "important",      label: "Important",     icon: <StarOutlined /> },
  { key: "ai_replied",     label: "AI Replied",    icon: <RobotOutlined /> },
  { key: "pending_review", label: "Drafts",        icon: <EditOutlined /> },
  { key: "all",            label: "All Mail",      icon: <InboxOutlined /> },
];

// ── Category + priority mapping ────────────────────────────────────────────────

interface Cat { label: string; color: string; bg: string; }

const CATEGORY: Record<string, Cat> = {
  reply_needed:    { label: "Reply Needed",  color: "#9a3412", bg: "#fff7ed" },
  complaint:       { label: "Complaint",     color: "#991b1b", bg: "#fef2f2" },
  meeting_related: { label: "Meeting",       color: "#1e40af", bg: "#eff6ff" },
  support_request: { label: "Support",       color: "#6b21a8", bg: "#faf5ff" },
  follow_up:       { label: "Follow-up",     color: "#0e7490", bg: "#ecfeff" },
  informational:   { label: "Informational", color: "#374151", bg: "#f9fafb" },
};

const priorityStyle = (p: string) => {
  const v = (p || "").toLowerCase();
  if (v === "high" || v === "urgent") return { label: "High",   color: C.high,   bg: C.highBg };
  if (v === "medium")                 return { label: "Medium", color: C.medium, bg: C.mediumBg };
  return                                     { label: "Low",    color: C.low,    bg: C.lowBg };
};

// ── Helpers ────────────────────────────────────────────────────────────────────

const avatarColor = (s: string) => {
  const map: Record<string, string> = {
    A:"#b45309",B:"#7c3aed",C:"#d97706",D:"#0e7490",E:"#1d4ed8",
    F:"#b45309",G:"#7c3aed",H:"#d97706",I:"#0e7490",J:"#1d4ed8",
    K:"#15803d",L:"#be185d",M:"#c2410c",N:"#c2410c",O:"#0f766e",
    P:"#15803d",Q:"#1d4ed8",R:"#6b21a8",S:"#b91c1c",T:"#b45309",
    U:"#1d4ed8",V:"#7c3aed",W:"#d97706",X:"#0e7490",Y:"#c2410c",Z:"#6b21a8",
  };
  return map[(s || "U").trim().charAt(0).toUpperCase()] || "#1d4ed8";
};

const formatDate = (d: string | null): string => {
  if (!d) return "";
  try {
    const dt  = new Date(d);
    const now = new Date();
    const h   = (now.getTime() - dt.getTime()) / 3_600_000;
    if (h < 1)  return "Just now";
    if (h < 24) return `${Math.floor(h)}h ago`;
    if (h < 48) return "Yesterday";
    return dt.toLocaleDateString("en-US", { month: "short", day: "numeric" });
  } catch { return d; }
};

const isNew = (d: string | null) =>
  !!d && Date.now() - new Date(d).getTime() < 86_400_000;

const hasAttachment = (body: string) =>
  /\b(attach|attachment|enclosed|please find)\b/i.test(body || "");

// ── localStorage helpers ───────────────────────────────────────────────────────

const loadReadIds = (): Set<string> => {
  try { return new Set(JSON.parse(localStorage.getItem("hermes_read_ids") || "[]")); }
  catch { return new Set(); }
};
const saveReadIds = (ids: Set<string>) => {
  try { localStorage.setItem("hermes_read_ids", JSON.stringify([...ids])); } catch {}
};

// ── EmailCard ──────────────────────────────────────────────────────────────────

interface CardProps { item: any; isUnread: boolean; onClick: () => void; }

const EmailCard: React.FC<CardProps> = ({ item, isUnread, onClick }) => {
  const [hovered, setHovered] = useState(false);

  const cat  = CATEGORY[item.intent] ?? null;
  const pri  = priorityStyle(item.priority);
  const showNew   = isNew(item.received_date);
  const showClip  = hasAttachment(item.show_body);

  return (
    <div
      onClick={onClick}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        display:     "flex",
        alignItems:  "stretch",
        background:  isUnread ? C.unreadBg : C.bgCard,
        border:      `1px solid ${isUnread ? "#bfdbfe" : C.border}`,
        borderLeft:  `3px solid ${isUnread ? C.unreadBdr : "transparent"}`,
        borderRadius: 8,
        marginBottom: 6,
        cursor:      "pointer",
        boxShadow:   hovered
          ? "0 4px 16px rgba(0,0,0,0.10)"
          : "0 1px 3px rgba(0,0,0,0.04)",
        transform:   hovered ? "translateY(-1px)" : "none",
        transition:  "box-shadow 0.18s ease, transform 0.18s ease, border-color 0.18s ease",
      }}
    >
      {/* Unread dot */}
      <div style={{ display: "flex", alignItems: "center", padding: "0 10px 0 12px", flexShrink: 0 }}>
        <div style={{
          width: 7, height: 7, borderRadius: "50%",
          background: isUnread ? C.primary : "transparent",
          border:     isUnread ? "none" : `1.5px solid ${C.border}`,
          transition: "background 0.2s",
        }} />
      </div>

      {/* Avatar */}
      <div style={{ display: "flex", alignItems: "center", paddingRight: 14, flexShrink: 0 }}>
        <Avatar
          size={36}
          style={{
            background: avatarColor(item.sender),
            fontWeight: 600, fontSize: 14,
            flexShrink: 0,
          }}
        >
          {(item.sender || "U").charAt(0).toUpperCase()}
        </Avatar>
      </div>

      {/* Content */}
      <div style={{ flex: 1, padding: "13px 0", minWidth: 0, overflow: "hidden" }}>

        {/* Sender row */}
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
          <span style={{
            fontWeight:   isUnread ? 600 : 500,
            fontSize:     13,
            color:        C.text1,
            whiteSpace:   "nowrap",
            overflow:     "hidden",
            textOverflow: "ellipsis",
            maxWidth:     260,
          }}>
            {item.sender || "Unknown Sender"}
          </span>
          {showNew && (
            <span style={{
              fontSize: 10, fontWeight: 600, letterSpacing: 0.4,
              color: C.primary,
              background: "#dbeafe",
              padding: "1px 7px", borderRadius: 4,
              flexShrink: 0,
            }}>
              NEW
            </span>
          )}
          {showClip && (
            <PaperClipOutlined style={{ color: C.text3, fontSize: 12, flexShrink: 0 }} />
          )}
        </div>

        {/* Subject */}
        <div style={{
          fontWeight:   isUnread ? 600 : 400,
          fontSize:     13,
          color:        isUnread ? C.text1 : C.text2,
          whiteSpace:   "nowrap",
          overflow:     "hidden",
          textOverflow: "ellipsis",
          marginBottom: 4,
        }}>
          {item.show_subject}
        </div>

        {/* Preview */}
        <div style={{
          fontSize:     12,
          color:        C.text3,
          whiteSpace:   "nowrap",
          overflow:     "hidden",
          textOverflow: "ellipsis",
          marginBottom: 8,
        }}>
          {(item.show_body || "No preview available.").slice(0, 140)}
        </div>

        {/* Tags row */}
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
          {cat && (
            <span style={{
              fontSize: 11, fontWeight: 500,
              padding: "2px 8px", borderRadius: 4,
              background: cat.bg, color: cat.color,
              border: `1px solid ${cat.color}28`,
            }}>
              {cat.label}
            </span>
          )}
          {item.requires_human_review && (
            <span style={{
              fontSize: 11, fontWeight: 500,
              padding: "2px 8px", borderRadius: 4,
              background: "#fffbeb", color: "#92400e",
              border: "1px solid #fde68a",
            }}>
              Review Required
            </span>
          )}
          {item.source_type === "o365" && (
            <span style={{
              fontSize: 11, fontWeight: 400,
              padding: "2px 8px", borderRadius: 4,
              background: "#f8fafc", color: C.text3,
              border: `1px solid ${C.border}`,
            }}>
              Outlook
            </span>
          )}
        </div>
      </div>

      {/* Right — date + priority */}
      <div style={{
        display:        "flex",
        flexDirection:  "column",
        alignItems:     "flex-end",
        justifyContent: "space-between",
        padding:        "13px 16px",
        flexShrink:     0,
        minWidth:       110,
      }}>
        <span style={{ fontSize: 11, color: C.text3, whiteSpace: "nowrap" }}>
          {formatDate(item.received_date)}
        </span>
        <span style={{
          fontSize:     10,
          fontWeight:   600,
          padding:      "2px 8px",
          borderRadius: 4,
          background:   pri.bg,
          color:        pri.color,
          letterSpacing: 0.2,
          display:      "flex",
          alignItems:   "center",
          gap:          4,
        }}>
          {pri.label === "High" && (
            <FlagFilled style={{ fontSize: 9 }} />
          )}
          {pri.label}
        </span>
      </div>
    </div>
  );
};

// ── Main component ─────────────────────────────────────────────────────────────

const EmailTable: React.FC = () => {
  const [emails, setEmails]           = useState<any[]>([]);
  const [total, setTotal]             = useState(0);
  const [hasMore, setHasMore]         = useState(true);
  const [loading, setLoading]         = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [stats, setStats]             = useState({ total: 0, unread: 0, needs_review: 0, high_priority: 0 });

  const [activeFilter, setActiveFilter]       = useState("7days");
  const [searchText, setSearchText]           = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [priorityFilter, setPriorityFilter]   = useState<string | undefined>();
  const [safetyFilter, setSafetyFilter]       = useState<string | undefined>();
  const [actionFilter, setActionFilter]       = useState<string | undefined>();
  const [readIds, setReadIds]                 = useState<Set<string>>(loadReadIds);

  const pageRef      = useRef(0);
  const hasMoreRef   = useRef(true);
  const isLoadingRef = useRef(false);
  const sentinelRef  = useRef<HTMLDivElement>(null);
  const navigate     = useNavigate();

  // Debounce
  useEffect(() => {
    const t = setTimeout(() => setDebouncedSearch(searchText), 400);
    return () => clearTimeout(t);
  }, [searchText]);

  // Stats
  useEffect(() => {
    fetchStats().then(setStats).catch(() => {});
  }, []);

  // Load page
  const loadPage = useCallback(async (page: number, reset: boolean) => {
    if (isLoadingRef.current) return;
    isLoadingRef.current = true;
    reset ? setLoading(true) : setLoadingMore(true);
    try {
      const data = await fetchBatch({
        page,
        limit:    PAGE_SIZE,
        filter:   activeFilter,
        search:   debouncedSearch,
        priority: priorityFilter || "",
        safety:   safetyFilter   || "",
        action:   actionFilter   || "",
      });
      const transformed = (data.results || []).map((item: any) => ({
        ...item,
        show_subject: item.subject || "(No Subject)",
        show_body:    item.body    || "",
      }));
      setEmails(prev => reset ? transformed : [...prev, ...transformed]);
      setTotal(data.total);
      setHasMore(data.has_more);
      hasMoreRef.current = data.has_more;
      pageRef.current    = page;

      const backendRead: string[] = transformed.filter((e: any) => e.is_read).map((e: any) => e.id);
      if (backendRead.length) {
        setReadIds(prev => {
          const m = new Set([...prev, ...backendRead]);
          saveReadIds(m);
          return m;
        });
      }
    } catch { /* silent */ }
    finally {
      isLoadingRef.current = false;
      reset ? setLoading(false) : setLoadingMore(false);
    }
  }, [activeFilter, debouncedSearch, priorityFilter, safetyFilter, actionFilter]);

  // Reset on filter change
  useEffect(() => {
    pageRef.current = 0; hasMoreRef.current = true;
    setHasMore(true); setEmails([]);
    loadPage(1, true);
  }, [loadPage]);

  // Infinite scroll
  useEffect(() => {
    const el = sentinelRef.current;
    if (!el) return;
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting && hasMoreRef.current && !isLoadingRef.current) loadPage(pageRef.current + 1, false); },
      { rootMargin: "300px", threshold: 0 }
    );
    obs.observe(el);
    return () => obs.disconnect();
  }, [loadPage]);

  const handleMarkAsRead = useCallback((id: string) => {
    setReadIds(prev => {
      if (prev.has(id)) return prev;
      const u = new Set([...prev, id]);
      saveReadIds(u);
      markEmailRead(id).catch(() => {});
      return u;
    });
  }, []);

  const handleClick = useCallback((item: any) => {
    handleMarkAsRead(item.id);
    navigate(`/email/${item.id}`);
  }, [handleMarkAsRead, navigate]);

  const handleReload = useCallback(() => {
    pageRef.current = 0; hasMoreRef.current = true;
    setHasMore(true); setEmails([]);
    loadPage(1, true);
    fetchStats().then(setStats).catch(() => {});
  }, [loadPage]);

  const handleFilterClick = (key: string) => {
    setActiveFilter(key);
    setSearchText(""); setPriorityFilter(undefined);
    setSafetyFilter(undefined); setActionFilter(undefined);
  };

  const activeFilterLabel = FILTERS.find(f => f.key === activeFilter)?.label ?? "";

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* ── Stats strip ───────────────────────────────────────────────── */}
      <Row gutter={[12, 12]}>
        {[
          { label: "Total Emails",   value: stats.total,          accent: "#6366f1" },
          { label: "Unread",         value: stats.unread,          accent: C.primary },
          { label: "Needs Review",   value: stats.needs_review,    accent: "#d97706" },
          { label: "High Priority",  value: stats.high_priority,   accent: "#dc2626" },
        ].map(s => (
          <Col xs={12} sm={6} key={s.label}>
            <div style={{
              background:   C.bgCard,
              border:       `1px solid ${C.border}`,
              borderTop:    `3px solid ${s.accent}`,
              borderRadius: 8,
              padding:      "14px 18px",
            }}>
              <div style={{ fontSize: 26, fontWeight: 700, color: C.text1, lineHeight: 1 }}>
                {s.value}
              </div>
              <div style={{ fontSize: 11, color: C.text3, marginTop: 4, fontWeight: 500, textTransform: "uppercase", letterSpacing: 0.6 }}>
                {s.label}
              </div>
            </div>
          </Col>
        ))}
      </Row>

      {/* ── Main panel ────────────────────────────────────────────────── */}
      <div style={{
        background:   C.bgCard,
        border:       `1px solid ${C.border}`,
        borderRadius: 10,
        overflow:     "hidden",
        boxShadow:    "0 1px 4px rgba(0,0,0,0.05)",
      }}>

        {/* Panel header */}
        <div style={{
          padding:       "16px 20px 14px",
          borderBottom:  `1px solid ${C.border}`,
          display:       "flex",
          justifyContent: "space-between",
          alignItems:    "center",
        }}>
          <div>
            <Title level={5} style={{ margin: 0, fontWeight: 700, color: C.text1, fontSize: 15 }}>
              Inbox — {activeFilterLabel}
            </Title>
            <Text style={{ fontSize: 12, color: C.text3 }}>
              {total} message{total !== 1 ? "s" : ""} &middot; {stats.unread} unread
            </Text>
          </div>
          <Button
            icon={<ReloadOutlined />}
            onClick={handleReload}
            loading={loading}
            size="small"
            style={{ borderRadius: 6, fontSize: 12, fontWeight: 500 }}
          >
            Refresh
          </Button>
        </div>

        {/* Filter tabs */}
        <div style={{
          display:      "flex",
          gap:          0,
          borderBottom: `1px solid ${C.border}`,
          overflowX:    "auto",
          padding:      "0 4px",
        }}>
          {FILTERS.map(f => {
            const active = activeFilter === f.key;
            return (
              <button
                key={f.key}
                onClick={() => handleFilterClick(f.key)}
                style={{
                  display:       "flex",
                  alignItems:    "center",
                  gap:           6,
                  padding:       "10px 14px",
                  border:        "none",
                  borderBottom:  active ? `2px solid ${C.primary}` : "2px solid transparent",
                  background:    "transparent",
                  color:         active ? C.primary : C.text2,
                  cursor:        "pointer",
                  fontSize:      13,
                  fontWeight:    active ? 600 : 400,
                  whiteSpace:    "nowrap",
                  transition:    "color 0.15s, border-color 0.15s",
                  marginBottom:  -1,
                }}
              >
                <span style={{ fontSize: 12 }}>{f.icon}</span>
                {f.label}
              </button>
            );
          })}
        </div>

        {/* Search + filters bar */}
        <div style={{
          padding:      "12px 20px",
          borderBottom: `1px solid ${C.border}`,
          background:   "#fafafa",
        }}>
          <Row gutter={[10, 10]} align="middle">
            <Col xs={24} sm={12} md={10}>
              <Input.Search
                placeholder="Search by sender or subject"
                value={searchText}
                onChange={e => setSearchText(e.target.value)}
                allowClear
                size="middle"
                style={{ borderRadius: 6 }}
              />
            </Col>
            <Col xs={8} sm={4} md={4}>
              <Select
                placeholder="Priority"
                value={priorityFilter}
                onChange={v => setPriorityFilter(v)}
                allowClear size="middle" style={{ width: "100%" }}
              >
                <Option value="high">High</Option>
                <Option value="medium">Medium</Option>
                <Option value="low">Low</Option>
              </Select>
            </Col>
            <Col xs={8} sm={4} md={4}>
              <Select
                placeholder="Safety"
                value={safetyFilter}
                onChange={v => setSafetyFilter(v)}
                allowClear size="middle" style={{ width: "100%" }}
              >
                <Option value="safe">Safe</Option>
                <Option value="suspicious">Suspicious</Option>
                <Option value="spam">Spam</Option>
              </Select>
            </Col>
            <Col xs={8} sm={4} md={4}>
              <Select
                placeholder="Action"
                value={actionFilter}
                onChange={v => setActionFilter(v)}
                allowClear size="middle" style={{ width: "100%" }}
              >
                <Option value="generate_draft_and_notify">Draft &amp; Notify</Option>
                <Option value="summarize_only">Summarize</Option>
                <Option value="ignore">Ignored</Option>
              </Select>
            </Col>
          </Row>
        </div>

        {/* Email list */}
        <div style={{ padding: "12px 16px" }}>
          {loading ? (
            <div style={{ display: "flex", justifyContent: "center", padding: "60px 0" }}>
              <Space direction="vertical" align="center" size={12}>
                <Spin size="large" />
                <Text style={{ color: C.text3, fontSize: 13 }}>Loading messages…</Text>
              </Space>
            </div>
          ) : emails.length === 0 ? (
            <div style={{ textAlign: "center", padding: "60px 0" }}>
              <InboxOutlined style={{ fontSize: 40, color: C.border, marginBottom: 14 }} />
              <div style={{ fontSize: 15, fontWeight: 600, color: C.text2, marginBottom: 6 }}>
                No messages found
              </div>
              <div style={{ fontSize: 13, color: C.text3 }}>
                Try a different filter or refresh the list.
              </div>
            </div>
          ) : (
            emails.map(item => (
              <EmailCard
                key={item.id}
                item={item}
                isUnread={!readIds.has(item.id)}
                onClick={() => handleClick(item)}
              />
            ))
          )}

          {/* Scroll sentinel + end-of-list */}
          <div
            ref={sentinelRef}
            style={{ display: "flex", justifyContent: "center", alignItems: "center", padding: "16px 0", minHeight: 48 }}
          >
            {loadingMore && (
              <Space size={8}>
                <Spin size="small" />
                <Text style={{ color: C.text3, fontSize: 12 }}>Loading more messages…</Text>
              </Space>
            )}
            {!hasMore && emails.length > 0 && !loading && (
              <Text style={{ color: C.text3, fontSize: 12 }}>
                — End of results · {total} message{total !== 1 ? "s" : ""} total —
              </Text>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailTable;
