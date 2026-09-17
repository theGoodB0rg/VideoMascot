import http from 'http';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';

const projectRoot = process.cwd();
const previewDir = path.join(projectRoot, 'preview');
const debugDir = path.join(previewDir, 'debug');

function generateHtml(config) {
    const configJson = JSON.stringify(config);
    return `<!DOCTYPE html>
<html>
<head>
    <script type="importmap">
    {
        "imports": {
            "three": "/node_modules/three/build/three.module.js"
        }
    }
    </script>
    <style>
        body { margin: 0; background: #121218; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <script type="module">
        import * as THREE from 'three';
        import { LegoGeometryFactory } from '/src/three_mascot/geometry/LegoGeometryFactory.js';
        import { LegoMaterialFactory } from '/src/three_mascot/materials/LegoMaterialFactory.js';
        import { ProceduralFacePainter, EMOTIONS } from '/src/three_mascot/textures/ProceduralFacePainter.js';

        const config = ${configJson};

        const canvas = document.getElementById('c');
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
        renderer.setSize(600, 600);
        renderer.setPixelRatio(2);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.05;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x121218);

        // Studio 3-point lighting
        const ambient = new THREE.AmbientLight(0x40352c, 1.2);
        scene.add(ambient);

        const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
        keyLight.position.set(3.0, 5.0, 4.0);
        scene.add(keyLight);

        const fillLight = new THREE.DirectionalLight(0xa5c4e8, 0.9);
        fillLight.position.set(-3.5, 2.5, 2.5);
        scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0xffeedd, 1.6);
        rimLight.position.set(0.5, 4.0, -3.5);
        scene.add(rimLight);

        const camera = new THREE.PerspectiveCamera(28, 1.0, 0.1, 100);
        camera.position.set(0, 2.04, 2.7);
        camera.lookAt(0, 2.04, 0);

        const geomFactory = new LegoGeometryFactory();
        const matFactory = new LegoMaterialFactory();

        // 100% Coded Procedural Vector Face Painter
        const painter = new ProceduralFacePainter({ width: 2048, height: 1024 });
        const faceCanvas = painter.initCanvas();

        if (config.emotion) painter.setEmotion(config.emotion, config.emotionIntensity ?? 1.0);
        if (config.gazeYaw !== undefined) painter.setGazeAngle(config.gazeYaw, config.gazePitch ?? 0);
        if (config.viseme) painter.setState({ viseme: config.viseme });
        if (config.blink !== undefined) painter.setState({ blink: config.blink });

        painter.render();

        const cleanTex = new THREE.CanvasTexture(faceCanvas);
        cleanTex.colorSpace = THREE.SRGBColorSpace;

        // Head assembly
        const headData = geomFactory.createHeadGeometry();
        const headGroup = headData.group;
        headGroup.position.set(0, 2.04, 0);

        const headMesh = headGroup.getObjectByName('head_main');
        const studMesh = headGroup.getObjectByName('head_stud');
        headMesh.material = matFactory.createHeadMaterial(cleanTex);
        studMesh.material = matFactory.createSkinMaterial();

        // Lego Afro Hair Piece (Part 21778)
        function createLegoAfroHair() {
            const group = new THREE.Group();
            group.name = 'afro_hair';
            const hairMat = new THREE.MeshStandardMaterial({
                color: 0x1a1715,
                roughness: 0.82,
                metalness: 0.02
            });

            const nTheta = 48;
            const nY = 24;
            const geom = new THREE.BufferGeometry();
            const positions = [];
            const uvs = [];
            const indices = [];

            function getBottomY(theta) {
                const zNorm = -Math.cos(theta);
                const xVal = 0.545 * Math.sin(theta);

                if (zNorm < -0.1) {
                    return -0.12;
                } else if (zNorm < 0.35) {
                    const t = (zNorm - (-0.1)) / 0.45;
                    return -0.12 + 0.10 * t;
                } else {
                    const yForehead = 0.29 - 0.40 * (xVal * xVal);
                    const t = Math.min(1.0, (zNorm - 0.35) / 0.35);
                    return -0.02 * (1.0 - t) + yForehead * t;
                }
            }

            const yTop = 0.75;
            const capCenterY = 0.26;
            const capH = yTop - capCenterY;

            for (let j = 0; j <= nY; j++) {
                const vFrac = j / nY;
                for (let i = 0; i <= nTheta; i++) {
                    const theta = -Math.PI + (2.0 * Math.PI * i) / nTheta;
                    const yBot = getBottomY(theta);
                    const y = yTop - vFrac * (yTop - yBot);

                    let px, py, pz;
                    if (j === 0) {
                        px = 0; py = yTop; pz = 0;
                    } else {
                        let r;
                        if (y >= capCenterY) {
                            const relY = (y - capCenterY) / capH;
                            r = 0.548 * Math.sqrt(Math.max(0, 1.0 - relY * relY));
                        } else {
                            r = 0.548;
                        }
                        px = r * Math.sin(theta);
                        pz = -r * Math.cos(theta);
                        py = y;
                    }
                    positions.push(px, py, pz);
                    uvs.push(i / nTheta, vFrac);
                }
            }

            for (let j = 0; j < nY; j++) {
                for (let i = 0; i < nTheta; i++) {
                    const row1 = j * (nTheta + 1);
                    const row2 = (j + 1) * (nTheta + 1);
                    indices.push(row1 + i, row2 + i, row1 + i + 1);
                    indices.push(row1 + i + 1, row2 + i, row2 + i + 1);
                }
            }

            geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
            geom.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
            geom.setIndex(indices);
            geom.computeVertexNormals();

            const capMesh = new THREE.Mesh(geom, hairMat);
            capMesh.castShadow = true;
            group.add(capMesh);

            const curlGeom = new THREE.SphereGeometry(0.034, 8, 6);
            const curlCount = 900;
            const curls = new THREE.InstancedMesh(curlGeom, hairMat, curlCount);
            curls.castShadow = true;

            const dummy = new THREE.Object3D();
            let cIdx = 0;
            for (let i = 0; i < 850; i++) {
                const phi = Math.acos(1.0 - 0.95 * ((i + 0.5) / 850));
                const theta = Math.sqrt(850 * Math.PI) * phi;
                const yBot = getBottomY(theta);
                const relY = Math.cos(phi);
                const y = capCenterY + capH * relY;
                if (y < yBot + 0.015) continue;
                const r = 0.552 * Math.sin(phi);
                const px = r * Math.sin(theta);
                const pz = -r * Math.cos(theta);
                dummy.position.set(px, y, pz);
                dummy.scale.set(1.0, 1.0, 1.0);
                dummy.updateMatrix();
                curls.setMatrixAt(cIdx++, dummy.matrix);
            }

            const rimSteps = 36;
            for (let i = 0; i <= rimSteps; i++) {
                const t = -1.0 + (2.0 * i) / rimSteps;
                const theta = Math.PI * (1.0 - 0.42 * t);
                const yBot = getBottomY(theta);
                const r = 0.554;
                const px = r * Math.sin(theta);
                const pz = -r * Math.cos(theta);
                if (cIdx < curlCount) {
                    dummy.position.set(px, yBot - 0.008, pz);
                    dummy.scale.set(1.12, 1.12, 1.12);
                    dummy.updateMatrix();
                    curls.setMatrixAt(cIdx++, dummy.matrix);
                }
            }
            curls.count = cIdx;
            curls.instanceMatrix.needsUpdate = true;
            group.add(curls);

            return group;
        }

        const hair = createLegoAfroHair();
        headGroup.add(hair);
        scene.add(headGroup);

        renderer.render(scene, camera);
        window.__READY__ = true;
    </script>
</body>
</html>`;
}

