"use client"

import { useEffect, useRef, useState } from "react"

interface Props {
  zh?: string
  en?: string
  containerRef: React.RefObject<HTMLElement>
}

export default function DraggableSubtitlesOverlay({
  zh,
  en,
  containerRef,
}: Props) {
  const overlayRef = useRef<HTMLDivElement>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [isDragging, setIsDragging] = useState(false)
  const [startOffset, setStartOffset] = useState({ x: 0, y: 0 })

  useEffect(() => {
    if (containerRef.current) {
      const { offsetWidth, offsetHeight } = containerRef.current
      setPosition({
        x: offsetWidth / 2 - 150,
        y: offsetHeight - 140,
      })
    }
  }, [containerRef])

  const onMouseDown = (e: React.MouseEvent<HTMLDivElement>) => {
    e.preventDefault()
    setIsDragging(true)
    const containerRect = containerRef.current?.getBoundingClientRect()
    setStartOffset({
      x: e.clientX - (containerRect?.left || 0) - position.x,
      y: e.clientY - (containerRect?.top || 0) - position.y,
    })
  }

  const onMouseMove = (e: MouseEvent) => {
    if (!isDragging || !containerRef.current) return
    const containerRect = containerRef.current.getBoundingClientRect()
    const x = e.clientX - containerRect.left - startOffset.x
    const y = e.clientY - containerRect.top - startOffset.y
    setPosition({ x, y })
  }

  const onMouseUp = () => setIsDragging(false)

  useEffect(() => {
    window.addEventListener("mousemove", onMouseMove)
    window.addEventListener("mouseup", onMouseUp)
    return () => {
      window.removeEventListener("mousemove", onMouseMove)
      window.removeEventListener("mouseup", onMouseUp)
    }
  }, [isDragging, startOffset])

  return (
    <div
      ref={overlayRef}
      onMouseDown={onMouseDown}
      style={{
        position: "absolute",
        left: position.x,
        top: position.y,
        cursor: "grab",
        transition: isDragging ? "none" : "all 0.2s ease",
        zIndex: 50,
      }}
      className="bg-black/70 text-white text-center rounded-md backdrop-blur-sm max-w-[90%] px-6 py-3 space-y-1 select-none"
    >
      {zh && <div className="text-lg font-semibold">{zh}</div>}
      {en && <div className="text-sm text-neutral-300">{en}</div>}
    </div>
  )
}
