"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { Mic, Send, Check } from "lucide-react"

interface VoiceFormProps {
  isConnected: boolean
}

interface FormData {
  name: string
  email: string
  message: string
}

export function VoiceForm({ isConnected }: VoiceFormProps) {
  const [formData, setFormData] = useState<FormData>({
    name: "",
    email: "",
    message: "",
  })
  const [isListening, setIsListening] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [lastCommand, setLastCommand] = useState("")

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

    setIsListening(true)
    // In a real implementation, this would start audio capture
    // For now, we'll simulate it
    setTimeout(() => setIsListening(false), 3000)
  }

  return (
    <div className="space-y-6">
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
          onClick={startListening}
          disabled={!isConnected || isListening}
          variant="outline"
          className="flex-1 bg-transparent"
        >
          <Mic className={`w-4 h-4 mr-2 ${isListening ? "animate-pulse" : ""}`} />
          {isListening ? "Listening..." : "Voice Fill"}
        </Button>

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
              <strong>Last command:</strong> {lastCommand}
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
