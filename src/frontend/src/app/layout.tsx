import type { Metadata } from "next";
import "./globals.css";
import { Toaster } from "./_components/ui/sonner";
import Lightning from "./_components/lightning";
import localfont from "next/font/local";

export const metadata: Metadata = {
  title: "Ambalabu",
  description: "Jangan ke sorong~",
};

const deadfall = localfont({
  src: "../../public/fonts/Deadfall-Regular.ttf",
  variable: "--deadfall",
});

const was = localfont({
  src: "../../public/fonts/who-asks-satan.ttf",
  variable: "--was",
});

const bloody = localfont({
  src: "../../public/fonts/BLOODY.ttf",
  variable: "--bloody",
});

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`antialiased bg-[url('/bg.png')] min-h-screen backdrop-blur-sm flex flex-row 
          ${deadfall.variable} ${was.variable} ${bloody.variable}`}
      >
        {children}

        <Lightning />
        <Toaster position="bottom-center" />
      </body>
    </html>
  );
}
