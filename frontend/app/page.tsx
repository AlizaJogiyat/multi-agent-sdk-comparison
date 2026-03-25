import SdkCard from "@/components/SdkCard";
import { sdkList } from "@/lib/sdk-data";

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto px-6 py-16">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-bold tracking-tight mb-4">
          Multi-Agent SDK Comparison
        </h1>
        <p className="text-lg text-gray-400 max-w-2xl mx-auto">
          Same 4-agent investment memo pipeline built with different SDKs.
          Compare how Claude, OpenAI, and Google ADK handle tool use, handoffs, and orchestration.
        </p>
        <div className="flex items-center justify-center gap-2 mt-6 text-sm text-gray-500 flex-wrap">
          <span className="px-2 py-1 rounded bg-gray-800 text-gray-300">Researcher</span>
          <span>→</span>
          <span className="px-2 py-1 rounded bg-gray-800 text-gray-300">Analyzer</span>
          <span>→</span>
          <span className="px-2 py-1 rounded bg-gray-800 text-gray-300">Writer</span>
          <span>→</span>
          <span className="px-2 py-1 rounded bg-gray-800 text-gray-300">QA/Review</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {sdkList.map((sdk) => (
          <SdkCard key={sdk.slug} sdk={sdk} />
        ))}
      </div>
    </div>
  );
}
