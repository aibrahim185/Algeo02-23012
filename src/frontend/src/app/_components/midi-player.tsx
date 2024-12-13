import React, { useEffect, useRef } from "react";
import dynamic from "next/dynamic";

const MidiPlayer = dynamic(() => import("react-midi-player"), { ssr: false });

const MidiPlayerComponent: React.FC = () => {
  const midiPlayerRef = useRef<HTMLDivElement>(null);
  const midiFilePath = "/midi/test1.mid";

  useEffect(() => {
    if (midiPlayerRef.current) {
      const loopButton = midiPlayerRef.current.querySelector('[title="loop"]');
      const midiButton = midiPlayerRef.current.querySelector('[title="midi"]');

      loopButton?.remove();
      midiButton?.remove();
    }
  }, []);

  return (
    <div
      ref={midiPlayerRef}
      className="midi-player-wrapper flex justify-center"
    >
      <MidiPlayer
        src={midiFilePath}
        autoplay={false}
        loop={false}
        onStart={() => console.log("Midi started")}
        onStop={() => console.log("Midi stopped")}
        onPause={() => console.log("Midi paused")}
        onEnd={() => console.log("Midi ended")}
      />
    </div>
  );
};

export default MidiPlayerComponent;
