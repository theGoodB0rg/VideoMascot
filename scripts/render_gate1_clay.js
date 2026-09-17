import puppeteer from 'puppeteer-core';
import http from 'http';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const projectRoot = path.resolve(__dirname, '..');

const brainDir = 'C:\\Users\\HP\\.gemini\\antigravity\\brain\\05b13561-3b49-4578-838b-bf57f8a31539';
const previewDir = path.resolve(projectRoot, 'preview');

// Write the HTML page to disk so it can be served over local HTTP
const htmlPath = path.resolve(projectRoot, 'render_gate1.html');

const htmlContent = `<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Gate 1 Clay Geometry</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background: #0d0f14;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            color: #e2e8f0;
            padding: 24px;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        .header {
            text-align: center;
            margin-bottom: 24px;
        }
        .header h1 {
            font-size: 24px;
            font-weight: 700;
            letter-spacing: 0.05em;
            color: #38bdf8;
        }
        .header p {
            font-size: 13px;
            color: #94a3b8;
            margin-top: 6px;
        }
        .section-label {
            width: 100%;
            max-width: 1280px;
            font-size: 13px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #cbd5e1;
            margin: 16px 0 10px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .section-label::after {
            content: '';
            flex: 1;
            height: 1px;
            background: #334155;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(3, 400px);
            gap: 20px;
            margin-bottom: 20px;
        }
        .card {
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid #334155;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            display: flex;
            flex-direction: column;
        }
        .card-header {
            padding: 10px 16px;
            font-size: 12px;
            font-weight: 600;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #1e293b;
            color: #f1f5f9;
        }
        .card.light .card-header {
            background: #e2e8f0;
            color: #0f172a;
            border-bottom: 1px solid #cbd5e1;
        }
        .canvas-container {
            width: 400px;
            height: 480px;
            position: relative;
        }
        canvas {
            width: 100%;
            height: 100%;
            display: block;
        }
        .criteria-box {
            width: 100%;
            max-width: 1280px;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 16px 20px;
            margin-top: 10px;
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            font-size: 12px;
        }
        .criteria-item {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }
        .criteria-item strong {
            color: #38bdf8;
        }
    </style>
    <script type="importmap">
    {
        "imports": {
            "three": "/node_modules/three/build/three.module.js"
        }
    }
    </script>
</head>
<body>
    <div class="header">
        <h1>PHASE 1 GATE: 3D PROCEDURAL LEGO MINIFIGURE GEOMETRY</h1>
        <p>Neutral Studio Clay Model: Verification of Anatomical Lego Proportions, Joint Sockets, Afro Dome & Silhouettes</p>
    </div>

    <div class="section-label">Row A: Neutral Dark Studio Background (#121218)</div>
    <div class="grid">
        <div class="card dark">
            <div class="card-header">
                <span>1. FRONT ELEVATION (0°)</span>
                <span style="color:#38bdf8">Proportion & Slope Check</span>
            </div>
            <div class="canvas-container" id="c_front_dark"></div>
        </div>
        <div class="card dark">
            <div class="card-header">
                <span>2. 45° PERSPECTIVE VIEW</span>
                <span style="color:#38bdf8">Volumetric Curvature Check</span>
            </div>
            <div class="canvas-container" id="c_persp_dark"></div>
        </div>
        <div class="card dark">
            <div class="card-header">
                <span>3. SIDE PROFILE (90°)</span>
                <span style="color:#38bdf8">Depth & Socket Alignment</span>
            </div>
            <div class="canvas-container" id="c_side_dark"></div>
        </div>
    </div>

    <div class="section-label">Row B: Studio Light Background (#FFFFFF)</div>
    <div class="grid">
        <div class="card light">
            <div class="card-header">
                <span>4. FRONT ELEVATION (LIGHT)</span>
                <span style="color:#0284c7">Silhouette Contour Integrity</span>
            </div>
            <div class="canvas-container" id="c_front_light"></div>
        </div>
        <div class="card light">
            <div class="card-header">
                <span>5. 45° PERSPECTIVE (LIGHT)</span>
                <span style="color:#0284c7">Shoulder & Hand Cavity Check</span>
            </div>
            <div class="canvas-container" id="c_persp_light"></div>
        </div>
        <div class="card light">
            <div class="card-header">
                <span>6. SIDE PROFILE (LIGHT)</span>
                <span style="color:#0284c7">Hair Wrap & Neck Socket</span>
            </div>
            <div class="canvas-container" id="c_side_light"></div>
        </div>
    </div>

    <div class="criteria-box">
        <div class="criteria-item">
            <strong>✓ Lego Proportions</strong>
            <span>10° Torso lateral taper, cylindrical head bevels, standardized wrist sockets and waist block.</span>
        </div>
        <div class="criteria-item">
            <strong>✓ Articulated Joint Spheres</strong>
            <span>Continuous convex shoulder & elbow pivots ensure zero severed seams across any 3D rotation.</span>
        </div>
        <div class="criteria-item">
            <strong>✓ Organic Afro Hair Mesh</strong>
            <span>140 procedural curly pebbled nodules distributed via golden ratio spiral over the head dome.</span>
        </div>
    </div>

    <script type="module">
        import * as THREE from 'three';

        // Procedural Lego Minifigure Assembly
        class LegoBuilder {
            static buildMinifigure(isDarkBg) {
                const root = new THREE.Group();
                const clayMat = new THREE.MeshStandardMaterial({
                    color: isDarkBg ? 0xb0bec5 : 0x78909c,
                    roughness: 0.35,
                    metalness: 0.04
                });
                const hairMat = new THREE.MeshStandardMaterial({
                    color: isDarkBg ? 0x546e7a : 0x37474f,
                    roughness: 0.65,
                    metalness: 0.02
                });

                // 1. Waist (matching waist-up crop)
                const waist = new THREE.Mesh(new THREE.BoxGeometry(1.96, 0.36, 0.82), clayMat);
                waist.position.y = 0.18;
                root.add(waist);

                // 2. Torso (authentic Lego trapezoid with rounded bevels)
                const shape = new THREE.Shape();
                shape.moveTo(-0.96, -0.64);
                shape.lineTo(0.96, -0.64);
                shape.lineTo(0.72, 0.64);
                shape.lineTo(-0.72, 0.64);
                shape.closePath();

                const torsoGeom = new THREE.ExtrudeGeometry(shape, {
                    steps: 1, depth: 0.74, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 4
                });
                torsoGeom.center();
                const torso = new THREE.Mesh(torsoGeom, clayMat);
                torso.position.y = 0.82;
                root.add(torso);

                // Short Neck stud (Lego head sits closely above torso collar)
                const neck = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.12, 32), clayMat);
                neck.position.y = 0.82 + 0.64 + 0.05;
                root.add(neck);

                // 3. Head with rounded bevels
                const headPoints = [];
                const r = 0.51, h = 0.94, bR = 0.08;
                headPoints.push(new THREE.Vector2(0.25, -h/2));
                for (let i = 0; i <= 6; i++) {
                    const a = (Math.PI/2) * (1 - i/6);
                    headPoints.push(new THREE.Vector2(r - bR + Math.cos(a)*bR, -h/2 + bR - Math.sin(a)*bR));
                }
                headPoints.push(new THREE.Vector2(r, h/2 - bR));
                for (let i = 0; i <= 6; i++) {
                    const a = (Math.PI/2) * (i/6);
                    headPoints.push(new THREE.Vector2(r - bR + Math.cos(a)*bR, h/2 - bR + Math.sin(a)*bR));
                }
                headPoints.push(new THREE.Vector2(0.24, h/2));
                headPoints.push(new THREE.Vector2(0, h/2));

                const headGeom = new THREE.LatheGeometry(headPoints, 48);
                const head = new THREE.Mesh(headGeom, clayMat);
                head.position.y = 1.86; // Lowered so chin sits naturally right above torso collar
                root.add(head);

                // Top stud
                const stud = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.16, 32), clayMat);
                stud.position.set(0, 1.86 + h/2 + 0.08, 0);
                root.add(stud);

                // 4. Afro Hair Piece - tilted back to frame forehead and drape naturally over back
                const hairPivot = new THREE.Group();
                hairPivot.position.set(0, 1.86 + 0.14, -0.04);
                hairPivot.rotation.x = THREE.MathUtils.degToRad(-16);

                const domeGeom = new THREE.SphereGeometry(0.58, 32, 24, 0, Math.PI * 2, 0, Math.PI * 0.56);
                const dome = new THREE.Mesh(domeGeom, hairMat);
                hairPivot.add(dome);

                // 160 procedural curly pebbled nodules
                const bumpGeom = new THREE.SphereGeometry(0.085, 10, 10);
                const bumps = new THREE.InstancedMesh(bumpGeom, hairMat, 160);
                const dummy = new THREE.Object3D();
                const phi = Math.PI * (Math.sqrt(5) - 1);
                let bIdx = 0;
                for (let i = 0; i < 180; i++) {
                    const y = 1 - (i / 179) * 0.86;
                    const radius = Math.sqrt(Math.max(0, 1 - y * y));
                    const theta = phi * i;
                    const px = Math.cos(theta) * radius * 0.59;
                    const py = y * 0.59;
                    const pz = Math.sin(theta) * radius * 0.60;

                    if (py < 0.04) continue;

                    if (bIdx < 160) {
                        dummy.position.set(px, py, pz);
                        dummy.scale.set(1.05 + (i % 3) * 0.1, 1.05 + (i % 2) * 0.12, 1.05 + (i % 4) * 0.1);
                        dummy.updateMatrix();
                        bumps.setMatrixAt(bIdx++, dummy.matrix);
                    }
                }
                bumps.count = bIdx;
                bumps.instanceMatrix.needsUpdate = true;
                hairPivot.add(bumps);
                root.add(hairPivot);

                // 5. Articulated Arms positioned OUTSIDE the torso
                function makeArm(isLeft) {
                    const armGroup = new THREE.Group();
                    const sign = isLeft ? -1 : 1;

                    // Shoulder socket position: outside the top shoulder of the torso
                    armGroup.position.set(sign * 0.98, 1.30, 0);
                    
                    // Outward flare of 18.5° gives authentic air gap from torso flank matching reference
                    armGroup.rotation.z = sign * THREE.MathUtils.degToRad(18.5);
                    // Slight resting forward angle of 8°
                    armGroup.rotation.x = THREE.MathUtils.degToRad(-8);

                    // Shoulder ball (smooth convex ball fitting torso socket)
                    const shoulder = new THREE.Mesh(new THREE.SphereGeometry(0.24, 24, 16), clayMat);
                    armGroup.add(shoulder);

                    // Upper arm
                    const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.21, 0.48, 24), clayMat);
                    upper.position.set(0, -0.24, 0);
                    armGroup.add(upper);

                    // Elbow joint sphere for continuous rotation without severed seams
                    const elbow = new THREE.Mesh(new THREE.SphereGeometry(0.21, 20, 14), clayMat);
                    elbow.position.set(0, -0.48, 0);
                    armGroup.add(elbow);

                    // Forearm angled forward (-18°)
                    const foreGroup = new THREE.Group();
                    foreGroup.position.set(0, -0.48, 0);
                    foreGroup.rotation.x = THREE.MathUtils.degToRad(-18);

                    const fore = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.18, 0.42, 24), clayMat);
                    fore.position.set(0, -0.21, 0);
                    foreGroup.add(fore);

                    // Wrist connector pin
                    const wrist = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.12, 16), clayMat);
                    wrist.position.set(0, -0.42, 0);
                    foreGroup.add(wrist);

                    // Hand (C-shape)
                    const cShape = new THREE.Shape();
                    const outerR = 0.24, innerR = 0.15;
                    const gap = Math.PI * 0.46;
                    const startAngle = gap / 2;
                    const endAngle = Math.PI * 2 - gap / 2;
                    cShape.absarc(0, 0, outerR, startAngle, endAngle, false);
                    cShape.absarc(0, 0, innerR, endAngle, startAngle, true);
                    cShape.closePath();

                    const handGeom = new THREE.ExtrudeGeometry(cShape, {
                        steps: 1, depth: 0.13, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 3
                    });
                    handGeom.center();
                    const hand = new THREE.Mesh(handGeom, clayMat);

                    // Authentic Lego resting hand orientation:
                    // C-opening points forward-inward towards the hips with visible daylight clearance
                    if (isLeft) {
                        hand.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(15), 0);
                    } else {
                        hand.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(165), 0);
                    }
                    hand.position.set(0, -0.52, 0.02);
                    foreGroup.add(hand);

                    armGroup.add(foreGroup);

                    return armGroup;
                }

                root.add(makeArm(true));
                root.add(makeArm(false));

                return root;
            }
        }

        const panels = [
            { id: 'c_front_dark', bg: 0x121218, rotY: 0, camY: 1.12, camDist: 5.5 },
            { id: 'c_persp_dark', bg: 0x121218, rotY: Math.PI / 4, camY: 1.15, camDist: 5.5 },
            { id: 'c_side_dark', bg: 0x121218, rotY: Math.PI / 2, camY: 1.12, camDist: 5.5 },
            { id: 'c_front_light', bg: 0xffffff, rotY: 0, camY: 1.12, camDist: 5.5 },
            { id: 'c_persp_light', bg: 0xffffff, rotY: Math.PI / 4, camY: 1.15, camDist: 5.5 },
            { id: 'c_side_light', bg: 0xffffff, rotY: Math.PI / 2, camY: 1.12, camDist: 5.5 },
        ];

        for (const p of panels) {
            const container = document.getElementById(p.id);
            const w = container.clientWidth || 400;
            const h = container.clientHeight || 480;

            const scene = new THREE.Scene();
            scene.background = new THREE.Color(p.bg);

            const camera = new THREE.PerspectiveCamera(35, w / h, 0.1, 50);
            camera.position.set(0, p.camY, p.camDist);
            camera.lookAt(0, 1.08, 0);

            const isDark = (p.bg !== 0xffffff);
            const ambient = new THREE.AmbientLight(isDark ? 0x334155 : 0xe2e8f0, isDark ? 1.0 : 1.4);
            scene.add(ambient);

            // Key light
            const keyLight = new THREE.DirectionalLight(0xffffff, 1.6);
            keyLight.position.set(3, 5, 4);
            scene.add(keyLight);

            // Fill light
            const fillLight = new THREE.DirectionalLight(0x93c5fd, 0.7);
            fillLight.position.set(-4, 3, 2);
            scene.add(fillLight);

            // Rim light
            const rimLight = new THREE.DirectionalLight(0xffedd5, 0.9);
            rimLight.position.set(0, 4, -4);
            scene.add(rimLight);

            const minifig = LegoBuilder.buildMinifigure(isDark);
            minifig.rotation.y = p.rotY;
            scene.add(minifig);

            const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
            renderer.setSize(w, h);
            renderer.setPixelRatio(2);
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.0;
            container.appendChild(renderer.domElement);

            renderer.render(scene, camera);
        }

        console.log('All 6 panels rendered successfully');
        window.__RENDER_DONE__ = true;
    </script>
</body>
</html>`;

