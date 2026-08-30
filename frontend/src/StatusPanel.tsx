import { Activity, ShieldCheck, Database, Cpu } from 'lucide-react';
import type { EngineStatus } from './api';

interface StatusPanelProps {
  status: EngineStatus | null;
  connectionState: 'connecting' | 'connected' | 'reconnecting' | 'offline';
}

export function StatusPanel({ status, connectionState }: StatusPanelProps) {
  const getStatusColor = () => {
    if (connectionState !== 'connected') return 'var(--text-muted)';
    if (!status) return 'var(--text-muted)';
    switch (status.engine_status) {
      case 'READY': return 'var(--severity-low)';
      case 'TRAINING': return 'var(--severity-medium)';
      case 'UNTRAINED': return 'var(--severity-high)';
      default: return 'var(--text-muted)';
    }
  };

  const getStatusText = () => {
    if (connectionState === 'connecting') return 'Connecting...';
    if (connectionState === 'reconnecting') return 'Reconnecting...';
    if (connectionState === 'offline') return 'Offline';
    return status?.engine_status || 'Unknown';
  };

  const items = [
    {
      icon: <Activity size={18} color={getStatusColor()} />,
      label: 'Engine Status',
      value: getStatusText(),
      valueColor: getStatusColor(),
    },
    {
      icon: <ShieldCheck size={18} color="var(--accent-primary)" />,
      label: 'Threshold',
      value: status?.anomaly_threshold ? status.anomaly_threshold.toFixed(4) : 'N/A',
      mono: true,
    },
    {
      icon: <Database size={18} color="var(--accent-secondary)" />,
      label: 'Training Samples',
      value: (status?.metadata?.n_training_samples as number) || 0,
      mono: true,
    },
    {
      icon: <Cpu size={18} color="var(--text-secondary)" />,
      label: 'Model Version',
      value: status?.model_version || '—',
      mono: true,
    },
  ];

  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
        gap: '12px',
      }}
    >
      {items.map((item, i) => (
        <div
          key={item.label}
          className="card animate-slide-up"
          style={{
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            gap: '14px',
            animationDelay: `${i * 50}ms`,
          }}
        >
          <div
            style={{
              width: '36px',
              height: '36px',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-surface-elevated)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexShrink: 0,
            }}
          >
            {item.icon}
          </div>
          <div style={{ minWidth: 0 }}>
            <div
              style={{
                fontSize: '10px',
                fontWeight: 600,
                color: 'var(--text-muted)',
                textTransform: 'uppercase',
                letterSpacing: '0.8px',
                marginBottom: '3px',
              }}
            >
              {item.label}
            </div>
            <div
              className={item.mono ? 'mono' : ''}
              style={{
                fontSize: '15px',
                fontWeight: 700,
                color: item.valueColor || 'var(--text-primary)',
                lineHeight: 1,
              }}
            >
              {item.value}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
