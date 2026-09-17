import http from 'http';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';
import { execSync } from 'child_process';

const projectRoot = process.cwd();

// HTML page that renders 3 camera views (Front, 45 deg, Close-up) on a specified background color
function generateHtml(bgColorHex, isDark) {
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
        body { margin: 0; background: #${bgColorHex}; overflow: hidden; }
        canvas { display: block; }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <script type="module">
        import * as THREE from 'three';

        const canvas = document.getElementById('c');
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
        renderer.setSize(700, 850);
        renderer.setPixelRatio(2);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.05;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x${bgColorHex});

        // 3-Point Studio Lighting matching reference CGI render
        const ambient = new THREE.AmbientLight(0x40352c, ${isDark ? '1.1' : '1.3'});
        scene.add(ambient);

        const keyLight = new THREE.DirectionalLight(0xffffff, 2.2);
        keyLight.position.set(3.0, 5.0, 4.0);
        scene.add(keyLight);

        const fillLight = new THREE.DirectionalLight(0xa5c4e8, 0.85);
        fillLight.position.set(-3.5, 2.5, 2.5);
        scene.add(fillLight);

        const rimLight = new THREE.DirectionalLight(0xffeedd, 1.4);
        rimLight.position.set(0.5, 4.0, -3.5);
        scene.add(rimLight);

        // Texture Loader
        const loader = new THREE.TextureLoader();
        const faceTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_face_2k.png');
        faceTex.colorSpace = THREE.SRGBColorSpace;

        const torsoTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_torso_1k.png');
        torsoTex.colorSpace = THREE.SRGBColorSpace;

        const sleeveTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_sleeve_1k.png');
        sleeveTex.colorSpace = THREE.SRGBColorSpace;
        sleeveTex.wrapS = THREE.RepeatWrapping; sleeveTex.wrapT = THREE.RepeatWrapping; sleeveTex.repeat.set(1, 2);

        const forearmTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_forearm_1k.png');
        forearmTex.colorSpace = THREE.SRGBColorSpace;

        // PBR ABS Materials
        const skinMat = new THREE.MeshPhysicalMaterial({ color: 0x9a572e, roughness: 0.25, clearcoat: 0.45, clearcoatRoughness: 0.15 });
        const headMat = new THREE.MeshPhysicalMaterial({ map: faceTex, roughness: 0.25, clearcoat: 0.45, clearcoatRoughness: 0.15 });
        const hairMat = new THREE.MeshStandardMaterial({ color: 0x181615, roughness: 0.78, metalness: 0.02 });
        const torsoMat = new THREE.MeshPhysicalMaterial({ map: torsoTex, roughness: 0.28, clearcoat: 0.38, clearcoatRoughness: 0.20 });
        const torsoSidesMat = new THREE.MeshPhysicalMaterial({ color: 0x9bc3ea, roughness: 0.28, clearcoat: 0.38 });
        const upperArmMat = new THREE.MeshPhysicalMaterial({ map: sleeveTex, roughness: 0.28, clearcoat: 0.38 });
        const forearmMat = new THREE.MeshPhysicalMaterial({ map: forearmTex, roughness: 0.26, clearcoat: 0.42 });
        const waistMat = new THREE.MeshPhysicalMaterial({ color: 0x1c2b46, roughness: 0.30, clearcoat: 0.35 });

        const root = new THREE.Group();
        scene.add(root);

        // 1. Waist
        const waist = new THREE.Mesh(new THREE.BoxGeometry(1.96, 0.36, 0.82), waistMat);
        waist.position.y = 0.18;
        root.add(waist);

        // 2. Torso
        const shape = new THREE.Shape();
        shape.moveTo(-0.96, -0.64); shape.lineTo(0.96, -0.64); shape.lineTo(0.72, 0.64); shape.lineTo(-0.72, 0.64); shape.closePath();
        const torsoGeom = new THREE.ExtrudeGeometry(shape, { steps: 1, depth: 0.74, bevelEnabled: true, bevelThickness: 0.04, bevelSize: 0.04, bevelSegments: 4 });
        torsoGeom.center();
        const posAttr = torsoGeom.attributes.position;
        const uvAttr = torsoGeom.attributes.uv;
        for (let i = 0; i < posAttr.count; i++) {
            const x = posAttr.getX(i), y = posAttr.getY(i), z = posAttr.getZ(i);
            if (z > 0.25) {
                const w = 0.96 - ((y + 0.64) / 1.28) * 0.24;
                uvAttr.setXY(i, Math.max(0, Math.min(1, (x + w) / (2.0 * w))), Math.max(0, Math.min(1, (y + 0.64) / 1.28)));
            }
        }
        uvAttr.needsUpdate = true;
        const torso = new THREE.Mesh(torsoGeom, [torsoMat, torsoSidesMat]);
        torso.position.y = 0.82;
        root.add(torso);

        // 3. Neck
        const neckH = 0.05, neckR = 0.24;
        const neck = new THREE.Mesh(new THREE.CylinderGeometry(neckR, neckR, neckH, 32), skinMat);
        neck.position.y = 0.82 + 0.64 + neckH / 2.0; // 1.485
        root.add(neck);

        // 4. Head
        const headH = 1.06, headR = 0.52;
        const headGroup = new THREE.Group();
        headGroup.position.set(0, 0.82 + 0.64 + neckH + headH / 2.0, 0); // 2.04
        root.add(headGroup);

        const headPoints = [];
        const bR = 0.08;
        headPoints.push(new THREE.Vector2(0.24, -headH/2));
        for (let i = 0; i <= 6; i++) {
            const a = (Math.PI/2) * (1 - i/6);
            headPoints.push(new THREE.Vector2(headR - bR + Math.cos(a)*bR, -headH/2 + bR - Math.sin(a)*bR));
        }
        headPoints.push(new THREE.Vector2(headR, headH/2 - bR));
        for (let i = 0; i <= 6; i++) {
            const a = (Math.PI/2) * (i/6);
            headPoints.push(new THREE.Vector2(headR - bR + Math.cos(a)*bR, headH/2 - bR + Math.sin(a)*bR));
        }
        headPoints.push(new THREE.Vector2(0.24, headH/2));
        headPoints.push(new THREE.Vector2(0, headH/2));

        const headGeom = new THREE.LatheGeometry(headPoints, 64, -Math.PI, Math.PI * 2);
        const hPos = headGeom.attributes.position;
        const hUv = headGeom.attributes.uv;
        for (let i = 0; i < hPos.count; i++) {
            const px = hPos.getX(i), py = hPos.getY(i), pz = hPos.getZ(i);
            const theta = Math.atan2(px, pz);
            hUv.setXY(i, 0.5 + theta / (Math.PI * 2), (py + headH / 2) / headH);
        }
        hUv.needsUpdate = true;
        const head = new THREE.Mesh(headGeom, headMat);
        headGroup.add(head);

        const stud = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.16, 32), skinMat);
        stud.position.y = headH/2 + 0.08;
        headGroup.add(stud);

        // 5. Authentic Lego Afro Hair Piece
        const hairGroup = new THREE.Group();
        hairGroup.position.set(0, 0.22, -0.04);
        headGroup.add(hairGroup);

        const crownGeom = new THREE.SphereGeometry(0.58, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.42);
        crownGeom.scale(1.04, 0.92, 1.04);
        const crownMesh = new THREE.Mesh(crownGeom, hairMat);
        crownMesh.position.set(0, 0.22, -0.01);
        hairGroup.add(crownMesh);

        const sidesGeom = new THREE.SphereGeometry(0.58, 32, 16, Math.PI * 0.72, Math.PI * 1.56, Math.PI * 0.35, Math.PI * 0.42);
        sidesGeom.scale(1.04, 1.05, 1.04);
        const sidesMesh = new THREE.Mesh(sidesGeom, hairMat);
        sidesMesh.position.set(0, 0.12, -0.01);
        hairGroup.add(sidesMesh);

        // Sideburns / Temple lobes
        const leftSide = new THREE.Mesh(new THREE.SphereGeometry(0.24, 18, 14), hairMat);
        leftSide.position.set(-0.48, -0.08, -0.01);
        leftSide.scale.set(0.8, 1.3, 1.0);
        hairGroup.add(leftSide);

        const rightSide = new THREE.Mesh(new THREE.SphereGeometry(0.24, 18, 14), hairMat);
        rightSide.position.set(0.48, -0.08, -0.01);
        rightSide.scale.set(0.8, 1.3, 1.0);
        hairGroup.add(rightSide);

        // Neck Drape down back of head
        const neckDrape = new THREE.Mesh(
            new THREE.CylinderGeometry(0.52, 0.48, 0.36, 24, 1, false, Math.PI * 0.58, Math.PI * 0.84),
            hairMat
        );
        neckDrape.position.set(0, -0.22, -0.06);
        hairGroup.add(neckDrape);

        // Curly pebbled surface bumps
        const bumpGeom = new THREE.SphereGeometry(0.068, 8, 8);
        const bumpCount = 340;
        const bumps = new THREE.InstancedMesh(bumpGeom, hairMat, bumpCount);
        const dummy = new THREE.Object3D();
        const phi = Math.PI * (Math.sqrt(5) - 1);
        let bIdx = 0;
        for (let i = 0; i < 320; i++) {
            const y = 1 - (i / 319) * 1.6;
            if (y < -0.6) continue;
            const radius = Math.sqrt(Math.max(0, 1 - y * y * 0.7));
            const theta = phi * i;
            const px = Math.cos(theta) * radius * 0.60;
            const py = 0.22 + y * 0.55;
            const pz = -0.02 + Math.sin(theta) * radius * 0.61;

            // Don't place bumps in the open face region (high forehead down to chin)
            if (pz > 0.06 && py < 0.16 && Math.abs(px) < 0.38) continue;
            if (pz > 0.18 && py < 0.22 && Math.abs(px) < 0.34) continue;

            if (bIdx < bumpCount) {
                dummy.position.set(px, py, pz);
                const s = 0.95 + (i % 3) * 0.1;
                dummy.scale.set(s, s, s);
                dummy.updateMatrix();
                bumps.setMatrixAt(bIdx++, dummy.matrix);
            }
        }

        // Arched hairline bumps across forehead top (y = 0.12 in hair space = +0.50 in head space)
        const hSteps = 9;
        for (let i = 0; i < hSteps; i++) {
            const t = -1.0 + (2.0 * i) / (hSteps - 1);
            const hx = 0.34 * t;
            const cylR = 0.54;
            const hz = Math.sqrt(Math.max(0, cylR * cylR - hx * hx));
            const hy = 0.10 + 0.05 * (1.0 - t * t);
            if (bIdx < bumpCount) {
                dummy.position.set(hx, hy, hz);
                dummy.scale.set(0.9, 0.9, 0.9);
                dummy.updateMatrix();
                bumps.setMatrixAt(bIdx++, dummy.matrix);
            }
        }
        bumps.count = bIdx;
        bumps.instanceMatrix.needsUpdate = true;
        hairGroup.add(bumps);

        // 6. Arms
        function makeArm(isLeft) {
            const sign = isLeft ? -1 : 1;
            const armRoot = new THREE.Group();
            armRoot.position.set(sign * 0.98, 1.30, 0);
            armRoot.rotation.z = sign * THREE.MathUtils.degToRad(18.5);
            armRoot.rotation.x = THREE.MathUtils.degToRad(-8);
            const shoulder = new THREE.Mesh(new THREE.SphereGeometry(0.24, 24, 16), upperArmMat);
            armRoot.add(shoulder);
            const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.21, 0.46, 24), upperArmMat);
            upper.position.set(0, -0.23, 0);
            armRoot.add(upper);
            const foreGroup = new THREE.Group();
            foreGroup.position.set(0, -0.46, 0);
            foreGroup.rotation.x = THREE.MathUtils.degToRad(-16);
            const elbow = new THREE.Mesh(new THREE.SphereGeometry(0.21, 20, 14), forearmMat);
            foreGroup.add(elbow);
            const fore = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.18, 0.38, 24), forearmMat);
            fore.position.set(0, -0.19, 0);
            foreGroup.add(fore);

            // Wrist peg
            const wrist = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.08, 16), skinMat);
            wrist.position.set(0, -0.40, 0);
            foreGroup.add(wrist);

            // C-Hand: spine connects at wrist, opening faces inward (towards body)
            const cShape = new THREE.Shape();
            const cx = 0.07, cy = -0.14;
            const rOut = 0.17, rIn = 0.10;
            cShape.absarc(cx, cy, rOut, Math.PI * 0.25, Math.PI * 1.75, false);
            cShape.absarc(cx, cy, rIn, Math.PI * 1.75, Math.PI * 0.25, true);
            cShape.closePath();

            const handGeom = new THREE.ExtrudeGeometry(cShape, {
                steps: 1, depth: 0.11, bevelEnabled: true, bevelThickness: 0.015, bevelSize: 0.015, bevelSegments: 3
            });
            handGeom.computeBoundingBox();
            const zMid = (handGeom.boundingBox.min.z + handGeom.boundingBox.max.z) / 2;
            handGeom.translate(0, 0, -zMid);

            const hand = new THREE.Mesh(handGeom, skinMat);
            hand.scale.set(sign, 1, 1);
            hand.position.set(0, -0.42, 0);
            hand.rotation.set(THREE.MathUtils.degToRad(12), sign * THREE.MathUtils.degToRad(-10), 0);
            foreGroup.add(hand);

            armRoot.add(foreGroup);
            return armRoot;
        }
        root.add(makeArm(true));
        root.add(makeArm(false));

        // Camera Views
        const camera = new THREE.PerspectiveCamera(26, 700 / 850, 0.1, 50);

        window.__setCameraView = function(viewType) {
            if (viewType === 'front') {
                camera.position.set(0, 1.42, 7.6);
                camera.lookAt(0, 1.40, 0);
            } else if (viewType === 'perspective') {
                camera.position.set(4.0, 1.65, 6.5);
                camera.lookAt(0, 1.40, 0);
            } else if (viewType === 'closeup') {
                camera.position.set(0, 2.08, 2.8);
                camera.lookAt(0, 2.04, 0);
            }
            renderer.render(scene, camera);
        };

        THREE.DefaultLoadingManager.onLoad = () => {
            window.__READY_FOR_RENDER__ = true;
        };
    </script>
