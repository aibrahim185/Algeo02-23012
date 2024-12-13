"use client";

import { useEffect, useState } from "react";

export default function Lightning() {
  const [isLightning, setIsLightning] = useState(false);

  useEffect(() => {
    const triggerLightning = () => {
      setIsLightning(true);
      setTimeout(() => setIsLightning(false), 150);
      setTimeout(() => {
        setIsLightning(true);
        setTimeout(() => setIsLightning(false), 100);
      }, Math.random() * 200 + 100);
    };

    const lightningInterval = setInterval(() => {
      triggerLightning();
    }, Math.random() * 8000 + 3000);

    return () => clearInterval(lightningInterval);
  }, []);
  return (
    <div
      className={`h-full w-full  inset-0 absolute -z-50 ${
        isLightning ? "bg-white" : ""
      }`}
    ></div>
  );
}
