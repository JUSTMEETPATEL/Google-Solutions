/** PDFExport — one-click PDF download button (WEB-06). */

import { useState } from 'react';
import { generateReport } from '../api/client';
import { FileDown, Loader2 } from 'lucide-react';

interface PDFExportProps {
  sessionId: string;
}

export function PDFExport({ sessionId }: PDFExportProps) {
  const [downloading, setDownloading] = useState(false);

  const handleExport = async () => {
    setDownloading(true);
    try {
      const blob = await generateReport(sessionId, 'pdf');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `faircheck-report-${sessionId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      // Silently ignore
    } finally {
      setDownloading(false);
    }
  };

  return (
    <button
      onClick={handleExport}
      disabled={downloading}
      className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
        downloading 
          ? 'bg-dark-800 text-dark-400 cursor-not-allowed border border-white/5' 
          : 'bg-white text-dark-950 hover:bg-dark-100 hover:scale-105 shadow-xl shadow-white/10 active:scale-95'
      }`}
    >
      {downloading ? (
        <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
      ) : (
        <FileDown className="w-4 h-4" />
      )}
      {downloading ? 'Generating Report...' : 'Export Audit PDF'}
    </button>
  );
}
