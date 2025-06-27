"use client"

import React, { useEffect, useRef, useState } from "react"
import ReactPlayer from "react-player"
import { parseSync } from "subtitle"

type Subtitle = {
  start: number
  end: number
  text: string
}

interface Props {
  videoUrl: string
  subtitleUrl: string // 預設雙語 SRT 路徑
}

export default function EchoSubPlayer({ videoUrl, subtitleUrl }: Props) {
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const [currentSub, setCurrentSub] = useState("")
  const playerRef = useRef<ReactPlayer | null>(null)

  useEffect(() => {
    fetch(subtitleUrl)
      .then((res) => res.text())
      .then((data) => {
        const parsed = parseSync(data).filter((e) => e.type === "cue")
        setSubtitles(
          parsed.map((e) => ({
            start: e.data.start,
            end: e.data.end,
            text: e.data.text,
          })) as Subtitle[]
        )
      })
  }, [subtitleUrl])

  const handleProgress = ({ playedSeconds }: { playedSeconds: number }) => {
    const active = subtitles.find(
      (s) => playedSeconds * 1000 >= s.start && playedSeconds * 1000 <= s.end
    )
    setCurrentSub(active ? active.text : "")
  }

  return (
    <div className="w-full max-w-screen-lg mx-auto px-4 mt-8 space-y-4">
      <ReactPlayer
        key={videoUrl}
        url={videoUrl}
        controls
        ref={playerRef}
        width="100%"
        height="500px" // 固定高度，與 YouTube 播放器在桌面上的常見高度一致
        className="react-player"
        onProgress={handleProgress}
        config={{
          youtube: {
            playerVars: { showinfo: 1 },
          },
        }}
      />
      <div className="p-4 bg-black text-white text-center text-xl rounded-lg">
        {currentSub}
      </div>
    </div>
  )
}
