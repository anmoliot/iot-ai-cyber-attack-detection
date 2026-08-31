import { useCallback, useEffect, useRef, useState } from 'react';
import { Activity, AlertTriangle, Network, Play, Radar, RotateCcw, ServerCog, ShieldAlert, Square } from 'lucide-react';
import { AlertFeed } from './AlertFeed';
import { AnomalyTrendChart } from './AnomalyTrendChart';
import { AttackTypeChart } from './AttackTypeChart';
import { ConnectionBanner } from './ConnectionBanner';
import { ModelRegistry } from './ModelRegistry';
import { ProtocolDistribution } from './ProtocolDistribution';
import { SeverityDonut } from './SeverityDonut';
import { StatsSummaryBar } from './StatsSummaryBar';
import { StatusPanel } from './StatusPanel';
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
  const [isRetrainConfirmationOpen, setIsRetrainConfirmationOpen] = useState(false);
  const [isCapturing, setIsCapturing] = useState(false);
  const [isCaptureChanging, setIsCaptureChanging] = useState(false);
  const currentRunSince = useRef<number | null>(null);
  const { alerts, connectionState } = useAlertStream(initialAlerts);

  const fetchAnalytics = useCallback(async () => {
    try {
      const statusData = await API.getStatus();
      const since = currentRunSince.current ?? statusData.started_at;
      currentRunSince.current = since;
      const [summary, attackers, protocols, atkTypes, kitsune, edgeBinary, edgeAttackType, capture] = await Promise.all([
        API.getStatsSummary(since),
        API.getTopAttackers(10, since),
        API.getProtocolDistribution(since),
        API.getAttackTypeDistribution(since),
        API.getKitsuneModelStatus(),
        API.getEdgeIIoTModelStatus(),
        API.getEdgeIIoTAttackTypeModelStatus(),
        API.getCaptureStatus(),
      ]);
      setStatus(statusData);
      setStats(summary);
      setTopAttackers(attackers);
      setProtocolDist(protocols);
      setAttackTypes(atkTypes);
      setKitsuneModel(kitsune);
      setEdgeBinaryModel(edgeBinary);
      setEdgeAttackTypeModel(edgeAttackType);
      setIsCapturing(capture.capturing);
    } catch {
      // ConnectionBanner describes the unavailable service.
    }
  }, []);

  useEffect(() => {
    const init = async () => {
      try {
        const statusData = await API.getStatus();
        currentRunSince.current = statusData.started_at;
        setStatus(statusData);
        setInitialAlerts(await API.getRecentAlerts(100, undefined, undefined, statusData.started_at));
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
    setIsRetrainConfirmationOpen(false);
    setIsRetraining(true);
    try {
      await API.postRetrain();
      await fetchAnalytics();
    } finally {
      setIsRetraining(false);
    }
  };

  const handleCapture = async () => {
    if (isCaptureChanging) return;
    setIsCaptureChanging(true);
    try {
      const capture = isCapturing ? await API.stopCapture() : await API.startCapture();
      setIsCapturing(capture.capturing);
      await fetchAnalytics();
    } finally {
      setIsCaptureChanging(false);
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
            <button className="retrain-button capture-button" onClick={handleCapture} disabled={isCaptureChanging}>
              {isCapturing ? <Square size={15} /> : <Play size={15} />}
              {isCaptureChanging ? 'Updating capture' : isCapturing ? 'Stop capture' : 'Start capture'}
            </button>
            <button className="retrain-button" onClick={() => setIsRetrainConfirmationOpen(true)} disabled={isRetraining}>
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
              <span>Packet capture</span>
              <strong>{isCapturing ? 'Running' : 'Stopped'}</strong>
            </div>
          </header>

          <StatsSummaryBar stats={stats} uptime={status?.uptime_seconds ?? 0} />
          <StatusPanel status={status} connectionState={connectionState} />
          <ModelRegistry kitsune={kitsuneModel} edgeBinary={edgeBinaryModel} edgeAttackType={edgeAttackTypeModel} />
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
      {isRetrainConfirmationOpen && (
        <div className="retrain-dialog-backdrop" role="presentation">
          <section className="retrain-dialog" role="dialog" aria-modal="true" aria-labelledby="retrain-dialog-title">
            <AlertTriangle size={19} aria-hidden="true" />
            <div>
              <h2 id="retrain-dialog-title">Retrain live anomaly model?</h2>
              <p>This clears the live autoencoder baseline and starts a new 500-packet grace period. Saved supervised classifiers are not changed.</p>
            </div>
            <div className="retrain-dialog-actions">
              <button onClick={() => setIsRetrainConfirmationOpen(false)} disabled={isRetraining}>Cancel</button>
              <button className="confirm-retrain" onClick={handleRetrain} disabled={isRetraining}>
                {isRetraining ? 'Retraining' : 'Clear and retrain'}
              </button>
            </div>
          </section>
        </div>
      )}
    </div>
  );
}
