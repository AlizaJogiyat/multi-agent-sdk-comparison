"use client";

import { useEffect, useRef } from "react";

export interface TerminalLine {
  type: string;
  text: string;
}

export default function TerminalOutput({ lines }: { lines: TerminalLine[] }) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [lines]);

  const getLineStyle = (type: string) => {
    switch (type) {
      case "agent_start":
        return "text-yellow-400 font-bold text-base mt-3";
      case "pipeline_start":
        return "text-cyan-400 font-bold text-base";
      case "pipeline_complete":
        return "text-green-400 font-bold text-base mt-3";
      case "iteration":
        return "text-gray-400 text-sm";
      case "tool_call":
        return "text-purple-400 text-sm";
      case "tool_result":
        return "text-gray-500 text-sm";
      case "agent_text":
        return "text-gray-200 text-sm";
      case "agent_complete":
        return "text-green-300 text-sm mt-1";
      case "agent_output":
        return "text-white text-sm mt-2 mb-2";
      case "error":
        return "text-red-400 font-bold";
      default:
        return "text-gray-300 text-sm";
    }
  };

  return (
    <div className="bg-gray-950 border border-gray-800 rounded-xl p-4 font-mono text-sm max-h-[600px] overflow-y-auto">
      {lines.length === 0 ? (
        <p className="text-gray-600 italic">Waiting for output...</p>
      ) : (
        lines.map((line, i) => (
          <div key={i} className={getLineStyle(line.type)}>
            <pre className="whitespace-pre-wrap break-words">{line.text}</pre>
          </div>
        ))
      )}
      <div ref={bottomRef} />
    </div>
  );
}
