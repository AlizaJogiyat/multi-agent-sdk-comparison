"use client";

import { useState, useCallback } from "react";
import jsPDF from "jspdf";
import TerminalOutput, { TerminalLine } from "./TerminalOutput";

// Empty string = relative URL so Vercel routes /api/* to the Python serverless function.
// Set NEXT_PUBLIC_API_URL to point at a standalone backend when running outside Vercel
// (e.g. NEXT_PUBLIC_API_URL=http://localhost:8000 for local development without rewrites).
const API_URL = process.env.NEXT_PUBLIC_API_URL || "";

function parseSSEMessages(
  buffer: string,
  onEvent: (eventType: string, data: string) => void
): string {
  let idx = buffer.indexOf("\n\n");
  while (idx !== -1) {
    const message = buffer.slice(0, idx);
    buffer = buffer.slice(idx + 2);

    let eventType = "";
    let data = "";
    for (const line of message.split("\n")) {
      if (line.startsWith(":")) continue;
      if (line.startsWith("event:")) eventType = line.slice(6).trim();
      else if (line.startsWith("data:")) data = line.slice(5).trim();
    }

    if (data) {
      onEvent(eventType, data);
    }

    idx = buffer.indexOf("\n\n");
  }
  return buffer;
}

interface FinalResults {
  research: string;
  analysis: string;
  memo: string;
  qa_review: string;
}

function generatePDF(companyName: string, results: FinalResults) {
  const doc = new jsPDF();
  const pageWidth = doc.internal.pageSize.getWidth();
  const margin = 20;
  const maxWidth = pageWidth - margin * 2;
  let y = 20;

  const addPageIfNeeded = (requiredSpace: number) => {
    if (y + requiredSpace > doc.internal.pageSize.getHeight() - 20) {
      doc.addPage();
      y = 20;
    }
  };

  const addTitle = (text: string) => {
    addPageIfNeeded(20);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(18);
    doc.setTextColor(30, 30, 30);
    doc.text(text, pageWidth / 2, y, { align: "center" });
    y += 10;
  };

  const addSubtitle = (text: string) => {
    addPageIfNeeded(15);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(10);
    doc.setTextColor(100, 100, 100);
    doc.text(text, pageWidth / 2, y, { align: "center" });
    y += 8;
  };

  const addDivider = () => {
    addPageIfNeeded(8);
    doc.setDrawColor(200, 200, 200);
    doc.line(margin, y, pageWidth - margin, y);
    y += 8;
  };

  const addSectionHeader = (text: string, color: [number, number, number]) => {
    addPageIfNeeded(16);
    doc.setFont("helvetica", "bold");
    doc.setFontSize(13);
    doc.setTextColor(...color);
    doc.text(text, margin, y);
    y += 8;
  };

  const addBody = (text: string) => {
    doc.setFont("helvetica", "normal");
    doc.setFontSize(9);
    doc.setTextColor(50, 50, 50);

    const lines = doc.splitTextToSize(text, maxWidth);
    for (const line of lines) {
      addPageIfNeeded(5);
      doc.text(line, margin, y);
      y += 4.5;
    }
    y += 4;
  };

  // ── Header ──
  addTitle(`Investment Report: ${companyName}`);
  addSubtitle(`Generated on ${new Date().toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}`);
  addSubtitle("AI Investment Research Pipeline — Multi-Agent SDK Comparison");
  y += 4;
  addDivider();

  // ── Section 1: Research ──
  if (results.research) {
    addSectionHeader("Agent 1: Researcher", [180, 130, 20]);
    addBody(results.research);
    addDivider();
  }

  // ── Section 2: Analysis ──
  if (results.analysis) {
    addSectionHeader("Agent 2: Analyzer", [120, 60, 180]);
    addBody(results.analysis);
    addDivider();
  }

  // ── Section 3: Investment Memo ──
  if (results.memo) {
    addSectionHeader("Agent 3: Writer — Investment Memo", [30, 140, 60]);
    addBody(results.memo);
    addDivider();
  }

  // ── Section 4: QA Review ──
  if (results.qa_review) {
    addSectionHeader("Agent 4: QA / Review", [200, 60, 60]);
    addBody(results.qa_review);
  }

  // ── Footer on each page ──
  const totalPages = doc.getNumberOfPages();
  for (let i = 1; i <= totalPages; i++) {
    doc.setPage(i);
    doc.setFont("helvetica", "normal");
    doc.setFontSize(8);
    doc.setTextColor(150, 150, 150);
    doc.text(
      `CONFIDENTIAL — Page ${i} of ${totalPages}`,
      pageWidth / 2,
      doc.internal.pageSize.getHeight() - 10,
      { align: "center" }
    );
  }

  doc.save(`${companyName.replace(/\s+/g, "_")}_Investment_Report.pdf`);
}

