"use client"

import { useState, useRef, useEffect } from "react"
import { MicStream } from "@/components/mic-stream"
import { VoiceForm } from "@/components/voice-form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { WebSocketService } from "@/utils/ws"

export default function Home() {
  const [isConnected, setIsConnected] = useState(false)
  const [activeTab, setActiveTab] = useState("stream")
  const wsRef = useRef<WebSocketService | null>(null)

  useEffect(() => {
    // Initialize WebSocket service for voice commands
    wsRef.current = new WebSocketService()

    wsRef.current.onConnectionChange = (connected) => {
      setIsConnected(connected)
    }

    wsRef.current.onTextReceived = (text) => {
      processVoiceCommand(text)
    }

    wsRef.current.onVoiceCommandResponse = (response) => {
      handleVoiceCommandResponse(response)
    }

    // Connect to WebSocket immediately
    wsRef.current.connect().catch((error) => {
      console.error("Failed to connect to WebSocket:", error)
    })

    return () => {
      wsRef.current?.disconnect()
    }
  }, [])

  const processVoiceCommand = (command: string) => {
    const lowerCommand = command.toLowerCase()
    console.log("Processing voice command:", command)

    // Tab switching commands
    if (lowerCommand.includes("open voice form") || lowerCommand.includes("switch to form") || lowerCommand.includes("go to form")) {
      setActiveTab("form")
      console.log("Switching to Voice Form tab")
      return
    }

    if (lowerCommand.includes("open voice stream") || lowerCommand.includes("switch to stream") || lowerCommand.includes("go to stream")) {
      setActiveTab("stream")
      console.log("Switching to Voice Stream tab")
      return
    }

    // Other voice commands can be added here
    console.log("Unknown voice command:", command)
  }

  const handleVoiceCommandResponse = (response: any) => {
    console.log("Handling voice command response:", response)
    
    // Get the voice form instance once
    const voiceForm = (window as any).voiceForm
    
    switch (response.action) {
      case "switch_tab":
        if (response.tab === "form") {
          setActiveTab("form")
          console.log("Switched to form tab")
        } else if (response.tab === "stream") {
          setActiveTab("stream")
          console.log("Switched to stream tab")
        }
        break
        
      case "fill_field":
        // Update the form field using the exposed method
        if (voiceForm && voiceForm.updateField) {
          voiceForm.updateField(response.field, response.value)
          console.log(`Updated field ${response.field} with ${response.value}`)
        } else {
          console.log(`Field ${response.field} should be filled with ${response.value}`)
        }
        break
        
      case "submit_form":
        if (voiceForm && voiceForm.submitForm) {
          voiceForm.submitForm()
          console.log("Form submitted")
        } else {
          console.log("Form should be submitted")
        }
        break
        
      case "clear_form":
        if (voiceForm && voiceForm.clearForm) {
          voiceForm.clearForm()
          console.log("Form cleared")
        } else {
          console.log("Form should be cleared")
        }
        break
        
      default:
        console.log("Unknown action:", response.action)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Voice AI Assistant</h1>
          <p className="text-lg text-gray-600">Powered by Gemini Live - Speak naturally and interact with AI</p>
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
            <h3 className="font-semibold text-blue-800 mb-2">Voice Commands:</h3>
            <div className="text-sm text-blue-700 space-y-1">
              <p>• "Open voice form" - Switch to the form tab</p>
              <p>• "Open voice stream" - Switch to the stream tab</p>
              <p>• "My name is [name]" - Fill the name field</p>
              <p>• "My email is [email]" - Fill the email field</p>
              <p>• "My message is [message]" - Fill the message field</p>
              <p>• "Submit" or "Send form" - Submit the form</p>
            </div>
          </div>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="stream">Voice Stream</TabsTrigger>
            <TabsTrigger value="form">Voice Form</TabsTrigger>
          </TabsList>

          <TabsContent value="stream" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Live Voice Interaction</CardTitle>
                <CardDescription>Start speaking to interact with Gemini Live AI</CardDescription>
              </CardHeader>
              <CardContent>
                <MicStream onConnectionChange={setIsConnected} />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="form" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Voice-Controlled Form</CardTitle>
                <CardDescription>Fill out the form using voice commands like "My name is John"</CardDescription>
              </CardHeader>
              <CardContent>
                <VoiceForm isConnected={isConnected} />
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

                  <div className="mt-8 text-center space-y-4">
            <div
              className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
                isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
              }`}
            >
              <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? "bg-green-500" : "bg-red-500"}`} />
              {isConnected ? "Connected" : "Disconnected"}
            </div>
            
            {/* Test buttons for voice commands */}
            <div className="flex justify-center space-x-2">
              <button
                onClick={() => wsRef.current?.sendText("open voice form")}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                Test: Open Form
              </button>
              <button
                onClick={() => wsRef.current?.sendText("my name is John Doe")}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                Test: Set Name
              </button>
              <button
                onClick={() => wsRef.current?.sendText("my email is john@example.com")}
                className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
              >
                Test: Set Email
              </button>
            </div>
          </div>
      </div>
    </main>
  )
}
