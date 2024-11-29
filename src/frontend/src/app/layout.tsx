import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "./_components/navbar";

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
        className={`antialiased bg-[url('/bg2.png')] min-h-screen backdrop-blur-sm`}
      >
        <div className="flex justify-center w-full top-6 sticky">
          <Navbar />
        </div>
        {children}
      </body>
    </html>
  );
}
