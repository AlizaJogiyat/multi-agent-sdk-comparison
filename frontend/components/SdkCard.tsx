import Link from "next/link";
import type { SDK } from "@/lib/sdk-data";

export default function SdkCard({ sdk }: { sdk: SDK }) {
  return (
    <Link href={`/sdk/${sdk.slug}`}>
      <div
        className="group relative rounded-2xl border border-gray-800 bg-gray-900 p-6 hover:border-gray-600 transition-all duration-300 hover:shadow-lg cursor-pointer h-full"
        style={{ "--accent": sdk.color } as React.CSSProperties}
      >
        <div className="flex items-center justify-between mb-4">
          <span className="text-3xl">{sdk.icon}</span>
          <span
            className={`text-xs font-medium px-2.5 py-1 rounded-full ${
              sdk.status === "active"
                ? "bg-green-900/50 text-green-400 border border-green-800"
                : "bg-gray-800 text-gray-400 border border-gray-700"
            }`}
          >
            {sdk.status === "active" ? "Live" : "Coming Soon"}
          </span>
        </div>

        <h3 className="text-xl font-semibold mb-2 group-hover:text-white transition-colors">
          {sdk.name}
        </h3>
        <p className="text-sm text-gray-400 mb-4">{sdk.tagline}</p>

        <div className="flex flex-wrap gap-1.5">
          {sdk.agents.map((agent) => (
            <span
              key={agent.name}
              className="text-xs px-2 py-0.5 rounded bg-gray-800 text-gray-300"
            >
              {agent.name}
            </span>
          ))}
        </div>

        <div className="mt-4 pt-4 border-t border-gray-800">
          <span className="text-sm font-medium group-hover:underline" style={{ color: sdk.color }}>
            View Details →
          </span>
        </div>
      </div>
    </Link>
  );
}