const server = http.createServer((req, res) => {
    let reqPath = req.url.split('?')[0];
    if (reqPath === '/') reqPath = '/index.html';
    const filePath = path.join(projectRoot, reqPath);

    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        const ext = path.extname(filePath);
        const mime = ext === '.html' ? 'text/html' : (ext === '.js' ? 'application/javascript' : 'application/octet-stream');
        res.writeHead(200, { 'Content-Type': mime });
        fs.createReadStream(filePath).pipe(res);
    } else {
        res.writeHead(404); res.end();
    }
});

server.listen(0, async () => {
    const port = server.address().port;
    console.log(`Rendering animation demonstration frames on port ${port}...`);

    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--enable-webgl']
        });

        const page = await browser.newPage();
        await page.setViewport({ width: 600, height: 600 });

        const frames = [
            // 1. Directional Gaze
            { id: 'gaze_center', title: 'Look Center (0°)', gazeYaw: 0, gazePitch: 0 },
            { id: 'gaze_right_30', title: 'Look Right 30°', gazeYaw: 30, gazePitch: 0 },
            { id: 'gaze_left_30', title: 'Look Left 30°', gazeYaw: -30, gazePitch: 0 },
            { id: 'gaze_up_right', title: 'Look Up-Right (25°, 18°)', gazeYaw: 25, gazePitch: 18 },

            // 2. Emotional Range
            { id: 'emotion_happy', title: 'Happy (Smiling Eyes)', emotion: 'HAPPY' },
            { id: 'emotion_thinking', title: 'Thinking (Code Review)', emotion: 'THINKING' },
            { id: 'emotion_surprised', title: 'Surprised', emotion: 'SURPRISED' },
            { id: 'emotion_skeptical', title: 'Skeptical (PR Review)', emotion: 'SKEPTICAL' },
            { id: 'emotion_blink', title: 'Eyelid Blink (Closed)', blink: 1.0 },

            // 3. 9-Viseme Speech Phonetics
            { id: 'viseme_rest', title: 'REST (Closed Confident)', viseme: 'REST' },
            { id: 'viseme_a_i', title: 'A / I (Jaw Drop)', viseme: 'A_I' },
            { id: 'viseme_e', title: 'E (Wide Dental)', viseme: 'E' },
            { id: 'viseme_o', title: 'O (Rounded)', viseme: 'O' },
            { id: 'viseme_u', title: 'U (Pucker)', viseme: 'U' },
            { id: 'viseme_m_b_p', title: 'M / B / P (Pressed)', viseme: 'M_B_P' },
            { id: 'viseme_f_v', title: 'F / V (Teeth on Lip)', viseme: 'F_V' },
            { id: 'viseme_l_th', title: 'L / TH (Tongue Raised)', viseme: 'L_TH' },
            { id: 'viseme_w_q', title: 'W / Q (Tight Pucker)', viseme: 'W_Q' },
        ];

        for (const f of frames) {
            fs.writeFileSync(path.join(projectRoot, 'temp_anim_frame.html'), generateHtml(f));
            await page.goto(`http://localhost:${port}/temp_anim_frame.html`, { waitUntil: 'networkidle0' });
            await page.waitForFunction('window.__READY__ === true', { timeout: 15000 });
            await new Promise(r => setTimeout(r, 150));
            const buf = await page.screenshot();
            fs.writeFileSync(path.join(debugDir, `${f.id}.png`), buf);
            console.log(`Saved debug/${f.id}.png`);
        }

        await browser.close();
        server.close();
        if (fs.existsSync(path.join(projectRoot, 'temp_anim_frame.html'))) {
            fs.unlinkSync(path.join(projectRoot, 'temp_anim_frame.html'));
        }
        console.log('All animation frames rendered successfully!');
    } catch (err) {
        console.error('Error rendering animation frames:', err);
        server.close();
        process.exit(1);
    }
});
