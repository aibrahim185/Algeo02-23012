"use client";

import { createContext, useState, ReactNode, useContext } from "react";

interface DataContextType {
  refreshKey: number;
  setRefreshKey: (key: number) => void;
  fetchUrl: string;
  setFetchUrl: (url: string) => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider = ({ children }: { children: ReactNode }) => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [fetchUrl, setFetchUrl] = useState("uploads");

  return (
    <DataContext.Provider
      value={{ refreshKey, setRefreshKey, fetchUrl, setFetchUrl }}
    >
      {children}
    </DataContext.Provider>
  );
};

export const useDataContext = () => {
  const context = useContext(DataContext);
  if (!context) {
    throw new Error("useDataContext must be used within a DataProvider");
  }
  return context;
};
