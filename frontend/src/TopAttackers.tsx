import type { TopAttacker } from './api';
import { User } from 'lucide-react';

interface TopAttackersProps {
  attackers: TopAttacker[];
}

export function TopAttackers({ attackers }: TopAttackersProps) {
  const maxCount = attackers.length > 0 ? attackers[0].count : 1;

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
        Top Attackers
      </h3>

      {attackers.length === 0 ? (
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
          No attack sources detected
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {attackers.slice(0, 8).map((attacker, i) => {
            const barWidth = (attacker.count / maxCount) * 100;
            return (
              <div
                key={attacker.ip}
                className="animate-slide-in"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '12px',
                  animationDelay: `${i * 40}ms`,
                }}
              >
                <User size={14} color="var(--text-muted)" style={{ flexShrink: 0 }} />
                <span
                  className="mono"
                  style={{ fontSize: '12px', width: '130px', flexShrink: 0, color: 'var(--text-secondary)' }}
                >
                  {attacker.ip}
                </span>
                <div
                  style={{
                    flex: 1,
                    height: '6px',
                    backgroundColor: 'var(--border-subtle)',
                    borderRadius: '3px',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      width: `${barWidth}%`,
                      height: '100%',
                      borderRadius: '3px',
                      background: 'var(--accent-gradient)',
                      transition: 'width var(--transition-slow)',
                    }}
                  />
                </div>
                <span
                  className="mono"
                  style={{ fontSize: '12px', fontWeight: 600, width: '30px', textAlign: 'right', flexShrink: 0 }}
                >
                  {attacker.count}
                </span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
