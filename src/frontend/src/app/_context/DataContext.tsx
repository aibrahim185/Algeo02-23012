"use client";

import { createContext, useState, ReactNode, useContext } from "react";

interface DataContextType {
  refreshKey: number;
  setRefreshKey: (key: number) => void;
  fetchUrl: string;
  setFetchUrl: (url: string) => void;
  midiFilePath: string;
  setMidiFilePath: (path: string) => void;
  imageFilePath: string;
  setImageFilePath: (path: string) => void;
  title: string;
  setTitle: (title: string) => void;
}

const DataContext = createContext<DataContextType | undefined>(undefined);

export const DataProvider = ({ children }: { children: ReactNode }) => {
  const [refreshKey, setRefreshKey] = useState(0);
  const [fetchUrl, setFetchUrl] = useState("uploads");
  const [midiFilePath, setMidiFilePath] = useState("/midi/test1.mid");
  const [imageFilePath, setImageFilePath] = useState("/favicon.ico");
  const [title, setTitle] = useState("Test Title");

  return (
    <DataContext.Provider
      value={{
        refreshKey,
        setRefreshKey,
        fetchUrl,
        setFetchUrl,
        midiFilePath,
        setMidiFilePath,
        imageFilePath,
        setImageFilePath,
        title,
        setTitle,
      }}
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