</body>
</html>`;
}

async function renderView(page, viewType) {
    await page.evaluate((v) => window.__setCameraView(v), viewType);
    await new Promise(r => setTimeout(r, 200));
    return await page.screenshot();
}

const server = http.createServer((req, res) => {
    let reqUrl = req.url.split('?')[0];
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
    console.log(`Rendering Gate 2 on port ${port}...`);

    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader']
        });

        // 1. Render Dark Views
        fs.writeFileSync(path.resolve(projectRoot, 'temp_gate2_dark.html'), generateHtml('121218', true));
        const pageDark = await browser.newPage();
        await pageDark.setViewport({ width: 700, height: 850 });
        await pageDark.goto(`http://localhost:${port}/temp_gate2_dark.html`, { waitUntil: 'networkidle0' });
        await pageDark.waitForFunction('window.__READY_FOR_RENDER__ === true', { timeout: 15000 });

        const darkFront = await renderView(pageDark, 'front');
        const darkPersp = await renderView(pageDark, 'perspective');
        const darkClose = await renderView(pageDark, 'closeup');
        await pageDark.close();
        fs.unlinkSync(path.resolve(projectRoot, 'temp_gate2_dark.html'));

        // 2. Render Light Views
        fs.writeFileSync(path.resolve(projectRoot, 'temp_gate2_light.html'), generateHtml('ffffff', false));
        const pageLight = await browser.newPage();
        await pageLight.setViewport({ width: 700, height: 850 });
        await pageLight.goto(`http://localhost:${port}/temp_gate2_light.html`, { waitUntil: 'networkidle0' });
        await pageLight.waitForFunction('window.__READY_FOR_RENDER__ === true', { timeout: 15000 });

        const lightFront = await renderView(pageLight, 'front');
        const lightPersp = await renderView(pageLight, 'perspective');
        const lightClose = await renderView(pageLight, 'closeup');
        await pageLight.close();
        fs.unlinkSync(path.resolve(projectRoot, 'temp_gate2_light.html'));

        await browser.close();

        // Save view screenshots
        fs.writeFileSync(path.resolve(projectRoot, 'preview/temp_g2_dark_front.png'), darkFront);
        fs.writeFileSync(path.resolve(projectRoot, 'preview/temp_g2_dark_persp.png'), darkPersp);
        fs.writeFileSync(path.resolve(projectRoot, 'preview/temp_g2_dark_close.png'), darkClose);

        fs.writeFileSync(path.resolve(projectRoot, 'preview/temp_g2_light_front.png'), lightFront);
        fs.writeFileSync(path.resolve(projectRoot, 'preview/temp_g2_light_persp.png'), lightPersp);
        fs.writeFileSync(path.resolve(projectRoot, 'preview/temp_g2_light_close.png'), lightClose);

        console.log('Saved 6 perspective view renders.');
        console.log('Running python scripts/composite_gate2.py to generate final inspection sheet...');
        execSync('python scripts/composite_gate2.py', { stdio: 'inherit' });
    } catch (err) {
        console.error('Error generating Gate 2 sheet:', err);
    } finally {
        server.close();
    }
});
