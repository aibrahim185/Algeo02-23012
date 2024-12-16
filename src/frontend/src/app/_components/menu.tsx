/* eslint-disable @typescript-eslint/no-unused-vars */
"use client";

import Image from "next/image";
import { useState } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { toast } from "sonner";
import MidiPlayerComponent from "./midi-player";
import { useDataContext } from "../_context/DataContext";
import axios from "axios";

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
        const res = await axios.post("api/uploaddata", formData, {
          headers: { "Content-Type": "multipart/form-data" },
          timeout: 30 * 60 * 1000, // 30 minutes
        });

        if (res.status === 200) {
          toast.success("File Submitted Successfully!");
          setImageFilePath("/placeholder.png");
          setTitle("Ambalabu");
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_uploads");
        } else {
          throw new Error("Failed to upload");
        }
      } catch (error) {
        if (axios.isAxiosError(error)) {
          if (error.code === "ECONNRESET") {
            toast.error("Connection was lost");
          } else {
            toast.error("Upload failed", { description: error.message });
          }
        } else {
          toast.error("Upload failed", { description: "Unknown error" });
        }
      }
    }
  };

  const handleDelete = async () => {
    try {
      const res = await axios.delete("api/delete_data", {
        timeout: 30 * 60 * 1000, // 30 minutes
      });
      if (res.status === 200) {
        toast.success("Data deleted successfully!");
        setImageFilePath("/placeholder.png");
        setTitle("Ambalabu");
        setRefreshKey(refreshKey + 1);
        setFetchUrl("get_uploads");
        setMidiFilePath("/midi/placeholder.mid");
      } else {
        throw new Error("Failed to delete");
      }
    } catch (error) {
      if (error instanceof Error) {
        toast.error("Delete failed", { description: error.message });
      } else {
        toast.error("Delete failed", { description: "Unknown error" });
      }
    }
  };

  const handleMapperUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const file = e.target.files[0];
      setSelectedFiles([file]);

      const formData = new FormData();
      formData.append("mapper_file", file);

      try {
        const res = await axios.post("api/upload_mapper", formData, {
          timeout: 30 * 60 * 1000, // 30 minutes
        });
        if (res.status === 200) {
          setImageFilePath("/placeholder.png");
          setTitle("Ambalabu");
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_uploads");
          setMidiFilePath("/midi/placeholder.mid");
          toast.success("Mapper Loaded!");
        } else {
          throw new Error("Failed to upload mapper");
        }
      } catch (error) {
        if (error instanceof Error) {
          if (error instanceof Error) {
            toast.error("Something Went Wrong!", {
              description: error.message,
            });
          } else {
            toast.error("Something Went Wrong!", {
              description: "Unknown error",
            });
          }
        } else {
          toast.error("Something Went Wrong!", {
            description: "Unknown error",
          });
        }
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
        const res = await axios.post("api/find_similar_images", formData, {
          timeout: 30 * 60 * 1000, // 30 minutes
        });
        if (res.status === 200) {
          const data = res.data;
          setImageFilePath(`/api/uploads/query/${file.name}`);
          setTitle(file.name);
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_cache");
          setMidiFilePath("");
          if (data.notfound) {
            toast.error("No dataset found");
          } else {
            toast.success("Image query completed!", {
              duration: 30000,
              description: `preprocess time ${data.preprocess} ms, fitting time ${data.fit} ms, query time ${data.query} ms`,
            });
          }
        } else {
          throw new Error("Failed to find similar image");
        }
      } catch (error) {
        if (error instanceof Error) {
          if (error instanceof Error) {
            toast.error("Something Went Wrong!", {
              description: error.message,
            });
          } else {
            toast.error("Something Went Wrong!", {
              description: "Unknown error",
            });
          }
        } else {
          toast.error("Something Went Wrong!", {
            description: "Unknown error",
          });
        }
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
        const res = await axios.post("api/find_similar_audio", formData, {
          timeout: 30 * 60 * 1000, // 30 minutes
        });
        if (res.status === 200) {
          const data = res.data;
          setImageFilePath("/placeholder.png");
          setTitle(file.name);
          setRefreshKey(refreshKey + 1);
          setFetchUrl("get_cache");
          setMidiFilePath(`/api/uploads/query/${file.name}`);
          if (data.notfound) {
            toast.error("No dataset found");
          } else {
            toast.success("Audio query completed!", {
              duration: 30000,
              description: `Time taken: ${data.time}`,
            });
          }
        } else {
          throw new Error("Failed to find similar audio");
        }
      } catch (error) {
        if (error instanceof Error) {
          if (error instanceof Error) {
            toast.error("Something Went Wrong!", {
              description: error.message,
            });
          } else {
            toast.error("Something Went Wrong!", {
              description: "Unknown error",
            });
          }
        } else {
          toast.error("Something Went Wrong!", {
            description: "Unknown error",
          });
        }
      }
    }
  };

  const handleDrop = async (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    const filesArray = Array.from(event.dataTransfer.files);
    setSelectedFiles(filesArray);

    const formData = new FormData();
    filesArray.forEach((file) => formData.append("file_uploads", file));

    try {
      const res = await axios.post("api/uploaddata", formData, {
        timeout: 30 * 60 * 1000, // 30 minutes
      });
      if (res.status === 200) {
        toast.success("File Submitted Successfully!");
        setImageFilePath("/placeholder.png");
        setTitle("Ambalabu");
        setRefreshKey(refreshKey + 1);
        setFetchUrl("get_uploads");
      } else {
        throw new Error("Failed to upload");
      }
    } catch (error) {
      if (error instanceof Error) {
        if (error instanceof Error) {
          toast.error("Something Went Wrong!", {
            description: error.message,
          });
        } else {
          toast.error("Something Went Wrong!", {
            description: "Unknown error",
          });
        }
      } else {
        toast.error("Something Went Wrong!", {
          description: "Unknown error",
        });
      }
    }
  };

  return (
    <div className="h-[96vh] min-w-sm max-w-sm sticky top-5 mx-5 flex">
      <div className="h-full p-6 rounded-3xl flex flex-col justify-between gap-6">
        <div className="bg-[url('/bg-card.jpeg')] p-3 rounded-lg flex flex-col items-center border-2 border-red-900">
          <Image
            src={imageFilePath}
            alt={title}
            width={200}
            height={200}
            className="rounded-lg w-full size-[270px] mb-3"
          />
          {midiFilePath != "" && (
            <MidiPlayerComponent midiFilePath={midiFilePath} />
          )}
          {/* <AudioRecorder /> */}
          <div className="text-center overflow-hidden max-w-[270px] w-full">
            <h1 className="text-3xl font-extrabold font-bloody tracking-widest marquee">
              {title}
            </h1>
          </div>
        </div>
        <div
          className="flex flex-col justify-between gap-3 bg-[url('/bg-card.jpeg')] p-3 rounded-lg border-2 border-red-900 font-bloody tracking-widest"
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
              className="w-full text-red-600 border-2 border-red-900 hover:bg-red-900 rounded-lg h-full"
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
