import puppeteer from 'puppeteer-core';
import fs from 'fs';

async function test() {
    const browser = await puppeteer.launch({
        executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    const page = await browser.newPage();
    await page.setViewport({ width: 800, height: 600 });
    await page.setContent('<html><body style="background:#121218;color:white;"><h1>Headless Chrome WebGL Ready</h1></body></html>');
    await page.screenshot({ path: 'test_puppeteer.png' });
    await browser.close();
    console.log('Puppeteer test passed! Screenshot saved:', fs.existsSync('test_puppeteer.png'));
    if (fs.existsSync('test_puppeteer.png')) {
        fs.unlinkSync('test_puppeteer.png');
    }
}
test();
