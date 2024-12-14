"use client";

import { useState } from "react";

export default function AudioRecorder() {
  const [isRecording, setIsRecording] = useState(false);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(
    null
  );
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);

  // Start recording audio
  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: true,
      });

      const recorder = new MediaRecorder(stream);

      // Event handler for when data is available
      recorder.ondataavailable = (event: BlobEvent) => {
        setAudioChunks((prevChunks) => [...prevChunks, event.data]);
      };

      // Event handler for when the recording is stopped
      recorder.onstop = () => {
        const blob = new Blob(audioChunks, { type: "audio/wav" });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        setAudioChunks([]); // Clear chunks after stopping
      };

      recorder.start();
      setMediaRecorder(recorder);
      setIsRecording(true);
    } catch (err) {
      console.error("Error accessing microphone", err);
    }
  };

  // Stop recording audio
  const stopRecording = () => {
    if (mediaRecorder) {
      mediaRecorder.stop();
      setIsRecording(false);
    }
  };

  // Send the recorded audio to the backend for MIDI conversion
  const sendAudioToBackend = async () => {
    if (audioBlob) {
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.wav");

      try {
        const response = await fetch("api/upload-audio", {
          method: "POST",
          body: formData,
        });

        if (!response.ok) {
          throw new Error("Failed to upload audio");
        }

        // Handle the response (file MIDI or success message)
        const data = await response.json();
        console.log(data);
        alert("MIDI file generated!");
      } catch (error) {
        console.error("Error uploading audio:", error);
      }
    }
  };

  return (
    <div>
      <h1>Audio to MIDI Converter</h1>
      <div>
        {!isRecording ? (
          <button onClick={startRecording}>Start Recording</button>
        ) : (
          <button onClick={stopRecording}>Stop Recording</button>
        )}
      </div>
      {audioUrl && (
        <div>
          <h3>Recorded Audio</h3>
          <audio controls src={audioUrl}></audio>
        </div>
      )}
      {audioBlob && !isRecording && (
        <div>
          <button onClick={sendAudioToBackend}>
            Send to Backend for MIDI Conversion
          </button>
        </div>
      )}
    </div>
  );
}
