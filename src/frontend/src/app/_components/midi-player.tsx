"use client";

import React from "react";
import dynamic from "next/dynamic";

const MidiPlayer = dynamic(() => import("react-midi-player"), { ssr: false });

const MidiPlayerComponent: React.FC = () => {
  const midiFilePath = "/midi/Un_po_dazzurro.mid";

  return (
    <div>
      <MidiPlayer
        src={midiFilePath} // Path ke file MIDI
        autoplay={false} // Atur autoplay
        loop={false} // Atur apakah loop diaktifkan
        onStart={() => console.log("Midi started")}
        onStop={() => console.log("Midi stopped")}
        onPause={() => console.log("Midi paused")}
        onEnd={() => console.log("Midi ended")}
      />
    </div>
  );
};

export default MidiPlayerComponent;
