import { useEffect, useRef } from 'react';
import type { Alert } from './api';
import {
  X, Shield, Cpu, Network, Clock, Activity,
  AlertTriangle, Target, Zap, HelpCircle,
} from 'lucide-react';

interface AlertDetailModalProps {
  alert: Alert | null;
  onClose: () => void;
}

// Attack type → icon mapping
function AttackIcon({ type }: { type: string }) {
  const props = { size: 18 };
  switch (type) {
    case 'syn_flood':   return <Zap {...props} />;
    case 'udp_flood':   return <Zap {...props} />;
    case 'icmp_flood':  return <Zap {...props} />;
    case 'port_scan':   return <Target {...props} />;
    case 'brute_force': return <Shield {...props} />;
    case 'data_exfil':  return <Network {...props} />;
    case 'arp_poison':  return <AlertTriangle {...props} />;
    default:            return <HelpCircle {...props} />;
  }
}

// Gauge bar for anomaly score
function ScoreGauge({ score, threshold }: { score: number; threshold: number }) {
  const pct = Math.min(score * 100, 100);
  const isAbove = score > threshold;
  const color = score > 0.9
    ? 'var(--severity-critical)'
    : score > 0.7
    ? 'var(--severity-high)'
    : score > 0.5
    ? 'var(--severity-medium)'
    : 'var(--severity-low)';

  // Threshold marker position as percentage of the gauge
  const threshPct = Math.min(threshold * 100, 100);

  return (
    <div style={{ marginTop: 8 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>
        <span>0.0</span>
        <span style={{ color: isAbove ? color : 'var(--text-secondary)', fontWeight: 700 }}>
          Score: {score.toFixed(4)}
        </span>
        <span>1.0+</span>
      </div>
      <div style={{ position: 'relative', height: 10, borderRadius: 5, backgroundColor: 'var(--border-subtle)' }}>
        {/* Fill */}
        <div style={{
          width: `${pct}%`,
          height: '100%',
          borderRadius: 5,
          backgroundColor: color,
          transition: 'width 0.5s ease',
          boxShadow: isAbove ? `0 0 8px ${color}` : 'none',
        }} />
        {/* Threshold marker */}
        <div style={{
          position: 'absolute',
          left: `${threshPct}%`,
          top: -4,
          width: 2,
          height: 18,
          backgroundColor: 'var(--severity-critical)',
          borderRadius: 1,
          transform: 'translateX(-50%)',
        }}>
          <div style={{
            position: 'absolute',
            top: 22,
            left: '50%',
            transform: 'translateX(-50%)',
            fontSize: 9,
            color: 'var(--severity-critical)',
            whiteSpace: 'nowrap',
            fontWeight: 700,
          }}>
            threshold
          </div>
        </div>
      </div>
    </div>
  );
}

// Confidence bar
function ConfidenceBar({ confidence }: { confidence: number }) {
  const pct = Math.round(confidence * 100);
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <div style={{ flex: 1, height: 6, borderRadius: 3, backgroundColor: 'var(--border-subtle)' }}>
        <div style={{
          width: `${pct}%`,
          height: '100%',
          borderRadius: 3,
          background: 'var(--accent-gradient)',
        }} />
      </div>
      <span className="mono" style={{ fontSize: 12, fontWeight: 700, minWidth: 36 }}>{pct}%</span>
    </div>
  );
}

function formatTime(ts: number) {
  return new Date(ts * 1000).toLocaleString([], {
    dateStyle: 'medium',
    timeStyle: 'medium',
  });
}

function SeverityBadge({ severity }: { severity: Alert['severity'] }) {
  return (
    <span className={`badge badge-${severity}`} style={{ fontSize: 13, padding: '6px 16px' }}>
      {severity}
    </span>
  );
}

function InfoRow({ label, value, mono = false }: { label: string; value: React.ReactNode; mono?: boolean }) {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      padding: '10px 0',
      borderBottom: '1px solid var(--border-subtle)',
    }}>
      <span style={{ fontSize: 12, color: 'var(--text-muted)', fontWeight: 500 }}>{label}</span>
      <span className={mono ? 'mono' : ''} style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-primary)' }}>
        {value}
      </span>
    </div>
  );
}

