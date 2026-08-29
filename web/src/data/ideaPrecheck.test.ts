import { describe, expect, it } from 'vitest'
import { evaluateIdeaPrecheck } from './ideaPrecheck'

describe('idea precheck scoring', () => {
  it('rewards a specific short-video idea with hook, place, format, and CTA', () => {
    const result = evaluateIdeaPrecheck(
      '福州三坊七巷 City Walk 15s 竖屏短片：牛导发现三坊七巷只剩六巷，结尾反转第七巷今日调休，CTA 来三坊七巷找到你的第七巷。',
    )

    expect(result.verdict).toBe('ready')
    expect(result.overallScore).toBeGreaterThanOrEqual(82)
    expect(result.viralScore).toBeGreaterThan(result.tokenLoadScore - 20)
    expect(result.highlights).toContain('有短视频钩子')
  })

  it('flags vague and expensive ideas before generation starts', () => {
    const result = evaluateIdeaPrecheck(
      '做一个电影级超长大片，加入大量复杂多角色和十几个镜头，要震撼、梦幻、赛博、史诗，最好全景切换。',
    )

    expect(result.verdict).not.toBe('ready')
    expect(result.tokenLoadScore).toBeLessThan(70)
    expect(result.warnings).toContain('想法信息量偏重，后续 Prompt 可能更耗 token')
  })
})
