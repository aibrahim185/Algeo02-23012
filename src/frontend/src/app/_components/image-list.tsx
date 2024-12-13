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
  image: string;
  title: string;
}

export default function ImageList() {
  const [items, setItems] = useState<DataItem[]>([]);
  const [page, setPage] = useState(1);
  const [size] = useState(28);
  const [total, setTotal] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch(`api/faker?page=${page}&size=${size}`, {
        method: "GET",
      });
      const data = await res.json();
      setItems(data.items);
      setTotal(data.total);
    };

    fetchData();
  }, [page, size]);

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
          className={p === page ? "bg-gray-900 text-white" : ""}
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
          <Image
            src={d.image}
            alt={d.title}
            width={100}
            height={100}
            className="rounded-lg"
          />
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
