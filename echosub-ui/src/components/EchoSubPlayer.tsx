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
  const [dragging, setDragging] = useState(false)
  const [position, setPosition] = useState({ x: 100, y: 100 })
  const offset = useRef({ x: 0, y: 0 })

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (dragging) {
        setPosition({ x: e.clientX - offset.current.x, y: e.clientY - offset.current.y })
      }
    }
    const handleMouseUp = () => setDragging(false)

    window.addEventListener("mousemove", handleMouseMove)
    window.addEventListener("mouseup", handleMouseUp)
    return () => {
      window.removeEventListener("mousemove", handleMouseMove)
      window.removeEventListener("mouseup", handleMouseUp)
    }
  }, [dragging])

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

  const handleMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    offset.current = { x: e.clientX - position.x, y: e.clientY - position.y }
    setDragging(true)
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
      <div
        className="p-4 bg-black text-white text-center text-xl rounded-lg cursor-move fixed"
        style={{ left: position.x, top: position.y, width: "fit-content" }}
        onMouseDown={handleMouseDown}
      >
        {currentSub}
      </div>
    </div>
  )
}
