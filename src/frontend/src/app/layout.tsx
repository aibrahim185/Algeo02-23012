import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "./_components/ui/sonner";
import Lightning from "./_components/lightning";

export const metadata: Metadata = {
  title: "Ambalabu",
  description: "Jangan ke sorong~",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`antialiased bg-[url('/bg2.png')] min-h-screen backdrop-blur-sm flex flex-row`}
      >
        {children}

        <Lightning />
        <Toaster />
      </body>
    </html>
  );
}
