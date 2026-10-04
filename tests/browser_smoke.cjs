// Run with NODE_PATH pointing to a Playwright installation; local demo database.
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
(async () => {
  const browser = await chromium.launch({channel: 'msedge', headless: true});
  try {
    const page = await browser.newPage({viewport: {width: 1280, height: 1000}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto('http://127.0.0.1:5001/auth/login');
    await page.locator('[name=email]').fill('marie@santebridge.com');
    await page.locator('[name=password]').fill('patient123');
    await page.locator('button[type=submit]').click();
    await page.waitForURL('**/patient/assistant');
    await page.locator('#message').fill('Bonjour');
    await page.locator('#send').click();
    assert.match(await page.locator('#status').innerText(), /accepter/);
    await page.locator('#language').selectOption('ln');
    assert.equal(await page.locator('#send').innerText(), 'Tinda →');
    await page.locator('#language').selectOption('fr');
    await page.screenshot({path: 'instance/assistant-desktop.png', fullPage: true});
    await page.route('**/patient/assistant/message', route => route.fulfill({
      contentType: 'application/json', body: JSON.stringify({reply: '<script>unsafe</script> Réponse simulée pour test.', urgent: false,
        providers: [{name: 'Médecin de test', role: 'doctor', specialty: 'Gynécologue', workplace: 'Établissement de test', url: '/patient/book/1'}]})
    }));
    await page.locator('#consent').check();
    await page.locator('#send').click();
    await page.locator('.provider-card').waitFor();
    assert.equal(await page.locator('#messages script').count(), 0);
    assert.equal(await page.locator('.provider-card a').getAttribute('href'), '/patient/book/1');
    await page.locator('#reset').click();
    await page.waitForFunction(() => document.querySelectorAll('.chat-message').length === 1);
    await page.unroute('**/patient/assistant/message');
    await page.route('**/patient/assistant/message', route => route.fulfill({status:503, contentType:'application/json',body:'{"error":"unavailable"}'}));
    await page.locator('#message').fill('Test indisponibilité');
    await page.locator('#send').click();
    await page.waitForFunction(() => document.querySelector('#status').textContent.includes('indisponible'));
    assert.equal(await page.locator('#message').inputValue(), 'Test indisponibilité');
    await page.setViewportSize({width: 390, height: 844});
    await page.locator('#language').selectOption('ln');
    await page.screenshot({path: 'instance/assistant-mobile.png', fullPage: true});
    assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth));
    assert.deepEqual(errors, []);
    console.log('Browser checks passed: login, consent, FR/LN, cards, XSS, reset, API error, mobile. AI responses mocked.');
  } finally { await browser.close(); }
})().catch(error => { console.error(error.message); process.exit(1); });
