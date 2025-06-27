"use client"

import React, { useEffect, useRef, useState } from "react"
import ReactPlayer from "react-player"
import { parseSync } from "subtitle"
import DraggableSubtitlesOverlay from "./DraggableSubtitlesOverlay"

type Subtitle = {
  start: number
  end: number
  zh?: string
  en?: string
}

interface Props {
  videoUrl: string
  subtitleUrl: string
}

export default function EchoSubPlayer({ videoUrl, subtitleUrl }: Props) {
  const [subtitles, setSubtitles] = useState<Subtitle[]>([])
  const [currentSub, setCurrentSub] = useState<Subtitle | null>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const playerRef = useRef<ReactPlayer>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  // 👉 進入容器全螢幕
  const goFullscreen = () => {
    containerRef.current?.requestFullscreen?.()
  }

  useEffect(() => {
    const handleFullscreenChange = () => {
      if (containerRef.current) {
        const { offsetWidth, offsetHeight } = containerRef.current
        setPosition({
          x: offsetWidth / 2 - 150,
          y: offsetHeight - 140,
        })
      }
    }

    document.addEventListener("fullscreenchange", handleFullscreenChange)
    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange)
    }
  }, [containerRef])

  // 👉 載入 SRT 並做中英分行拆解
  useEffect(() => {
    fetch(subtitleUrl)
      .then((res) => res.text())
      .then((data) => {
        const parsed = parseSync(data).filter((e) => e.type === "cue")
        const formatted = parsed.map((e: any) => {
          const [zh, en] = e.data.text.split(/\r?\n/)
          return {
            start: e.data.start,
            end: e.data.end,
            zh: zh?.trim(),
            en: en?.trim(),
          }
        })
        setSubtitles(formatted)
      })
  }, [subtitleUrl])

  // 👉 每秒檢查目前時間對應字幕
  const handleProgress = ({ playedSeconds }: { playedSeconds: number }) => {
    const now = playedSeconds * 1000
    const active = subtitles.find((s) => now >= s.start && now <= s.end)
    setCurrentSub(active || null)
  }

  return (
    <div
      ref={containerRef}
      className="relative aspect-video w-full max-w-5xl mx-auto">
      <ReactPlayer
        key={videoUrl}
        url={videoUrl}
        controls
        ref={playerRef}
        width="100%"
        height="100%"
        onProgress={handleProgress}
        className="react-player"
        wrapperClassName="relative w-full h-full"
        config={{ youtube: { playerVars: { showinfo: 1 } } }}
      />

      {/* 字幕顯示區 */}
      {currentSub && (
        <DraggableSubtitlesOverlay
          zh={currentSub.zh}
          en={currentSub.en}
          containerRef={containerRef}
        />
      )}

      {/* 全螢幕控制按鈕 */}
      <div className="absolute top-2 right-2 z-10">
        <button
          className="bg-teal-500 text-white px-4 py-1 text-sm rounded hover:bg-teal-600 transition"
          onClick={goFullscreen}>
          全螢幕
        </button>
      </div>
    </div>
  )
}
