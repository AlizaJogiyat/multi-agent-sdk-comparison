import { sdks } from "@/lib/sdk-data";
import { notFound } from "next/navigation";
import TestNowForm from "@/components/TestNowForm";

export default async function SdkPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const sdk = sdks[slug];

  if (!sdk) notFound();

  return (
    <div className="max-w-4xl mx-auto px-6 py-12">
      {/* Header */}
      <div className="mb-10">
        <div className="flex items-center gap-3 mb-3">
          <span className="text-4xl">{sdk.icon}</span>
          <div>
            <h1 className="text-3xl font-bold">{sdk.name}</h1>
            <p className="text-gray-400">{sdk.tagline}</p>
          </div>
          <span
            className={`ml-auto text-xs font-medium px-2.5 py-1 rounded-full ${
              sdk.status === "active"
                ? "bg-green-900/50 text-green-400 border border-green-800"
                : "bg-gray-800 text-gray-400 border border-gray-700"
            }`}
          >
            {sdk.status === "active" ? "Live" : "Coming Soon"}
          </span>
        </div>
      </div>

      {/* How It Works */}
      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">How It Works</h2>
        <p className="text-gray-300 leading-relaxed mb-4">{sdk.description}</p>
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
          <p className="text-sm text-gray-400 font-mono">{sdk.architecture}</p>
        </div>
      </section>

      {/* Agents */}
      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">Pipeline Agents</h2>
        <div className={`grid grid-cols-1 gap-4 ${sdk.agents.length === 4 ? "sm:grid-cols-2 lg:grid-cols-4" : "sm:grid-cols-3"}`}>
          {sdk.agents.map((agent, i) => (
            <div key={agent.name} className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <div className="text-xs text-gray-500 mb-1">Agent {i + 1}</div>
              <div className="font-semibold mb-1">{agent.name}</div>
              <div className="text-sm text-gray-400">{agent.role}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="mb-10">
        <h2 className="text-xl font-semibold mb-3">Key Features</h2>
        <ul className="space-y-2">
          {sdk.features.map((f) => (
            <li key={f} className="flex items-start gap-2 text-gray-300">
              <span className="mt-1.5 w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ backgroundColor: sdk.color }} />
              {f}
            </li>
          ))}
        </ul>
      </section>

      {/* Test Now */}
      <section>
        <h2 className="text-xl font-semibold mb-3">Test Now</h2>
        {sdk.status === "active" ? (
          <TestNowForm slug={sdk.slug} />
        ) : (
          <div className="bg-gray-900 border border-gray-800 rounded-xl p-8 text-center">
            <p className="text-gray-400 text-lg mb-2">Coming Soon</p>
            <p className="text-gray-500 text-sm">
              This SDK integration is under development. Check back later.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}
