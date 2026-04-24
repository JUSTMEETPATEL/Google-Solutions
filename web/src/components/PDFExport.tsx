/** PDFExport — one-click PDF download button (WEB-06). */

import { useState } from "react";
import { Loader2, Lock, FileText, Image as ImageIcon } from "lucide-react";
import { useAppStore } from "../store/appStore";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";
import { toJpeg } from "html-to-image";
import { createRoot } from "react-dom/client";
import { PrintReport } from "./PrintReport";

interface PDFExportProps {
  sessionId: string;
  sessionData?: any;
}

export function PDFExport({ sessionId, sessionData }: PDFExportProps) {
  const [downloadingVisual, setDownloadingVisual] = useState(false);
  const [downloadingFormal, setDownloadingFormal] = useState(false);

  const {
    oversightApproved,
    oversightReviewer,
    oversightDecision,
    oversightDate,
    currentScanResult,
    regulation,
  } = useAppStore();

  const handleExportFormal = () => {
    if (!oversightApproved) return;
    setDownloadingFormal(true);

    try {
      const doc = new jsPDF();
      const session = sessionData || currentScanResult;

      // Header
      doc.setFont("helvetica", "bold");
      doc.setFontSize(22);
      doc.text("FAIRCHECK COMPLIANCE AUDIT REPORT", 14, 20);

      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      doc.text(`Audit ID: ${sessionId.toUpperCase()}`, 14, 28);
      doc.text(`Date Generated: ${new Date().toLocaleString()}`, 14, 33);
      doc.text(
        `Regulation Framework: ${(regulation || "STANDARD").toUpperCase()}`,
        14,
        38,
      );

      doc.setDrawColor(200, 200, 200);
      doc.line(14, 43, 196, 43);

      // 1. Model Identification
      const modelName = session?.model_name || "Unknown Model";
      const riskLevel =
        session?.analysis_results?.overall_risk_level || "UNKNOWN";

      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.text("1. Model Identification", 14, 53);

      doc.setFontSize(11);
      doc.setFont("helvetica", "normal");
      doc.text(`Target Model: ${modelName}`, 14, 61);
      doc.text(
        `Overall Computed Risk Level: ${riskLevel.toUpperCase()}`,
        14,
        68,
      );

      // 2. Fairness Metrics Analysis
      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.text("2. Fairness Metrics Analysis", 14, 83);

      const tableData: any[] = [];
      const results = session?.analysis_results?.results || {};

      for (const [attr, attrData] of Object.entries(results)) {
        const metrics = (attrData as any).metrics || {};
        for (const [mName, mData] of Object.entries(metrics)) {
          tableData.push([
            attr.toUpperCase(),
            mName.replace(/_/g, " ").toUpperCase(),
            typeof (mData as any).value === "number"
              ? ((mData as any).value as number).toFixed(4)
              : (mData as any).value,
            ((mData as any).status || "UNKNOWN").toUpperCase(),
          ]);
        }
      }

      if (tableData.length === 0)
        tableData.push(["N/A", "No metrics found", "-", "-"]);

      autoTable(doc, {
        startY: 88,
        head: [["Protected Attribute", "Metric", "Score", "Status"]],
        body: tableData,
        theme: "grid",
        headStyles: { fillColor: [10, 10, 10], textColor: 255 },
        styles: { fontSize: 9, cellPadding: 4 },
        columnStyles: { 3: { fontStyle: "bold" } },
        didParseCell: function (data) {
          if (data.section === "body" && data.column.index === 3) {
            const status = data.cell.raw as string;
            if (status === "PASS") data.cell.styles.textColor = [5, 150, 105];
            else if (status === "FAIL")
              data.cell.styles.textColor = [225, 29, 72];
            else if (status === "WARNING")
              data.cell.styles.textColor = [217, 119, 6];
          }
        },
      });

      let finalY = (doc as any).lastAutoTable.finalY + 15;

      // 3. Plain-English Explanations
      const explanations = session?.explanations;
      if (explanations && Object.keys(explanations).length > 0) {
        if (finalY > 250) {
          doc.addPage();
          finalY = 20;
        }
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("3. Metric Explanations", 14, finalY);

        const expData: any[] = [];
        for (const [attr, metrics] of Object.entries(explanations)) {
          for (const [mName, exp] of Object.entries((metrics || {}) as any)) {
            expData.push([
              attr.toUpperCase(),
              mName.replace(/_/g, " ").toUpperCase(),
              (exp as any).summary || "",
              (exp as any).recommendation || "",
              ((exp as any).severity || "UNKNOWN").toUpperCase(),
            ]);
          }
        }

        autoTable(doc, {
          startY: finalY + 5,
          head: [
            ["Attribute", "Metric", "Summary", "Recommendation", "Severity"],
          ],
          body: expData,
          theme: "grid",
          headStyles: { fillColor: [10, 10, 10], textColor: 255 },
          styles: { fontSize: 8, cellPadding: 3 },
          columnStyles: { 4: { fontStyle: "bold" } },
          didParseCell: function (data) {
            if (data.section === "body" && data.column.index === 4) {
              const status = data.cell.raw as string;
              if (status === "PASS") data.cell.styles.textColor = [5, 150, 105];
              else if (status === "FAIL")
                data.cell.styles.textColor = [225, 29, 72];
              else if (status === "WARNING")
                data.cell.styles.textColor = [217, 119, 6];
            }
          },
        });
        finalY = (doc as any).lastAutoTable.finalY + 15;
      }

      // 4. Intersectional Analysis
      const intersectional = session?.intersectional_analysis;
      if (
        intersectional &&
        intersectional.intersections &&
        intersectional.intersections.length > 0
      ) {
        if (finalY > 250) {
          doc.addPage();
          finalY = 20;
        }
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("4. Intersectional Analysis", 14, finalY);

        if (intersectional.most_disadvantaged) {
          doc.setFontSize(10);
          doc.setFont("helvetica", "normal");
          doc.text(
            `Most Disadvantaged Group: ${intersectional.most_disadvantaged.group} (${intersectional.most_disadvantaged.intersection})`,
            14,
            finalY + 8,
          );
          doc.text(
            `Predicted Positive Rate: ${(intersectional.most_disadvantaged.predicted_positive_rate * 100).toFixed(1)}% (n=${intersectional.most_disadvantaged.count})`,
            14,
            finalY + 13,
          );
          finalY += 18;
        } else {
          finalY += 5;
        }

        const intData: any[] = [];
        intersectional.intersections.forEach((int: any) => {
          Object.entries(int.metrics || {}).forEach(
            ([mName, mData]: [string, any]) => {
              intData.push([
                (int.intersection || "UNKNOWN").toUpperCase(),
                (mName || "").replace(/_/g, " ").toUpperCase(),
                mData?.value != null ? mData.value.toFixed(4) : "N/A",
                (mData?.status || "UNKNOWN").toUpperCase(),
              ]);
            },
          );
        });

        autoTable(doc, {
          startY: finalY,
          head: [["Intersection", "Metric", "Score", "Status"]],
          body: intData,
          theme: "grid",
          headStyles: { fillColor: [10, 10, 10], textColor: 255 },
          styles: { fontSize: 8, cellPadding: 3 },
        });
        finalY = (doc as any).lastAutoTable.finalY + 15;
      }

      // 5. Feature Attribution (Bias Drivers)
      const attribution = session?.feature_attribution;
      if (
        attribution &&
        attribution.bias_drivers &&
        attribution.bias_drivers.length > 0
      ) {
        if (finalY > 250) {
          doc.addPage();
          finalY = 20;
        }
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("5. Feature Attribution & Bias Drivers", 14, finalY);

        const driverData = attribution.bias_drivers.map((d: any) => [
          d.feature,
          `${(d.importance_spread * 100).toFixed(1)}%`,
          d.explanation,
        ]);

        autoTable(doc, {
          startY: finalY + 5,
          head: [["Feature", "Spread", "Explanation"]],
          body: driverData,
          theme: "grid",
          headStyles: { fillColor: [10, 10, 10], textColor: 255 },
          styles: { fontSize: 8, cellPadding: 3 },
        });
        finalY = (doc as any).lastAutoTable.finalY + 15;
      }

      // 6. Mitigation Recommendations
      const recs = session?.recommendations;
      if (recs && recs.length > 0) {
        if (finalY > 250) {
          doc.addPage();
          finalY = 20;
        }
        doc.setFontSize(14);
        doc.setFont("helvetica", "bold");
        doc.text("6. Mitigation Recommendations", 14, finalY);

        const recData = recs.map((r: any) => [
          r.algorithm || "Unknown",
          (r.category || "N/A").toUpperCase(),
          (r.confidence || "N/A").toUpperCase(),
          (r.priority ?? "N/A").toString(),
        ]);

        autoTable(doc, {
          startY: finalY + 5,
          head: [["Algorithm", "Category", "Confidence", "Priority"]],
          body: recData,
          theme: "grid",
          headStyles: { fillColor: [10, 10, 10], textColor: 255 },
          styles: { fontSize: 8, cellPadding: 3 },
        });
        finalY = (doc as any).lastAutoTable.finalY + 15;
      }

      // 7. Human Oversight
      if (finalY > 250) {
        doc.addPage();
        finalY = 20;
      }

      doc.setFontSize(14);
      doc.setFont("helvetica", "bold");
      doc.text("7. Human Oversight & Sign-off", 14, finalY);

      doc.setFontSize(11);
      doc.setFont("helvetica", "normal");
      doc.text(`Reviewer Name: ${oversightReviewer || "N/A"}`, 14, finalY + 10);
      doc.text(
        `Decision: ${(oversightDecision || "N/A").toUpperCase()}`,
        14,
        finalY + 17,
      );
      doc.text(`Review Date: ${oversightDate || "N/A"}`, 14, finalY + 24);

      doc.line(14, finalY + 45, 80, finalY + 45);
      doc.setFontSize(9);
      doc.text("Authorized Signature", 14, finalY + 50);

      // Download using explicit Blob and anchor tag to force filename
      const blob = doc.output("blob");
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.style.display = "none";
      a.href = url;
      a.download = `faircheck-report-formal-${sessionId || "audit"}.pdf`;
      document.body.appendChild(a);
      a.click();

      setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      }, 1000);
    } catch (e: any) {
      console.error("Formal PDF Generation failed", e);
      alert("PDF Error: " + (e.message || e));
    } finally {
      setDownloadingFormal(false);
    }
  };

  const handleExportVisual = () => {
    if (!oversightApproved) return;
    setDownloadingVisual(true);

    try {
      const session = sessionData || currentScanResult;
      if (!session) {
        setDownloadingVisual(false);
        return;
      }

      // 1. Create a temporary container for the print view
      const container = document.createElement("div");
      container.style.position = "absolute";
      container.style.top = "0";
      container.style.left = "0";
      container.style.width = "1200px";
      container.style.zIndex = "-9999";
      container.style.opacity = "0.01"; // Force browser to fully render it
      container.style.pointerEvents = "none";
      document.body.appendChild(container);

      // 2. Render the full dashboard to the container
      const root = createRoot(container);
      root.render(
        <PrintReport
          session={session}
          regulation={regulation}
          oversightReviewer={oversightReviewer}
          oversightDecision={oversightDecision}
          oversightDate={oversightDate}
        />,
      );

      // 3. Wait for Recharts animations to finish (usually ~1500ms)
      setTimeout(async () => {
        try {
          const printElement = document.getElementById("print-report");
          if (!printElement) throw new Error("Print container not found");

          // 4. Capture the DOM as a high-res image (html-to-image handles oklab/oklch colors natively)
          const imgData = await toJpeg(printElement, {
            quality: 0.95,
            backgroundColor: "#09090b",
            pixelRatio: 2,
          });

          // 5. Create a PDF with custom dimensions to fit the entire image on one page
          const elWidth = printElement.offsetWidth;
          const elHeight = printElement.offsetHeight;

          const pdfWidth = 210; // A4 width in mm
          const pdfHeight = (elHeight * pdfWidth) / elWidth;

          const doc = new jsPDF({
            orientation: "portrait",
            unit: "mm",
            format: [pdfWidth, pdfHeight],
          });

          doc.addImage(imgData, "JPEG", 0, 0, pdfWidth, pdfHeight);

          // 6. Download using explicit Blob and anchor tag to force filename
          const blob = doc.output("blob");
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.style.display = "none";
          a.href = url;
          a.download = `faircheck-report-visual-${sessionId || "audit"}.pdf`;
          document.body.appendChild(a);
          a.click();

          setTimeout(() => {
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
          }, 1000);
        } catch (e: any) {
          console.error("PDF Image Generation failed", e);
          alert("PDF Image Error: " + (e.message || e));
        } finally {
          // Cleanup
          root.unmount();
          document.body.removeChild(container);
          setDownloadingVisual(false);
        }
      }, 2000); // 2 seconds delay for animations
    } catch (e: any) {
      console.error("PDF Setup failed", e);
      alert("PDF Error: " + (e.message || e));
      setDownloadingVisual(false);
    }
  };

  if (!oversightApproved) {
    return (
      <div className="flex gap-2">
        <button
          disabled
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 bg-dark-900 text-dark-500 cursor-not-allowed border border-white/5"
          title="Human oversight must be approved before PDF export"
        >
          <Lock className="w-4 h-4" />
          Export Formal PDF
        </button>
        <button
          disabled
          className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 bg-dark-900 text-dark-500 cursor-not-allowed border border-white/5"
          title="Human oversight must be approved before PDF export"
        >
          <Lock className="w-4 h-4" />
          Export Visual PDF
        </button>
      </div>
    );
  }

  return (
    <div className="flex gap-2">
      <button
        onClick={handleExportFormal}
        disabled={downloadingFormal || downloadingVisual}
        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
          downloadingFormal
            ? "bg-dark-800 text-dark-400 cursor-not-allowed border border-white/5"
            : "bg-white text-dark-950 hover:bg-dark-100 hover:scale-105 shadow-xl shadow-white/10 active:scale-95"
        }`}
      >
        {downloadingFormal ? (
          <Loader2 className="w-4 h-4 animate-spin text-primary-500" />
        ) : (
          <FileText className="w-4 h-4" />
        )}
        {downloadingFormal ? "Generating..." : "Formal PDF"}
      </button>

      <button
        onClick={handleExportVisual}
        disabled={downloadingFormal || downloadingVisual}
        className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 ${
          downloadingVisual
            ? "bg-dark-800 text-dark-400 cursor-not-allowed border border-white/5"
            : "bg-primary-600 text-white hover:bg-primary-500 hover:scale-105 shadow-xl shadow-primary-500/20 active:scale-95"
        }`}
      >
        {downloadingVisual ? (
          <Loader2 className="w-4 h-4 animate-spin text-white" />
        ) : (
          <ImageIcon className="w-4 h-4" />
        )}
        {downloadingVisual ? "Generating..." : "Visual PDF"}
      </button>
    </div>
  );
}
