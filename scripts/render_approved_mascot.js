import http from 'http';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';

const ROOT = 'C:/Users/HP/Desktop/Personal Websites/VideoMascot';
const previewDir = path.join(ROOT, 'preview');
const debugDir = path.join(previewDir, 'debug');

function generateHtml(options = {}) {
    const viseme = options.viseme || 'REST';
    const blink = options.blink || 0.0;
    const hideHead = options.hideHead || false;
    const hideBody = options.hideBody || false;
    const gesture = options.gesture || 'idle';

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
        body { margin: 0; background: transparent; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <script type="module">
        import * as THREE from 'three';
        import { LegoGeometryFactory } from '/src/three_mascot/geometry/LegoGeometryFactory.js';
        import { LegoMaterialFactory } from '/src/three_mascot/materials/LegoMaterialFactory.js';
        import { ProceduralFacePainter } from '/src/three_mascot/textures/ProceduralFacePainter.js';
        import { ProceduralTorsoPainter } from '/src/three_mascot/textures/ProceduralTorsoPainter.js';

        try {
            const canvas = document.getElementById('c');
            const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
            renderer.setSize(1000, 1000);
            renderer.setPixelRatio(1);
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.toneMappingExposure = 1.05;

            const scene = new THREE.Scene();

            // Studio Lighting matching test_render_heads.js
            const ambient = new THREE.AmbientLight(0x40352c, 1.2);
            scene.add(ambient);

            const keyLight = new THREE.DirectionalLight(0xffffff, 2.4);
            keyLight.position.set(3.0, 5.0, 4.0);
            scene.add(keyLight);

            const fillLight = new THREE.DirectionalLight(0xa5c4e8, 0.9);
            fillLight.position.set(-3.5, 2.5, 2.5);
            scene.add(fillLight);

            const frontLight = new THREE.DirectionalLight(0xfff0e4, 0.75);
            frontLight.position.set(0, 2.0, 4.5);
            scene.add(frontLight);

            const rimLight = new THREE.DirectionalLight(0xffeedd, 1.6);
            rimLight.position.set(0.5, 4.0, -3.5);
            scene.add(rimLight);

            const geomFactory = new LegoGeometryFactory();
            const matFactory = new LegoMaterialFactory();

            // 1. Head Assembly with Approved Hair & Procedural Face
            const painter = new ProceduralFacePainter({ width: 2048, height: 1024 });
            const faceCanvas = painter.initCanvas();
            painter.setState({ viseme: '${viseme}', blink: ${blink} });
            painter.render();

            const cleanTex = new THREE.CanvasTexture(faceCanvas);
            cleanTex.colorSpace = THREE.SRGBColorSpace;

            const headData = geomFactory.createHeadGeometry();
            const headGroup = headData.group;
            headGroup.position.set(0, 2.04, 0);

            const headMesh = headGroup.getObjectByName('head_main');
            const studMesh = headGroup.getObjectByName('head_stud');
            headMesh.material = matFactory.createHeadMaterial(cleanTex);
            studMesh.material = matFactory.createSkinMaterial();

            // Afro Hair from test_render_heads.js (Approved Part 21778)
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

                const capRadius = 0.548;
                const yTop = 0.84;
                const capCenterY = 0.28;
                const capH = yTop - capCenterY;

                function getBottomY(theta) {
                    const zNorm = -Math.cos(theta);
                    const xVal = capRadius * Math.sin(theta);
                    if (zNorm < -0.1) return -0.12;
                    else if (zNorm < 0.35) {
                        const t = (zNorm - (-0.1)) / 0.45;
                        return -0.12 + 0.16 * t;
                    } else {
                        const yForehead = 0.27 - 0.38 * (xVal * xVal);
                        const t = Math.min(1.0, (zNorm - 0.35) / 0.35);
                        return 0.04 * (1.0 - t) + yForehead * t;
                    }
                }

                for (let j = 0; j <= nY; j++) {
                    const vFrac = j / nY;
                    for (let i = 0; i <= nTheta; i++) {
                        const theta = -Math.PI + (2.0 * Math.PI * i) / nTheta;
                        const yBot = getBottomY(theta);
                        const y = yTop - vFrac * (yTop - yBot);
                        let px, py, pz;
                        if (j === 0) { px = 0; py = yTop; pz = 0; }
                        else {
                            let r;
                            if (y >= capCenterY) {
                                const relY = (y - capCenterY) / capH;
                                r = capRadius * Math.sqrt(Math.max(0, 1.0 - relY * relY));
                            } else { r = capRadius; }
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
                        const a = j * (nTheta + 1) + i;
                        const b = (j + 1) * (nTheta + 1) + i;
                        const c = (j + 1) * (nTheta + 1) + (i + 1);
                        const d = j * (nTheta + 1) + (i + 1);
                        indices.push(a, b, d);
                        indices.push(b, c, d);
                    }
                }
                geom.setIndex(indices);
                geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                geom.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
                geom.computeVertexNormals();

                const capMesh = new THREE.Mesh(geom, hairMat);
                capMesh.material.side = THREE.DoubleSide;
                group.add(capMesh);

                const curlGeom = new THREE.SphereGeometry(0.022, 8, 8);
                const curlCount = 1400;
                const curls = new THREE.InstancedMesh(curlGeom, hairMat, curlCount);
                const dummy = new THREE.Object3D();
                const goldenAngle = Math.PI * (3.0 - Math.sqrt(5));
                let cIdx = 0;
                const totalSamples = 1600;

                for (let i = 0; i < totalSamples && cIdx < curlCount; i++) {
                    const u = (i + 0.5) / totalSamples;
                    const theta = goldenAngle * i;
                    const normTheta = Math.atan2(Math.sin(theta), Math.cos(theta));
                    const yBot = getBottomY(normTheta);
                    const v = Math.sqrt(u);
                    const py = yTop - v * (yTop - yBot);
                    let r = py >= capCenterY ? 0.552 * Math.sqrt(Math.max(0, 1.0 - Math.pow((py - capCenterY) / capH, 2))) : 0.552;
                    const px = r * Math.sin(normTheta);
                    const pz = -r * Math.cos(normTheta);
                    if (cIdx < curlCount) {
                        dummy.position.set(px, py, pz);
                        const s = 0.88 + (i % 4) * 0.08;
                        dummy.scale.set(s, s, s);
                        dummy.updateMatrix();
                        curls.setMatrixAt(cIdx++, dummy.matrix);
                    }
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
                curls.instanceMatrix.needsUpdate = true;
                group.add(curls);
                return group;
            }

            const hair = createLegoAfroHair();
            hair.position.add(headGroup.position);

            const neckGeom = new THREE.CylinderGeometry(0.24, 0.24, 0.18, 32);
            const neckMesh = new THREE.Mesh(neckGeom, matFactory.createSkinMaterial());
            neckMesh.position.set(0, 2.04 - 0.56, 0);

            const fullHeadGroup = new THREE.Group();
            fullHeadGroup.add(headGroup);
            fullHeadGroup.add(hair);
            fullHeadGroup.add(neckMesh);
            if (options_hideHead) fullHeadGroup.visible = false;
            scene.add(fullHeadGroup);

            // 2. Procedural Torso Assembly
            const torsoPainter = new ProceduralTorsoPainter({ width: 1024, height: 1024 });
            const torsoCanvas = torsoPainter.initCanvas();
            torsoPainter.renderFront();
            const torsoTex = new THREE.CanvasTexture(torsoCanvas);
            torsoTex.colorSpace = THREE.SRGBColorSpace;

            const sleeveCanvas = torsoPainter.renderSleeve();
            const sleeveTex = new THREE.CanvasTexture(sleeveCanvas);
            sleeveTex.colorSpace = THREE.SRGBColorSpace;
            sleeveTex.wrapS = THREE.RepeatWrapping;
            sleeveTex.wrapT = THREE.RepeatWrapping;

            const forearmCanvas = torsoPainter.renderForearm();
            const forearmTex = new THREE.CanvasTexture(forearmCanvas);
            forearmTex.colorSpace = THREE.SRGBColorSpace;

            const armMats = matFactory.createArmMaterials(sleeveTex, forearmTex);
            const skinMat = matFactory.createSkinMaterial();

            const bodyGroup = new THREE.Group();

            // Waist
            const waistData = geomFactory.createWaistGeometry();
            const waist = waistData.group;
            waist.position.set(0, 0.18, 0);
            waist.traverse(c => { if (c.isMesh) c.material = matFactory.createWaistMaterial(); });
            bodyGroup.add(waist);

            // Torso
            const torsoData = geomFactory.createTorsoGeometry();
            const torso = torsoData.group;
            torso.position.set(0, 0.82, 0);
            const torsoMainMesh = torso.getObjectByName('torso_main');
            if (torsoMainMesh) {
                torsoMainMesh.material = [matFactory.createTorsoMaterial(torsoTex), matFactory.createTorsoSidesMaterial()];
            }
            const torsoNeckMesh = torso.getObjectByName('torso_neck');
            if (torsoNeckMesh) {
                torsoNeckMesh.material = skinMat;
            }
            bodyGroup.add(torso);

            // Arms & Hands
            const armLData = geomFactory.createArmGeometry(true);
            const armL = armLData.group;
            armL.position.set(-0.98, 1.30, 0);
            armL.traverse(c => { if (c.isMesh) c.material = armMats.upperArmMat; });

            const handLData = geomFactory.createHandGeometry(true);
            const handL = handLData.group;
            handL.position.set(-0.02, -1.14, 0.04);
            handL.traverse(c => { if (c.isMesh) c.material = skinMat; });
            armL.add(handL);

            const armRData = geomFactory.createArmGeometry(false);
            const armR = armRData.group;
            armR.position.set(0.98, 1.30, 0);
            armR.traverse(c => { if (c.isMesh) c.material = armMats.upperArmMat; });

            const handRData = geomFactory.createHandGeometry(false);
            const handR = handRData.group;
            handR.position.set(0.02, -1.14, 0.04);
            handR.traverse(c => { if (c.isMesh) c.material = skinMat; });
            armR.add(handR);

            // Apply Gesture to Arms
            const gest = '${gesture}';
            if (gest === 'idle') {
                armL.rotation.z = THREE.MathUtils.degToRad(-18.5);
                armL.rotation.x = THREE.MathUtils.degToRad(-8);
                handL.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(15), 0);
                armR.rotation.z = THREE.MathUtils.degToRad(18.5);
                armR.rotation.x = THREE.MathUtils.degToRad(-8);
                handR.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(165), 0);
            } else if (gest === 'point_left') {
                armL.rotation.z = THREE.MathUtils.degToRad(-65);
                armL.rotation.x = THREE.MathUtils.degToRad(-25);
                handL.rotation.set(0, THREE.MathUtils.degToRad(45), 0);
                armR.rotation.z = THREE.MathUtils.degToRad(18.5);
                armR.rotation.x = THREE.MathUtils.degToRad(-8);
                handR.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(165), 0);
            } else if (gest === 'point_right') {
                armR.rotation.z = THREE.MathUtils.degToRad(65);
                armR.rotation.x = THREE.MathUtils.degToRad(-25);
                handR.rotation.set(0, THREE.MathUtils.degToRad(-45), 0);
                armL.rotation.z = THREE.MathUtils.degToRad(-18.5);
                armL.rotation.x = THREE.MathUtils.degToRad(-8);
                handL.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(15), 0);
            } else if (gest === 'wave') {
                armL.rotation.z = THREE.MathUtils.degToRad(-130);
                armL.rotation.x = THREE.MathUtils.degToRad(-15);
                handL.rotation.set(0, 0, THREE.MathUtils.degToRad(30));
                armR.rotation.z = THREE.MathUtils.degToRad(18.5);
                armR.rotation.x = THREE.MathUtils.degToRad(-8);
                handR.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(165), 0);
            }

            bodyGroup.add(armL);
            bodyGroup.add(armR);
            if (options_hideBody) bodyGroup.visible = false;
            scene.add(bodyGroup);

            // 3. Unified Camera Setup for exact 1:1 front_full registration
            const camera = new THREE.PerspectiveCamera(28, 1.0, 0.1, 50);
            camera.position.set(0, 1.45, 5.85);
            camera.lookAt(0, 1.45, 0);

            renderer.render(scene, camera);
            window.__READY__ = true;
        } catch (err) {
            console.error('Three.js Script Error:', err);
            window.__ERROR__ = err.message;
        }
    </script>
