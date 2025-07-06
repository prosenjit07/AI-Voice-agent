"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Mic, MicOff, Volume2 } from "lucide-react"
import { WebSocketService } from "@/utils/ws"
import { AudioProcessor } from "@/utils/audio-processor"

interface MicStreamProps {
  onConnectionChange?: (connected: boolean) => void
}

export function MicStream({ onConnectionChange }: MicStreamProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(0)

  const wsRef = useRef<WebSocketService | null>(null)
  const audioProcessorRef = useRef<AudioProcessor | null>(null)
  const animationFrameRef = useRef<number>()

  const updateVolume = useCallback(() => {
    if (audioProcessorRef.current) {
      const currentVolume = audioProcessorRef.current.getVolume()
      setVolume(currentVolume)
    }
    animationFrameRef.current = requestAnimationFrame(updateVolume)
  }, [])

  useEffect(() => {
    // Initialize WebSocket service
    wsRef.current = new WebSocketService()

    wsRef.current.onConnectionChange = (connected) => {
      setIsConnected(connected)
      onConnectionChange?.(connected)
    }

    wsRef.current.onAudioReceived = (audioData) => {
      setIsPlaying(true)
      // Stop recording when receiving audio (turn-taking)
      if (isRecording) {
        stopRecording()
      }

      // Play received audio
      audioProcessorRef.current?.playAudio(audioData).then(() => {
        setIsPlaying(false)
      })
    }

    // Initialize audio processor
    audioProcessorRef.current = new AudioProcessor()

    audioProcessorRef.current.onAudioData = (audioData) => {
      if (wsRef.current && isConnected) {
        wsRef.current.sendAudio(audioData)
      }
    }

    audioProcessorRef.current.onSpeechStart = () => {
      // Interrupt playback when user starts speaking
      audioProcessorRef.current?.stopPlayback()
      setIsPlaying(false)
    }

    // Connect to WebSocket immediately
    console.log("Attempting to connect to WebSocket...")
    wsRef.current.connect().catch((error) => {
      console.error("Failed to connect to WebSocket:", error)
    })

    return () => {
      stopRecording()
      wsRef.current?.disconnect()
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [onConnectionChange])

  useEffect(() => {
    if (isRecording) {
      updateVolume()
    } else if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      setVolume(0)
    }
  }, [isRecording, updateVolume])

  const startRecording = async () => {
    try {
      await audioProcessorRef.current?.startRecording()
      setIsRecording(true)
      
      // For testing: simulate voice commands after a delay
      setTimeout(() => {
        if (wsRef.current) {
          // Simulate some test commands
          const testCommands = [
            "open voice form",
            "my name is John Doe",
            "my email is john@example.com",
            "my message is Hello world"
          ]
          
          testCommands.forEach((command, index) => {
            setTimeout(() => {
              // Send the command to the backend
              wsRef.current?.sendText(command)
            }, (index + 1) * 2000) // Send commands 2 seconds apart
          })
        }
      }, 3000) // Start after 3 seconds
      
    } catch (error) {
      console.error("Failed to start recording:", error)
      alert("Failed to access microphone. Please check permissions.")
    }
  }

  const stopRecording = () => {
    audioProcessorRef.current?.stopRecording()
    setIsRecording(false)
  }

  const toggleRecording = () => {
    if (isRecording) {
      stopRecording()
    } else {
      startRecording()
    }
  }

  const VolumeIndicator = () => (
    <div className="flex items-center space-x-2">
      <div className="flex space-x-1">
        {[...Array(10)].map((_, i) => (
          <div
            key={i}
            className={`w-1 h-8 rounded-full transition-colors duration-100 ${
              volume * 10 > i ? "bg-green-500" : "bg-gray-200"
            }`}
          />
        ))}
      </div>
      <span className="text-sm text-gray-600 min-w-[3rem]">{Math.round(volume * 100)}%</span>
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex flex-col items-center space-y-4">
        <Button
          onClick={toggleRecording}
          disabled={!isConnected}
          size="lg"
          className={`w-20 h-20 rounded-full transition-all duration-200 ${
            isRecording ? "bg-red-500 hover:bg-red-600 animate-pulse" : "bg-blue-500 hover:bg-blue-600"
          }`}
        >
          {isRecording ? <MicOff className="w-8 h-8 text-white" /> : <Mic className="w-8 h-8 text-white" />}
        </Button>

        <div className="text-center">
          <p className="text-lg font-medium">{isRecording ? "Recording..." : "Click to start"}</p>
          <p className="text-sm text-gray-600">{isConnected ? "Ready to stream" : "Connecting..."}</p>
        </div>
      </div>

      {isRecording && (
        <div className="bg-white rounded-lg p-4 shadow-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Microphone Level</span>
            <Mic className="w-4 h-4 text-gray-500" />
          </div>
          <VolumeIndicator />
        </div>
      )}

      {isPlaying && (
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-center space-x-2">
            <Volume2 className="w-5 h-5 text-blue-600 animate-pulse" />
            <span className="text-blue-800 font-medium">AI is speaking...</span>
          </div>
        </div>
      )}

      <div className="text-xs text-gray-500 text-center">
        <p>• Speak naturally - the AI will respond</p>
        <p>• Start speaking to interrupt AI responses</p>
        <p>• Make sure your microphone is enabled</p>
      </div>
    </div>
  )
}
