"use client";

import Image from "next/image";
import { SetStateAction, useEffect, useState } from "react";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "./ui/pagination";
import { useDataContext } from "../_context/DataContext";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Dialog, DialogTrigger, DialogContent, DialogTitle } from "./ui/dialog";
import MidiPlayerComponent from "./midi-player";
import { Search } from "lucide-react";
import { toast } from "sonner";

interface DataItem {
  id: string;
  display: string;
  title: string;
  image: string;
  audio: string;
  sim?: string;
  dist?: string;
}

export default function MediaList() {
  const { refreshKey, setRefreshKey, fetchUrl } = useDataContext();
  const [items, setItems] = useState<DataItem[]>([]);
  const [page, setPage] = useState(1);
  const [size] = useState(28);
  const [total, setTotal] = useState(0);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(
        `api/${fetchUrl}?page=${page}&size=${size}&search=${searchTerm}`,
        {
          method: "GET",
        }
      );
      const data = await res.json();

      if (data && Array.isArray(data.items)) {
        setItems(data.items);
      } else {
        setItems([]);
      }

      setTotal(data.total);
    };

    fetchData();
  }, [page, size, fetchUrl, refreshKey, searchTerm]);

  const totalPages = Math.ceil(total / size);

  const handleSearchChange = (e: {
    target: { value: SetStateAction<string> };
  }) => {
    setSearchTerm(e.target.value);
  };

  const handleNext = () => {
    if (page < totalPages) setPage(page + 1);
  };

  const handlePrevious = () => {
    if (page > 1) setPage(page - 1);
  };

  const handleJumpToPage = (jumpPage: number) => {
    setPage(jumpPage);
  };

  const handleRefresh = () => {
    const fetchTimeCache = async () => {
      try {
        const res = await fetch("api/get_time_cache", {
          method: "GET",
        });
        const data = await res.json();
        if (data) {
          toast.custom(
            (t) => (
              <div className="bg-transparent">
                <div className="bg-[url('/bg-card.jpeg')] gap-5 border-2 rounded-xl p-4 flex flex-col items-center">
                  <div className="flex flex-col items-center">
                    {data.preprocess && <p>Preprocess: {data.preprocess}</p>}
                    {data.fit && <p>Fit: {data.fit}</p>}
                    {data.query && <p>Query: {data.query}</p>}
                    {data.time && <p>Time taken: {data.time}</p>}
                  </div>
                  <Button
                    variant={"ghost"}
                    onClick={() => toast.dismiss(t)}
                    className="border-2"
                  >
                    Dismiss
                  </Button>
                </div>
              </div>
            ),
            {
              duration: Infinity,
              style: {
                background: "transparent",
              },
            }
          );
        } else {
          toast.error("Failed to fetch cache time");
        }
      } catch {
        toast.error("Error fetching cache time");
      }
    };

    fetchTimeCache();
  };

  const renderPageNumbers = () => {
    const visiblePages = 3;
    const pages: number[] = [];

    for (
      let i = Math.max(1, page - visiblePages);
      i <= Math.min(totalPages, page + visiblePages);
      i++
    ) {
      pages.push(i);
    }

    return pages.map((p) => (
      <PaginationItem key={p}>
        <PaginationLink
          href="#"
          onClick={() => handleJumpToPage(p)}
          className={p === page ? "bg-red-950" : ""}
        >
          {p}
        </PaginationLink>
      </PaginationItem>
    ));
  };

  return (
    <div className="flex flex-wrap gap-6 justify-items-center overflow-hidden max-w-7xl">
      <div className="bg-[url('/bg-card.jpeg')] border-2 mx-7 rounded-xl flex flex-row items-center px-2 max-w-7xl w-[1040px]">
        <Button
          onClick={() => {
            setPage(1);
            setRefreshKey(refreshKey + 1);
            handleRefresh();
          }}
          className="p-2 bg-transparent"
        >
          <Image
            src={"/placeholder.png"}
            alt="refresh"
            width={25}
            height={25}
          />
        </Button>
        <Search />
        <Input
          className="border-none focus-visible:ring-0 placeholder:text-red-900 font-deadfall"
          placeholder="Search..."
          value={searchTerm}
          onChange={handleSearchChange}
        />
      </div>
      <div className="grid grid-cols-7 gap-6 justify-center items-center max-w-7xl px-7">
        {items.map((d) => (
          <Dialog key={d.id}>
            <DialogTrigger asChild>
              <Button
                variant={"ghost"}
                className="h-[140px] w-[120px] overflow-hidden p-2 pb-0 gap-0 bg-[url('/bg-card.jpeg')] rounded-xl flex flex-col text-center border-2 transition-transform duration-300 ease-in-out transform hover:scale-150 hover:z-50"
              >
                <Image
                  src={d.image || "/placeholder.png"}
                  alt={d.display}
                  width={100}
                  height={100}
                  className="rounded-lg size-[100px]"
                />

                <h1 className="font-bold m-1 max-w-[92px] overflow-hidden whitespace-nowrap">
                  <span className="inline-block font-was tracking-widest">
                    {d.display}
                  </span>
                </h1>
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-[url('/bg-card.jpeg')] p-6 rounded-lg flex flex-col items-center w-fit border-red-600">
              <DialogTitle className="truncate max-w-[400px] font-bloody tracking-widest relative">
                {d.title}
              </DialogTitle>
              <Image
                src={d.image || "/placeholder.png"}
                alt={d.id}
                width={200}
                height={200}
                className="rounded-lg w-full size-[400px] mb-3"
              />
              {d.audio !== "/midi/placeholder.mid" && d.audio !== null && (
                <MidiPlayerComponent midiFilePath={d.audio} />
              )}
              {d.dist && (
                <p className="font-bloody tracking-widest">dist: {d.dist}</p>
              )}
              {d.sim && (
                <p className="font-bloody tracking-widest">sim: {d.sim}</p>
              )}
            </DialogContent>
          </Dialog>
        ))}
      </div>

      <div className="w-full font-bloody">
        <Pagination className="w-fit bg-[url('/bg-card.jpeg')] rounded-xl flex items-center border-2">
          <PaginationContent>
            {page > 1 && (
              <PaginationItem>
                <PaginationPrevious
                  onClick={handlePrevious}
                  className="hover:bg-red-900 cursor-pointer"
                >
                  Previous
                </PaginationPrevious>
              </PaginationItem>
            )}

            {renderPageNumbers()}

            {page + 3 < totalPages && (
              <PaginationItem>
                <PaginationEllipsis />
              </PaginationItem>
            )}

            {page < totalPages && (
              <PaginationItem>
                <PaginationNext
                  onClick={handleNext}
                  className="hover:bg-red-900 cursor-pointer"
                >
                  Next
                </PaginationNext>
              </PaginationItem>
            )}
          </PaginationContent>
        </Pagination>
      </div>
    </div>
  );
}
