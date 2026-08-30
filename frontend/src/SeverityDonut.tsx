import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';
import type { StatsSummary } from './api';

interface SeverityDonutProps {
  stats: StatsSummary | null;
}

const SEVERITY_COLORS: Record<string, string> = {
  Critical: '#f85149',
  High: '#f0883e',
  Medium: '#d29922',
  Low: '#3fb950',
};

export function SeverityDonut({ stats }: SeverityDonutProps) {
  const data = stats
    ? [
        { name: 'Critical', value: stats.critical_count },
        { name: 'High', value: stats.high_count },
        { name: 'Medium', value: stats.medium_count },
        { name: 'Low', value: stats.low_count },
      ].filter((d) => d.value > 0)
    : [];

  const total = data.reduce((sum, d) => sum + d.value, 0);

  return (
    <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
      <h3
        style={{
          margin: '0 0 16px',
          fontSize: '13px',
          fontWeight: 600,
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          letterSpacing: '0.8px',
        }}
      >
        Severity Breakdown
      </h3>

      {data.length === 0 ? (
        <div
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--text-muted)',
            fontSize: '13px',
          }}
        >
          No alerts yet
        </div>
      ) : (
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flex: 1 }}>
          <div style={{ width: '140px', height: '140px', position: 'relative' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={42}
                  outerRadius={64}
                  paddingAngle={3}
                  dataKey="value"
                  strokeWidth={0}
                >
                  {data.map((entry) => (
                    <Cell
                      key={entry.name}
                      fill={SEVERITY_COLORS[entry.name]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-default)',
                    borderRadius: '8px',
                    fontSize: '12px',
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
            {/* Center label */}
            <div
              style={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                textAlign: 'center',
              }}
            >
              <div className="mono" style={{ fontSize: '20px', fontWeight: 700 }}>
                {total}
              </div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>total</div>
            </div>
          </div>

          {/* Legend */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {data.map((entry) => (
              <div
                key={entry.name}
                style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px' }}
              >
                <div
                  style={{
                    width: '10px',
                    height: '10px',
                    borderRadius: '3px',
                    backgroundColor: SEVERITY_COLORS[entry.name],
                    flexShrink: 0,
                  }}
                />
                <span style={{ color: 'var(--text-secondary)' }}>{entry.name}</span>
                <span className="mono" style={{ fontWeight: 600, marginLeft: 'auto' }}>
                  {entry.value}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
