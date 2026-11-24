import type { Metadata } from "next";
import "@livekit/components-styles";
import "./globals.css";
export const metadata: Metadata = { title: "AI SDR · Voice studio", description: "Test your AI sales assistant" };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
