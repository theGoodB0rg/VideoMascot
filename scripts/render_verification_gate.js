import http from 'http';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';

const PORT = 8890;
const ROOT = process.cwd();

const server = http.createServer((req, res) => {
    const cleanUrl = req.url.split('?')[0].replace(/^\/+/, '');
    let filePath = path.join(ROOT, cleanUrl);
    if (!cleanUrl) filePath = path.join(ROOT, 'preview/gate_renderer.html');

    fs.readFile(filePath, (err, data) => {
        if (err) {
            console.error('404:', req.url, '->', filePath);
            res.writeHead(404);
            res.end('Not found');
            return;
        }
        if (filePath.endsWith('.html')) res.setHeader('Content-Type', 'text/html');
        else if (filePath.endsWith('.js')) res.setHeader('Content-Type', 'application/javascript');
        else if (filePath.endsWith('.png')) res.setHeader('Content-Type', 'image/png');
        else if (filePath.endsWith('.css')) res.setHeader('Content-Type', 'text/css');
        res.writeHead(200);
        res.end(data);
    });
});

server.listen(PORT, async () => {
    console.log(`Verification Gate Server running on http://localhost:${PORT}`);
    const browser = await puppeteer.launch({
        executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        headless: 'new',
        args: [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--enable-webgl',
            '--ignore-gpu-blocklist',
        ]
    });

    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 4096, height: 1144 });

        page.on('console', msg => console.log('GATE LOG:', msg.text()));
        page.on('pageerror', err => console.error('GATE ERROR:', err));

        await page.goto(`http://localhost:${PORT}/preview/gate_renderer.html`, { waitUntil: 'networkidle0' });

        // Wait until gate render completes
        await page.waitForFunction(() => window.__GATE_RENDERED === true, { timeout: 30000 });

        // Get canvas data
        const dataUrl = await page.evaluate(() => {
            return document.getElementById('canvasMaster').toDataURL('image/png');
        });

        const base64Data = dataUrl.replace(/^data:image\/png;base64,/, '');
        const outputPath = path.join(ROOT, 'preview/verification_gate_likeness.png');
        fs.writeFileSync(outputPath, Buffer.from(base64Data, 'base64'));

        console.log('✓ SUCCESS: Verification Gate Image saved to:', outputPath);
        console.log('File size:', fs.statSync(outputPath).size, 'bytes');
    } catch (e) {
        console.error('Verification Gate Render failed:', e);
    } finally {
        await browser.close();
        server.close();
    }
});
