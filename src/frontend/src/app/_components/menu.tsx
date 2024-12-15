/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import Image from "next/image";
import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { toast } from "sonner";
import MidiPlayerComponent from "./midi-player";
import { useDataContext } from "../_context/DataContext";

export default function Menu() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const {
    refreshKey,
    setRefreshKey,
    setFetchUrl,
    imageFilePath,
    setImageFilePath,
    midiFilePath,
    setMidiFilePath,
    title,
    setTitle,
  } = useDataContext();

  const handleUploadDataset = async (
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
          toast("File Submitted Successfully!");

          setImageFilePath("/favicon.ico");
          setTitle("Ambalabu");
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_uploads");
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

  const handleDelete = async () => {
    try {
      const res = await fetch("api/delete_data", {
        method: "DELETE",
      });

      if (res.ok) {
        toast("Data deleted successfully!");
        setImageFilePath("/favicon.ico");
        setTitle("Ambalabu");
        setRefreshKey(refreshKey + 1);
        setFetchUrl("get_uploads");
        setMidiFilePath("/midi/Never_Gonna_Give_You_Up.mid");
      } else {
        toast("Error deleting the data. 1");
      }
    } catch (error) {
      console.error("There was an error deleting the data", error);
      toast("Error deleting the data.");
    }
  };

  const handleMapperUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFiles([file]);

      const formData = new FormData();
      formData.append("mapper_file", file);

      try {
        const endPoint = "api/upload_mapper";
        const res = await fetch(endPoint, {
          method: "POST",
          body: formData,
        });

        if (res.ok) {
          const data = await res.json();
          console.log(data);

          setImageFilePath("/placeholder.ico");
          setTitle("Ambalabu");
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_uploads");
          setMidiFilePath("/midi/Never_Gonna_Give_You_Up.mid");

          toast.success("Mapper Loaded!");
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
          setFetchUrl("get_cache");
          setMidiFilePath("/midi/Never_Gonna_Give_You_Up.mid");

          toast.success("Image query completed!", {
            duration: Infinity,
          });
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

      // const controller = new AbortController();
      // const timeout = 500000;
      // const timeoutId = setTimeout(() => {
      //   controller.abort();
      // }, timeout);

      try {
        const endPoint = "api/find_similar_audio";
        const res = await fetch(endPoint, {
          method: "POST",
          body: formData,
          // signal: controller.signal,
        });

        // clearTimeout(timeoutId);

        if (res.ok) {
          const data = await res.json();
          console.log(data);

          setImageFilePath(`/placeholder.ico`);
          setTitle(file.name);
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_cache");
          setMidiFilePath("/api/uploads/query/" + file.name);

          toast.success("Audio query completed!", {
            duration: Infinity,
          });
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
        toast("File Submitted Successfully!");

        setImageFilePath("/favicon.ico");
        setTitle("Ambalabu");
        setRefreshKey(refreshKey + 1);
        setFetchUrl("get_uploads");
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
        <div className="bg-black p-3 rounded-lg flex flex-col items-center border-2 border-red-900">
          <Image
            src={imageFilePath}
            alt={title}
            width={200}
            height={200}
            className="rounded-lg w-full size-[270px] mb-3"
          />
          <MidiPlayerComponent midiFilePath={midiFilePath} />
          {/* <AudioRecorder /> */}
          <div className="text-center overflow-hidden max-w-[270px]">
            <h1 className="text-3xl font-extrabold font-bloody tracking-widest marquee w-fit">
              {title}
            </h1>
          </div>
        </div>
        <div
          className="flex flex-col justify-between gap-3 bg-black p-3 rounded-lg border-2 border-red-900 font-bloody tracking-widest"
          onDrop={handleDrop}
          onDragOver={(e) => e.preventDefault()}
        >
          <div className="flex flex-row gap-3">
            <div className="relative border-2 border-red-900 hover:bg-red-900 rounded-lg">
              <Input
                type="file"
                id="file-input"
                className="absolute inset-0 opacity-0 cursor-pointer"
                onChange={handleUploadDataset}
                accept=".mid,.zip,.jpg,.jpeg,.png"
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
            <Button
              type="button"
              className="w-full text-red-600 border-2 border-red-900 hover:bg-red-900 rounded-lg"
              variant={"ghost"}
              onClick={handleDelete}
            >
              Delete
            </Button>
          </div>
          <div className="relative border-2 border-red-900 hover:bg-red-900 rounded-lg">
            <Input
              type="file"
              id="file-input"
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={handleMapperUpload}
              accept=".json"
            />
            <Button
              type="button"
              className="w-full text-red-600"
              variant={"ghost"}
            >
              Mapper
            </Button>
          </div>
          <div className="relative border-2 border-red-900 hover:bg-red-900 rounded-lg">
            <Input
              type="file"
              id="file-input"
              className="absolute inset-0 opacity-0 cursor-pointer"
              onChange={handleAudioUpload}
              accept=".mid"
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
