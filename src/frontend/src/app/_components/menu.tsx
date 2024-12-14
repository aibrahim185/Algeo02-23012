/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import Image from "next/image";
import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { toast } from "sonner";
import MidiPlayerComponent from "./midi-player";
import { useDataContext } from "../_context/DataContext";
import AudioRecorder from "./audio-recorder";

export default function Menu() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const {
    refreshKey,
    setRefreshKey,
    setFetchUrl,
    imageFilePath,
    setImageFilePath,
    midiFilePath,
    title,
    setTitle,
  } = useDataContext();

  const handleChangeAndSubmit = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (e.target.files) {
      const files = Array.from(e.target.files);
      setSelectedFiles(files);

      const formData = new FormData();
      files.forEach((file) => {
        formData.append("file_uploads", file);
      });

      try {
        const endPoint = "api/uploaddata";
        const res = await fetch(endPoint, {
          method: "POST",
          body: formData,
        });

        if (res.ok) {
          console.log("aman");
          toast("File Submitted Successfully!", {
            description: "Please continue to submit the data set.",
          });

          setImageFilePath("/favicon.ico");
          setTitle("Ambalabu");
          setRefreshKey(refreshKey + 1);
          setFetchUrl("uploads");
        } else {
          console.log("ga aman");
          toast("Something Went Wrong!", {
            description: "Please try again later",
          });
        }
      } catch {
        console.log("ga aman 2");
        toast("Something Went Wrong!", {
          description: "Please try again later",
        });
      }
    }
  };

  const handlePictureUpload = async (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFiles([file]);

      const formData = new FormData();
      formData.append("query_image", file);

      try {
        const endPoint = "api/find_similar_images";
        const res = await fetch(endPoint, {
          method: "POST",
          body: formData,
        });

        if (res.ok) {
          const data = await res.json();
          console.log(data);

          setImageFilePath(`/api/uploads/query/${file.name}`);
          setTitle(file.name);
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_similar_images");

          toast("Image Submitted Successfully!");
        } else {
          console.log("Upload failed");
          toast("Something Went Wrong!", {
            description: "Please try again later",
          });
        }
      } catch {
        console.log("Error in upload");
        toast("Something Went Wrong!", {
          description: "Please try again later",
        });
      }
    }
  };

  const handleAudioUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFiles([file]);

      const formData = new FormData();
      formData.append("query_audio", file);

      try {
        const endPoint = "api/find_similar_midi";
        const res = await fetch(endPoint, {
          method: "POST",
          body: formData,
        });

        if (res.ok) {
          const data = await res.json();
          console.log(data);

          setImageFilePath(`/placeholder.ico`);
          setTitle(file.name);
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_similar_midi");

          toast("Image Submitted Successfully!");
        } else {
          console.log("Upload failed");
          toast("Something Went Wrong!", {
            description: "Please try again later",
          });
        }
      } catch {
        console.log("Error in upload");
        toast("Something Went Wrong!", {
          description: "Please try again later",
        });
      }
    }
  };

  const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const filesArray = Array.from(event.dataTransfer.files);
    setSelectedFiles(filesArray);

    const formData = new FormData();
    filesArray.forEach((file) => {
      formData.append("file_uploads", file);
    });

    try {
      const endPoint = "api/uploaddata";
      const res = await fetch(endPoint, {
        method: "POST",
        body: formData,
      });

      if (res.ok) {
        console.log("aman");
        toast("File Submitted Successfully!", {
          description: "Please continue to submit the data set.",
        });

        setImageFilePath("/favicon.ico");
        setTitle("Ambalabu");
        setRefreshKey(refreshKey + 1);
        setFetchUrl("uploads");
      } else {
        console.log("ga aman");
        toast("Something Went Wrong!", {
          description: "Please try again later",
        });
      }
    } catch {
      console.log("ga aman 2");
      toast("Something Went Wrong!", {
        description: "Please try again later",
      });
    }
  };

  return (
    <div className="h-[96vh] min-w-sm max-w-sm sticky top-5 mx-5 flex">
      <div className="h-full p-6 rounded-3xl flex flex-col justify-between gap-6">
        <div className="bg-black p-3 rounded-lg flex flex-col items-center">
          <Image
            src={imageFilePath}
            alt={title}
            width={200}
            height={200}
            className="rounded-lg w-full size-[270px] mb-3"
          />
          <MidiPlayerComponent midiFilePath={midiFilePath} />
          <AudioRecorder />
          <div className="text-center overflow-hidden">
            <h1 className="text-3xl font-extrabold overflow-hidden max-w-[270px]">
              {title}
            </h1>
          </div>
        </div>
        <div
          className="flex flex-col justify-between gap-3 bg-black p-3 rounded-lg"
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          <div className="relative border-2 border-red-900 hover:bg-red-900 rounded-lg">
            <Input
              type="file"
              id="file-input"
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={handleChangeAndSubmit}
              ref={(input) => {
                if (input) {
                  input.setAttribute("webkitdirectory", "true");
                }
              }}
              accept=".mid,.zip,.rar,.7z,.ogg,.flac,.aac,.alac,.jpg,.jpeg,.png"
              multiple
            />
            <Button
              type="button"
              className="w-full text-red-600"
              variant={"ghost"}
            >
              Upload Dataset
            </Button>
          </div>
          <div className="relative border-2 border-red-900 hover:bg-red-900 rounded-lg">
            <Input
              type="file"
              id="file-input"
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={handleAudioUpload}
              accept=".mid, .wav"
            />
            <Button
              type="button"
              className="w-full text-red-600"
              variant={"ghost"}
            >
              Audio
            </Button>
          </div>
          <div className="relative border-2 border-red-900 hover:bg-red-900 rounded-lg">
            <Input
              type="file"
              id="file-input"
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={handlePictureUpload}
              accept=".jpg,.jpeg,.png"
            />
            <Button
              type="button"
              className="w-full text-red-600"
              variant={"ghost"}
            >
              Picture
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
