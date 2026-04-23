/** FileUpload — drag-and-drop upload component (WEB-02). */

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { runScan } from '../api/client';
import type { ScanResult } from '../api/client';
import { useAppStore } from '../store/appStore';
import { UploadCloud, FileJson, Cpu, ShieldCheck, AlertCircle, Loader2 } from 'lucide-react';

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

  const getDropzoneStyle = (isDragActive: boolean, hasFile: boolean) => {
    if (isDragActive) return "border-primary-500 bg-primary-500/10 text-primary-400";
    if (hasFile) return "border-emerald-500 bg-emerald-500/5 text-emerald-400 border-solid";
    return "border-white/10 hover:border-white/30 hover:bg-white/5 text-dark-400 border-dashed";
  };

  const riskLevel = scanResult?.analysis_results?.overall_risk_level;
  const riskColor = riskLevel === 'high' ? 'text-red-500' : riskLevel === 'medium' ? 'text-yellow-500' : 'text-emerald-500';

  return (
    <div className="w-full max-w-2xl mx-auto glass-panel p-8 md:p-12 rounded-[2rem] shadow-2xl relative overflow-hidden animate-in fade-in zoom-in-95 duration-500">
      <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/10 rounded-full blur-[100px] -z-10" />
      <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-500/10 rounded-full blur-[100px] -z-10" />
      
      <div className="text-center mb-10">
        <div className="inline-flex items-center justify-center p-3 bg-white/5 rounded-2xl mb-4 shadow-inner border border-white/5">
          <ShieldCheck className="w-8 h-8 text-primary-400" />
        </div>
        <h2 className="text-2xl md:text-3xl font-extrabold text-white tracking-tight mb-2">
          New Bias Analysis
        </h2>
        <p className="text-dark-400">Upload your model and test dataset to generate a compliance report.</p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Model Upload */}
        <div 
          {...modelDropzone.getRootProps()} 
          className={`flex flex-col items-center justify-center p-8 rounded-2xl border-2 transition-all cursor-pointer group ${getDropzoneStyle(modelDropzone.isDragActive, !!modelFile)}`}
        >
          <input {...modelDropzone.getInputProps()} />
          <div className={`p-3 rounded-xl mb-4 transition-transform group-hover:scale-110 ${modelFile ? 'bg-emerald-500/20 text-emerald-400' : 'bg-dark-800 text-dark-300'}`}>
            <Cpu className="w-6 h-6" />
          </div>
          <div className={`text-sm font-semibold mb-1 text-center ${modelFile ? 'text-emerald-100' : 'text-white'}`}>
            {modelFile ? modelFile.name : 'Drop model file'}
          </div>
          <div className="text-[11px] font-medium opacity-60">.pkl, .joblib, .onnx</div>
        </div>

        {/* Dataset Upload */}
        <div 
          {...datasetDropzone.getRootProps()} 
          className={`flex flex-col items-center justify-center p-8 rounded-2xl border-2 transition-all cursor-pointer group ${getDropzoneStyle(datasetDropzone.isDragActive, !!datasetFile)}`}
        >
          <input {...datasetDropzone.getInputProps()} />
          <div className={`p-3 rounded-xl mb-4 transition-transform group-hover:scale-110 ${datasetFile ? 'bg-emerald-500/20 text-emerald-400' : 'bg-dark-800 text-dark-300'}`}>
            <FileJson className="w-6 h-6" />
          </div>
          <div className={`text-sm font-semibold mb-1 text-center ${datasetFile ? 'text-emerald-100' : 'text-white'}`}>
            {datasetFile ? datasetFile.name : 'Drop dataset file'}
          </div>
          <div className="text-[11px] font-medium opacity-60">.csv, .parquet, .json</div>
        </div>
      </div>

      <button
        onClick={handleScan}
        disabled={!modelFile || !datasetFile || scanning}
        className={`w-full py-4 px-6 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${
          modelFile && datasetFile && !scanning
            ? 'bg-gradient-to-r from-primary-600 to-primary-500 hover:from-primary-500 hover:to-primary-400 text-white shadow-lg shadow-primary-500/25 hover:shadow-primary-500/40 hover:-translate-y-0.5' 
            : 'bg-dark-800 text-dark-500 cursor-not-allowed border border-white/5'
        }`}
      >
        {scanning ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            Analyzing bias...
          </>
        ) : (
          <>
            <UploadCloud className="w-5 h-5" />
            Run Bias Analysis
          </>
        )}
      </button>

      {error && (
        <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}

      {scanResult && (
        <div className="mt-6 p-5 rounded-2xl bg-emerald-500/10 border border-emerald-500/20 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-2xl" />
          <div className="relative z-10">
            <p className="flex items-center gap-2 text-emerald-400 text-sm font-bold mb-3">
              <ShieldCheck className="w-5 h-5" />
              Bias analysis complete
            </p>
            <p className="text-emerald-100/70 text-xs mb-1">
              Model: <span className="font-semibold text-emerald-100">{scanResult.model_name || modelFile?.name}</span>
            </p>
            {riskLevel && (
              <p className={`text-xs font-bold uppercase tracking-wide mt-2 ${riskColor}`}>
                Risk Level: {riskLevel}
              </p>
            )}
            {scanResult.analysis_results?.protected_attributes && (
              <p className="text-emerald-100/50 text-[11px] mt-3">
                Analyzed attributes: {scanResult.analysis_results.protected_attributes.join(', ')}
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

