import { useState } from 'react';
import { ArrowRight, Lock, ShieldAlert } from 'lucide-react';

interface AuthWrapperProps {
  children: React.ReactNode;
}

export function AuthWrapper({ children }: AuthWrapperProps) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);
  const [isLoading, setIsLoading] = useState(false);

  const checkPassword = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate a small delay for UX feel
    setTimeout(() => {
      if (password === 'admin123') {
        setIsAuthenticated(true);
        setError(false);
      } else {
        setError(true);
        setPassword('');
      }
      setIsLoading(false);
    }, 300);
  };

  if (isAuthenticated) {
    return <>{children}</>;
  }

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: 'var(--bg-base)',
      }}
    >
      <div
        className="card animate-fade-in"
        style={{
          padding: '42px 36px',
          maxWidth: '380px',
          width: '100%',
          textAlign: 'center',
        }}
      >
        {/* Logo */}
        <div
          style={{
            display: 'flex',
            justifyContent: 'center',
            marginBottom: '24px',
          }}
        >
          <div
            style={{
              width: '56px',
              height: '56px',
              background: 'var(--accent-primary)',
              borderRadius: 'var(--radius-md)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <ShieldAlert size={28} color="#08231e" />
          </div>
        </div>

        <h2 style={{ margin: '0 0 6px', fontSize: '22px', fontWeight: 700 }}>SentinelAI</h2>
        <p
          style={{
            color: 'var(--text-muted)',
            marginBottom: '32px',
            fontSize: '13px',
            lineHeight: 1.5,
          }}
        >
          IoT Security Operations Center
        </p>

        <form
          onSubmit={checkPassword}
          style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
        >
          <input
            type="password"
            placeholder="Enter access password"
            value={password}
            onChange={(e) => {
              setPassword(e.target.value);
              if (error) setError(false);
            }}
            style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              border: `1px solid ${error ? 'var(--severity-critical)' : 'var(--border-default)'}`,
              backgroundColor: 'var(--bg-surface)',
              color: 'var(--text-primary)',
              outline: 'none',
              fontSize: '14px',
              fontFamily: 'var(--font-sans)',
              transition: 'border-color var(--transition-fast)',
            }}
            onFocus={(e) => {
              if (!error) e.currentTarget.style.borderColor = 'var(--accent-primary)';
            }}
            onBlur={(e) => {
              if (!error) e.currentTarget.style.borderColor = 'var(--border-default)';
            }}
            autoFocus
          />
          {error && (
            <span
              style={{
                color: 'var(--severity-critical)',
                fontSize: '12px',
                textAlign: 'left',
              }}
            >
              Invalid credentials. Access denied.
            </span>
          )}
          <button
            type="submit"
            disabled={isLoading || !password}
            style={{
              padding: '12px 16px',
              borderRadius: 'var(--radius-md)',
              border: 'none',
              background: 'var(--accent-primary)',
              color: '#08231e',
              fontWeight: 600,
              fontSize: '14px',
              fontFamily: 'var(--font-sans)',
              cursor: isLoading || !password ? 'not-allowed' : 'pointer',
              opacity: isLoading || !password ? 0.5 : 1,
              transition: 'opacity var(--transition-fast), transform var(--transition-fast)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
            }}
          >
            {isLoading ? <Lock size={14} /> : <ArrowRight size={15} />}
            {isLoading ? 'Authenticating...' : 'Authenticate'}
          </button>
        </form>
      </div>
    </div>
  );
}
