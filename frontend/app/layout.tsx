import type { Metadata } from "next";
import { Inter as FontSans } from "next/font/google"
import "./globals.css";

import { cn } from "@/lib/utils"
import { ThemeProvider } from "@/components/theme-provider";
import { Header } from "@/components/header"; // Headerをインポート

const fontSans = FontSans({
  subsets: ["latin"],
  variable: "--font-sans",
})

export const metadata: Metadata = {
  title: "AgentHub",
  description: "Create and manage your AI agents",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={cn(
          "min-h-screen bg-background font-sans antialiased",
          fontSans.variable
        )}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          <Header /> {/* ここにHeaderを追加 */}
          <main>{children}</main> {/* childrenをmainタグで囲む */}
        </ThemeProvider>
      </body>
    </html>
  );
}

