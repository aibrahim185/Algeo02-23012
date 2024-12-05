"use client";

import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="grid place-content-center w-full overflow-hidden">
      <Link href={"/album"}>
        <Image
          src={"/ambalabu-text.png"}
          alt={"bg"}
          width={1000}
          height={1000}
        />
      </Link>
    </div>
  );
}
