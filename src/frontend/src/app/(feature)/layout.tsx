import type { Metadata } from "next";
import Menu from "../_components/menu";
import { DataProvider } from "../_context/DataContext";

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
      <DataProvider>
        <Menu />

        <div className="flex flex-col pt-12">{children}</div>
      </DataProvider>
    </div>
  );
}