</body>
</html>`.replace('options_hideHead', hideHead ? 'true' : 'false')
    .replace('options_hideBody', hideBody ? 'true' : 'false');
}

const server = http.createServer((req, res) => {
    let reqUrl = req.url.split('?')[0];
    if (reqUrl === '/') reqUrl = '/temp_render_approved.html';
    const filePath = path.join(ROOT, reqUrl);
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
    console.log(`Approved mascot renderer listening on port ${port}...`);

    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--enable-webgl']
        });
        const page = await browser.newPage();
        page.on('console', msg => console.log('PAGE LOG:', msg.text()));
        page.on('pageerror', err => console.error('PAGE ERROR:', err.message));
        await page.setViewport({ width: 1000, height: 1000 });

        const assetDir = path.join(ROOT, 'assets/mascots/brick_dev');
        const headDir = path.join(assetDir, 'head');
        const bodyDir = path.join(assetDir, 'body');
        fs.mkdirSync(path.join(headDir, 'mouth'), { recursive: true });
        fs.mkdirSync(path.join(headDir, 'eyes'), { recursive: true });
        fs.mkdirSync(path.join(bodyDir, 'hands'), { recursive: true });

        // 1. Render Approved Heads / Visemes in UNIFIED front_full registration
        const visemes = [
            { id: 'REST', name: 'rest', isBase: true },
            { id: 'A_AH', name: 'A_I' },
            { id: 'E_EE', name: 'E' },
            { id: 'O_OH', name: 'O' },
            { id: 'U', name: 'U' },
            { id: 'M_B_P', name: 'M_B_P' },
            { id: 'F_V', name: 'F_V' },
            { id: 'L_TH', name: 'L_D_T_N' },
            { id: 'W_Q', name: 'W_Q' },
            { id: 'SMILE_OPEN', name: 'open_smile' },
            { id: 'REST', name: 'smile' },
        ];

        for (const item of visemes) {
            fs.writeFileSync(path.join(ROOT, 'temp_render_approved.html'), generateHtml({
                viseme: item.id,
                hideBody: true,
                hideHead: false
            }));
            await page.goto(`http://localhost:${port}/temp_render_approved.html`, { waitUntil: 'networkidle0' });
            await page.waitForFunction('window.__READY__ === true || window.__ERROR__', { timeout: 15000 });
            const hasErr = await page.evaluate(() => window.__ERROR__);
            if (hasErr) throw new Error('Page reported: ' + hasErr);
            const buf = await page.screenshot({ omitBackground: true });

            fs.writeFileSync(path.join(headDir, `head_${item.name}.png`), buf);
            if (item.isBase) {
                fs.writeFileSync(path.join(headDir, 'head_base.png'), buf);
                fs.writeFileSync(path.join(headDir, 'head_rest.png'), buf);
                fs.writeFileSync(path.join(headDir, 'head_point.png'), buf);
                fs.writeFileSync(path.join(headDir, 'head_wave.png'), buf);
                fs.writeFileSync(path.join(debugDir, 'head_3d_clean_molded_alpha.png'), buf);
            }
            console.log(`Rendered transparent head viseme: head_${item.name}.png`);
        }

        // Render Blink Head
        fs.writeFileSync(path.join(ROOT, 'temp_render_approved.html'), generateHtml({
            viseme: 'REST',
            blink: 1.0,
            hideBody: true,
            hideHead: false
        }));
        await page.goto(`http://localhost:${port}/temp_render_approved.html`, { waitUntil: 'networkidle0' });
        await page.waitForFunction('window.__READY__ === true || window.__ERROR__', { timeout: 15000 });
        const blinkBuf = await page.screenshot({ omitBackground: true });
        fs.writeFileSync(path.join(headDir, 'head_blink.png'), blinkBuf);
        console.log('Rendered transparent head viseme: head_blink.png');

        // 2. Render Full Body Poses in UNIFIED front_full registration
        const gestures = [
            { id: 'idle', file: 'torso.png' },
            { id: 'idle', file: 'torso_rest.png' },
            { id: 'point_left', file: 'torso_point_l.png' },
            { id: 'point_right', file: 'torso_point_r.png' },
            { id: 'wave', file: 'torso_wave.png' },
        ];

        for (const g of gestures) {
            fs.writeFileSync(path.join(ROOT, 'temp_render_approved.html'), generateHtml({
                gesture: g.id,
                hideHead: true,
                hideBody: false
            }));
            await page.goto(`http://localhost:${port}/temp_render_approved.html`, { waitUntil: 'networkidle0' });
            await page.waitForFunction('window.__READY__ === true || window.__ERROR__', { timeout: 15000 });
            const bodyBuf = await page.screenshot({ omitBackground: true });
            fs.writeFileSync(path.join(bodyDir, g.file), bodyBuf);
            console.log(`Rendered transparent procedural body: ${g.file}`);
        }

        // 3. Render Full Composite Check (Head + Body together)
        fs.writeFileSync(path.join(ROOT, 'temp_render_approved.html'), generateHtml({
            gesture: 'idle',
            hideHead: false,
            hideBody: false
        }));
        await page.goto(`http://localhost:${port}/temp_render_approved.html`, { waitUntil: 'networkidle0' });
        await page.waitForFunction('window.__READY__ === true || window.__ERROR__', { timeout: 15000 });
        const fullBuf = await page.screenshot({ omitBackground: true });
        fs.writeFileSync(path.join(previewDir, 'check_approved_full_minifigure.png'), fullBuf);
        console.log('Rendered full composite check: preview/check_approved_full_minifigure.png');

        await browser.close();
        server.close();
        if (fs.existsSync(path.join(ROOT, 'temp_render_approved.html'))) {
            fs.unlinkSync(path.join(ROOT, 'temp_render_approved.html'));
        }
        console.log('ALL APPROVED ASSETS RENDERED IN UNIFIED 1:1 REGISTRATION SUCCESSFULLY!');
    } catch (err) {
        console.error('Error rendering approved mascot:', err);
        server.close();
        process.exit(1);
    }
});
