import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchEmail } from "../api";
import {
  Row,
  Col,
  Card,
  Tag,
  Typography,
  Divider,
  Collapse,
  Button,
  Space,
  Avatar,
  Input,
  message
} from "antd";

const { Paragraph, Title, Text } = Typography;
const { Panel } = Collapse;

function actionColor(action: string) {
  switch (action) {
    case 'generate_draft_and_notify': return 'geekblue';
    case 'notify_only': return 'green';
    case 'summarize_only': return 'purple';
    default: return 'default';
  }
}
function getFriendlyAction(action: string) {
  switch (action) {
    case 'generate_draft_and_notify': return 'Draft generated & team notified';
    case 'notify_only': return 'Alert notification sent';
    case 'summarize_only': return 'Email summarized only';
    default: return action || 'No action';
  }
}
const getAvatarColor = (sender: string) => {
  const char = (sender || "U").trim().charAt(0).toUpperCase();
  const colors: { [key: string]: string } = {
    A: "#f56a00", B: "#7265e6", C: "#ffbf00", D: "#00a2ae", E: "#1890ff",
    F: "#f56a00", G: "#7265e6", H: "#ffbf00", I: "#00a2ae", J: "#1890ff",
    K: "#a0d911", L: "#eb2f96", M: "#fa8c16", N: "#fa541c", O: "#13c2c2",
    P: "#52c41a", Q: "#2f54eb", R: "#722ed1", S: "#f5222d", T: "#faad14",
    U: "#1890ff", V: "#7265e6", W: "#ffbf00", X: "#00a2ae", Y: "#fa8c16", Z: "#722ed1"
  };
  return colors[char] || "#1890ff";
};
const getPriorityTag = (priority: string) => {
  const p = (priority || "").toLowerCase();
  if (p === "high" || p === "urgent") {
    return <Tag color="error" style={{ fontWeight: 600, borderRadius: 4 }}>🚨 HIGH</Tag>;
  } else if (p === "medium") {
    return <Tag color="warning" style={{ fontWeight: 600, borderRadius: 4 }}>⚡ MEDIUM</Tag>;
  } else {
    return <Tag color="success" style={{ fontWeight: 600, borderRadius: 4 }}>🍃 LOW</Tag>;
  }
};
const getSafetyTag = (safety: string) => {
  const s = (safety || "").toLowerCase();
  if (s === "safe") {
    return <Tag color="success" style={{ borderRadius: 4 }}>🛡️ SAFE</Tag>;
  } else if (s === "suspicious") {
    return <Tag color="warning" style={{ borderRadius: 4 }}>⚠️ SUSPICIOUS</Tag>;
  } else if (s === "malicious") {
    return <Tag color="error" style={{ borderRadius: 4 }}>☣️ MALICIOUS</Tag>;
  } else {
    return <Tag color="default" style={{ borderRadius: 4 }}>🛡️ SAFE</Tag>;
  }
};

const EmailDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const [copied, setCopied] = useState(false);
  const [draftText, setDraftText] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [actionState, setActionState] = useState<'pending' | 'approved' | 'rejected'>('pending');
  const [isDispatching, setIsDispatching] = useState(false);
  useEffect(() => {
    if (id) {
      fetchEmail(id).then((res) => {
        setData(res);
        setDraftText(res.draft || "");
        setActionState(res.requires_human_review ? 'pending' : 'approved');
      });
    }
  }, [id]);
  const handleCopy = () => {
    if (draftText) {
      navigator.clipboard.writeText(draftText);
      setCopied(true);
      message.success("Draft response copied to clipboard!");
      setTimeout(() => setCopied(false), 2000);
    }
  };
  const handleSaveDraft = () => {
    setIsEditing(false);
    message.success("Reply draft updated and saved locally!");
  };
  const handleApprove = () => {
    setIsDispatching(true);
    setTimeout(() => {
      setIsDispatching(false);
      setActionState('approved');
      message.success("Draft approved! Response dispatched via SMTP service.");
    }, 1200);
  };
  const handleReject = () => {
    setActionState('rejected');
    message.warning("Draft rejected and archived. No action taken.");
  };

  if (!data) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "300px" }}>
        <div style={{ fontSize: 18, color: "#999" }}>Loading email intelligence details...</div>
      </div>
    );
  }
  // Extract backend fields with full fallback for guaranteed display
  const sender = data.original_sender || data.sender || data.classification?.source || "unknown@source.com";
  const subject = data.original_subject || data.subject || "No Subject";

  // ---- NEW BODY EXTRACTION LOGIC ----
  let body = data.original_body;
  let isHtml = false;
  if (!body && data.original_html_body) {
    body = data.original_html_body;
    isHtml = true;
  }
  if (!body) {
    body = "No email body text was extracted.";
  }
  //------------------------------------

  const timestamp = data.received_date ? new Date(data.received_date).toLocaleString() : "Date unavailable";
  const threadId = data.thread_id || null;
  const isExternal = data.metadata?.is_external ?? true;

  return (
    <div style={{ maxWidth: 1280, margin: "0 auto", padding: "0 10px" }}>
      <div style={{ marginBottom: 20 }}>
        <Link to="/" style={{ display: "inline-flex", alignItems: "center", gap: 8, color: "#0f172a", fontWeight: 600 }}>
          <span>←</span> Back to Batch Workspace
        </Link>
      </div>
      <div style={{ 
        background: "white", 
        padding: "24px", 
        borderRadius: "12px", 
        boxShadow: "0 4px 12px rgba(0,0,0,0.03)", 
        border: "1px solid #e2e8f0",
        marginBottom: 24 
      }}>
        <Row align="middle" justify="space-between" gutter={[16, 16]}>
          <Col xs={24} md={16}>
            <Title level={3} style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
              {subject}
            </Title>
            <div style={{ marginTop: 8, display: "flex", gap: 8, flexWrap: "wrap", alignItems: "center" }}>
              {getPriorityTag(data.classification?.priority || data.priority)}
              {getSafetyTag(data.classification?.safety || data.safety)}
              {isExternal && <Tag color="blue" style={{ borderRadius: 4, fontWeight: 500 }}>EXTERNAL EMAIL</Tag>}
              {threadId && <Tag style={{ borderRadius: 4 }}>Thread: {threadId}</Tag>}
            </div>
          </Col>
          <Col xs={24} md={8} style={{ textAlign: "right" }}>
            <span style={{ fontSize: 13, color: "#64748b" }}>
              Received: <strong>{timestamp}</strong>
            </span>
          </Col>
        </Row>
      </div>
      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          <Card
            title={
              <div style={{ display: "flex", alignItems: "center", gap: 12, padding: "8px 0" }}>
                <Avatar style={{ backgroundColor: getAvatarColor(sender), verticalAlign: "middle" }} size="large">
                  {(sender || "U").trim().charAt(0).toUpperCase()}
                </Avatar>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 15, lineHeight: 1.2, color: "#0f172a" }}>{sender}</div>
                  <div style={{ fontSize: 12, color: "#64748b", fontWeight: 500, marginTop: 2 }}>To: Hermes AI Agent</div>
                </div>
              </div>
            }
            bordered={false}
            style={{ marginBottom: 18, borderRadius: 10, minHeight: 260 }}
          >
            <div style={{ fontWeight: 500, color: "#0f172a", fontSize: 14, marginBottom: 10 }}>ORIGINAL RECEIVED EMAIL</div>
            <div style={{ color: body !== "No email body text was extracted." ? "#0f172a" : "#cbd5e1", background: body !== "No email body text was extracted." ? "#f1f5f9" : "#e0e7ef", borderRadius: 8, padding: 14, minHeight: 90 }}>
              {isHtml ? <span dangerouslySetInnerHTML={{ __html: body }} /> : body}
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card bordered={false} style={{ borderRadius: 10, minHeight: 260, boxShadow: "0 2px 8px rgba(0,0,0,0.04)" }}>
            <div style={{ marginBottom: 16, display: 'flex', gap: 16, alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ fontWeight: 700, fontSize: 15, color: '#0f172a' }}>Pipeline Intelligence Outcomes</div>
              {actionState === 'pending' && (
                <Tag color="warning" style={{ fontWeight: 600, borderRadius: 4 }}>Pending Human Approval</Tag>
              )}
              {actionState === 'approved' && <Tag color="success" style={{ fontWeight: 600, borderRadius: 4 }}>Approved & Sent</Tag>}
              {actionState === 'rejected' && <Tag color="default" style={{ fontWeight: 600, borderRadius: 4 }}>Rejected/Archived</Tag>}
            </div>
            <div style={{ marginBottom: 12 }}><b>Classified Intent:</b> {data.classification?.intent || data.intent || "N/A"}</div>
            <div style={{ marginBottom: 12 }}><b>Decided Action:</b> {getFriendlyAction(data.action)}</div>
            <div style={{ marginBottom: 12, color: '#64748b' }}>
              Pipeline Explanation: {data.reasoning || "N/A"}
            </div>
            <Divider />
            <div style={{ marginBottom: 6, fontWeight: 700, color: '#0f172a' }}>AI Generated Reply Draft</div>
            <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 12 }}>
              <Button size="small" onClick={() => setIsEditing(x => !x)}>Edit Draft</Button>
              <Button size="small" onClick={handleCopy} disabled={!draftText}>{copied ? "Copied" : "Copy Draft"}</Button>
            </div>
            {isEditing ? (
              <Input.TextArea rows={8} style={{ fontSize: 15, marginBottom: 10 }} value={draftText} onChange={e => setDraftText(e.target.value)} />
            ) : (
              <div style={{ whiteSpace: "pre-wrap", background: "#f9fafb", color: "#22223b", fontSize: 15, padding: 12, borderRadius: 8 }}>
                {draftText || <Text type="secondary">No draft generated.</Text>}
              </div>
            )}
            {isEditing && <Button type="primary" onClick={handleSaveDraft} style={{ marginTop: 8 }}>Save Draft</Button>}
            <Divider />
            <div style={{ display: 'flex', gap: 10 }}>
              <Button type="primary" onClick={handleApprove} loading={isDispatching} disabled={actionState !== 'pending'}>
                Approve & Dispatch
              </Button>
              <Button danger onClick={handleReject} disabled={actionState !== 'pending'}>
                Reject & Archive
              </Button>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};
export default EmailDetails;
