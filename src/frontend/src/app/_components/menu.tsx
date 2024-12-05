import Image from "next/image";

import { Button } from "./ui/button";
import { Input } from "./ui/input";

export default function Menu() {
  return (
    <div className="h-[96vh] min-w-sm max-w-sm sticky top-5 mx-5 flex">
      <div className="h-full p-6 rounded-3xl flex flex-col justify-between gap-6">
        <div className="size-fit bg-black p-3 rounded-lg">
          <Image
            src={"/favicon.ico"}
            alt={""}
            width={100}
            height={100}
            className="rounded-lg w-[50vw]"
          />
          <div>
            <h1 className="text-3xl font-extrabold">Judul</h1>
            <p className="truncate">Audio</p>
            <p className="truncate">Picture</p>
            <p className="truncate">Mapper</p>
          </div>
        </div>
        <div className="flex flex-col justify-between gap-3 bg-black p-3 rounded-lg">
          <div className="relative border-2 border-red-900 hover:bg-red-900 rounded-lg ">
            <Input
              type="file"
              id="file-input"
              className="absolute inset-0 opacity-0 cursor-pointer"
              multiple
            />
            <Button
              className="w-full text-red-600 border-red-600"
              variant={"ghost"}
            >
              Upload
            </Button>
          </div>
          <Button
            className="w-full text-red-600 border-red-900 hover:bg-red-900 border-2 "
            variant={"ghost"}
          >
            Audio
          </Button>
          <Button
            className="w-full text-red-600 border-red-900 hover:bg-red-900 border-2 "
            variant={"ghost"}
          >
            Picture
          </Button>
          <Button
            className="w-full text-red-600 border-red-900 hover:bg-red-900 border-2 "
            variant={"ghost"}
          >
            Mapper
          </Button>
        </div>
      </div>
    </div>
  );
}
