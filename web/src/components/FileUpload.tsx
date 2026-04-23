/** FileUpload — drag-and-drop upload component (WEB-02). */

import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { runScan } from '../api/client';
import { useAppStore } from '../store/appStore';
import { UploadCloud, FileJson, Cpu, AlertCircle, Loader2, Network } from 'lucide-react';

export function FileUpload() {
  const [modelFile, setModelFile] = useState<File | null>(null);
  const [datasetFile, setDatasetFile] = useState<File | null>(null);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const { setSelectedSession, setCurrentScanResult } = useAppStore();

  const onDropModel = useCallback((files: File[]) => {
    if (files[0]) { setModelFile(files[0]); }
  }, []);

  const onDropDataset = useCallback((files: File[]) => {
    if (files[0]) { setDatasetFile(files[0]); }
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
    try {
      const result = await runScan(modelFile, datasetFile);
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

  return (
    <div className="w-full max-w-4xl mx-auto my-16 animate-in fade-in zoom-in-95 duration-700">
      <div className="glass-panel p-8 md:p-10 rounded-3xl relative overflow-hidden group/upload border border-white/5 shadow-2xl">
        {/* Subtle background glow */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary-500/10 rounded-full blur-[80px] -z-10 pointer-events-none" />
        <div className="absolute bottom-0 left-0 w-64 h-64 bg-success-500/10 rounded-full blur-[80px] -z-10 pointer-events-none" />

        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center p-3 rounded-2xl bg-dark-950/50 border border-white/10 mb-4 shadow-inner">
            <Network className="w-8 h-8 text-white" />
          </div>
          <h2 className="text-3xl font-extrabold text-white tracking-tight mb-2">Configure Analysis Pipeline</h2>
          <p className="text-dark-400 font-medium">Upload your model weights and validation dataset to initialize the audit.</p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8 relative z-10">
          {/* Model Upload */}
          <div 
            {...modelDropzone.getRootProps()} 
            className={`flex flex-col items-center justify-center p-8 rounded-2xl border-2 transition-all duration-300 cursor-pointer ${
              modelDropzone.isDragActive ? 'border-primary-500 bg-primary-500/10 shadow-[0_0_30px_rgba(6,182,212,0.2)] scale-[1.02]' : 
              modelFile ? 'border-success-500 bg-success-500/10 shadow-[inset_0_0_20px_rgba(5,150,105,0.2),0_0_15px_rgba(5,150,105,0.2)]' : 
              'border-white/10 bg-dark-950/40 hover:border-white/30 hover:bg-dark-900'
            }`}
          >
            <input {...modelDropzone.getInputProps()} />
            <div className={`p-4 rounded-xl mb-4 transition-transform duration-300 ${modelFile ? 'bg-success-500/20 text-success-400 scale-110 shadow-[0_0_15px_rgba(5,150,105,0.4)]' : 'bg-dark-800 text-dark-400 group-hover/upload:text-white'}`}>
              <Cpu className="w-8 h-8" />
            </div>
            <p className={`text-lg font-bold truncate max-w-[200px] mb-1 transition-colors ${modelFile ? 'text-success-400' : 'text-white'}`}>
              {modelFile ? modelFile.name : 'Drop Model'}
            </p>
            <p className="text-xs font-mono text-dark-500 tracking-widest uppercase">.pkl, .joblib, .onnx</p>
          </div>

          {/* Dataset Upload */}
          <div 
            {...datasetDropzone.getRootProps()} 
            className={`flex flex-col items-center justify-center p-8 rounded-2xl border-2 transition-all duration-300 cursor-pointer ${
              datasetDropzone.isDragActive ? 'border-primary-500 bg-primary-500/10 shadow-[0_0_30px_rgba(6,182,212,0.2)] scale-[1.02]' : 
              datasetFile ? 'border-success-500 bg-success-500/10 shadow-[inset_0_0_20px_rgba(5,150,105,0.2),0_0_15px_rgba(5,150,105,0.2)]' : 
              'border-white/10 bg-dark-950/40 hover:border-white/30 hover:bg-dark-900'
            }`}
          >
            <input {...datasetDropzone.getInputProps()} />
            <div className={`p-4 rounded-xl mb-4 transition-transform duration-300 ${datasetFile ? 'bg-success-500/20 text-success-400 scale-110 shadow-[0_0_15px_rgba(5,150,105,0.4)]' : 'bg-dark-800 text-dark-400 group-hover/upload:text-white'}`}>
              <FileJson className="w-8 h-8" />
            </div>
            <p className={`text-lg font-bold truncate max-w-[200px] mb-1 transition-colors ${datasetFile ? 'text-success-400' : 'text-white'}`}>
              {datasetFile ? datasetFile.name : 'Drop Dataset'}
            </p>
            <p className="text-xs font-mono text-dark-500 tracking-widest uppercase">.csv, .json, .parquet</p>
          </div>
        </div>

        {/* Execute Button */}
        <button
          onClick={handleScan}
          disabled={!modelFile || !datasetFile || scanning}
          className={`w-full py-4 rounded-xl font-bold text-[13px] uppercase tracking-widest transition-all duration-300 flex items-center justify-center gap-3 border ${
            modelFile && datasetFile && !scanning
              ? 'bg-white text-black hover:bg-dark-100 hover:scale-[1.01] shadow-[0_0_20px_rgba(255,255,255,0.1)] border-transparent' 
              : 'bg-dark-950/50 text-dark-600 border-white/5 cursor-not-allowed'
          }`}
        >
          {scanning ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin text-primary-500" />
              Initializing Pipeline...
            </>
          ) : (
            <>
              <UploadCloud className="w-5 h-5" />
              Execute Analysis
            </>
          )}
        </button>
        
        {/* Progress Bar (Scanning) */}
        {scanning && (
          <div className="absolute bottom-0 left-0 right-0 h-1 bg-dark-800 overflow-hidden">
            <div className="absolute top-0 bottom-0 left-0 w-1/3 bg-primary-500 animate-[scan_1.5s_ease-in-out_infinite]" />
          </div>
        )}

        {error && (
          <div className="mt-6 p-4 bg-danger-500/10 border border-danger-500/20 rounded-xl flex items-center gap-3 text-danger-400">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm font-semibold">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

