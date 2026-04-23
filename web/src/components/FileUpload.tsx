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

  const getDropzoneStyle = (isDragActive: boolean, hasFile: boolean) => {
    if (isDragActive) return "border-primary-500 bg-primary-500/10 shadow-[0_0_30px_rgba(6,182,212,0.3)] scale-105";
    if (hasFile) return "border-success-500/50 bg-success-500/5 shadow-[0_0_20px_rgba(5,150,105,0.1)]";
    return "border-white/10 bg-dark-900/30 hover:bg-dark-800/50 hover:border-white/20 border-dashed";
  };

  return (
    <div className="w-full max-w-4xl mx-auto flex flex-col items-center justify-center min-h-[70vh]">
      <div className="text-center mb-10 animate-in slide-in-from-top-8 fade-in duration-700">
        <div className="inline-flex items-center justify-center p-4 bg-primary-500/10 rounded-2xl mb-6 shadow-[0_0_40px_rgba(6,182,212,0.2)] border border-primary-500/20">
          <ShieldCheck className="w-10 h-10 text-primary-400" />
        </div>
        <h1 className="text-4xl md:text-5xl font-extrabold text-white tracking-tighter mb-4 text-balance">
          Initialize Bias Audit
        </h1>
        <p className="text-dark-300 text-lg max-w-xl mx-auto font-light">
          Deploy your model architecture and validation dataset to begin the compliance analysis pipeline.
        </p>
      </div>

      <div className="w-full glass-panel p-8 md:p-10 rounded-[2rem] relative overflow-hidden animate-in zoom-in-95 fade-in duration-700 shadow-2xl border-white/5">
        {/* Scanning Beam Animation Effect */}
        {scanning && (
          <div className="absolute inset-0 z-0 pointer-events-none">
            <div className="w-full h-1 bg-primary-500/50 shadow-[0_0_20px_rgba(6,182,212,1)] absolute animate-[scan_2s_ease-in-out_infinite]" />
          </div>
        )}

        <div className="relative z-10 grid md:grid-cols-2 gap-8 mb-8">
          {/* Model Upload */}
          <div 
            {...modelDropzone.getRootProps()} 
            className={`flex flex-col items-center justify-center p-10 rounded-2xl border-2 transition-all duration-300 cursor-pointer group ${getDropzoneStyle(modelDropzone.isDragActive, !!modelFile)}`}
          >
            <input {...modelDropzone.getInputProps()} />
            <div className={`p-4 rounded-xl mb-6 transition-transform duration-500 group-hover:-translate-y-2 ${modelFile ? 'bg-success-500/20 text-success-400' : 'bg-dark-800 text-dark-300 shadow-inner border border-white/5'}`}>
              <Cpu className="w-8 h-8" />
            </div>
            <div className={`text-lg font-bold mb-2 text-center transition-colors ${modelFile ? 'text-success-100' : 'text-white'}`}>
              {modelFile ? modelFile.name : 'Drop Model Weights'}
            </div>
            <div className="text-xs font-mono text-dark-400 tracking-widest uppercase">.pkl • .joblib • .onnx</div>
          </div>

          {/* Dataset Upload */}
          <div 
            {...datasetDropzone.getRootProps()} 
            className={`flex flex-col items-center justify-center p-10 rounded-2xl border-2 transition-all duration-300 cursor-pointer group ${getDropzoneStyle(datasetDropzone.isDragActive, !!datasetFile)}`}
          >
            <input {...datasetDropzone.getInputProps()} />
            <div className={`p-4 rounded-xl mb-6 transition-transform duration-500 group-hover:-translate-y-2 ${datasetFile ? 'bg-success-500/20 text-success-400' : 'bg-dark-800 text-dark-300 shadow-inner border border-white/5'}`}>
              <FileJson className="w-8 h-8" />
            </div>
            <div className={`text-lg font-bold mb-2 text-center transition-colors ${datasetFile ? 'text-success-100' : 'text-white'}`}>
              {datasetFile ? datasetFile.name : 'Drop Validation Data'}
            </div>
            <div className="text-xs font-mono text-dark-400 tracking-widest uppercase">.csv • .json • .parquet</div>
          </div>
        </div>

        <button
          onClick={handleScan}
          disabled={!modelFile || !datasetFile || scanning}
          className={`w-full py-5 rounded-xl font-black text-sm uppercase tracking-[0.2em] transition-all duration-500 flex items-center justify-center gap-3 relative overflow-hidden group ${
            modelFile && datasetFile && !scanning
              ? 'bg-white text-dark-950 hover:bg-primary-50 shadow-[0_0_30px_rgba(255,255,255,0.2)] hover:shadow-[0_0_40px_rgba(6,182,212,0.4)] hover:scale-[1.02]' 
              : 'bg-dark-900 text-dark-600 cursor-not-allowed border border-white/5'
          }`}
        >
          {modelFile && datasetFile && !scanning && (
            <div className="absolute inset-0 w-full h-full bg-gradient-to-r from-transparent via-primary-500/20 to-transparent -translate-x-full group-hover:animate-[shimmer_1.5s_infinite]" />
          )}
          
          {scanning ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              Initializing Pipeline...
            </>
          ) : (
            <>
              <UploadCloud className="w-5 h-5" />
              Execute Analysis
            </>
          )}
        </button>

        {error && (
          <div className="mt-6 p-4 bg-danger-500/10 border border-danger-500/30 rounded-xl flex items-center gap-3 text-danger-400 animate-in slide-in-from-top-2">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <p className="text-sm font-bold tracking-wide">{error}</p>
          </div>
        )}
      </div>
    </div>
  );
}

