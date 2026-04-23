/** FileUpload — drag-and-drop upload component (WEB-02). */

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { runScan } from '../api/client';
import type { ScanResult } from '../api/client';
import { useAppStore } from '../store/appStore';

export function FileUpload() {
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [datasetFile, setDatasetFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const { setSelectedSession, setCurrentScanResult } = useAppStore();

  const onDropModel = useCallback((files: File[]) => {
    if (files[0]) { setModelFile(files[0]); setScanResult(null); }
  }, []);

  const onDropDataset = useCallback((files: File[]) => {
    if (files[0]) { setDatasetFile(files[0]); setScanResult(null); }
  }, []);

  const modelDropzone = useDropzone({
    onDrop: onDropModel,
    accept: { 'application/octet-stream': ['.pkl', '.joblib', '.onnx'] },
    multiple: false,
  });

  const datasetDropzone = useDropzone({
    onDrop: onDropDataset,
    accept: { 'text/csv': ['.csv'], 'application/json': ['.json'], 'application/octet-stream': ['.parquet'] },
    multiple: false,
  });

  const handleScan = async () => {
    if (!modelFile || !datasetFile) return;
    setScanning(true);
    setError(null);
    setScanResult(null);
    try {
      const result = await runScan(modelFile, datasetFile);
      setScanResult(result);
      setCurrentScanResult(result);
      if (result.session_id) {
        setSelectedSession(result.session_id);
      }
    } catch (e: any) {
      setError(e.message || 'Scan failed');
    } finally {
      setScanning(false);
    }
  };

  const dropStyle = (isDragActive: boolean, hasFile: boolean): React.CSSProperties => ({
    border: `2px dashed ${isDragActive ? '#3b82f6' : hasFile ? '#22c55e' : '#334155'}`,
    borderRadius: 12,
    padding: '24px 16px',
    textAlign: 'center',
    cursor: 'pointer',
    background: isDragActive ? 'rgba(59,130,246,0.08)' : hasFile ? 'rgba(34,197,94,0.05)' : 'transparent',
    transition: 'all 0.2s',
  });

  // Extract risk level from results
  const riskLevel = scanResult?.analysis_results?.overall_risk_level;
  const riskColor = riskLevel === 'high' ? '#ef4444' : riskLevel === 'medium' ? '#eab308' : '#22c55e';

  return (
    <div style={{ padding: 24, maxWidth: 600 }}>
      <h2 style={{ fontSize: 20, fontWeight: 600, marginBottom: 20, color: '#f1f5f9' }}>
        Upload Model & Dataset
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
        <div {...modelDropzone.getRootProps()} style={dropStyle(modelDropzone.isDragActive, !!modelFile)}>
          <input {...modelDropzone.getInputProps()} />
          <div style={{ fontSize: 28, marginBottom: 8 }}>🤖</div>
          <div style={{ fontSize: 13, fontWeight: 500, color: '#f1f5f9' }}>
            {modelFile ? modelFile.name : 'Drop model file'}
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>.pkl .joblib .onnx</div>
        </div>

        <div {...datasetDropzone.getRootProps()} style={dropStyle(datasetDropzone.isDragActive, !!datasetFile)}>
          <input {...datasetDropzone.getInputProps()} />
          <div style={{ fontSize: 28, marginBottom: 8 }}>📊</div>
          <div style={{ fontSize: 13, fontWeight: 500, color: '#f1f5f9' }}>
            {datasetFile ? datasetFile.name : 'Drop dataset file'}
          </div>
          <div style={{ fontSize: 11, color: '#64748b', marginTop: 4 }}>.csv .parquet .json</div>
        </div>
      </div>

      <button
        onClick={handleScan}
        disabled={!modelFile || !datasetFile || scanning}
        style={{
          width: '100%',
          padding: '12px 0',
          borderRadius: 8,
          border: 'none',
          background: modelFile && datasetFile ? '#3b82f6' : '#334155',
          color: '#fff',
          fontSize: 14,
          fontWeight: 600,
          cursor: modelFile && datasetFile ? 'pointer' : 'not-allowed',
          opacity: scanning ? 0.7 : 1,
          transition: 'all 0.2s',
        }}
      >
        {scanning ? '⏳ Analyzing bias... (this may take a moment)' : '⚖️ Run Bias Analysis'}
      </button>

      {error && <p style={{ color: '#ef4444', fontSize: 13, marginTop: 12 }}>✗ {error}</p>}

      {scanResult && (
        <div style={{
          marginTop: 16,
          padding: 16,
          borderRadius: 10,
          background: 'rgba(34,197,94,0.08)',
          border: '1px solid rgba(34,197,94,0.2)',
        }}>
          <p style={{ color: '#22c55e', fontSize: 14, fontWeight: 600, marginBottom: 8 }}>
            ✓ Bias analysis complete
          </p>
          <p style={{ color: '#94a3b8', fontSize: 12 }}>
            Model: {scanResult.model_name || modelFile?.name}
          </p>
          {riskLevel && (
            <p style={{ color: riskColor, fontSize: 13, fontWeight: 700, marginTop: 4, textTransform: 'uppercase' }}>
              Risk Level: {riskLevel}
            </p>
          )}
          {scanResult.analysis_results?.protected_attributes && (
            <p style={{ color: '#94a3b8', fontSize: 12, marginTop: 4 }}>
              Protected attributes analyzed: {scanResult.analysis_results.protected_attributes.join(', ')}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