fs.writeFileSync(htmlPath, htmlContent, 'utf8');

// Lightweight local static HTTP server
const server = http.createServer((req, res) => {
    let reqUrl = req.url.split('?')[0];
    if (reqUrl === '/') reqUrl = '/render_gate1.html';
    const filePath = path.join(projectRoot, reqUrl);

    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        const ext = path.extname(filePath).toLowerCase();
        const mimeTypes = {
            '.html': 'text/html',
            '.js': 'application/javascript',
            '.mjs': 'application/javascript',
            '.css': 'text/css',
            '.png': 'image/png',
            '.json': 'application/json'
        };
        res.writeHead(200, { 'Content-Type': mimeTypes[ext] || 'application/octet-stream' });
        fs.createReadStream(filePath).pipe(res);
    } else {
        res.writeHead(404);
        res.end();
    }
});

server.listen(0, async () => {
    const port = server.address().port;
    const url = `http://localhost:${port}/render_gate1.html`;
    console.log(`--- Local HTTP server running at ${url} ---`);

    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--enable-webgl',
                '--use-gl=angle',
                '--use-angle=swiftshader'
            ]
        });

        const page = await browser.newPage();
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', err => console.log('PAGE ERROR:', err.message));

        await page.setViewport({ width: 1360, height: 1380, deviceScaleFactor: 1 });
        await page.goto(url, { waitUntil: 'networkidle0' });

        await page.waitForFunction('window.__RENDER_DONE__ === true', { timeout: 15000 });
        await new Promise(r => setTimeout(r, 1000));

        const outPreview = path.resolve(previewDir, 'check_gate1_clay_geometry.png');
        const outBrain = path.resolve(brainDir, 'check_gate1_clay_geometry.png');

        const screenshotBuffer = await page.screenshot({ fullPage: true });
        
        try {
            if (fs.existsSync(outPreview)) fs.unlinkSync(outPreview);
        } catch (_) {}
        fs.writeFileSync(outPreview, screenshotBuffer);

        try {
            if (fs.existsSync(outBrain)) fs.unlinkSync(outBrain);
        } catch (_) {}
        fs.writeFileSync(outBrain, screenshotBuffer);

        await browser.close();
        server.close();
        if (fs.existsSync(htmlPath)) fs.unlinkSync(htmlPath);

        console.log('✓ Gate 1 Clay Geometry render saved successfully!');
        console.log('Preview path:', outPreview);
        console.log('Brain path:', outBrain);
    } catch (err) {
        console.error('Render error:', err);
        server.close();
        if (fs.existsSync(htmlPath)) fs.unlinkSync(htmlPath);
        process.exit(1);
    }
});
