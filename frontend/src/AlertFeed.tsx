import { useState } from 'react';
import type { Alert } from './api';
import { Filter, MousePointerClick } from 'lucide-react';
import { AlertDetailModal } from './AlertDetailModal';

interface AlertFeedProps {
  alerts: Alert[];
}

type SeverityFilter = 'all' | 'critical' | 'high' | 'medium' | 'low';

// Attack type → compact badge colour
const ATTACK_COLORS: Record<string, string> = {
  syn_flood:   'var(--severity-critical)',
  udp_flood:   'var(--severity-critical)',
  icmp_flood:  'var(--severity-high)',
  port_scan:   'var(--severity-medium)',
  brute_force: 'var(--severity-high)',
  data_exfil:  'var(--severity-critical)',
  arp_poison:  'var(--severity-high)',
  unknown:     'var(--text-muted)',
};

export function AlertFeed({ alerts }: AlertFeedProps) {
  const [filter, setFilter]           = useState<SeverityFilter>('all');
  const [visibleCount, setVisibleCount] = useState(50);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);

  const filteredAlerts =
    filter === 'all' ? alerts : alerts.filter((a) => a.severity === filter);
  const visibleAlerts = filteredAlerts.slice(0, visibleCount);

  const formatTime = (ts: number) => {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const filterOptions: SeverityFilter[] = ['all', 'critical', 'high', 'medium', 'low'];

  return (
    <>
      {/* Detail Modal */}
      <AlertDetailModal alert={selectedAlert} onClose={() => setSelectedAlert(null)} />

      <div className="card" style={{ padding: '24px', flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '16px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <h3 style={{
              margin: 0,
              fontSize: '13px',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              letterSpacing: '0.8px',
            }}>
              Live Alert Feed
            </h3>
            {alerts.length > 0 && (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: 4,
                fontSize: 10,
                color: 'var(--text-muted)',
                fontWeight: 500,
              }}>
                <MousePointerClick size={11} />
                click row for details
              </span>
            )}
          </div>

          {/* Filter pills */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Filter size={13} color="var(--text-muted)" />
            {filterOptions.map((opt) => (
              <button
                key={opt}
                onClick={() => { setFilter(opt); setVisibleCount(50); }}
                style={{
                  padding: '4px 10px',
                  borderRadius: '20px',
                  border: 'none',
                  fontSize: '11px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  textTransform: 'uppercase',
                  letterSpacing: '0.3px',
                  transition: 'all var(--transition-fast)',
                  backgroundColor: filter === opt ? 'var(--accent-primary-dim)' : 'transparent',
                  color: filter === opt ? 'var(--accent-primary)' : 'var(--text-muted)',
                  fontFamily: 'var(--font-sans)',
                }}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>

        {/* Table */}
        {visibleAlerts.length === 0 ? (
          <div style={{ padding: '48px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
            {filter === 'all'
              ? 'No alerts detected. Monitoring traffic...'
              : `No ${filter} alerts detected.`}
          </div>
        ) : (
          <>
            <div style={{ overflowX: 'auto', flex: 1 }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{
                    borderBottom: '1px solid var(--border-subtle)',
                    color: 'var(--text-muted)',
                    fontSize: '11px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.6px',
                  }}>
                    <th style={{ padding: '10px 12px', fontWeight: 600 }}>Time</th>
                    <th style={{ padding: '10px 12px', fontWeight: 600 }}>Source IP</th>
                    <th style={{ padding: '10px 12px', fontWeight: 600 }}>Destination IP</th>
                    <th style={{ padding: '10px 12px', fontWeight: 600 }}>Protocol</th>
                    <th style={{ padding: '10px 12px', fontWeight: 600 }}>Attack Type</th>
                    <th style={{ padding: '10px 12px', fontWeight: 600 }}>Severity</th>
                    <th style={{ padding: '10px 12px', fontWeight: 600, textAlign: 'right' }}>Score</th>
                  </tr>
                </thead>
                <tbody>
                  {visibleAlerts.map((alert, idx) => (
                    <tr
                      key={alert.id}
                      className={idx < 3 ? 'animate-slide-in' : ''}
                      onClick={() => setSelectedAlert(alert)}
                      onKeyDown={(event) => {
                        if (event.key === 'Enter' || event.key === ' ') {
                          event.preventDefault();
                          setSelectedAlert(alert);
                        }
                      }}
                      role="button"
                      tabIndex={0}
                      aria-label={`Open details for ${alert.attack_label || 'network'} alert from ${alert.src_ip}`}
                      style={{
                        borderBottom: '1px solid var(--border-subtle)',
                        cursor: 'pointer',
                        transition: 'background-color var(--transition-fast)',
                        animationDelay: idx < 3 ? `${idx * 60}ms` : undefined,
                      }}
                      onMouseOver={(e) => (e.currentTarget.style.backgroundColor = 'var(--bg-surface-hover)')}
                      onMouseOut={(e) =>  (e.currentTarget.style.backgroundColor = 'transparent')}
                    >
                      <td className="mono" style={{ padding: '12px', fontSize: '12px', color: 'var(--text-muted)' }}>
                        {formatTime(alert.timestamp)}
                      </td>
                      <td className="mono" style={{ padding: '12px', fontSize: '12px' }}>
                        {alert.src_ip}
                      </td>
                      <td className="mono" style={{ padding: '12px', fontSize: '12px' }}>
                        {alert.dst_ip}
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span className="mono" style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary)' }}>
                          {alert.protocol || '—'}
                        </span>
                      </td>
                      {/* Attack Type — new column */}
                      <td style={{ padding: '12px' }}>
                        <span style={{
                          fontSize: '11px',
                          fontWeight: 700,
                          color: ATTACK_COLORS[alert.attack_type] || 'var(--text-muted)',
                        }}>
                          {alert.attack_label || '—'}
                        </span>
                      </td>
                      <td style={{ padding: '12px' }}>
                        <span className={`badge badge-${alert.severity}`}>
                          {alert.severity}
                        </span>
                      </td>
                      <td className="mono" style={{ padding: '12px', fontSize: '12px', textAlign: 'right', fontWeight: 600 }}>
                        {alert.anomaly_score.toFixed(4)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Load More */}
            {visibleCount < filteredAlerts.length && (
              <button
                onClick={() => setVisibleCount((c) => c + 50)}
                style={{
                  marginTop: '12px',
                  padding: '8px 20px',
                  borderRadius: 'var(--radius-md)',
                  border: '1px solid var(--border-default)',
                  backgroundColor: 'transparent',
                  color: 'var(--text-secondary)',
                  fontSize: '12px',
                  fontWeight: 600,
                  cursor: 'pointer',
                  alignSelf: 'center',
                  transition: 'all var(--transition-fast)',
                  fontFamily: 'var(--font-sans)',
                }}
              >
                Load More ({filteredAlerts.length - visibleCount} remaining)
              </button>
            )}
          </>
        )}
      </div>
    </>
  );
}
