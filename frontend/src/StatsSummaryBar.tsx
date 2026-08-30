import type { StatsSummary } from './api';
import { ShieldAlert, Crosshair, Wifi, Clock } from 'lucide-react';

interface StatsSummaryBarProps {
  stats: StatsSummary | null;
  uptime: number;
}

interface StatCardProps {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  accent?: string;
  delay?: number;
}

function StatCard({ icon, label, value, accent, delay = 0 }: StatCardProps) {
  return (
    <div
      className="card animate-slide-up"
      style={{
        padding: '20px 24px',
        display: 'flex',
        alignItems: 'center',
        gap: '16px',
        animationDelay: `${delay}ms`,
      }}
    >
      <div
        style={{
          width: '44px',
          height: '44px',
          borderRadius: 'var(--radius-md)',
          background: accent || 'var(--accent-primary-dim)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          flexShrink: 0,
        }}
      >
        {icon}
      </div>
      <div style={{ minWidth: 0 }}>
        <div
          style={{
            fontSize: '11px',
            fontWeight: 600,
            color: 'var(--text-muted)',
            textTransform: 'uppercase',
            letterSpacing: '0.8px',
            marginBottom: '4px',
          }}
        >
          {label}
        </div>
        <div
          className="mono"
          style={{
            fontSize: '22px',
            fontWeight: 700,
            lineHeight: 1,
          }}
        >
          {value}
        </div>
      </div>
    </div>
  );
}

function formatUptime(seconds: number): string {
  if (!seconds) return '0s';
  const d = Math.floor(seconds / 86400);
  const h = Math.floor((seconds % 86400) / 3600);
  const m = Math.floor((seconds % 3600) / 60);
  if (d > 0) return `${d}d ${h}h`;
  if (h > 0) return `${h}h ${m}m`;
  return `${m}m ${seconds % 60}s`;
}

export function StatsSummaryBar({ stats, uptime }: StatsSummaryBarProps) {
  return (
    <div
      style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
      }}
    >
      <StatCard
        icon={<ShieldAlert size={20} color="var(--severity-critical)" />}
        label="Total Threats"
        value={stats?.total_alerts ?? '—'}
        accent="var(--severity-critical-dim)"
        delay={0}
      />
      <StatCard
        icon={<Crosshair size={20} color="var(--severity-high)" />}
        label="Critical + High"
        value={
          stats
            ? `${stats.critical_count + stats.high_count}`
            : '—'
        }
        accent="var(--severity-high-dim)"
        delay={50}
      />
      <StatCard
        icon={<Wifi size={20} color="var(--accent-primary)" />}
        label="Unique Attackers"
        value={stats?.unique_src_ips ?? '—'}
        accent="var(--accent-primary-dim)"
        delay={100}
      />
      <StatCard
        icon={<Clock size={20} color="var(--accent-secondary)" />}
        label="Uptime"
        value={formatUptime(uptime)}
        accent="var(--accent-secondary-dim)"
        delay={150}
      />
    </div>
  );
}