export function AlertDetailModal({ alert, onClose }: AlertDetailModalProps) {
  const overlayRef = useRef<HTMLDivElement>(null);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  // Close on overlay click
  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === overlayRef.current) onClose();
  };

  if (!alert) return null;

  const severityColor =
    alert.severity === 'critical' ? 'var(--severity-critical)'
    : alert.severity === 'high'   ? 'var(--severity-high)'
    : alert.severity === 'medium' ? 'var(--severity-medium)'
    : 'var(--severity-low)';

  return (
    <div
      ref={overlayRef}
      onClick={handleOverlayClick}
      className="animate-fade-in"
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(0,0,0,0.6)',
        backdropFilter: 'blur(4px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: 24,
      }}
    >
      <div
        className="animate-slide-up"
        style={{
          width: '100%',
          maxWidth: 560,
          backgroundColor: 'var(--bg-surface)',
          border: `1px solid ${severityColor}33`,
          borderRadius: 'var(--radius-xl)',
          boxShadow: `0 24px 64px rgba(0,0,0,0.7), 0 0 0 1px ${severityColor}22`,
          overflow: 'hidden',
        }}
      >
        {/* Header */}
        <div style={{
          padding: '20px 24px',
          borderBottom: '1px solid var(--border-subtle)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          background: `linear-gradient(135deg, ${severityColor}08, transparent)`,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div style={{
              width: 40,
              height: 40,
              borderRadius: 'var(--radius-md)',
              backgroundColor: `${severityColor}18`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: severityColor,
            }}>
              <AttackIcon type={alert.attack_type} />
            </div>
            <div>
              <div style={{ fontSize: 16, fontWeight: 700 }}>{alert.attack_label}</div>
              <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>
                Alert ID: <span className="mono" style={{ fontSize: 11 }}>{alert.id}</span>
              </div>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <SeverityBadge severity={alert.severity} />
            <button
              onClick={onClose}
              style={{
                background: 'transparent',
                border: '1px solid var(--border-default)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--text-muted)',
                cursor: 'pointer',
                padding: '6px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                transition: 'all var(--transition-fast)',
              }}
              onMouseOver={e => {
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-primary)';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border-strong)';
              }}
              onMouseOut={e => {
                (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-muted)';
                (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border-default)';
              }}
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Body */}
        <div style={{ padding: '24px', overflowY: 'auto', maxHeight: '65vh' }}>

          {/* Anomaly Score Section */}
          <div style={{ marginBottom: 24 }}>
            <h4 style={{ margin: '0 0 12px', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
              <Activity size={12} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Anomaly Score
            </h4>
            <ScoreGauge score={alert.anomaly_score} threshold={alert.threshold} />
          </div>

          {/* Attack Classification */}
          <div style={{ marginBottom: 24 }}>
            <h4 style={{ margin: '0 0 12px', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
              <Cpu size={12} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Attack Classification
            </h4>
            <div style={{
              padding: '14px 16px',
              backgroundColor: 'var(--bg-surface-elevated)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
                <span style={{ fontSize: 14, fontWeight: 700, color: severityColor }}>{alert.attack_label}</span>
                <span className="mono" style={{ fontSize: 11, color: 'var(--text-muted)' }}>{alert.attack_type}</span>
              </div>
              <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 8 }}>Classifier Confidence</div>
              <ConfidenceBar confidence={alert.attack_confidence} />
            </div>
          </div>

          {/* Network Details */}
          <div style={{ marginBottom: 24 }}>
            <h4 style={{ margin: '0 0 4px', fontSize: 11, fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.8px' }}>
              <Network size={12} style={{ marginRight: 6, verticalAlign: 'middle' }} />
              Network Details
            </h4>
            <div>
              <InfoRow label="Source IP"      value={alert.src_ip}    mono />
              <InfoRow label="Destination IP" value={alert.dst_ip}    mono />
              <InfoRow label="Protocol"       value={alert.protocol}  mono />
              <InfoRow
                label="Timestamp"
                value={
                  <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Clock size={12} style={{ color: 'var(--text-muted)' }} />
                    {formatTime(alert.timestamp)}
                  </span>
                }
              />
              <InfoRow
                label="Threshold"
                value={
                  <span className="mono" style={{ color: 'var(--severity-critical)' }}>
                    {alert.threshold.toFixed(4)}
                  </span>
                }
              />
            </div>
          </div>

          {/* Footer note */}
          <div style={{
            padding: '10px 14px',
            backgroundColor: 'var(--severity-critical-dim)',
            borderRadius: 'var(--radius-md)',
            border: '1px solid rgba(248,81,73,0.15)',
            fontSize: 12,
            color: 'var(--severity-critical)',
            display: 'flex',
            gap: 8,
          }}>
            <AlertTriangle size={14} style={{ flexShrink: 0, marginTop: 1 }} />
            <span>
              This packet's reconstruction error exceeded the learned normal-traffic threshold
              by <strong>{((alert.anomaly_score / Math.max(alert.threshold, 0.0001) - 1) * 100).toFixed(0)}%</strong>.
              Investigate source <span className="mono">{alert.src_ip}</span> immediately.
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
