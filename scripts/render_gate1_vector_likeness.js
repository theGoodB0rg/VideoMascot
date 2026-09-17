import http from 'http';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';
import { execSync } from 'child_process';

const projectRoot = process.cwd();
const previewDir = path.join(projectRoot, 'preview');
const tempDir = path.join(previewDir, 'temp_gate1');
fs.mkdirSync(tempDir, { recursive: true });

function generateHtml() {
    return `<!DOCTYPE html>
<html>
<head>
    <style>
        body { margin: 0; background: #0b0f19; }
        canvas { display: none; }
    </style>
</head>
<body>
    <script type="module">
        import { ProceduralFacePainter } from '/src/three_mascot/textures/ProceduralFacePainter.js';
        import { ProceduralTorsoPainter } from '/src/three_mascot/textures/ProceduralTorsoPainter.js';

        window.facePainter = new ProceduralFacePainter({ width: 2048, height: 1024 });
        window.torsoPainter = new ProceduralTorsoPainter({ width: 1024, height: 1024 });

        // Helper to render face state to data URL
        window.renderFace = (viseme, blink = 0.0) => {
            const canvas = document.createElement('canvas');
            canvas.width = 2048;
            canvas.height = 1024;
            const ctx = canvas.getContext('2d');
            window.facePainter.setState({ viseme, blink });
            window.facePainter.render(ctx);

            // Also crop the face area (center 700x700 around eye/mouth landmarks)
            // landmarks.centerX = 1024. EyeY = 510. MouthY = 700.
            // Center of face roughly (1024, 580). Crop 800x800.
            const cropCanvas = document.createElement('canvas');
            cropCanvas.width = 800;
            cropCanvas.height = 800;
            const cropCtx = cropCanvas.getContext('2d');
            cropCtx.drawImage(canvas, 1024 - 400, 580 - 400, 800, 800, 0, 0, 800, 800);

            return {
                full: canvas.toDataURL('image/png'),
                crop: cropCanvas.toDataURL('image/png')
            };
        };

        // Helper to render mouth close-up
        window.renderMouthCrop = (viseme) => {
            const canvas = document.createElement('canvas');
            canvas.width = 2048;
            canvas.height = 1024;
            const ctx = canvas.getContext('2d');
            window.facePainter.setState({ viseme, blink: 0.0 });
            window.facePainter.render(ctx);

            // Crop mouth region: center (1024, 715), size 400x240
            const mouthCanvas = document.createElement('canvas');
            mouthCanvas.width = 400;
            mouthCanvas.height = 240;
            const mCtx = mouthCanvas.getContext('2d');
            mCtx.drawImage(canvas, 1024 - 200, 715 - 120, 400, 240, 0, 0, 400, 240);
            return mouthCanvas.toDataURL('image/png');
        };

        // Helper to render torso textures
        window.renderTorso = () => {
            const canvas = document.createElement('canvas');
            canvas.width = 1024;
            canvas.height = 1024;
            const ctx = canvas.getContext('2d');
            window.torsoPainter.render(ctx);

            // Collar close-up: center 512, top 0 to 480, width 700
            const collarCanvas = document.createElement('canvas');
            collarCanvas.width = 700;
            collarCanvas.height = 480;
            const cCtx = collarCanvas.getContext('2d');
            cCtx.drawImage(canvas, 512 - 350, 0, 700, 480, 0, 0, 700, 480);

            // Sleeve
            const sleeveCanvas = window.torsoPainter.renderSleeve(null, 512, 512);
            // Forearm
            const forearmCanvas = window.torsoPainter.renderForearm(null, 512, 512);

            return {
                torsoFull: canvas.toDataURL('image/png'),
                collarCrop: collarCanvas.toDataURL('image/png'),
                sleeve: sleeveCanvas.toDataURL('image/png'),
                forearm: forearmCanvas.toDataURL('image/png')
            };
        };

        window.__READY__ = true;
    </script>
</body>
</html>`;
}

