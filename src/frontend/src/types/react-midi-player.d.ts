declare module "react-midi-player" {
  const MidiPlayer: React.FC<{
    src: string;
    autoplay?: boolean;
    loop?: boolean;
    onStart?: () => void;
    onStop?: () => void;
    onPause?: () => void;
    onEnd?: () => void;
  }>;
  export default MidiPlayer;
}
