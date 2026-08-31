import { useCallback, useEffect, useState } from 'react';
import { Activity, Network, Radar, RotateCcw, ServerCog, ShieldAlert } from 'lucide-react';
import { AlertFeed } from './AlertFeed';
import { AnomalyTrendChart } from './AnomalyTrendChart';
import { AttackTypeChart } from './AttackTypeChart';
import { ConnectionBanner } from './ConnectionBanner';
import { ModelRegistry } from './ModelRegistry';
import { ProtocolDistribution } from './ProtocolDistribution';
import { SeverityDonut } from './SeverityDonut';
import { StatsSummaryBar } from './StatsSummaryBar';
import { StatusPanel } from './StatusPanel';
import { SupervisedModelDemo } from './SupervisedModelDemo';
import { TopAttackers } from './TopAttackers';
import { useAlertStream } from './useAlertStream';
import {
  API,
  type Alert,
  type AttackTypeDistribution,
  type EngineStatus,
  type PersistedModelStatus,
  type ProtocolDistribution as ProtocolDist,
  type StatsSummary,
  type TopAttacker,
} from './api';

export function DashboardShell() {
  const [status, setStatus] = useState<EngineStatus | null>(null);
  const [initialAlerts, setInitialAlerts] = useState<Alert[]>([]);
  const [stats, setStats] = useState<StatsSummary | null>(null);
  const [topAttackers, setTopAttackers] = useState<TopAttacker[]>([]);
  const [protocolDist, setProtocolDist] = useState<ProtocolDist | null>(null);
  const [attackTypes, setAttackTypes] = useState<AttackTypeDistribution>({});
  const [kitsuneModel, setKitsuneModel] = useState<PersistedModelStatus | null>(null);
  const [edgeBinaryModel, setEdgeBinaryModel] = useState<PersistedModelStatus | null>(null);
  const [edgeAttackTypeModel, setEdgeAttackTypeModel] = useState<PersistedModelStatus | null>(null);
  const [isRetraining, setIsRetraining] = useState(false);
  const { alerts, connectionState } = useAlertStream(initialAlerts);

  const fetchAnalytics = useCallback(async () => {
    try {
      const [statusData, summary, attackers, protocols, atkTypes, kitsune, edgeBinary, edgeAttackType] = await Promise.all([
        API.getStatus(),
        API.getStatsSummary(),
        API.getTopAttackers(10),
        API.getProtocolDistribution(),
        API.getAttackTypeDistribution(),
        API.getKitsuneModelStatus(),
        API.getEdgeIIoTModelStatus(),
        API.getEdgeIIoTAttackTypeModelStatus(),
      ]);
      setStatus(statusData);
      setStats(summary);
      setTopAttackers(attackers);
      setProtocolDist(protocols);
      setAttackTypes(atkTypes);
      setKitsuneModel(kitsune);
      setEdgeBinaryModel(edgeBinary);
      setEdgeAttackTypeModel(edgeAttackType);
    } catch {
      // ConnectionBanner describes the unavailable service.
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      try {
        setInitialAlerts((await API.getRecentAlerts(100)).reverse());
      } catch {
        // Polling retries analytics after startup.
      }
      fetchAnalytics();
    };
    init();
    const interval = setInterval(fetchAnalytics, 5000);
    return () => clearInterval(interval);
  }, [fetchAnalytics]);

  const handleRetrain = async () => {
    if (isRetraining) return;
    setIsRetraining(true);
    try {
      await API.postRetrain();
      await fetchAnalytics();
    } finally {
      setIsRetraining(false);
    }
  };

  return (
    <div className="app-shell">
      <ConnectionBanner connectionState={connectionState} />
      <div className="workspace-layout">
        <aside className="sidebar">
          <div className="brand-lockup">
            <div className="brand-mark"><ShieldAlert size={18} /></div>
            <div><strong>SentinelAI</strong><span>IoT security</span></div>
          </div>
          <nav className="side-nav" aria-label="Workspace navigation">
            <div className="nav-item is-active"><Activity size={16} /><span>Live monitor</span></div>
            <div className="nav-item"><Network size={16} /><span>Traffic analysis</span></div>
            <div className="nav-item"><ServerCog size={16} /><span>Model registry</span></div>
          </nav>
          <div className="sidebar-footer">
            <button className="retrain-button" onClick={handleRetrain} disabled={isRetraining}>
              <RotateCcw size={15} className={isRetraining ? 'spin' : ''} />
              {isRetraining ? 'Retraining model' : 'Retrain live model'}
            </button>
            <div className={`connection-indicator ${connectionState}`}>
              <span aria-hidden="true" />{connectionState}
            </div>
          </div>
        </aside>

        <main className="dashboard-main">
          <header className="dashboard-header">
            <div>
              <span className="eyebrow">Operations workspace</span>
              <h1>Network security monitor</h1>
              <p>Real-time anomaly signals and trained IoT threat classifiers.</p>
            </div>
            <div className="header-status">
              <Radar size={17} />
              <span>Sensor stream</span>
              <strong>{connectionState === 'connected' ? 'Online' : connectionState}</strong>
            </div>
          </header>

          <StatsSummaryBar stats={stats} uptime={status?.uptime_seconds ?? 0} />
          <StatusPanel status={status} connectionState={connectionState} />
          <ModelRegistry kitsune={kitsuneModel} edgeBinary={edgeBinaryModel} edgeAttackType={edgeAttackTypeModel} />
          <SupervisedModelDemo />

          <div className="chart-row chart-row-primary">
            <AnomalyTrendChart alerts={alerts} threshold={status?.anomaly_threshold} />
            <SeverityDonut stats={stats} />
          </div>
          <div className="chart-row chart-row-secondary">
            <TopAttackers attackers={topAttackers} />
            <ProtocolDistribution distribution={protocolDist} />
            <AttackTypeChart distribution={attackTypes} />
          </div>
          <AlertFeed alerts={alerts} />
        </main>
      </div>
    </div>
  );
}
