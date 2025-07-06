"use client"

import { useState, useRef, useEffect, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Mic, MicOff, Volume2 } from "lucide-react"
import { WebSocketService } from "@/utils/ws"
import { AudioProcessor } from "@/utils/audio-processor"

interface MicStreamProps {
  onConnectionChange?: (connected: boolean) => void
  webSocketService?: WebSocketService
  onVoiceCommand?: (command: string) => void
}

export function MicStream({ onConnectionChange, webSocketService, onVoiceCommand }: MicStreamProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [volume, setVolume] = useState(0)
  const [recognizedText, setRecognizedText] = useState("")

  const wsRef = useRef<WebSocketService | null>(null)
  const audioProcessorRef = useRef<AudioProcessor | null>(null)
  const animationFrameRef = useRef<number>()
  const recognitionRef = useRef<any>(null)

  const updateVolume = useCallback(() => {
    if (audioProcessorRef.current) {
      const currentVolume = audioProcessorRef.current.getVolume()
      setVolume(currentVolume)
    }
    animationFrameRef.current = requestAnimationFrame(updateVolume)
  }, [])

  useEffect(() => {
    // Initialize speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
      recognitionRef.current = new SpeechRecognition()
      recognitionRef.current.continuous = false
      recognitionRef.current.interimResults = false
      recognitionRef.current.lang = 'en-US'
      
      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript
        setRecognizedText(transcript)
        console.log("🎤 Speech recognized:", transcript)
        
        // Send to WebSocket for voice command processing
        if (wsRef.current && wsRef.current.isConnected()) {
          wsRef.current.sendText(transcript)
        }
        
        // Call the voice command callback
        onVoiceCommand?.(transcript)
      }
      
      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error)
      }
    } else {
      console.warn("Speech recognition not supported in this browser")
    }

    // Use provided WebSocket service or create new one
    if (webSocketService) {
      wsRef.current = webSocketService
    } else {
      wsRef.current = new WebSocketService()
    }

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

    // Connect to WebSocket if not already connected
    if (!webSocketService) {
      console.log("Attempting to connect to WebSocket...")
      wsRef.current.connect().catch((error) => {
        console.error("Failed to connect to WebSocket:", error)
      })
    }

    return () => {
      stopRecording()
      // Only disconnect if we created the WebSocket service
      if (!webSocketService && wsRef.current) {
        wsRef.current.disconnect()
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [onConnectionChange, webSocketService])

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
      
      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start()
        console.log("🎤 Speech recognition started")
      }
    } catch (error) {
      console.error("Failed to start recording:", error)
      alert("Failed to access microphone. Please check permissions.")
    }
  }

  const stopRecording = () => {
    audioProcessorRef.current?.stopRecording()
    setIsRecording(false)
    
    // Stop speech recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      console.log("🎤 Speech recognition stopped")
    }
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

      {recognizedText && (
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-center space-x-2">
            <Mic className="w-5 h-5 text-green-600" />
            <span className="text-green-800 font-medium">Recognized: "{recognizedText}"</span>
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
