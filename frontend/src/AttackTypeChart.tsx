import { BarChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';
import type { AttackTypeDistribution } from './api';

interface AttackTypeChartProps {
  distribution: AttackTypeDistribution;
}

const ATTACK_LABELS: Record<string, string> = {
  syn_flood:   'SYN Flood',
  udp_flood:   'UDP Flood',
  icmp_flood:  'ICMP Flood',
  port_scan:   'Port Scan',
  brute_force: 'Brute Force',
  data_exfil:  'Exfil',
  arp_poison:  'ARP Poison',
  unknown:     'Unknown',
};

const ATTACK_COLORS: Record<string, string> = {
  syn_flood:   '#f85149',
  udp_flood:   '#f85149',
  icmp_flood:  '#f0883e',
  port_scan:   '#d29922',
  brute_force: '#f0883e',
  data_exfil:  '#f85149',
  arp_poison:  '#d29922',
  unknown:     '#484f58',
};

export function AttackTypeChart({ distribution }: AttackTypeChartProps) {
  const data = Object.entries(distribution)
    .filter(([, v]) => v > 0)
    .sort(([, a], [, b]) => b - a)
    .map(([key, value]) => ({
      name: ATTACK_LABELS[key] || key,
      value,
      key,
    }));

  return (
    <div className="card" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
      <h3 style={{
        margin: '0 0 16px',
        fontSize: '13px',
        fontWeight: 600,
        color: 'var(--text-secondary)',
        textTransform: 'uppercase',
        letterSpacing: '0.8px',
      }}>
        Attack Types
      </h3>

      {data.length === 0 ? (
        <div style={{
          flex: 1,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: 'var(--text-muted)',
          fontSize: '13px',
        }}>
          No attack data yet
        </div>
      ) : (
        <div style={{ flex: 1, width: '100%', minHeight: '160px' }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} layout="vertical" margin={{ top: 0, right: 8, left: 0, bottom: 0 }}>
              <XAxis type="number" hide />
              <YAxis
                type="category"
                dataKey="name"
                width={72}
                tick={{ fill: 'var(--text-secondary)', fontSize: 11, fontFamily: 'var(--font-sans)' }}
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
              <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={16}>
                {data.map((entry) => (
                  <Cell
                    key={entry.key}
                    fill={ATTACK_COLORS[entry.key] || '#484f58'}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
