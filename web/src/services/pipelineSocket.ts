import type { PipelineSocketEvent } from '../types/pipeline'

export type SocketState = 'reserved' | 'connecting' | 'connected' | 'closed' | 'error'
export type PipelineSocketListener = (event: PipelineSocketEvent) => void

export interface PipelineSocketGateway {
  readonly state: SocketState
  connect(projectId: string): void
  disconnect(): void
  subscribe(listener: PipelineSocketListener): () => void
}

/**
 * Reserved realtime boundary. Without VITE_PIPELINE_WS_URL it intentionally
 * stays inert so the prototype never presents mock data as a live backend.
 */
export class BrowserPipelineSocket implements PipelineSocketGateway {
  private socket: WebSocket | null = null
  private listeners = new Set<PipelineSocketListener>()
  private currentState: SocketState = 'reserved'

  constructor(private readonly baseUrl = import.meta.env.VITE_PIPELINE_WS_URL ?? '') {}

  get state(): SocketState {
    return this.currentState
  }

  connect(projectId: string): void {
    if (!this.baseUrl || this.socket) return

    this.currentState = 'connecting'
    const target = new URL(this.baseUrl)
    target.searchParams.set('project_id', projectId)
    this.socket = new WebSocket(target)

    this.socket.addEventListener('open', () => {
      this.currentState = 'connected'
    })
    this.socket.addEventListener('message', (message) => {
      const event = JSON.parse(String(message.data)) as PipelineSocketEvent
      this.listeners.forEach((listener) => listener(event))
    })
    this.socket.addEventListener('error', () => {
      this.currentState = 'error'
    })
    this.socket.addEventListener('close', () => {
      this.currentState = 'closed'
      this.socket = null
    })
  }

  disconnect(): void {
    this.socket?.close()
    this.socket = null
    this.currentState = this.baseUrl ? 'closed' : 'reserved'
  }

  subscribe(listener: PipelineSocketListener): () => void {
    this.listeners.add(listener)
    return () => this.listeners.delete(listener)
  }
}

export const pipelineSocket = new BrowserPipelineSocket()
