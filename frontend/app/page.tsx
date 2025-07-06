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
  const [wsReady, setWsReady] = useState(false)
  const [debugMessages, setDebugMessages] = useState<string[]>([])
  const wsRef = useRef<WebSocketService | null>(null)

  const addDebugMessage = (message: string) => {
    console.log(`🔍 DEBUG: ${message}`)
    setDebugMessages(prev => [...prev.slice(-9), message]) // Keep last 10 messages
  }

  useEffect(() => {
    addDebugMessage("Initializing WebSocket service...")
    
    // Initialize WebSocket service for voice commands
    wsRef.current = new WebSocketService()

    wsRef.current.onConnectionChange = (connected) => {
      addDebugMessage(`WebSocket connection changed: ${connected}`)
      setIsConnected(connected)
      if (connected) {
        setWsReady(true)
        addDebugMessage("WebSocket is ready for voice commands")
      }
    }

    // Only process voice commands from voice command responses, not from all text
    wsRef.current.onVoiceCommandResponse = (response) => {
      addDebugMessage(`Received voice command response: ${JSON.stringify(response)}`)
      handleVoiceCommandResponse(response)
    }

    // Connect to WebSocket immediately
    addDebugMessage("Attempting to connect to WebSocket...")
    wsRef.current.connect().catch((error) => {
      addDebugMessage(`Failed to connect to WebSocket: ${error}`)
      console.error("Failed to connect to WebSocket:", error)
    })

    return () => {
      addDebugMessage("Cleaning up WebSocket connection...")
      wsRef.current?.disconnect()
    }
  }, [])

  // This function is now only called manually for testing or from actual voice input
  const processVoiceCommand = (command: string) => {
    const lowerCommand = command.toLowerCase()
    addDebugMessage(`Processing voice command: ${command}`)

    // Tab switching commands
    if (lowerCommand.includes("open voice form") || lowerCommand.includes("switch to form") || lowerCommand.includes("go to form")) {
      addDebugMessage("Switching to Voice Form tab")
      setActiveTab("form")
      console.log("✅ Switching to Voice Form tab")
      return
    }

    if (lowerCommand.includes("open voice stream") || lowerCommand.includes("switch to stream") || lowerCommand.includes("go to stream")) {
      addDebugMessage("Switching to Voice Stream tab")
      setActiveTab("stream")
      console.log("✅ Switching to Voice Stream tab")
      return
    }

        // Form field commands - process regardless of current tab (for better UX)
    // This allows voice commands to work even if user is on stream tab but wants to fill form
    
    // Name extraction
    const namePatterns = [
      /(?:my name is|i am|i'm|name is|call me)\s+([a-zA-Z\s]+)/i,
      /(?:set name to|put name as)\s+([a-zA-Z\s]+)/i,
      /(?:name)\s+([a-zA-Z\s]+)/i
    ]
    
    for (const pattern of namePatterns) {
      const nameMatch = lowerCommand.match(pattern)
      if (nameMatch) {
        const name = nameMatch[1].trim()
        addDebugMessage(`Setting name field to: ${name}`)
        updateFormField("name", name)
        console.log(`✅ Set name to: ${name}`)
        return
      }
    }

    // Email extraction
    const emailPatterns = [
      /(?:my email is|email is|my email address is|email address)\s+([^\s]+@[^\s]+\.[^\s]+)/i,
      /(?:set email to|put email as)\s+([^\s]+@[^\s]+\.[^\s]+)/i,
      /(?:email)\s+([^\s]+@[^\s]+\.[^\s]+)/i
    ]
    
    for (const pattern of emailPatterns) {
      const emailMatch = lowerCommand.match(pattern)
      if (emailMatch) {
        const email = emailMatch[1].trim()
        addDebugMessage(`Setting email field to: ${email}`)
        updateFormField("email", email)
        console.log(`✅ Set email to: ${email}`)
        return
      }
    }

    // Message extraction
    const messagePatterns = [
      /(?:my message is|message is|i want to say|tell them)\s+(.+)/i,
      /(?:set message to|put message as)\s+(.+)/i,
      /(?:message)\s+(.+)/i
    ]
    
    for (const pattern of messagePatterns) {
      const messageMatch = lowerCommand.match(pattern)
      if (messageMatch) {
        const message = messageMatch[1].trim()
        addDebugMessage(`Setting message field to: ${message}`)
        updateFormField("message", message)
        console.log(`✅ Set message to: ${message}`)
        return
      }
    }

    // Submit command
    const submitPatterns = [
      /(?:submit|send form|send it|submit form|send the form)/i,
      /(?:i'm done|finished|complete|done)/i
    ]
    
    for (const pattern of submitPatterns) {
      if (pattern.test(lowerCommand)) {
        addDebugMessage("Submitting form")
        submitForm()
        console.log("✅ Submitting form")
        return
      }
    }

    // Clear command
    const clearPatterns = [
      /(?:clear|reset|clear form|reset form|start over)/i,
      /(?:clear all|reset all|clear everything)/i
    ]
    
    for (const pattern of clearPatterns) {
      if (pattern.test(lowerCommand)) {
        addDebugMessage("Clearing form")
        clearForm()
        console.log("✅ Cleared form")
        return
      }
    }

    addDebugMessage(`No matching command found for: ${command}`)
    console.log("❌ No matching command found for:", command)
  }

  const updateFormField = (field: string, value: string) => {
    addDebugMessage(`Updating form field: ${field} = ${value}`)
    const voiceForm = (window as any).voiceForm
    if (voiceForm && voiceForm.updateField) {
      voiceForm.updateField(field, value)
      addDebugMessage(`Form field updated successfully`)
    } else {
      addDebugMessage(`VoiceForm not available for field update`)
      console.warn("VoiceForm not available for field update")
    }
  }

  const submitForm = () => {
    addDebugMessage("Submitting form")
    const voiceForm = (window as any).voiceForm
    if (voiceForm && voiceForm.submitForm) {
      voiceForm.submitForm()
      addDebugMessage("Form submitted successfully")
    } else {
      addDebugMessage("VoiceForm not available for submission")
      console.warn("VoiceForm not available for submission")
    }
  }

  const clearForm = () => {
    addDebugMessage("Clearing form")
    const voiceForm = (window as any).voiceForm
    if (voiceForm && voiceForm.clearForm) {
      voiceForm.clearForm()
      addDebugMessage("Form cleared successfully")
    } else {
      addDebugMessage("VoiceForm not available for clearing")
      console.warn("VoiceForm not available for clearing")
    }
  }

  const handleVoiceCommandResponse = (response: any) => {
    addDebugMessage(`Handling voice command response: ${JSON.stringify(response)}`)
    console.log("🎯 Main page received voice command response:", response)
    
    switch (response.action) {
      case "switch_tab":
        if (response.tab === "form") {
          addDebugMessage("Switching to form tab via response")
          setActiveTab("form")
          console.log("✅ Switched to form tab")
        } else if (response.tab === "stream") {
          addDebugMessage("Switching to stream tab via response")
          setActiveTab("stream")
          console.log("✅ Switched to stream tab")
        }
        break
        
      case "fill_field":
        addDebugMessage(`Filling field via response: ${response.field} = ${response.value}`)
        updateFormField(response.field, response.value)
        break
        
      case "submit_form":
        addDebugMessage("Submitting form via response")
        submitForm()
        break
        
      case "clear_form":
        addDebugMessage("Clearing form via response")
        clearForm()
        break
        
      default:
        addDebugMessage(`Unknown action in response: ${response.action}`)
        console.log("❌ Unknown action:", response.action)
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
                <MicStream 
                  onConnectionChange={setIsConnected} 
                  webSocketService={wsReady ? wsRef.current! : undefined}
                  onVoiceCommand={processVoiceCommand}
                />
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
                <VoiceForm 
                  isConnected={isConnected} 
                  webSocketService={wsReady ? wsRef.current! : undefined}
                  onVoiceCommand={processVoiceCommand}
                />
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
              onClick={() => {
                addDebugMessage("Test button clicked: Open Form")
                wsRef.current?.sendText("open voice form")
                processVoiceCommand("open voice form")
              }}
              className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            >
              Test: Open Form
            </button>
            <button
              onClick={() => {
                addDebugMessage("Test button clicked: Set Name")
                wsRef.current?.sendText("my name is John Doe")
                processVoiceCommand("my name is John Doe")
              }}
              className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            >
              Test: Set Name
            </button>
            <button
              onClick={() => {
                addDebugMessage("Test button clicked: Set Email")
                wsRef.current?.sendText("my email is john@example.com")
                processVoiceCommand("my email is john@example.com")
              }}
              className="px-3 py-1 bg-blue-500 text-white rounded text-sm hover:bg-blue-600"
            >
              Test: Set Email
            </button>
          </div>

          {/* Debug messages */}
          <div className="mt-4 p-4 bg-gray-100 rounded-lg border">
            <h4 className="font-semibold text-gray-800 mb-2">Debug Messages:</h4>
            <div className="text-xs text-gray-600 space-y-1 max-h-32 overflow-y-auto">
              {debugMessages.map((msg, index) => (
                <div key={index} className="font-mono">{msg}</div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
