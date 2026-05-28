import React, { useEffect, useState } from "react";
import { 
  Table, 
  Tag, 
  Button, 
  Typography, 
  Row, 
  Col, 
  Card, 
  Input, 
  Select, 
  Space, 
  Avatar, 
  Divider 
} from "antd";
import { useNavigate } from "react-router-dom";
import { fetchBatch } from "../api";

const { Paragraph, Title, Text } = Typography;
const { Option } = Select;

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
    case 'generate_draft_and_notify': return 'Draft & Notify';
    case 'notify_only': return 'Notify Only';
    case 'summarize_only': return 'Summarize Only';
    default: return action || 'N/A';
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

const EmailTable: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [searchText, setSearchText] = useState("");
  const [priorityFilter, setPriorityFilter] = useState<string | undefined>(undefined);
  const [safetyFilter, setSafetyFilter] = useState<string | undefined>(undefined);
  const [actionFilter, setActionFilter] = useState<string | undefined>(undefined);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const reload = () => {
    setLoading(true);
    fetchBatch()
      .then(res => {
        // Ensure correct fields for original info
        const newData = (res || []).map((item: any) => ({
          ...item,
          show_subject: item.original_subject || item.subject || "(No Subject)",
          show_body: item.body || item.original_body || "",
        }));
        setData(newData);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    reload();
  }, []);

  const totalCount = data.length;
  const reviewCount = data.filter(item => item.requires_human_review).length;
  const highPriorityCount = data.filter(item => {
    const p = (item.priority || "").toLowerCase();
    return p === "high" || p === "urgent";
  }).length;
  const threatCount = data.filter(item => {
    const s = (item.safety || "").toLowerCase();
    return s === "suspicious" || s === "malicious";
  }).length;
  const filteredData = data.filter((item) => {
    const matchesSearch = 
      (item.sender || "").toLowerCase().includes(searchText.toLowerCase()) ||
      (item.show_subject || "").toLowerCase().includes(searchText.toLowerCase());
    const matchesPriority = !priorityFilter || (item.priority || "").toLowerCase() === priorityFilter.toLowerCase();
    const matchesSafety = !safetyFilter || (item.safety || "").toLowerCase() === safetyFilter.toLowerCase();
    const matchesAction = !actionFilter || item.action === actionFilter;
    return matchesSearch && matchesPriority && matchesSafety && matchesAction;
  });

  const columns = [
    {
      title: "Sender",
      dataIndex: "sender",
      key: "sender",
      render: (txt: string) => <span>{txt || <Text type="secondary">Unknown</Text>}</span>
    },
    {
      title: "Subject",
      dataIndex: "show_subject",
      key: "show_subject",
      render: (subj: string, row: any) => <a onClick={() => navigate(`/email/${row.id}`)}>{subj || <Text type="secondary">(No Subject)</Text>}</a>,
    },
    {
      title: "Body Snippet",
      dataIndex: "show_body",
      key: "show_body",
      render: (body: string) => <span>{(body && body.length > 100 ? body.slice(0, 100) + "..." : body) || <Text type="secondary">(No Body)</Text>}</span>
    },
    {
      title: "Action",
      dataIndex: "action",
      key: "action",
      render: (val: string) => <Tag color={actionColor(val)}>{getFriendlyAction(val)}</Tag>
    },
    {
      title: "Priority",
      dataIndex: "priority",
      key: "priority",
      render: (p: string) => <span>{p || <Text type="secondary">N/A</Text>}</span>
    },
    {
      title: "Safety",
      dataIndex: "safety",
      key: "safety",
      render: (s: string) => <span>{s || <Text type="secondary">N/A</Text>}</span>
    },
    {
      title: "Review Queue",
      dataIndex: "requires_human_review",
      key: "requires_human_review",
      render: (val: boolean) => val ? <Tag color="warning">ACTION NEEDED</Tag> : <Tag color="success">Auto</Tag>
    },
  ];

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
      {/* KPIDashboard omitted for brevity, keep as is */}
      <Card
        bordered={false}
        style={{ borderRadius: 12, boxShadow: "0 4px 12px rgba(0,0,0,0.03)", border: "1px solid #e2e8f0" }}>
        <Space direction="vertical" size={16} style={{ width: "100%" }}>
          <Row justify="space-between" align="middle" gutter={[16, 16]}>
            <Col>
              <Title level={4} style={{ margin: 0, fontWeight: 700, color: "#0f172a" }}>
                Pipeline Workspace
              </Title>
              <Text type="secondary" style={{ fontSize: 13 }}>
                Review/approve results and monitor inbox automation.
              </Text>
            </Col>
            <Col><Button onClick={reload} loading={loading}>Reload Batch Results</Button></Col>
          </Row>
          <Input.Search placeholder="Search by subject/sender" value={searchText} onChange={e => setSearchText(e.target.value)} style={{ maxWidth: 320 }} allowClear />
            <Divider />
            <Table 
              loading={loading}
              columns={columns}
              dataSource={filteredData}
              pagination={{ pageSize: 10 }}
              rowKey="id"
              size="middle"
            />
        </Space>
      </Card>
    </div>
  );
};

export default EmailTable;
