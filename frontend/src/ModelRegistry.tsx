import { CheckCircle2, CircleAlert, Database, Layers3, ShieldCheck, type LucideIcon } from 'lucide-react';
import type { PersistedModelStatus } from './api';

interface ModelRegistryProps {
  kitsune: PersistedModelStatus | null;
  edgeBinary: PersistedModelStatus | null;
  edgeAttackType: PersistedModelStatus | null;
}

interface ModelDefinition {
  key: 'kitsune' | 'edgeBinary' | 'edgeAttackType';
  name: string;
  purpose: string;
  icon: LucideIcon;
}

const definitions: ModelDefinition[] = [
  { key: 'kitsune', name: 'Kitsune RF', purpose: 'Binary attack classification', icon: ShieldCheck },
  { key: 'edgeBinary', name: 'Edge-IIoT Binary', purpose: 'Benign or attack decision', icon: Database },
  { key: 'edgeAttackType', name: 'Edge-IIoT Attack Type', purpose: '15-class attack attribution', icon: Layers3 },
];

export function ModelRegistry({ kitsune, edgeBinary, edgeAttackType }: ModelRegistryProps) {
  const statuses = { kitsune, edgeBinary, edgeAttackType };

  return (
    <section className="model-registry" aria-label="Persisted model registry">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Model Registry</span>
          <h2>Trained classifiers</h2>
        </div>
        <span className="registry-caption">Available for feature-record classification</span>
      </div>
      <div className="model-registry-grid">
        {definitions.map(({ key, name, purpose, icon: Icon }) => {
          const model = statuses[key];
          const ready = model?.ready === true;
          return (
            <div className="model-row" key={key}>
              <div className="model-symbol" aria-hidden="true"><Icon size={17} /></div>
              <div className="model-copy">
                <strong>{name}</strong>
                <span>{purpose}</span>
              </div>
              <div className="model-meta">
                <span className="mono">{model?.feature_count ?? '—'} fields</span>
                <span className={ready ? 'model-state is-ready' : 'model-state'}>
                  {ready ? <CheckCircle2 size={13} /> : <CircleAlert size={13} />}
                  {ready ? 'Ready' : model ? 'Unavailable' : 'Checking'}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
