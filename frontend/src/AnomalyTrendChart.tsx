import { useMemo } from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import type { Alert } from './api';

interface AnomalyTrendChartProps {
  alerts: Alert[];
  threshold?: number | null;
}

export function AnomalyTrendChart({ alerts, threshold }: AnomalyTrendChartProps) {
  const data = useMemo(() => {
    if (!alerts.length) return [];
    const chronological = [...alerts].reverse();
    const recent = chronological.slice(-60);

    return recent.map((a) => ({
      time: new Date(a.timestamp * 1000).toLocaleTimeString([], {
        hour12: false,
        minute: '2-digit',
        second: '2-digit',
      }),
      score: a.anomaly_score,
    }));
  }, [alerts]);

  return (
    <div
      className="card"
      style={{ padding: '24px', height: '320px', display: 'flex', flexDirection: 'column' }}
    >
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
        Anomaly Score Trend
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
          Waiting for anomaly data...
        </div>
      ) : (
        <div style={{ flex: 1, width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 8, right: 8, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f0883e" stopOpacity={0.25} />
                  <stop offset="95%" stopColor="#f0883e" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="var(--border-subtle)"
                vertical={false}
              />
              <XAxis
                dataKey="time"
                stroke="var(--text-muted)"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                interval="preserveStartEnd"
              />
              <YAxis
                stroke="var(--text-muted)"
                fontSize={10}
                tickLine={false}
                axisLine={false}
                domain={[0, 'auto']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-default)',
                  borderRadius: '8px',
                  fontSize: '12px',
                }}
                itemStyle={{ color: 'var(--text-primary)', fontWeight: 600 }}
              />
              {threshold && (
                <ReferenceLine
                  y={threshold}
                  stroke="var(--severity-critical)"
                  strokeDasharray="4 4"
                  strokeWidth={1.5}
                  label={{
                    position: 'insideTopRight',
                    value: 'Threshold',
                    fill: 'var(--severity-critical)',
                    fontSize: 10,
                  }}
                />
              )}
              <Area
                type="monotone"
                dataKey="score"
                stroke="#f0883e"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorScore)"
                isAnimationActive={false}
                dot={false}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
