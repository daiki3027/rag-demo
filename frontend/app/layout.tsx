import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "RAG v0",
  description: "Minimal RAG prototype",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body className="app-body">
        <main className="app-shell">{children}</main>
      </body>
    </html>
  );
}
