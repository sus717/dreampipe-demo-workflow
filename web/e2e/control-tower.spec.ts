import { expect, test } from '@playwright/test'

test('renders the control tower and completes the selective retry', async ({ page }) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('./')

  await expect(page.getByRole('heading', { name: '从创作意图到可交付成片' })).toBeVisible()
  await expect(page.getByText('S03 / SELECTIVE RETRY')).toBeVisible()
  await expect(page.getByText('RESERVED · 未接后端')).toBeVisible()

  await page.getByRole('button', { name: '资产门禁' }).click()
  await expect(page.getByText('等待资产', { exact: true })).toBeVisible()

  await page.getByRole('button', { name: '局部重试', exact: true }).click()
  await page.getByRole('button', { name: '执行 S03 Retry' }).click()
  await expect(page.getByText('模拟完成', { exact: true })).toBeVisible()
  await expect(page.getByText('3 / 3 PASS')).toBeVisible()
  await expect(page.getByRole('button', { name: '暂无真实视频' })).toBeDisabled()

  await page.getByRole('button', { name: '测试与实现清单' }).click()
  await expect(page.getByRole('heading', { name: '测试与实现清单' })).toBeVisible()
  await expect(page.getByText('当前流水线事件 · SUCCEEDED')).toBeVisible()
  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: '下载当前测试数据' }).click()
  expect((await downloadPromise).suggestedFilename()).toBe('dreampipe-completed.json')
  await page.getByRole('button', { name: '关闭', exact: true }).click()
  await expect(page.getByRole('dialog')).toHaveCount(0)

  await expect.poll(() => page.locator('img').evaluateAll((images) => images.every((image) => image.complete && image.naturalWidth > 0)), { timeout: 20000 }).toBe(true)

  const viewportFits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
  expect(viewportFits).toBe(true)
  expect(errors).toEqual([])
  await page.screenshot({ path: test.info().outputPath('integrated-demo.png'), fullPage: true })
})
