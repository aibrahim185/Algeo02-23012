import type { Metadata } from "next";
import { Navbar } from "../_components/navbar";
import Menu from "../_components/menu";

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
    <div
      className={`antialiasedmin-h-screen backdrop-blur-sm flex flex-row px-12`}
    >
      <Menu />

      <div className="flex flex-col">
        <div className="w-full flex justify-center">
          <Navbar />
        </div>

        {children}
      </div>
    </div>
  );
}
