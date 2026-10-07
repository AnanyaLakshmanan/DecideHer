import React, { useState } from 'react';
import { X, Copy, Check, Download, Printer, FileCode, Sparkles } from 'lucide-react';
import { INITIATIVE_CLUSTERS, DEPARTMENT_DATA, PORTFOLIO_METRICS } from '../data/dashboardData';
import { DecideHerLogo } from './DecideHerLogo';

interface ExportSummaryModalProps {
  isOpen: boolean;
  onClose: () => void;
  onTriggerPrint?: () => void;
}

export const ExportSummaryModal: React.FC<ExportSummaryModalProps> = ({
  isOpen,
  onClose,
  onTriggerPrint,
}) => {
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const generateMarkdownSummary = () => {
    return `# DecideHer Executive Summary: AI Investment Portfolio
Generated from the live DecideHer pipeline
Framework: DecideHer — From ideas to impact

## 1. High-Level Portfolio Metrics
- Total Improvement Reports: ${PORTFOLIO_METRICS.reports} across ${PORTFOLIO_METRICS.departments} departments
- AI Opportunities: ${PORTFOLIO_METRICS.opportunities} consolidated initiative themes
- Cross-Departmental Scope: ${PORTFOLIO_METRICS.crossFunctional} initiatives span 3+ departments
- Existing System Candidates: ${PORTFOLIO_METRICS.existingSystems} initiatives
- Requiring Further Evidence: ${PORTFOLIO_METRICS.needEvidence} initiatives

## 2. Key Bottleneck Finding (Blocker Analysis)
- Primary Blocker: ${PORTFOLIO_METRICS.primaryBlocker.count} reports (${PORTFOLIO_METRICS.primaryBlocker.percentage}%) cite "${PORTFOLIO_METRICS.primaryBlocker.blocker}".

## 3. Recommended Investment Portfolio
${INITIATIVE_CLUSTERS.map(
  (c) =>
    `${c.id}. ${c.name}
   - Departments: ${c.departments.join(', ')} (${c.useCasesCount} use cases)
   - Impact: ${c.impact} | Readiness: ${c.readiness} | Evidence: ${c.evidence}
   - Span 3+ Depts: ${c.spans3PlusDepts ? 'Yes' : 'No'}
   - Primary Blocker: ${c.primaryBlocker}
   - Finding: ${c.findingText}`
).join('\n\n')}

## 4. Ideas By Department Breakdown
${DEPARTMENT_DATA.map((d) => `- ${d.name}: ${d.count} use cases (${d.percentage}%)`).join('\n')}
`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateMarkdownSummary());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadMarkdown = () => {
    const text = generateMarkdownSummary();
    const blob = new Blob([text], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'DecideHer-1Page-Executive-Summary.md';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Generate a standalone 1-page HTML document
  const handleDownloadStandaloneHTML = () => {
    const htmlContent = `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>DecideHer - 1-Page AI Investment Dashboard Summary</title>
  <style>
    @page { size: landscape; margin: 8mm; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #fff; color: #1c1917; font-size: 11px; line-height: 1.35; padding: 12px; }
    .header { display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #700E22; padding-bottom: 10px; margin-bottom: 12px; }
    .logo-text { font-size: 20px; font-weight: 800; color: #700E22; }
    .logo-text span { color: #EA580C; }
    .title { font-size: 16px; font-weight: 800; color: #1c1917; }
    .subtitle { font-size: 11px; color: #57534e; }
    .metrics { display: grid; grid-template-columns: repeat(5, 1fr); gap: 8px; margin-bottom: 12px; }
    .metric-card { border: 1px solid #e7e5e4; border-radius: 8px; padding: 8px 10px; background: #fafaf9; }
    .metric-value { font-size: 20px; font-weight: 900; color: #700E22; }
    .metric-title { font-size: 11px; font-weight: 700; color: #292524; }
    .content-grid { display: grid; grid-template-columns: 3fr 2fr; gap: 12px; }
    table { width: 100%; border-collapse: collapse; font-size: 10.5px; }
    th { background: #f5f5f4; text-align: left; padding: 6px 8px; border-bottom: 1px solid #d6d3d1; font-weight: 700; color: #44403c; }
    td { padding: 5px 8px; border-bottom: 1px solid #f5f5f4; }
    .badge { display: inline-block; padding: 2px 6px; border-radius: 4px; font-weight: 700; font-size: 9.5px; text-align: center; }
    .badge-high { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .badge-medium { background: #fef3c7; color: #b45309; border: 1px solid #fde68a; }
    .badge-low { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }
    .dept-pill { display: inline-block; padding: 1px 4px; border-radius: 3px; font-size: 9px; background: #f5f5f4; color: #44403c; margin: 1px; }
    .blocker-box { border: 1px solid #fecaca; background: #fff5f5; border-radius: 8px; padding: 10px; margin-top: 10px; }
    .blocker-title { font-weight: 800; color: #991b1b; font-size: 11px; margin-bottom: 4px; }
    .footer { margin-top: 10px; border-top: 1px solid #e7e5e4; padding-top: 6px; font-size: 9px; color: #78716c; text-align: right; }
  </style>
</head>
<body>
  <div class="header">
    <div>
      <div class="logo-text">Decide<span>Her</span></div>
      <div class="subtitle">From ideas to impact • AI Investment Intelligence</div>
    </div>
    <div style="text-align: right;">
      <div class="title">Turn employee ideas into smart AI investments</div>
      <div class="subtitle">${PORTFOLIO_METRICS.reports} Verified Input Reports</div>
    </div>
  </div>

  <div class="metrics">
    <div class="metric-card">
      <div class="metric-value">${PORTFOLIO_METRICS.reports}</div>
      <div class="metric-title">Improvement reports</div>
      <div class="subtitle">from ${PORTFOLIO_METRICS.departments} departments</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${PORTFOLIO_METRICS.opportunities}</div>
      <div class="metric-title">AI opportunities</div>
      <div class="subtitle">consolidated themes</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${PORTFOLIO_METRICS.crossFunctional}</div>
      <div class="metric-title">Span 3+ departments</div>
      <div class="subtitle">cross-functional clusters</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${PORTFOLIO_METRICS.existingSystems}</div>
      <div class="metric-title">May use existing systems</div>
      <div class="subtitle">e.g. CRM, ERP, M365</div>
    </div>
    <div class="metric-card">
      <div class="metric-value">${PORTFOLIO_METRICS.needEvidence}</div>
      <div class="metric-title">Need more evidence</div>
      <div class="subtitle">investigate next</div>
    </div>
  </div>

  <div class="content-grid">
    <div>
      <div style="font-weight: 800; margin-bottom: 6px; color: #1c1917;">Recommended Investment Portfolio</div>
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Initiative / Theme</th>
            <th>Departments</th>
            <th style="text-align:center;"># Cases</th>
            <th style="text-align:center;">Impact</th>
            <th style="text-align:center;">Readiness</th>
            <th style="text-align:center;">Evidence</th>
          </tr>
        </thead>
        <tbody>
          ${INITIATIVE_CLUSTERS.map(
            (c) => `
            <tr>
              <td><strong>${c.id}</strong></td>
              <td><strong>${c.name}</strong></td>
              <td>${c.departments.map((d) => `<span class="dept-pill">${d}</span>`).join(' ')}</td>
              <td style="text-align:center;"><strong>${c.useCasesCount}</strong></td>
              <td style="text-align:center;"><span class="badge badge-${c.impact.toLowerCase()}">${c.impact}</span></td>
              <td style="text-align:center;"><span class="badge badge-${c.readiness.toLowerCase()}">${c.readiness}</span></td>
              <td style="text-align:center;"><span class="badge badge-${c.evidence.toLowerCase()}">${c.evidence}</span></td>
            </tr>`
          ).join('')}
        </tbody>
      </table>
    </div>

    <div>
      <div style="font-weight: 800; margin-bottom: 6px; color: #1c1917;">Ideas by Department</div>
      <table>
        <thead>
          <tr>
            <th>Department</th>
            <th style="text-align:right;">Use Cases</th>
            <th style="text-align:right;">Share</th>
          </tr>
        </thead>
        <tbody>
          ${DEPARTMENT_DATA.map(
            (d) => `
            <tr>
              <td><span style="display:inline-block; width:8px; height:8px; border-radius:50%; background:${d.color}; margin-right:5px;"></span>${d.name}</td>
              <td style="text-align:right;"><strong>${d.count}</strong></td>
              <td style="text-align:right;">${d.percentage}%</td>
            </tr>`
          ).join('')}
        </tbody>
      </table>

      <div class="blocker-box">
        <div class="blocker-title">Primary Blocker: ${PORTFOLIO_METRICS.primaryBlocker.count} reports cite "${PORTFOLIO_METRICS.primaryBlocker.blocker}"</div>
        <p style="font-size: 10px; color: #44403c; line-height: 1.4;">
          In <strong>${PORTFOLIO_METRICS.primaryBlocker.percentage}% of submissions</strong>, this was the leading reported blocker. Validate ownership and evidence before selecting technology.
        </p>
        <div style="margin-top: 6px; font-size: 9.5px; color: #78716c;">
          Findings are calculated from the current intake records.
        </div>
      </div>
    </div>
  </div>

  <div class="footer">
    DecideHer AI Investment Dashboard • Live pipeline output • Strictly formatted to 1 single page
  </div>
</body>
</html>`;

    const blob = new Blob([htmlContent], { type: 'text/html' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'DecideHer-1Page-Dashboard.html';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handlePrint1Page = () => {
    onClose();
    setTimeout(() => {
      if (onTriggerPrint) {
        onTriggerPrint();
      } else {
        window.print();
      }
    }, 150);
  };

  return (
    <div
      id="export-summary-modal-backdrop"
      className="fixed inset-0 z-50 bg-stone-900/60 backdrop-blur-xs flex items-center justify-center p-4"
      onClick={onClose}
    >
      <div
        id="export-summary-modal-container"
        className="bg-white rounded-2xl max-w-2xl w-full border border-stone-200 shadow-2xl overflow-hidden my-6"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="p-4 border-b border-[#FBE0E5] flex items-center justify-between bg-[#FFF8F6]">
          <div className="flex items-center gap-3">
            <DecideHerLogo size="sm" variant="color" />
            <div>
              <h2 className="text-sm font-bold text-stone-900">
                Download & Export 1-Page Summary
              </h2>
              <div className="text-[11px] text-stone-500">
                Formatted strictly to keep to 1 page for executive presentation
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="w-7 h-7 rounded-lg bg-white border border-stone-200 hover:bg-stone-100 flex items-center justify-center text-stone-500 hover:text-stone-800 transition-colors"
          >
            <X className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="p-5 space-y-4">
          {/* Quick 1-Page Download Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <button
              id="modal-download-pdf-btn"
              onClick={handlePrint1Page}
              className="flex items-start gap-3 p-3 rounded-xl border border-[#700E22]/30 bg-[#FDF2F4]/60 hover:bg-[#FDF2F4] text-left transition-all hover:border-[#700E22] group shadow-xs"
            >
              <div className="w-9 h-9 rounded-lg bg-[#700E22] text-white flex items-center justify-center shrink-0 shadow-xs group-hover:scale-105 transition-transform">
                <Printer className="w-4 h-4 text-[#F5A623]" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#700E22] flex items-center gap-1">
                  <span>Download 1-Page PDF / Print</span>
                </div>
                <div className="text-[11px] text-stone-600 mt-0.5">
                  Prints landscape with exact 1-page layout, charts, and colors.
                </div>
              </div>
            </button>

            <button
              id="modal-download-html-btn"
              onClick={handleDownloadStandaloneHTML}
              className="flex items-start gap-3 p-3 rounded-xl border border-[#EA580C]/30 bg-[#FFF7ED]/60 hover:bg-[#FFF7ED] text-left transition-all hover:border-[#EA580C] group shadow-xs"
            >
              <div className="w-9 h-9 rounded-lg bg-[#EA580C] text-white flex items-center justify-center shrink-0 shadow-xs group-hover:scale-105 transition-transform">
                <FileCode className="w-4 h-4" />
              </div>
              <div>
                <div className="text-xs font-bold text-[#EA580C]">
                  Download Standalone 1-Page HTML
                </div>
                <div className="text-[11px] text-stone-600 mt-0.5">
                  Self-contained HTML file viewable offline or shareable by email.
                </div>
              </div>
            </button>
          </div>

          {/* Text preview */}
          <div>
            <div className="flex items-center justify-between text-xs font-bold text-stone-700 mb-1.5">
              <span>Executive Brief Preview (Markdown)</span>
              <span className="text-[10px] text-stone-400 font-normal">
                {PORTFOLIO_METRICS.reports} reports • {PORTFOLIO_METRICS.opportunities} initiatives • {PORTFOLIO_METRICS.departments} departments
              </span>
            </div>
            <div className="bg-[#2A050E] text-stone-200 rounded-xl p-3.5 font-mono text-xs max-h-52 overflow-y-auto leading-relaxed border border-[#400B17]">
              <pre className="whitespace-pre-wrap font-sans text-xs">
                {generateMarkdownSummary()}
              </pre>
            </div>
          </div>
        </div>

        <div className="p-3.5 bg-stone-50 border-t border-stone-100 flex items-center justify-between">
          <button
            onClick={handleCopy}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-stone-300 bg-white text-xs font-semibold text-stone-700 hover:bg-stone-100 transition-colors"
          >
            {copied ? (
              <>
                <Check className="w-3.5 h-3.5 text-emerald-600" />
                <span className="text-emerald-700 font-bold">Copied!</span>
              </>
            ) : (
              <>
                <Copy className="w-3.5 h-3.5 text-stone-500" />
                <span>Copy markdown</span>
              </>
            )}
          </button>

          <div className="flex items-center gap-2">
            <button
              onClick={handleDownloadMarkdown}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[#700E22] bg-white text-[#700E22] hover:bg-[#FDF2F4] text-xs font-bold transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Download .md</span>
            </button>
            <button
              onClick={onClose}
              className="px-3 py-1.5 rounded-lg text-xs font-medium text-stone-600 hover:text-stone-900 transition-colors"
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
