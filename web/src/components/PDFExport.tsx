/** PDFExport — one-click PDF download button (WEB-06). */

import { useState } from 'react';
import { FileDown, Loader2, Lock } from 'lucide-react';
import { useAppStore } from '../store/appStore';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

interface PDFExportProps {
  sessionId: string;
}

export function PDFExport({ sessionId }: PDFExportProps) {
  const [downloading, setDownloading] = useState(false);
  const { 
    oversightApproved, 
    oversightReviewer, 
    oversightDecision, 
    oversightDate,
    currentScanResult,
    regulation
  } = useAppStore();

  const handleExport = async () => {
    if (!oversightApproved) return;
    setDownloading(true);
    
    try {
      // Create formal PDF
      const doc = new jsPDF();
      
      // Header
      doc.setFont('helvetica', 'bold');
      doc.setFontSize(22);
      doc.text('FAIRCHECK COMPLIANCE AUDIT REPORT', 14, 20);
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Audit ID: ${sessionId.toUpperCase()}`, 14, 28);
      doc.text(`Date Generated: ${new Date().toLocaleString()}`, 14, 33);
      doc.text(`Regulation Framework: ${regulation.toUpperCase()}`, 14, 38);
      
      // Divider
      doc.setDrawColor(200, 200, 200);
      doc.line(14, 43, 196, 43);
      
      // Model Info
      const modelName = currentScanResult?.model_name || 'Unknown Model';
      const riskLevel = currentScanResult?.analysis_results?.overall_risk_level || 'UNKNOWN';
      
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('1. Model Identification', 14, 53);
      
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      doc.text(`Target Model: ${modelName}`, 14, 61);
      doc.text(`Overall Computed Risk Level: ${riskLevel.toUpperCase()}`, 14, 68);
      
      // Metrics Table
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('2. Fairness Metrics Analysis', 14, 83);
      
      const tableData: any[] = [];
      const results = currentScanResult?.analysis_results?.results || {};
      
      for (const [attr, attrData] of Object.entries(results)) {
        const metrics = (attrData as any).metrics || {};
        for (const [mName, mData] of Object.entries(metrics)) {
          tableData.push([
            attr.toUpperCase(),
            mName.replace(/_/g, ' ').toUpperCase(),
            typeof (mData as any).value === 'number' ? ((mData as any).value as number).toFixed(4) : (mData as any).value,
            ((mData as any).status || 'UNKNOWN').toUpperCase()
          ]);
        }
      }
      
      if (tableData.length === 0) {
        tableData.push(['N/A', 'No metrics found', '-', '-']);
      }

      autoTable(doc, {
        startY: 88,
        head: [['Protected Attribute', 'Metric', 'Score', 'Status']],
        body: tableData,
        theme: 'grid',
        headStyles: { fillColor: [10, 10, 10], textColor: 255 },
        styles: { fontSize: 9, cellPadding: 4 },
        columnStyles: { 
          3: { fontStyle: 'bold' } 
        },
        didParseCell: function(data) {
          if (data.section === 'body' && data.column.index === 3) {
            const status = data.cell.raw as string;
            if (status === 'PASS') data.cell.styles.textColor = [5, 150, 105];
            else if (status === 'FAIL') data.cell.styles.textColor = [225, 29, 72];
            else if (status === 'WARNING') data.cell.styles.textColor = [217, 119, 6];
          }
        }
      });
      
      // Human Oversight
      const finalY = (doc as any).lastAutoTable.finalY + 15;
      
      doc.setFontSize(14);
      doc.setFont('helvetica', 'bold');
      doc.text('3. Human Oversight & Sign-off', 14, finalY);
      
      doc.setFontSize(11);
      doc.setFont('helvetica', 'normal');
      doc.text(`Reviewer Name: ${oversightReviewer || 'N/A'}`, 14, finalY + 10);
      doc.text(`Decision: ${(oversightDecision || 'N/A').toUpperCase()}`, 14, finalY + 17);
      doc.text(`Review Date: ${oversightDate || 'N/A'}`, 14, finalY + 24);
      
      // Footer signature line
      doc.line(14, finalY + 45, 80, finalY + 45);
      doc.setFontSize(9);
      doc.text('Authorized Signature', 14, finalY + 50);

      // Download via data URI to bypass blob issues entirely
      const pdfDataUri = doc.output('datauristring');
      const a = document.createElement('a');
      a.href = pdfDataUri;
      a.download = `faircheck-report-${sessionId || 'audit'}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      
    } catch (e) {
      console.error("PDF Generation failed", e);
    } finally {
      setDownloading(false);
    }
  };

  if (!oversightApproved) {
    return (
      <button
        disabled
        className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 bg-dark-900 text-dark-500 cursor-not-allowed border border-white/5"
        title="Human oversight must be approved before PDF export"
      >
        <Lock className="w-4 h-4" />
        Export Audit PDF
      </button>
    );
  }

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
