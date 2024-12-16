"use client";

import { useEffect, useState } from "react";
import Image from "next/image";

export default function Lightning() {
  const [isLightning, setIsLightning] = useState(false);
  const [isBloody, setIsBloody] = useState(false);
  const [isJumpscare, setIsJumpscare] = useState(false);

  useEffect(() => {
    const triggerLightning = () => {
      setIsBloody(false);
      setIsJumpscare(false);
      setIsLightning(true);
      setTimeout(() => setIsLightning(false), 150);
      setTimeout(() => {
        setIsLightning(true);
        setTimeout(() => {
          setIsLightning(false);
          if (Math.random() < 0.1) {
            if (Math.random() < 0.5) {
              setIsBloody(true);
            } else {
              setIsJumpscare(true);
            }
          }
        }, 100);
      }, Math.random() * 200 + 100);
    };

    const lightningInterval = setInterval(() => {
      triggerLightning();
    }, Math.random() * 7000 + 3000);

    return () => clearInterval(lightningInterval);
  }, []);
  return (
    <div
      className={`size-full inset-0 absolute -z-50 ${
        isLightning ? "bg-white" : ""
      }`}
    >
      {isBloody && (
        <div className="size-full inset-0 absolute bg-[url('/blood.png')]"></div>
      )}
      {isJumpscare && (
        <Image
          src="/placeholder.png"
          width={200}
          height={200}
          alt="jumpscare"
          className="w-1/2 h-full inset-0 absolute animate-pulse"
        />
      )}
    </div>
  );
}
