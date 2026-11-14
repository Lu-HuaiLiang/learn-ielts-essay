import assert from 'node:assert/strict';
import {chromium} from 'playwright';

const baseUrl = process.env.COURSE_URL || 'http://127.0.0.1:4173/';
const browser = await chromium.launch({headless: true});
const page = await browser.newPage();
try {
  const requestedUrls = [];
  page.on('request', request => requestedUrls.push(request.url()));
  await page.goto(new URL('essays/conservation.html', baseUrl).href, {waitUntil: 'networkidle'});
  const buttons = page.locator('.essay-read-aloud');
  assert.equal(await buttons.count(), 4);
  assert.equal(await buttons.nth(0).getAttribute('aria-label'), '朗读第1段');
  await buttons.nth(0).click();
  await page.waitForTimeout(50);
  assert.equal(await buttons.nth(0).getAttribute('aria-label'), '停止朗读第1段');
  await buttons.nth(1).click();
  assert.equal(await buttons.nth(0).getAttribute('aria-label'), '朗读第1段');
  assert.equal(await buttons.nth(1).getAttribute('aria-label'), '停止朗读第2段');
  await page.waitForTimeout(100);
  assert.ok(requestedUrls.some(url => url.endsWith('/audio/essays/conservation/p02.mp3')));
  await page.locator('.essay-reader > summary').click();
  assert.equal(await buttons.nth(1).getAttribute('aria-label'), '朗读第2段');
  await page.goto(new URL('essays/nine-01.html', baseUrl).href, {waitUntil: 'networkidle'});
  assert.equal(await page.locator('.essay-read-aloud').first().getAttribute('aria-label'), '朗读第1段');
  console.log('PASS: browser paragraph audio labels, switching, collapse, route reset and static URL checked.');
} finally {
  await browser.close();
}