// Simple static file server
const server = http.createServer((req, res) => {
    let reqUrl = req.url.split('?')[0];
    if (reqUrl === '/') reqUrl = '/temp_gate1.html';
    const filePath = path.join(projectRoot, reqUrl);
    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        const ext = path.extname(filePath).toLowerCase();
        const mime = ext === '.html' ? 'text/html' : (ext === '.png' ? 'image/png' : (ext === '.js' ? 'text/javascript' : 'application/octet-stream'));
        res.writeHead(200, { 'Content-Type': mime });
        fs.createReadStream(filePath).pipe(res);
    } else {
        res.writeHead(404); res.end();
    }
});

server.listen(0, async () => {
    const port = server.address().port;
    console.log(`Rendering Gate 1 vector assets on port ${port}...`);

    try {
        fs.writeFileSync(path.join(projectRoot, 'temp_gate1.html'), generateHtml());

        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox']
        });

        const page = await browser.newPage();
        await page.goto(`http://localhost:${port}/temp_gate1.html`, { waitUntil: 'networkidle0' });
        await page.waitForFunction('window.__READY__ === true', { timeout: 10000 });

        console.log('Rendering face visemes...');
        const visemes = ['REST', 'A_AH', 'O_OH', 'E_EE', 'M_B_P', 'SMILE_OPEN'];
        for (const v of visemes) {
            const data = await page.evaluate((vis) => window.renderFace(vis, 0.0), v);
            const base64Crop = data.crop.replace(/^data:image\/png;base64,/, '');
            fs.writeFileSync(path.join(tempDir, `face_${v.toLowerCase()}.png`), Buffer.from(base64Crop, 'base64'));

            const mouthData = await page.evaluate((vis) => window.renderMouthCrop(vis), v);
            const mBase64 = mouthData.replace(/^data:image\/png;base64,/, '');
            fs.writeFileSync(path.join(tempDir, `mouth_${v.toLowerCase()}.png`), Buffer.from(mBase64, 'base64'));
        }

        // Full face 2k texture for REST
        const restFace = await page.evaluate(() => window.renderFace('REST', 0.0));
        fs.writeFileSync(path.join(tempDir, 'face_rest_full_2k.png'), Buffer.from(restFace.full.replace(/^data:image\/png;base64,/, ''), 'base64'));

        // Blink face
        const blinkData = await page.evaluate(() => window.renderFace('REST', 1.0));
        fs.writeFileSync(path.join(tempDir, 'face_blink.png'), Buffer.from(blinkData.crop.replace(/^data:image\/png;base64,/, ''), 'base64'));

        console.log('Rendering torso and sleeves...');
        const torsoData = await page.evaluate(() => window.renderTorso());
        fs.writeFileSync(path.join(tempDir, 'torso_full.png'), Buffer.from(torsoData.torsoFull.replace(/^data:image\/png;base64,/, ''), 'base64'));
        fs.writeFileSync(path.join(tempDir, 'collar_crop.png'), Buffer.from(torsoData.collarCrop.replace(/^data:image\/png;base64,/, ''), 'base64'));
        fs.writeFileSync(path.join(tempDir, 'sleeve.png'), Buffer.from(torsoData.sleeve.replace(/^data:image\/png;base64,/, ''), 'base64'));
        fs.writeFileSync(path.join(tempDir, 'forearm.png'), Buffer.from(torsoData.forearm.replace(/^data:image\/png;base64,/, ''), 'base64'));

        await browser.close();
        server.close();
        if (fs.existsSync(path.join(projectRoot, 'temp_gate1.html'))) {
            fs.unlinkSync(path.join(projectRoot, 'temp_gate1.html'));
        }

        console.log('All vector components rendered successfully to preview/temp_gate1/');
    } catch (err) {
        console.error('Error rendering Gate 1 vector assets:', err);
        server.close();
        process.exit(1);
    }
});
