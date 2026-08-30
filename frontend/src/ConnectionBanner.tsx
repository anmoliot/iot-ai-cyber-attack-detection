import { WifiOff } from 'lucide-react';

interface ConnectionBannerProps {
  connectionState: 'connecting' | 'connected' | 'reconnecting' | 'offline';
}

export function ConnectionBanner({ connectionState }: ConnectionBannerProps) {
  if (connectionState === 'connected') return null;

  const getMessage = () => {
    switch (connectionState) {
      case 'connecting':
        return 'Establishing connection to backend...';
      case 'reconnecting':
        return 'Connection lost. Reconnecting to backend...';
      case 'offline':
        return 'Backend unreachable. Dashboard is offline.';
      default:
        return 'Connection issue detected.';
    }
  };

  const isError = connectionState === 'offline';

  return (
    <div
      style={{
        padding: '10px 20px',
        background: isError
          ? 'var(--severity-critical-dim)'
          : 'var(--severity-medium-dim)',
        borderBottom: `1px solid ${isError ? 'rgba(248, 81, 73, 0.2)' : 'rgba(210, 153, 34, 0.2)'}`,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '10px',
        fontSize: '13px',
        fontWeight: 500,
        color: isError ? 'var(--severity-critical)' : 'var(--severity-medium)',
      }}
    >
      <WifiOff size={14} className={connectionState === 'reconnecting' ? 'animate-pulse' : ''} />
      {getMessage()}
    </div>
  );
}
