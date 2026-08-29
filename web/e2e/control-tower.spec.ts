import { expect, test } from '@playwright/test'

test('renders the control tower and completes the selective retry', async ({ page }) => {
  await page.goto('/')

  await expect(page.getByRole('heading', { name: '从创作意图到可交付成片' })).toBeVisible()
  await expect(page.getByText('S03 / SELECTIVE RETRY')).toBeVisible()
  await expect(page.getByText('RESERVED · 未接后端')).toBeVisible()

  await page.getByRole('button', { name: '资产门禁' }).click()
  await expect(page.getByText('等待资产', { exact: true })).toBeVisible()

  await page.getByRole('button', { name: '局部重试', exact: true }).click()
  await page.getByRole('button', { name: '执行 S03 Retry' }).click()
  await expect(page.getByText('可交付', { exact: true })).toBeVisible()
  await expect(page.getByText('3 / 3 PASS')).toBeVisible()

  const viewportFits = await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)
  expect(viewportFits).toBe(true)
})
