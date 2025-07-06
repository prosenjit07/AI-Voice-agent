export class AudioProcessor {
  private audioContext: AudioContext | null = null
  private mediaStream: MediaStream | null = null
  private processor: ScriptProcessorNode | null = null
  private analyser: AnalyserNode | null = null
  private dataArray: Uint8Array | null = null
  private isRecording = false
  private speechDetectionThreshold = 30
  private silenceTimeout: NodeJS.Timeout | null = null
  private isSpeaking = false

  public onAudioData?: (audioData: ArrayBuffer) => void
  public onSpeechStart?: () => void
  public onSpeechEnd?: () => void

  async startRecording(): Promise<void> {
    try {
      // Request microphone access
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      })

      // Create audio context
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000,
      })

      // Create analyser for volume detection
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = 256
      this.dataArray = new Uint8Array(this.analyser.frequencyBinCount)

      // Create source from microphone
      const source = this.audioContext.createMediaStreamSource(this.mediaStream)
      source.connect(this.analyser)

      // Create processor for audio data
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1)

      this.processor.onaudioprocess = (event) => {
        if (!this.isRecording) return

        const inputBuffer = event.inputBuffer
        const inputData = inputBuffer.getChannelData(0)

        // Convert to 16-bit PCM
        const pcmData = this.floatTo16BitPCM(inputData)

        // Detect speech
        this.detectSpeech()

        // Send audio data
        this.onAudioData?.(pcmData.buffer)
      }

      source.connect(this.processor)
      this.processor.connect(this.audioContext.destination)

      this.isRecording = true
      console.log("Recording started")
    } catch (error) {
      console.error("Error starting recording:", error)
      throw error
    }
  }

  stopRecording(): void {
    this.isRecording = false

    if (this.processor) {
      this.processor.disconnect()
      this.processor = null
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop())
      this.mediaStream = null
    }

    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    if (this.silenceTimeout) {
      clearTimeout(this.silenceTimeout)
      this.silenceTimeout = null
    }

    console.log("Recording stopped")
  }

  private floatTo16BitPCM(input: Float32Array): Int16Array {
    const output = new Int16Array(input.length)
    for (let i = 0; i < input.length; i++) {
      const sample = Math.max(-1, Math.min(1, input[i]))
      output[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff
    }
    return output
  }

  private detectSpeech(): void {
    if (!this.analyser || !this.dataArray) return

    this.analyser.getByteFrequencyData(this.dataArray)

    // Calculate average volume
    const average = this.dataArray.reduce((sum, value) => sum + value, 0) / this.dataArray.length

    const wasSpeaking = this.isSpeaking
    this.isSpeaking = average > this.speechDetectionThreshold

    // Speech started
    if (this.isSpeaking && !wasSpeaking) {
      this.onSpeechStart?.()
      if (this.silenceTimeout) {
        clearTimeout(this.silenceTimeout)
        this.silenceTimeout = null
      }
    }

    // Speech ended (with delay to avoid false positives)
    if (!this.isSpeaking && wasSpeaking) {
      this.silenceTimeout = setTimeout(() => {
        this.onSpeechEnd?.()
      }, 500)
    }
  }

  getVolume(): number {
    if (!this.analyser || !this.dataArray) return 0

    this.analyser.getByteFrequencyData(this.dataArray)
    const average = this.dataArray.reduce((sum, value) => sum + value, 0) / this.dataArray.length
    return Math.min(1, average / 128)
  }

  async playAudio(audioData: ArrayBuffer): Promise<void> {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)()
    }

    try {
      const audioBuffer = await this.audioContext.decodeAudioData(audioData.slice(0))
      const source = this.audioContext.createBufferSource()
      source.buffer = audioBuffer
      source.connect(this.audioContext.destination)

      return new Promise((resolve) => {
        source.onended = () => resolve()
        source.start()
      })
    } catch (error) {
      console.error("Error playing audio:", error)
    }
  }

  stopPlayback(): void {
    // In a real implementation, you'd keep track of playing sources
    // and stop them here for interruption handling
    console.log("Stopping audio playback for interruption")
  }
}
