/** PDFExport — one-click PDF download button (WEB-06). */

import { useState } from 'react';
import { generateReport } from '../api/client';

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
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 8,
        padding: '10px 16px',
        borderRadius: 8,
        border: '1px solid #334155',
        background: '#1e293b',
        color: '#f1f5f9',
        fontSize: 13,
        fontWeight: 500,
        cursor: downloading ? 'wait' : 'pointer',
        transition: 'all 0.2s',
      }}
    >
      {downloading ? '⏳' : '📄'} {downloading ? 'Generating...' : 'Export PDF'}
    </button>
  );
}
