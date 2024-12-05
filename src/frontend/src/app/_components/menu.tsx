/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import Image from "next/image";
import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { toast } from "sonner";
import MidiPlayerComponent from "./midi-player";

export default function Menu() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

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
        <div className="size-fit bg-black p-3 rounded-lg">
          <Image
            src={"/favicon.ico"}
            alt={""}
            width={100}
            height={100}
            className="rounded-lg w-[50vw] mb-3"
          />
          <MidiPlayerComponent />
          <div>
            <h1 className="text-3xl font-extrabold">Judul</h1>
            <p className="truncate">Audio</p>
            <p className="truncate">Picture</p>
            <p className="truncate">Mapper</p>
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
              Upload
            </Button>
          </div>
          <Button
            className="w-full text-red-600 border-red-900 hover:bg-red-900 border-2"
            variant={"ghost"}
          >
            Audio
          </Button>
          <Button
            className="w-full text-red-600 border-red-900 hover:bg-red-900 border-2"
            variant={"ghost"}
          >
            Picture
          </Button>
          <Button
            className="w-full text-red-600 border-red-900 hover:bg-red-900 border-2"
            variant={"ghost"}
          >
            Mapper
          </Button>
        </div>
      </div>
    </div>
  );
}
