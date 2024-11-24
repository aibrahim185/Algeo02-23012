import type { Metadata } from "next";
import "./globals.css";

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
      <body className={`antialiased bg-[url('/bg2.png')]  backdrop-blur-sm`}>
        {children}
      </body>
    </html>
  );
}
