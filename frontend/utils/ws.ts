export interface RTVIMessage {
  type: "audio" | "text" | "control" | "error"
  data?: any
  timestamp?: number
}

export class WebSocketService {
  private ws: WebSocket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private isConnecting = false

  public onConnectionChange?: (connected: boolean) => void
  public onAudioReceived?: (audioData: ArrayBuffer) => void
  public onTextReceived?: (text: string) => void
  public onError?: (error: string) => void

  constructor(private url = "ws://localhost:8000/ws") {}

  async connect(): Promise<void> {
    if (this.isConnecting || this.isConnected()) {
      return
    }

    this.isConnecting = true

    try {
      this.ws = new WebSocket(this.url)

      this.ws.onopen = () => {
        console.log("WebSocket connected")
        this.isConnecting = false
        this.reconnectAttempts = 0
        this.onConnectionChange?.(true)

        // Send initial connection message
        this.send({
          type: "control",
          data: { action: "connect", protocol: "rtvi" },
        })
      }

      this.ws.onmessage = (event) => {
        this.handleMessage(event)
      }

      this.ws.onclose = (event) => {
        console.log("WebSocket closed:", event.code, event.reason)
        this.isConnecting = false
        this.onConnectionChange?.(false)

        if (!event.wasClean && this.reconnectAttempts < this.maxReconnectAttempts) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = (error) => {
        console.error("WebSocket error:", error)
        this.isConnecting = false
        this.onError?.("Connection error")
      }
    } catch (error) {
      this.isConnecting = false
      console.error("Failed to connect:", error)
      throw error
    }
  }

  private handleMessage(event: MessageEvent) {
    try {
      if (event.data instanceof ArrayBuffer) {
        // Handle binary audio data
        this.onAudioReceived?.(event.data)
        return
      }

      if (typeof event.data === "string") {
        const message: RTVIMessage = JSON.parse(event.data)

        switch (message.type) {
          case "audio":
            if (message.data) {
              // Convert base64 to ArrayBuffer if needed
              const audioData = this.base64ToArrayBuffer(message.data)
              this.onAudioReceived?.(audioData)
            }
            break

          case "text":
            this.onTextReceived?.(message.data)
            break

          case "error":
            this.onError?.(message.data)
            break

          default:
            console.log("Unknown message type:", message.type)
        }
      }
    } catch (error) {
      console.error("Error handling message:", error)
    }
  }

  private base64ToArrayBuffer(base64: string): ArrayBuffer {
    const binaryString = atob(base64)
    const bytes = new Uint8Array(binaryString.length)
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }
    return bytes.buffer
  }

  private arrayBufferToBase64(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer)
    let binary = ""
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return btoa(binary)
  }

  private scheduleReconnect() {
    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`)

    setTimeout(() => {
      this.connect().catch(console.error)
    }, delay)
  }

  send(message: RTVIMessage): void {
    if (!this.isConnected()) {
      console.warn("WebSocket not connected")
      return
    }

    try {
      this.ws!.send(JSON.stringify(message))
    } catch (error) {
      console.error("Error sending message:", error)
    }
  }

  sendAudio(audioData: ArrayBuffer): void {
    if (!this.isConnected()) {
      return
    }

    try {
      // Send as binary data
      this.ws!.send(audioData)
    } catch (error) {
      console.error("Error sending audio:", error)
    }
  }

  sendText(text: string): void {
    this.send({
      type: "text",
      data: text,
      timestamp: Date.now(),
    })
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close(1000, "Client disconnect")
      this.ws = null
    }
  }
}
