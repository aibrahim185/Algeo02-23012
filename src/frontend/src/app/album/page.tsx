"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

export default function Home() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    const fetchData = async () => {
      const res = await fetch("api/album", {
        method: "GET",
      });
      console.log(res);
      const data = await res.json();
      setMessage(data.text);
    };

    fetchData();
  }, []);

  return (
    <div className="grid place-content-center w-full">
      <Image src={"/ambalabu-text.png"} alt={"bg"} width={1000} height={1000} />
      <h1>{message ? message : "Loading..."}</h1>
      {process.env.NEXT_PUBLIC_API_URL}
    </div>
  );
}
