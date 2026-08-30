import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import type { ProtocolDistribution as ProtocolDist } from './api';

interface ProtocolDistributionProps {
  distribution: ProtocolDist | null;
}

const PROTOCOL_COLORS: Record<string, string> = {
  TCP: '#58a6ff',
  UDP: '#bc8cff',
  ICMP: '#f0883e',
  OTHER: '#484f58',
};

export function ProtocolDistribution({ distribution }: ProtocolDistributionProps) {
  const data = distribution
    ? [
        { name: 'TCP', value: distribution.TCP },
        { name: 'UDP', value: distribution.UDP },
        { name: 'ICMP', value: distribution.ICMP },
        { name: 'OTHER', value: distribution.OTHER },
      ].filter((d) => d.value > 0)
    : [];

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
        Protocol Distribution
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
          No protocol data
        </div>
      ) : (
        <div style={{ flex: 1, width: '100%', minHeight: '160px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                width={50}
                tick={{ fill: 'var(--text-secondary)', fontSize: 12, fontFamily: 'var(--font-mono)' }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-default)',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                cursor={{ fill: 'rgba(255,255,255,0.03)' }}
              />
              <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={18}>
                {data.map((entry) => (
                  <Cell key={entry.name} fill={PROTOCOL_COLORS[entry.name] || '#484f58'} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
