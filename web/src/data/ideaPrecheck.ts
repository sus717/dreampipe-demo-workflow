export interface IdeaPrecheckResult {
  idea: string
  overallScore: number
  tokenLoadScore: number
  viralScore: number
  estimatedTokens: number
  verdict: 'ready' | 'revise' | 'risky'
  highlights: string[]
  warnings: string[]
}

const strongHookWords = ['只剩', '失踪', '调休', '追', '找到', '挑战', '打卡', '反转', '悬念', '荒诞']
const localWords = ['福州', '三坊七巷', '南后街', '衣锦坊', '黄巷', '塔巷', '文儒坊', '闽都', '虎纠']
const vagueWords = ['高级', '震撼', '大片', '炫酷', '史诗', '梦幻', '绝美', '赛博', '未来感']
const costWords = ['超长', '电影级', '大量', '复杂', '群演', '爆炸', '多角色', '全景切换', '十几个镜头']

function clamp(value: number) {
  return Math.max(0, Math.min(100, Math.round(value)))
}

function countHits(text: string, words: string[]) {
  return words.filter((word) => text.includes(word)).length
}

export function evaluateIdeaPrecheck(idea: string): IdeaPrecheckResult {
  const normalized = idea.trim()
  const charCount = normalized.length
  const estimatedTokens = Math.max(20, Math.ceil(charCount * 1.7))
  const hookHits = countHits(normalized, strongHookWords)
  const localHits = countHits(normalized, localWords)
  const vagueHits = countHits(normalized, vagueWords)
  const costHits = countHits(normalized, costWords)
  const hasAudience = /年轻|游客|抖音|小红书|本地|City Walk|city walk/i.test(normalized)
  const hasCta = /来|去|找到|打卡|预约|下单|关注|收藏/.test(normalized)
  const hasShortFormat = /15秒|15s|9:16|竖屏|三镜|3镜/.test(normalized)

  const tokenPenalty =
    Math.max(0, charCount - 90) * 0.22 +
    vagueHits * 7 +
    costHits * 11 +
    Math.max(0, estimatedTokens - 220) * 0.1

  const tokenLoadScore = clamp(92 - tokenPenalty)
  const viralScore = clamp(
    36 +
      hookHits * 11 +
      localHits * 7 +
      (hasAudience ? 10 : 0) +
      (hasCta ? 10 : 0) +
      (hasShortFormat ? 8 : 0) -
      vagueHits * 5,
  )
  const overallScore = clamp(tokenLoadScore * 0.36 + viralScore * 0.46 + (hasCta ? 10 : 2) + (hasShortFormat ? 8 : 0))

  const warnings: string[] = []
  if (tokenLoadScore < 70) warnings.push('想法信息量偏重，后续 Prompt 可能更耗 token')
  if (viralScore < 70) warnings.push('传播钩子还不够明确，建议增加反转或打卡动作')
  if (!hasCta) warnings.push('缺少明确 CTA，观众看完不知道下一步做什么')
  if (vagueHits > 0) warnings.push('抽象形容词偏多，建议换成具体画面')

  const highlights: string[] = []
  if (hookHits > 0) highlights.push('有短视频钩子')
  if (localHits > 0) highlights.push('有本地文旅识别点')
  if (hasShortFormat) highlights.push('规格清楚，方便控成本')
  if (hasCta) highlights.push('有转化动作')

  const verdict = overallScore >= 82 && tokenLoadScore >= 72 ? 'ready' : overallScore >= 65 ? 'revise' : 'risky'

  return {
    idea: normalized,
    overallScore,
    tokenLoadScore,
    viralScore,
    estimatedTokens,
    verdict,
    highlights: highlights.slice(0, 3),
    warnings: warnings.slice(0, 3),
  }
}
