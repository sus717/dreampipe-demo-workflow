import { describe, expect, it, vi } from 'vitest'
import { BrowserPipelineSocket } from './pipelineSocket'

describe('BrowserPipelineSocket', () => {
  it('remains reserved when the backend URL is not configured', () => {
    const gateway = new BrowserPipelineSocket('')
    gateway.connect('demo-project')
    expect(gateway.state).toBe('reserved')
  })

  it('allows subscribers to be removed without opening a connection', () => {
    const gateway = new BrowserPipelineSocket('')
    const listener = vi.fn()
    const unsubscribe = gateway.subscribe(listener)
    unsubscribe()
    gateway.disconnect()
    expect(listener).not.toHaveBeenCalled()
    expect(gateway.state).toBe('reserved')
  })
})
