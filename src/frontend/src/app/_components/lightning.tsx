"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import Particles, { initParticlesEngine } from "@tsparticles/react";
import { type Container } from "@tsparticles/engine";
import { loadSlim } from "@tsparticles/slim";

export default function Lightning() {
  const [isLightning, setIsLightning] = useState(false);
  const [isBloody, setIsBloody] = useState(false);
  const [isJumpscare, setIsJumpscare] = useState(false);

  const [init, setInit] = useState(false);

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
          if (Math.random() < 1) {
            if (Math.random() < 0) {
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

  useEffect(() => {
    initParticlesEngine(async (engine) => {
      await loadSlim(engine);
    }).then(() => {
      setInit(true);
    });
  }, []);

  const particlesLoaded = async (container?: Container): Promise<void> => {
    console.log(container);
  };

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
      {init && (
        <Particles
          particlesLoaded={particlesLoaded}
          options={{
            interactivity: {
              events: {
                onClick: {
                  enable: true,
                  mode: "repulse",
                },
                onHover: {
                  enable: true,
                  mode: "repulse",
                  parallax: {
                    enable: true,
                    force: 60,
                    smooth: 10,
                  },
                },
                resize: {
                  delay: 0.5,
                  enable: true,
                },
              },
            },
            particles: {
              number: {
                value: 250,
                density: {
                  enable: true,
                },
              },
              shape: {
                type: "circle",
              },
              opacity: {
                value: 0.5,
              },
              size: {
                value: 1,
                animation: {
                  enable: true,
                  speed: 40,
                },
              },
              move: {
                enable: true,
                speed: 1.5,
                direction: "none",
                random: true,
                straight: false,
                outModes: {
                  default: "out",
                },
              },
            },
            retina_detect: true,
          }}
        />
      )}
    </div>
  );
}
