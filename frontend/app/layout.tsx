import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Multi-Agent SDK Comparison",
  description: "Compare multi-agent pipelines across Claude, OpenAI, and Google ADK",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-950 text-gray-100 min-h-screen antialiased">
        <nav className="border-b border-gray-800 bg-gray-950/80 backdrop-blur-sm sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
            <a href="/" className="text-lg font-semibold tracking-tight">
              Multi-Agent SDK Comparison
            </a>
            <div className="flex gap-6 text-sm text-gray-400">
              <a href="/" className="hover:text-white transition-colors">Home</a>
              <a href="/sdk/claude" className="hover:text-white transition-colors">Claude</a>
              <a href="/sdk/openai" className="hover:text-white transition-colors">OpenAI</a>
              <a href="/sdk/google-adk" className="hover:text-white transition-colors">Google ADK</a>
            </div>
          </div>
        </nav>
        <main>{children}</main>
      </body>
    </html>
  );
}
