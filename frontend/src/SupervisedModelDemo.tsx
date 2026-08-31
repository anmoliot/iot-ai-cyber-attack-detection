import { useEffect, useState } from 'react';
import { CheckCircle2, CircleAlert, LoaderCircle, Play } from 'lucide-react';
import {
  API,
  type EdgeIIoTAttackTypePrediction,
  type EdgeIIoTBinaryPrediction,
  type EdgeIIoTDemoSamples,
} from './api';

function binaryLabel(value: string | number) {
  return Number(value) === 1 ? 'Attack' : 'Benign';
}

function confidence(value: number) {
  return `${(value * 100).toFixed(1)}% confidence`;
}

export function SupervisedModelDemo() {
  const [samples, setSamples] = useState<EdgeIIoTDemoSamples | null>(null);
  const [binaryIndex, setBinaryIndex] = useState(0);
  const [attackTypeIndex, setAttackTypeIndex] = useState(0);
  const [binaryResult, setBinaryResult] = useState<EdgeIIoTBinaryPrediction | null>(null);
  const [attackTypeResult, setAttackTypeResult] = useState<EdgeIIoTAttackTypePrediction | null>(null);
  const [running, setRunning] = useState<'binary' | 'attack-type' | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    API.getEdgeIIoTDemoSamples()
      .then(setSamples)
      .catch(() => setError('Demo records are unavailable. Start the backend with the demo fixture installed.'));
  }, []);

  const runBinary = async () => {
    const sample = samples?.binary[binaryIndex];
    if (!sample) return;
    setRunning('binary');
    setError(null);
    try {
      setBinaryResult(await API.postEdgeIIoTBinaryPrediction(sample.features));
    } catch {
      setError('The binary classifier could not process this record.');
    } finally {
      setRunning(null);
    }
  };

  const runAttackType = async () => {
    const sample = samples?.attack_type[attackTypeIndex];
    if (!sample) return;
    setRunning('attack-type');
    setError(null);
    try {
      setAttackTypeResult(await API.postEdgeIIoTAttackTypePrediction(sample.features));
    } catch {
      setError('The attack-type classifier could not process this record.');
    } finally {
      setRunning(null);
    }
  };

  return (
    <section className="model-demo" aria-labelledby="supervised-demo-title">
      <div className="section-heading">
        <div>
          <span className="eyebrow">Model validation</span>
          <h2 id="supervised-demo-title">Supervised model verification</h2>
        </div>
        <span className="demo-context">Held-out Edge-IIoT test records</span>
      </div>

      {error && <div className="demo-error"><CircleAlert size={16} />{error}</div>}
      {!samples && !error && <div className="demo-loading"><LoaderCircle size={16} className="spin" />Loading demonstration records</div>}

      {samples && (
        <div className="demo-columns">
          <div className="demo-column">
            <div className="demo-column-heading"><span>Binary detection</span><strong>Benign or attack</strong></div>
            <label className="demo-control">
              <span>Test record</span>
              <select value={binaryIndex} onChange={(event) => { setBinaryIndex(Number(event.target.value)); setBinaryResult(null); }}>
                {samples.binary.map((sample, index) => <option key={index} value={index}>Sample {index + 1} - expected {binaryLabel(sample.expected_label)}</option>)}
              </select>
            </label>
            <button className="demo-run" onClick={runBinary} disabled={running !== null}>
              {running === 'binary' ? <LoaderCircle size={15} className="spin" /> : <Play size={15} />}Run binary classifier
            </button>
            {binaryResult && <div className="demo-result"><CheckCircle2 size={17} /><div><span>Prediction</span><strong>{binaryResult.prediction}</strong><small>{confidence(binaryResult.confidence)}</small></div></div>}
          </div>
          <div className="demo-column">
            <div className="demo-column-heading"><span>Attack classification</span><strong>Threat category</strong></div>
            <label className="demo-control">
              <span>Test record</span>
              <select value={attackTypeIndex} onChange={(event) => { setAttackTypeIndex(Number(event.target.value)); setAttackTypeResult(null); }}>
                {samples.attack_type.map((sample, index) => <option key={index} value={index}>Sample {index + 1} - expected {sample.expected_label}</option>)}
              </select>
            </label>
            <button className="demo-run" onClick={runAttackType} disabled={running !== null}>
              {running === 'attack-type' ? <LoaderCircle size={15} className="spin" /> : <Play size={15} />}Run attack classifier
            </button>
            {attackTypeResult && <div className="demo-result"><CheckCircle2 size={17} /><div><span>Prediction</span><strong>{attackTypeResult.attack_type}</strong><small>{confidence(attackTypeResult.confidence)}</small></div></div>}
          </div>
        </div>
      )}
    </section>
  );
}
