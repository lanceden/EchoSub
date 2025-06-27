"use client";

import EchoSubPlayer from "@/components/EchoSubPlayer";
import { useState } from "react";

export default function Page() {
  const [url, setUrl] = useState("https://youtu.be/KrRD7r7y7NY?si=rf5ofVOLpOnytXs6");

  return (
    <div className="max-w-3xl mx-auto mt-10 space-y-6 pb-6">
      <h1 className="text-2xl font-semibold">🎬 EchoSub Demo Player</h1>

      <div className="flex gap-2 items-center">
        <input
          type="text"
          placeholder="請輸入影片連結，如 YouTube/Bilibili"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          className="w-full px-4 py-2 border rounded-md text-sm"
        />
        <button
          className="bg-black text-white px-4 py-2 rounded-md hover:bg-neutral-800"
          onClick={() => setUrl(url)}
        >
          播放
        </button>
      </div>

      <EchoSubPlayer
        videoUrl={url}
        subtitleUrl="/demo.srt" // 確保這個檔案在 public 資料夾中
      />
    </div>
  );
}
