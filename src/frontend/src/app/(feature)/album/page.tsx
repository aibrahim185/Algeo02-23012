"use client";

import ImageList from "../../_components/image-list";

export default function AlbumPage() {
  return (
    <div className="grid place-content-center w-full">
      <ImageList dataType={"image"} />
    </div>
  );
}
