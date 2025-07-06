"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent } from "@/components/ui/card"
import { Mic, Send, Check } from "lucide-react"
import { WebSocketService } from "@/utils/ws"

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
    setFormData(prev => ({ ...prev, [field]: value }))
  }

  const submitForm = () => {
    handleSubmit()
  }

  const clearForm = () => {
    setFormData({ name: "", email: "", message: "" })
  }

  // Expose these methods globally for the parent component to use
  useEffect(() => {
    ;(window as any).voiceForm = {
      updateField,
      submitForm,
      clearForm
    }
  }, [])

  const processVoiceCommand = (command: string) => {
    const lowerCommand = command.toLowerCase()
    console.log("VoiceForm processing command:", command)

    // Name extraction - more flexible patterns
    const namePatterns = [
      /(?:my name is|i am|i'm|name is|call me)\s+([a-zA-Z\s]+)/i,
      /(?:set name to|put name as)\s+([a-zA-Z\s]+)/i,
      /(?:name)\s+([a-zA-Z\s]+)/i
    ]
    
    for (const pattern of namePatterns) {
      const nameMatch = lowerCommand.match(pattern)
      if (nameMatch) {
        const name = nameMatch[1].trim()
        setFormData((prev) => ({ ...prev, name }))
        console.log("Set name to:", name)
        return
      }
    }

    // Email extraction - more flexible patterns
    const emailPatterns = [
      /(?:my email is|email is|my email address is|email address)\s+([^\s]+@[^\s]+\.[^\s]+)/i,
      /(?:set email to|put email as)\s+([^\s]+@[^\s]+\.[^\s]+)/i,
      /(?:email)\s+([^\s]+@[^\s]+\.[^\s]+)/i
    ]
    
    for (const pattern of emailPatterns) {
      const emailMatch = lowerCommand.match(pattern)
      if (emailMatch) {
        const email = emailMatch[1].trim()
        setFormData((prev) => ({ ...prev, email }))
        console.log("Set email to:", email)
        return
      }
    }

    // Message extraction - more flexible patterns
    const messagePatterns = [
      /(?:my message is|message is|i want to say|tell them)\s+(.+)/i,
      /(?:set message to|put message as)\s+(.+)/i,
      /(?:message)\s+(.+)/i
    ]
    
    for (const pattern of messagePatterns) {
      const messageMatch = lowerCommand.match(pattern)
      if (messageMatch) {
        const message = messageMatch[1].trim()
        setFormData((prev) => ({ ...prev, message }))
        console.log("Set message to:", message)
        return
      }
    }

    // Submit command - more variations
    const submitPatterns = [
      /(?:submit|send form|send it|submit form|send the form)/i,
      /(?:i'm done|finished|complete|done)/i
    ]
    
    for (const pattern of submitPatterns) {
      if (pattern.test(lowerCommand)) {
        handleSubmit()
        console.log("Submitting form")
        return
      }
    }

    // Clear command - more variations
    const clearPatterns = [
      /(?:clear|reset|clear form|reset form|start over)/i,
      /(?:clear all|reset all|clear everything)/i
    ]
    
    for (const pattern of clearPatterns) {
      if (pattern.test(lowerCommand)) {
        setFormData({ name: "", email: "", message: "" })
        console.log("Cleared form")
        return
      }
    }

    console.log("No matching command found for:", command)
  }

  const handleVoiceCommandResponse = (response: any) => {
    console.log("VoiceForm handling voice command response:", response)
    
    switch (response.action) {
      case "fill_field":
        if (response.field === "name") {
          setFormData((prev) => ({ ...prev, name: response.value }))
        } else if (response.field === "email") {
          setFormData((prev) => ({ ...prev, email: response.value }))
        } else if (response.field === "message") {
          setFormData((prev) => ({ ...prev, message: response.value }))
        }
        break
        
      case "submit_form":
        handleSubmit()
        break
        
      case "clear_form":
        setFormData({ name: "", email: "", message: "" })
        break
        
      default:
        console.log("Unknown action in VoiceForm:", response.action)
    }
  }

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