export default function TestNowForm({ slug }: { slug: string }) {
  const [companyName, setCompanyName] = useState("");
  const [lines, setLines] = useState<TerminalLine[]>([]);
  const [running, setRunning] = useState(false);
  const [finalResults, setFinalResults] = useState<FinalResults | null>(null);

  const addLine = useCallback((type: string, text: string) => {
    setLines((prev) => [...prev, { type, text }]);
  }, []);

  const handleRun = async () => {
    if (!companyName.trim() || running) return;

    setRunning(true);
    setLines([]);
    setFinalResults(null);

    try {
      const response = await fetch(`${API_URL}/api/run/${slug}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "text/event-stream",
        },
        body: JSON.stringify({ company_name: companyName.trim() }),
      });

      if (!response.ok) {
        addLine("error", `Error: ${response.status} ${response.statusText}`);
        setRunning(false);
        return;
      }

      const reader = response.body!.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      const handleEvent = (eventType: string, data: string) => {
        try {
          const parsed = JSON.parse(data);
          const type = eventType || parsed.type || "info";
          const text = parsed.message || parsed.text || "";

          if (type === "pipeline_complete") {
            setFinalResults({
              research: parsed.research || "",
              analysis: parsed.analysis || "",
              memo: parsed.memo || "",
              qa_review: parsed.qa_review || "",
            });
          }

          if (text) {
            addLine(type, text);
          }
        } catch {
          addLine("info", data);
        }
      };

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        buffer = parseSSEMessages(buffer, handleEvent);
      }

      if (buffer.trim()) {
        buffer += "\n\n";
        parseSSEMessages(buffer, handleEvent);
      }
    } catch (err) {
      addLine(
        "error",
        `Connection error: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex gap-3">
        <input
          type="text"
          placeholder="Enter company name (e.g. Stripe, Tesla)"
          value={companyName}
          onChange={(e) => setCompanyName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleRun()}
          disabled={running}
          className="flex-1 bg-gray-900 border border-gray-700 rounded-lg px-4 py-2.5 text-white placeholder-gray-500 focus:outline-none focus:border-gray-500 disabled:opacity-50"
        />
        <button
          onClick={handleRun}
          disabled={running || !companyName.trim()}
          className="px-6 py-2.5 bg-amber-600 hover:bg-amber-500 disabled:bg-gray-700 disabled:text-gray-500 text-white font-medium rounded-lg transition-colors whitespace-nowrap"
        >
          {running ? "Running..." : "Test Now"}
        </button>
      </div>

      {/* Live streaming output */}
      {(lines.length > 0 || running) && (
        <div>
          <h3 className="text-sm font-medium text-gray-400 mb-2">
            Live Agent Output
          </h3>
          <TerminalOutput lines={lines} />
        </div>
      )}

      {/* Final results cards */}
      {finalResults && (
        <div className="space-y-4 mt-6">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-white">Final Results</h3>
            <button
              onClick={() => generatePDF(companyName, finalResults)}
              className="flex items-center gap-2 px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition-colors"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="7 10 12 15 17 10" />
                <line x1="12" y1="15" x2="12" y2="3" />
              </svg>
              Download Report
            </button>
          </div>

          {finalResults.research && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h4 className="text-sm font-semibold text-yellow-400 mb-2">
                Agent 1: Researcher
              </h4>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words">
                {finalResults.research}
              </pre>
            </div>
          )}

          {finalResults.analysis && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h4 className="text-sm font-semibold text-purple-400 mb-2">
                Agent 2: Analyzer
              </h4>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words">
                {finalResults.analysis}
              </pre>
            </div>
          )}

          {finalResults.memo && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h4 className="text-sm font-semibold text-green-400 mb-2">
                Agent 3: Writer — Investment Memo
              </h4>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words">
                {finalResults.memo}
              </pre>
            </div>
          )}

          {finalResults.qa_review && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
              <h4 className="text-sm font-semibold text-red-400 mb-2">
                Agent 4: QA / Review
              </h4>
              <pre className="text-sm text-gray-300 whitespace-pre-wrap break-words">
                {finalResults.qa_review}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
