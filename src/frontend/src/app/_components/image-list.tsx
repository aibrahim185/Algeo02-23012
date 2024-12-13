"use client";

import Image from "next/image";
import { useEffect, useState } from "react";
import {
  Pagination,
  PaginationContent,
  PaginationEllipsis,
  PaginationItem,
  PaginationLink,
  PaginationNext,
  PaginationPrevious,
} from "./ui/pagination";

interface DataItem {
  id: number;
  title: string;
  image?: string;
  audio?: string;
}

interface MediaListProps {
  dataType: "image" | "music";
  fetchUrl: string;
}

export default function MediaList({ dataType, fetchUrl }: MediaListProps) {
  const [items, setItems] = useState<DataItem[]>([]);
  const [page, setPage] = useState(1);
  const [size] = useState(28);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(`api/${fetchUrl}?page=${page}&size=${size}`, {
        method: "GET",
      });
      const data = await res.json();

      if (data && Array.isArray(data.items)) {
        setItems(data.items);
      } else {
        setItems([]);
      }

      setTotal(data.total);
    };

    fetchData();
  }, [page, size, fetchUrl]);

  const totalPages = Math.ceil(total / size);

  const handleNext = () => {
    if (page < totalPages) setPage(page + 1);
  };

  const handlePrevious = () => {
    if (page > 1) setPage(page - 1);
  };

  const handleJumpToPage = (jumpPage: number) => {
    setPage(jumpPage);
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
          className={p === page ? "bg-gray-900" : ""}
        >
          {p}
        </PaginationLink>
      </PaginationItem>
    ));
  };

  return (
    <div className="flex flex-wrap gap-6 justify-items-center overflow-hidden max-w-7xl">
      {items.map((d) => (
        <div
          key={d.id}
          className="h-fit overflow-hidden p-2 pb-0 bg-black rounded-xl flex flex-col text-center"
        >
          {dataType === "image" ? (
            <Image
              src={d.image || "/placeholder.ico"}
              alt={d.title}
              width={100}
              height={100}
              className="rounded-lg"
            />
          ) : (
            <audio controls>
              <source src={d.audio || "/placeholder.mp3"} />
              Your browser does not support the audio element.
            </audio>
          )}

          <h1 className="font-bold m-1 max-w-[92px] overflow-hidden whitespace-nowrap">
            <span className="marquee inline-block">{d.title}</span>
          </h1>
        </div>
      ))}

      <div className="w-full">
        <Pagination className="w-fit bg-black rounded-xl flex items-center">
          <PaginationContent>
            {/* Previous Button */}
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

            {/* Page Numbers */}
            {renderPageNumbers()}

            {/* Ellipsis (if needed) */}
            {page + 3 < totalPages && (
              <PaginationItem>
                <PaginationEllipsis />
              </PaginationItem>
            )}

            {/* Next Button */}
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
