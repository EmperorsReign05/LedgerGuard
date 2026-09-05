import type { Metadata } from "next";
import { Inter, Source_Serif_4 } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });
const serif = Source_Serif_4({ subsets: ["latin"], variable: "--font-serif" });

export const metadata: Metadata = {
  title: "LedgerGuard",
  description: "AI-Powered Reconciliation Engine",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${serif.variable} font-sans bg-cream-50 text-forest-900 flex`}>
        <Sidebar />
        <main className="flex-1 min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
