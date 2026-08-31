// api.ts — SentinelAI Frontend API Client

const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface EngineStatus {
  engine_status: 'UNTRAINED' | 'TRAINING' | 'READY';
  anomaly_threshold: number | null;
  model_version: string;
  started_at: number;
  uptime_seconds: number;

  metadata: Record<string, unknown>;
}

export interface Alert {
  id: string;
  type: string;
  timestamp: number;
  src_ip: string;
  dst_ip: string;
  protocol: string;
  anomaly_score: number;
  threshold: number;
  severity: 'low' | 'medium' | 'high' | 'critical';
  attack_type: string;
  attack_label: string;
  attack_confidence: number;
}

export interface StatsSummary {
  total_alerts: number;
  critical_count: number;
  high_count: number;
  medium_count: number;
  low_count: number;
  unique_src_ips: number;
  unique_dst_ips: number;
}

export interface TopAttacker {
  ip: string;
  count: number;
  last_seen: number;
}

export interface ProtocolDistribution {
  TCP: number;
  UDP: number;
  ICMP: number;
  OTHER: number;
}

export interface AttackTypeDistribution {
  [attackType: string]: number;
}

export interface SeverityBucket {
  timestamp: number;
  critical: number;
  high: number;
  medium: number;
  low: number;
  total: number;
}

export interface HealthStatus {
  status: string;
  engine_status: string;

  uptime_seconds: number;
  sniffer_alive: boolean;
  db_ok: boolean;
  ws_clients: number;
}

export interface CaptureStatus {
  capturing: boolean;
  status?: 'started' | 'already_running' | 'stopping' | 'already_stopped';
}

export interface PersistedModelStatus {
  ready: boolean;
  feature_count: number;
  model_path: string;
  error: string | null;
  classes?: string[];
}

export interface DemoPredictionSample {
  expected_label: string | number;
  predicted_label: string | number;
  features: Record<string, string | number | null>;
}

export interface EdgeIIoTDemoSamples {
  dataset: string;
  source: string;
  binary: DemoPredictionSample[];
  attack_type: DemoPredictionSample[];
}

export interface EdgeIIoTBinaryPrediction {
  prediction: 'attack' | 'benign';
  prediction_code: number;
  attack_probability: number;
  confidence: number;
}

export interface EdgeIIoTAttackTypePrediction {
  prediction: 'attack' | 'benign';
  attack_type: string;
  confidence: number;
  is_attack: boolean;
}

// ---------------------------------------------------------------------------
// API Client
// ---------------------------------------------------------------------------

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) throw new Error(`API ${path} → ${res.status}`);
  return res.json();
}

export const API = {
  getHealth: () =>
    request<HealthStatus>('/health'),

  getStatus: () =>
    request<EngineStatus>('/api/status'),

  getCaptureStatus: () =>
    request<CaptureStatus>('/api/capture/status'),

  startCapture: () =>
    request<CaptureStatus>('/api/capture/start', { method: 'POST' }),

  stopCapture: () =>
    request<CaptureStatus>('/api/capture/stop', { method: 'POST' }),

  getKitsuneModelStatus: () =>
    request<PersistedModelStatus>('/api/kitsune/status'),

  getEdgeIIoTModelStatus: () =>
    request<PersistedModelStatus>('/api/edge-iiot/status'),

  getEdgeIIoTAttackTypeModelStatus: () =>
    request<PersistedModelStatus>('/api/edge-iiot/attack-type/status'),

  getEdgeIIoTDemoSamples: () =>
    request<EdgeIIoTDemoSamples>('/api/demo/edge-iiot-samples'),

  postEdgeIIoTBinaryPrediction: (features: DemoPredictionSample['features']) =>
    request<EdgeIIoTBinaryPrediction>('/api/edge-iiot/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features }),
    }),

  postEdgeIIoTAttackTypePrediction: (features: DemoPredictionSample['features']) =>
    request<EdgeIIoTAttackTypePrediction>('/api/edge-iiot/attack-type/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features }),
    }),

  getRecentAlerts: (limit = 50, severity?: string, protocol?: string, since?: number) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (severity) params.set('severity', severity);
    if (protocol) params.set('protocol', protocol);
    if (since) params.set('since', String(since));
    return request<Alert[]>(`/api/alerts/recent?${params}`);
  },

  getStatsSummary: (since?: number) =>
    request<StatsSummary>(`/api/stats/summary${since ? `?since=${since}` : ''}`),

  getTopAttackers: (limit = 10, since?: number) => {
    const params = new URLSearchParams({ limit: String(limit) });
    if (since) params.set('since', String(since));
    return request<TopAttacker[]>(`/api/stats/top-attackers?${params}`);
  },

  getProtocolDistribution: (since?: number) =>
    request<ProtocolDistribution>(`/api/stats/protocol-distribution${since ? `?since=${since}` : ''}`),

  getAttackTypeDistribution: (since?: number) =>
    request<AttackTypeDistribution>(`/api/stats/attack-types${since ? `?since=${since}` : ''}`),

  getSeverityTimeline: (bucketMinutes = 5) =>
    request<SeverityBucket[]>(
      `/api/stats/severity-timeline?bucket_minutes=${bucketMinutes}`
    ),

  postRetrain: () =>
    request<{ status: string; engine_status: string }>(
      '/api/model/retrain',
      { method: 'POST' }
    ),
};
