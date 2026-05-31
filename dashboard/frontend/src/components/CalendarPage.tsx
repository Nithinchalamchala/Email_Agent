import React, { useEffect, useState } from "react";
import {
  Alert,
  Badge,
  Button,
  Card,
  Col,
  Divider,
  Form,
  Input,
  Row,
  Space,
  Spin,
  Tag,
  Typography,
} from "antd";
import { useMsal } from "@azure/msal-react";
import { graphScopes } from "../auth/msalConfig";
import { fetchCalendarEvents, runCalendarPipeline } from "../api";

const { Title, Text } = Typography;
const { TextArea } = Input;

// ── helpers ──────────────────────────────────────────────────────────────────

function fmtDateTime(iso: string) {
  if (!iso) return "—";
  // Graph API returns datetimes without Z — append it so JS parses as UTC, not local
  const utcIso = iso.endsWith("Z") ? iso : iso + "Z";
  return new Date(utcIso).toLocaleString("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function actionTag(action: string) {
  switch (action) {
    case "event_created":
      return <Tag color="green" style={{ fontWeight: 600 }}>Event Created</Tag>;
    case "conflict_detected":
      return <Tag color="warning" style={{ fontWeight: 600 }}>Conflict Detected</Tag>;
    case "no_action":
      return <Tag color="default" style={{ fontWeight: 600 }}>No Action</Tag>;
    default:
      return <Tag color="default">{action || "—"}</Tag>;
  }
}

// ── Upcoming event card ───────────────────────────────────────────────────────

const EventCard: React.FC<{ event: any }> = ({ event }) => {
  const start = event.start?.dateTime || event.start?.date || "";
  const end = event.end?.dateTime || event.end?.date || "";
  const location = event.location?.displayName;
  const attendees: string[] = (event.attendees || []).map(
    (a: any) => a.emailAddress?.address || a.emailAddress?.name || ""
  );

  return (
    <div
      style={{
        background: "#f8fafc",
        border: "1px solid #e2e8f0",
        borderRadius: 10,
        padding: "14px 18px",
        marginBottom: 12,
        borderLeft: "4px solid #3b82f6",
      }}
    >
      <div style={{ fontWeight: 700, fontSize: 15, color: "#0f172a", marginBottom: 4 }}>
        {event.subject || "(No Title)"}
      </div>
      <Space size={6} wrap style={{ marginBottom: 4 }}>
        <Text style={{ fontSize: 13, color: "#475569" }}>
          🕐 {fmtDateTime(start)} → {fmtDateTime(end)}
        </Text>
      </Space>
      {location && (
        <div style={{ fontSize: 12, color: "#64748b", marginBottom: 4 }}>
          📍 {location}
        </div>
      )}
      {attendees.length > 0 && (
        <div style={{ fontSize: 12, color: "#64748b" }}>
          👥 {attendees.join(", ")}
        </div>
      )}
    </div>
  );
};

// ── Pipeline result panel ─────────────────────────────────────────────────────

const PipelineResult: React.FC<{ result: any }> = ({ result }) => {
  const ev = result.extracted_event || {};
  const created = result.event;

  return (
    <div
      style={{
        background: result.status === "success" ? "#f0fdf4" : result.status === "conflict" ? "#fffbeb" : "#f8fafc",
        border: `1px solid ${result.status === "success" ? "#86efac" : result.status === "conflict" ? "#fcd34d" : "#e2e8f0"}`,
        borderRadius: 10,
        padding: "16px 18px",
        marginTop: 16,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
        <Text strong style={{ fontSize: 15 }}>Pipeline Result</Text>
        {actionTag(result.action)}
        {result.requires_human_review && (
          <Tag color="orange" style={{ fontWeight: 600 }}>Review Needed</Tag>
        )}
      </div>

      <Row gutter={[16, 8]}>
        <Col span={12}><Text type="secondary">Title</Text><div style={{ fontWeight: 600 }}>{ev.title || "—"}</div></Col>
        <Col span={12}><Text type="secondary">Confidence</Text><div style={{ fontWeight: 600 }}>{ev.confidence !== undefined ? `${(ev.confidence * 100).toFixed(0)}%` : "—"}</div></Col>
        <Col span={12}><Text type="secondary">Start</Text><div style={{ fontWeight: 600 }}>{ev.start_time ? fmtDateTime(ev.start_time) : "—"}</div></Col>
        <Col span={12}><Text type="secondary">End</Text><div style={{ fontWeight: 600 }}>{ev.end_time ? fmtDateTime(ev.end_time) : "—"}</div></Col>
        <Col span={12}><Text type="secondary">Location</Text><div style={{ fontWeight: 600 }}>{ev.location || "—"}</div></Col>
        <Col span={12}><Text type="secondary">Attendees</Text><div style={{ fontWeight: 600 }}>{(ev.attendees || []).join(", ") || "—"}</div></Col>
      </Row>

      {result.status === "conflict" && (
        <Alert
          type="warning"
          showIcon
          message="A conflicting event already exists in this time slot. No event was created."
          style={{ marginTop: 12 }}
        />
      )}

      {result.status === "success" && created && (
        <Alert
          type="success"
          showIcon
          message={
            <span>
              Event created in Outlook.{" "}
              {result.details?.webLink && (
                <a href={result.details.webLink} target="_blank" rel="noreferrer">
                  Open in Outlook →
                </a>
              )}
            </span>
          }
          style={{ marginTop: 12 }}
        />
      )}

      {result.status === "skipped" && (
        <Alert
          type="info"
          showIcon
          message={result.details?.reason || "Not a clear meeting request."}
          style={{ marginTop: 12 }}
        />
      )}
    </div>
  );
};

// ── Main page ─────────────────────────────────────────────────────────────────

const CalendarPage: React.FC = () => {
  const { instance, accounts } = useMsal();
  const [calToken, setCalToken]       = useState<string | null>(null);
  const [events, setEvents]           = useState<any[]>([]);
  const [eventsLoading, setEventsLoading] = useState(false);
  const [pipelineLoading, setPipelineLoading] = useState(false);
  const [pipelineResult, setPipelineResult]   = useState<any>(null);
  const [pipelineError, setPipelineError]     = useState<string | null>(null);

  const [form] = Form.useForm();

  const acquireToken = async (): Promise<string | null> => {
    const account = accounts[0];
    if (!account) return null;
    try {
      const r = await instance.acquireTokenSilent({ scopes: graphScopes, account });
      setCalToken(r.accessToken);
      return r.accessToken;
    } catch { return null; }
  };

  const loadEvents = async () => {
    const token = calToken || await acquireToken();
    setEventsLoading(true);
    fetchCalendarEvents(7, token || undefined)
      .then((data) => { setEvents(data.value || []); setEventsLoading(false); })
      .catch(() => setEventsLoading(false));
  };

  useEffect(() => { loadEvents(); }, []); // run once on mount

  const handleRunPipeline = async (values: any) => {
    const token = calToken || await acquireToken();
    setPipelineLoading(true); setPipelineResult(null); setPipelineError(null);
    try {
      const result = await runCalendarPipeline({
        sender: values.sender, subject: values.subject,
        body: values.body, timestamp: new Date().toISOString(),
      }, token || undefined);
      setPipelineResult(result);
      if (result.status === "success") loadEvents();
    } catch (e: any) {
      setPipelineError(e?.response?.data?.detail || e.message || "Unknown error");
    } finally {
      setPipelineLoading(false);
    }
  };

  const todayEvents = events.filter((e) => {
    const start = e.start?.dateTime || e.start?.date || "";
    return start.startsWith(new Date().toISOString().slice(0, 10));
  });

  const nextEvent = events.find((e) => {
    const start = e.start?.dateTime || e.start?.date || "";
    return new Date(start) >= new Date();
  });

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>

      {/* Page header */}
      <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
        <div style={{
          background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
          width: 44, height: 44, borderRadius: 12,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 22, boxShadow: "0 0 14px rgba(99,102,241,0.4)",
        }}>📅</div>
        <div>
          <Title level={3} style={{ margin: 0, color: "#0f172a", fontWeight: 800 }}>
            Calendar Intelligence
          </Title>
          <Text type="secondary" style={{ fontSize: 13 }}>
            View upcoming events · Manually test the calendar pipeline
          </Text>
        </div>
      </div>

      {/* Integration status banner */}
      <Alert
        type="info"
        showIcon
        message={
          <span>
            <strong>Email pipeline integration is pending.</strong> The calendar module is fully built and working — you can test it manually below.
            Automatic triggering from incoming emails (wiring <code>run_calendar_pipeline</code> into <code>pipeline/orchestrator.py</code>)
            will be set up once the email ingestion flow is ready.
          </span>
        }
        style={{ borderRadius: 10 }}
      />

      {/* Stats row */}
      <Row gutter={[16, 16]}>
        {[
          {
            label: "Upcoming (7d)",
            value: eventsLoading ? <Spin size="small" /> : events.length,
            color: "#3b82f6",
            icon: "📆",
          },
          {
            label: "Today",
            value: eventsLoading ? <Spin size="small" /> : todayEvents.length,
            color: "#10b981",
            icon: "🗓️",
          },
          {
            label: "Next Event",
            value: nextEvent
              ? <span style={{ fontSize: 13 }}>{nextEvent.subject || "(No Title)"}</span>
              : <Text type="secondary">None</Text>,
            color: "#f59e0b",
            icon: "⏱️",
          },
        ].map((stat) => (
          <Col xs={24} sm={8} key={stat.label}>
            <Card
              bordered={false}
              style={{
                borderRadius: 12,
                border: "1px solid #e2e8f0",
                boxShadow: "0 2px 8px rgba(0,0,0,0.03)",
              }}
              bodyStyle={{ padding: "18px 22px" }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <div style={{
                  background: `${stat.color}18`,
                  width: 40, height: 40, borderRadius: 10,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 20,
                }}>
                  {stat.icon}
                </div>
                <div>
                  <Text type="secondary" style={{ fontSize: 12, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.5px" }}>
                    {stat.label}
                  </Text>
                  <div style={{ fontSize: 22, fontWeight: 800, color: "#0f172a", lineHeight: 1.2 }}>
                    {stat.value}
                  </div>
                </div>
              </div>
            </Card>
          </Col>
        ))}
      </Row>

      {/* Main two-column layout */}
      <Row gutter={[20, 20]}>

        {/* Left: Upcoming events */}
        <Col xs={24} lg={12}>
          <Card
            bordered={false}
            style={{ borderRadius: 12, border: "1px solid #e2e8f0", boxShadow: "0 2px 8px rgba(0,0,0,0.03)", height: "100%" }}
            title={
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: 700, color: "#0f172a" }}>Upcoming Events</span>
                <Button size="small" onClick={loadEvents} loading={eventsLoading}>Refresh</Button>
              </div>
            }
          >
            {eventsLoading ? (
              <div style={{ textAlign: "center", padding: 40 }}><Spin /></div>
            ) : events.length === 0 ? (
              <div style={{ textAlign: "center", padding: 40, color: "#94a3b8" }}>
                <div style={{ fontSize: 32, marginBottom: 8 }}>📭</div>
                <div>No events in the next 7 days</div>
              </div>
            ) : (
              events.map((ev, i) => <EventCard key={ev.id || i} event={ev} />)
            )}
          </Card>
        </Col>

        {/* Right: Test pipeline */}
        <Col xs={24} lg={12}>
          <Card
            bordered={false}
            style={{ borderRadius: 12, border: "1px solid #e2e8f0", boxShadow: "0 2px 8px rgba(0,0,0,0.03)" }}
            title={
              <div>
                <div style={{ fontWeight: 700, color: "#0f172a" }}>Test Calendar Pipeline</div>
                <div style={{ fontSize: 12, color: "#64748b", fontWeight: 400, marginTop: 2 }}>
                  Paste any email — the pipeline extracts, checks conflicts, and creates the event
                </div>
              </div>
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleRunPipeline}
              initialValues={{
                sender: "test@example.com",
                subject: "Meeting Request",
                body: "Hi, can we meet next Monday at 2pm IST for 1 hour to discuss project updates? Please confirm.",
              }}
            >
              <Form.Item label="Sender Email" name="sender" rules={[{ required: true, message: "Required" }]}>
                <Input placeholder="sender@example.com" />
              </Form.Item>
              <Form.Item label="Subject" name="subject" rules={[{ required: true, message: "Required" }]}>
                <Input placeholder="Meeting subject" />
              </Form.Item>
              <Form.Item label="Email Body" name="body" rules={[{ required: true, message: "Required" }]}>
                <TextArea rows={5} placeholder="Paste email body here..." />
              </Form.Item>

              <Button
                type="primary"
                htmlType="submit"
                loading={pipelineLoading}
                style={{
                  background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
                  border: "none",
                  borderRadius: 8,
                  fontWeight: 600,
                  height: 38,
                }}
                block
              >
                Run Calendar Pipeline
              </Button>
            </Form>

            {pipelineError && (
              <Alert type="error" showIcon message={pipelineError} style={{ marginTop: 16, borderRadius: 8 }} />
            )}

            {pipelineResult && (
              <>
                <Divider style={{ margin: "16px 0 4px" }} />
                <PipelineResult result={pipelineResult} />
              </>
            )}
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default CalendarPage;
