import { describe, expect, it } from 'vitest'
import { demoOrder, getMockPipeline } from './mockPipeline'

describe('DreamPipe mock runtime', () => {
  it('provides the four deterministic demo phases', () => {
    expect(demoOrder).toEqual(['waiting', 'running', 'retrying', 'completed'])
    expect(demoOrder.map((phase) => getMockPipeline(phase).phase)).toEqual(demoOrder)
  })

  it('keeps the selective retry isolated to S03', () => {
    const retrying = getMockPipeline('retrying')
    expect(retrying.shots.find((shot) => shot.id === 'S03')).toMatchObject({
      state: 'retrying',
      attempt: 1,
      score: 78,
    })
    expect(retrying.shots.filter((shot) => shot.state === 'passed')).toHaveLength(2)
  })

  it('records only S03 as attempt two after repair', () => {
    const completed = getMockPipeline('completed')
    expect(completed.shots.map(({ id, attempt, state }) => ({ id, attempt, state }))).toEqual([
      { id: 'S01', attempt: 1, state: 'passed' },
      { id: 'S02', attempt: 1, state: 'passed' },
      { id: 'S03', attempt: 2, state: 'passed' },
    ])
    expect(completed.retry.scoreAfter).toBe(95)
    expect(completed.preview.ready).toBe(false)
  })

  it('recomputes precheck from a custom user idea', () => {
    const custom = getMockPipeline('waiting', '电影级超长大片，大量复杂多角色，十几个镜头，震撼梦幻赛博。')
    expect(custom.ideaPrecheck.idea).toContain('电影级超长大片')
    expect(custom.ideaPrecheck.tokenLoadScore).toBeLessThan(70)
  })
})
