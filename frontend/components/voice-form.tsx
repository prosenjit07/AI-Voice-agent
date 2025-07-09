"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { Mic, Send, Check, MicOff, Volume2 } from "lucide-react"
import { WebSocketService } from "@/utils/ws"
import { AudioProcessor } from "@/utils/audio-processor"

// Type declarations for Speech Recognition API
interface SpeechRecognition extends EventTarget {
  continuous: boolean
  interimResults: boolean
  lang: string
  start(): void
  stop(): void
  onresult: ((event: any) => void) | null
  onerror: ((event: any) => void) | null
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionConstructor
    webkitSpeechRecognition: SpeechRecognitionConstructor
  }
}

interface VoiceFormProps {
  isConnected: boolean
  webSocketService?: WebSocketService
  onVoiceCommand?: (command: string) => void
}

interface FormData {
  name: string
  email: string
  message: string
}

export function VoiceForm({ isConnected, webSocketService, onVoiceCommand }: VoiceFormProps) {
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    message: "",
  })
  const [isListening, setIsListening] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [lastCommand, setLastCommand] = useState("")
  const [recognizedText, setRecognizedText] = useState("")
  const [volume, setVolume] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)

  const wsRef = useRef<WebSocketService | null>(null)
  const audioProcessorRef = useRef<AudioProcessor | null>(null)
  const animationFrameRef = useRef<number>()
  const recognitionRef = useRef<SpeechRecognition | null>(null)

  // Expose methods to parent component
  const updateField = (field: keyof FormData, value: string) => {
    console.log(`VoiceForm: Updating field ${field} with value: ${value}`)
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const submitForm = () => {
    console.log("VoiceForm: Submitting form via voice command")
    handleSubmit()
  }

  const clearForm = () => {
    console.log("VoiceForm: Clearing form via voice command")
    setFormData({ name: "", email: "", message: "" })
  }

  // Expose these methods globally for the parent component to use
  useEffect(() => {
    ;(window as any).voiceForm = {
      updateField,
      submitForm,
      clearForm
    }
    
    // Cleanup on unmount
    return () => {
      delete (window as any).voiceForm
    }
  }, [])

  // Initialize speech recognition and audio processing
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
        setLastCommand(transcript)
        console.log("🎤 VoiceForm: Speech recognized:", transcript)
        
        // Send to WebSocket for voice command processing
        if (wsRef.current && wsRef.current.isConnected()) {
          wsRef.current.sendText(transcript)
        }
        
        // Call the voice command callback
        onVoiceCommand?.(transcript)
      }
      
      recognitionRef.current.onerror = (event: any) => {
        console.error("VoiceForm: Speech recognition error:", event.error)
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

    wsRef.current.onAudioReceived = (audioData) => {
      setIsPlaying(true)
      // Stop recording when receiving audio (turn-taking)
      if (isListening) {
        stopListening()
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
      console.log("VoiceForm: Attempting to connect to WebSocket...")
      wsRef.current.connect().catch((error) => {
        console.error("VoiceForm: Failed to connect to WebSocket:", error)
      })
    }

    return () => {
      stopListening()
      // Only disconnect if we created the WebSocket service
      if (!webSocketService && wsRef.current) {
        wsRef.current.disconnect()
      }
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current)
      }
    }
  }, [onVoiceCommand, webSocketService, isConnected])

  // Volume indicator update
  useEffect(() => {
    const updateVolume = () => {
      if (audioProcessorRef.current) {
        const currentVolume = audioProcessorRef.current.getVolume()
        setVolume(currentVolume)
      }
      animationFrameRef.current = requestAnimationFrame(updateVolume)
    }

    if (isListening) {
      updateVolume()
    } else if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current)
      setVolume(0)
    }
  }, [isListening])

  const handleSubmit = () => {
    if (formData.name && formData.email && formData.message) {
      console.log("Form submitted:", formData)
      setIsSubmitted(true)
      setTimeout(() => setIsSubmitted(false), 3000)
    } else {
      alert("Please fill in all fields before submitting")
    }
  }

  const startListening = async () => {
    if (!isConnected) {
      alert("Please connect to the voice service first")
      return
    }

    try {
      await audioProcessorRef.current?.startRecording()
      setIsListening(true)
      
      // Start speech recognition
      if (recognitionRef.current) {
        recognitionRef.current.start()
        console.log("🎤 VoiceForm: Speech recognition started")
      }
    } catch (error) {
      console.error("VoiceForm: Failed to start recording:", error)
      alert("Failed to access microphone. Please check permissions.")
    }
  }

  const stopListening = () => {
    audioProcessorRef.current?.stopRecording()
    setIsListening(false)
    
    // Stop speech recognition
    if (recognitionRef.current) {
      recognitionRef.current.stop()
      console.log("🎤 VoiceForm: Speech recognition stopped")
    }
  }

  const toggleListening = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  const VolumeIndicator = () => (
    <div className="flex items-center space-x-2">
      <div className="flex space-x-1">
        {[...Array(10)].map((_, i) => (
          <div
            key={i}
            className={`w-1 h-6 rounded-full transition-colors duration-100 ${
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
      {/* Voice Input Section */}
      <Card className="bg-blue-50 border-blue-200">
        <CardContent className="pt-6">
          <div className="flex flex-col items-center gap-5">
            <Button
              onClick={toggleListening}
              disabled={!isConnected}
              size="icon"
              className={`w-20 h-20 shadow-lg border-2 border-transparent focus:ring-4 focus:ring-blue-300 transition-all duration-200 ${
                isListening
                  ? "bg-gradient-to-tr from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 animate-pulse"
                  : "bg-gradient-to-tr from-blue-500 to-cyan-500 hover:from-blue-600 hover:to-cyan-600"
              }`}
              aria-label={isListening ? "Stop listening" : "Start listening"}
            >
              {isListening ? (
                <MicOff className="w-8 h-8 text-white drop-shadow" />
              ) : (
                <Mic className="w-8 h-8 text-white drop-shadow" />
              )}
            </Button>

            <div className="text-center">
              <p className="text-lg font-medium text-blue-800">
                {isListening ? "Listening for voice commands..." : "Click to start voice input"}
              </p>
              <p className="text-sm text-blue-600">
                {isConnected ? "Ready for voice commands" : "Connecting..."}
              </p>
            </div>

            {isListening && (
              <div className="w-full max-w-xs">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-blue-700">Microphone Level</span>
                  <Mic className="w-4 h-4 text-blue-500" />
                </div>
                <VolumeIndicator />
              </div>
            )}

            {isPlaying && (
              <div className="flex items-center space-x-2 text-blue-700">
                <Volume2 className="w-5 h-5 animate-pulse" />
                <span className="font-medium">AI is speaking...</span>
              </div>
            )}

            {recognizedText && (
              <div className="w-full max-w-xs bg-white rounded-lg p-3 border border-green-200">
                <div className="flex items-center space-x-2">
                  <Mic className="w-4 h-4 text-green-600" />
                  <span className="text-green-800 text-sm">"{recognizedText}"</span>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Form Fields */}
      <div className="grid gap-4">
        <div className="space-y-2">
          <Label htmlFor="name">Name</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData((prev) => ({ ...prev, name: e.target.value }))}
            placeholder="Say: 'My name is John Doe'"
            className={formData.name ? "border-green-300 bg-green-50" : ""}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            value={formData.email}
            onChange={(e) => setFormData((prev) => ({ ...prev, email: e.target.value }))}
            placeholder="Say: 'My email is john@example.com'"
            className={formData.email ? "border-green-300 bg-green-50" : ""}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="message">Message</Label>
          <Textarea
            id="message"
            value={formData.message}
            onChange={(e) => setFormData((prev) => ({ ...prev, message: e.target.value }))}
            placeholder="Say: 'My message is I would like to learn more about your services'"
            rows={4}
            className={formData.message ? "border-green-300 bg-green-50" : ""}
          />
        </div>
      </div>

      <div className="flex space-x-4">
        <Button
          onClick={handleSubmit}
          disabled={!formData.name || !formData.email || !formData.message}
          className="flex-1"
        >
          {isSubmitted ? (
            <>
              <Check className="w-4 h-4 mr-2" />
              Submitted!
            </>
          ) : (
            <>
              <Send className="w-4 h-4 mr-2" />
              Submit
            </>
          )}
        </Button>
      </div>

      {lastCommand && (
        <Card className="bg-blue-50 border-blue-200">
          <CardContent className="pt-4">
            <p className="text-sm text-blue-800">
              <strong>Last voice command:</strong> {lastCommand}
            </p>
          </CardContent>
        </Card>
      )}

      <div className="text-xs text-gray-500 space-y-1">
        <p>
          <strong>Voice Commands:</strong>
        </p>
        <p>• "My name is [name]" - Sets the name field</p>
        <p>• "My email is [email]" - Sets the email field</p>
        <p>• "My message is [message]" - Sets the message field</p>
        <p>• "Submit" or "Send form" - Submits the form</p>
        <p>• "Clear" or "Reset" - Clears all fields</p>
      </div>
    </div>
  )
}
