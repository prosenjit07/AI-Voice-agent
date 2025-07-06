"use client"

import { useState } from "react"
import { MicStream } from "@/components/mic-stream"
import { VoiceForm } from "@/components/voice-form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default function Home() {
  const [isConnected, setIsConnected] = useState(false)

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <div className="container mx-auto max-w-4xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Voice AI Assistant</h1>
          <p className="text-lg text-gray-600">Powered by Gemini Live - Speak naturally and interact with AI</p>
        </div>

        <Tabs defaultValue="stream" className="w-full">
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

        <div className="mt-8 text-center">
          <div
            className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              isConnected ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"
            }`}
          >
            <div className={`w-2 h-2 rounded-full mr-2 ${isConnected ? "bg-green-500" : "bg-red-500"}`} />
            {isConnected ? "Connected" : "Disconnected"}
          </div>
        </div>
      </div>
    </main>
  )
}
