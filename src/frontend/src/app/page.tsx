import Image from "next/image";

export default function Home() {
  return (
    <div className="grid place-content-center min-h-screen w-full">
      <Image src={"/ambalabu-text.png"} alt={"bg"} width={1000} height={1000} />
    </div>
  );
}
