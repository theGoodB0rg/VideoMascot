import http from 'http';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';

const projectRoot = process.cwd();

const html = `<!DOCTYPE html>
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
        body { margin: 0; background: #121218; display: flex; justify-content: center; align-items: center; height: 100vh; }
        canvas { width: 600px; height: 720px; }
    </style>
</head>
<body>
    <canvas id="c"></canvas>
    <script type="module">
        import * as THREE from 'three';

        const canvas = document.getElementById('c');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x121218);

        const camera = new THREE.PerspectiveCamera(32, 600 / 720, 0.1, 50);
        camera.position.set(0, 1.45, 5.2);
        camera.lookAt(0, 1.38, 0);

        // 3-Point Studio Lighting
        const ambient = new THREE.AmbientLight(0x40352c, 1.1);
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

        // 3. Neck: authentic Lego neck cylinder rising cleanly out of the torso collar
        const neckH = 0.14, neckR = 0.24;
        const neck = new THREE.Mesh(new THREE.CylinderGeometry(neckR, neckR, neckH, 32), skinMat);
        neck.position.y = 0.82 + 0.64 + neckH / 2.0; // 1.53
        root.add(neck);

        // 4. Head: squat, authentic proportions (r=0.52, h=0.88)
        const headH = 0.88, headR = 0.52;
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
        // The hair is an authentic molded helmet: wide afro dome covering crown, sides, and back,
        // with an open face window so the eyes and expression are completely visible
        const hairGroup = new THREE.Group();
        hairGroup.position.set(0, 0.10, -0.04);
        headGroup.add(hairGroup);

        // A. Top Crown Dome (theta: 0 to 0.35*PI): covers top of head, stops at forehead hairline
        const crownGeom = new THREE.SphereGeometry(0.68, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.35);
        crownGeom.scale(1.06, 0.95, 1.06);
        const crownMesh = new THREE.Mesh(crownGeom, hairMat);
        crownMesh.position.set(0, 0.16, -0.02);
        hairGroup.add(crownMesh);

        // B. Back & Sides Shell: covers temples, sideburns, and back of head
        // In Three.js SphereGeometry, +Z (front) is at phi = 0.5*PI.
        // Opening front [-38 deg, +38 deg] means phi from 0.30*PI to 0.70*PI is EMPTY.
        // Shell runs around back: phiStart = 0.70*PI, phiLength = 1.60*PI
        const sidesGeom = new THREE.SphereGeometry(0.68, 32, 16, Math.PI * 0.70, Math.PI * 1.60, Math.PI * 0.30, Math.PI * 0.38);
        sidesGeom.scale(1.06, 0.95, 1.06);
        const sidesMesh = new THREE.Mesh(sidesGeom, hairMat);
        sidesMesh.position.set(0, 0.16, -0.02);
        hairGroup.add(sidesMesh);

        // C. Left and Right Ear/Temple Side Volumes (flares over ears/cheeks)
        const leftSide = new THREE.Mesh(new THREE.SphereGeometry(0.32, 20, 16), hairMat);
        leftSide.position.set(-0.48, 0.0, -0.02);
        leftSide.scale.set(0.9, 1.3, 1.1);
        hairGroup.add(leftSide);

        const rightSide = new THREE.Mesh(new THREE.SphereGeometry(0.32, 20, 16), hairMat);
        rightSide.position.set(0.48, 0.0, -0.02);
        rightSide.scale.set(0.9, 1.3, 1.1);
        hairGroup.add(rightSide);

        // D. Lower Back Neck Drape
        const neckDrape = new THREE.Mesh(
            new THREE.CylinderGeometry(0.58, 0.54, 0.30, 24, 1, false, Math.PI * 0.58, Math.PI * 0.84),
            hairMat
        );
        neckDrape.position.set(0, -0.10, -0.08);
        hairGroup.add(neckDrape);

        // E. Tight Curly Afro Pebbles on outer hair surface
        const bumpGeom = new THREE.SphereGeometry(0.082, 10, 10);
        const bumpCount = 380;
        const bumps = new THREE.InstancedMesh(bumpGeom, hairMat, bumpCount);
        const dummy = new THREE.Object3D();
        const phi = Math.PI * (Math.sqrt(5) - 1);
        let bIdx = 0;
        for (let i = 0; i < 360; i++) {
            const y = 1 - (i / 359) * 1.5;
            if (y < -0.5) continue;
            const radius = Math.sqrt(Math.max(0, 1 - y * y * 0.7));
            const theta = phi * i;
            const px = Math.cos(theta) * radius * 0.70;
            const py = 0.16 + y * 0.64;
            const pz = -0.02 + Math.sin(theta) * radius * 0.72;

            // Strict exclusion: keep face opening completely clear
            // Face window spans -0.38 to +0.38 in X, and up to y=0.34 in Y
            if (pz > 0.08 && py < 0.34 && Math.abs(px) < 0.40) continue;

            if (bIdx < bumpCount) {
                dummy.position.set(px, py, pz);
                const s = 0.95 + (i % 3) * 0.1;
                dummy.scale.set(s, s, s);
                dummy.updateMatrix();
                bumps.setMatrixAt(bIdx++, dummy.matrix);
            }
        }

        // Hairline curb (a single neat scalloped row right along the hairline arch)
        const hSteps = 9;
        for (let i = 0; i < hSteps; i++) {
            const t = -1.0 + (2.0 * i) / (hSteps - 1); // -1 to 1
            const hx = 0.32 * t;
            const cylR = 0.54;
            const hz = Math.sqrt(Math.max(0, cylR * cylR - hx * hx));
            // Gentle natural arch: 0.32 at center, 0.28 at temples
            const hy = 0.28 + 0.04 * (1.0 - t * t);
            if (bIdx < bumpCount) {
                dummy.position.set(hx, hy, hz);
                dummy.scale.set(1.0, 1.0, 1.0);
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
            const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.21, 0.48, 24), upperArmMat);
            upper.position.set(0, -0.24, 0);
            armRoot.add(upper);
            const foreGroup = new THREE.Group();
            foreGroup.position.set(0, -0.48, 0);
            foreGroup.rotation.x = THREE.MathUtils.degToRad(-18);
            const elbow = new THREE.Mesh(new THREE.SphereGeometry(0.21, 20, 14), forearmMat);
            foreGroup.add(elbow);
            const fore = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.18, 0.42, 24), forearmMat);
            fore.position.set(0, -0.21, 0);
            foreGroup.add(fore);
            const wrist = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.12, 16), skinMat);
            wrist.position.set(0, -0.42, 0);
            foreGroup.add(wrist);
            const cShape = new THREE.Shape();
            cShape.absarc(0, 0, 0.24, Math.PI * 0.23, Math.PI * 1.77, false);
            cShape.absarc(0, 0, 0.15, Math.PI * 1.77, Math.PI * 0.23, true);
            cShape.closePath();
            const handGeom = new THREE.ExtrudeGeometry(cShape, { steps: 1, depth: 0.13, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 3 });
            handGeom.center();
            const hand = new THREE.Mesh(handGeom, skinMat);
            hand.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(isLeft ? 15 : 165), 0);
            hand.position.set(0, -0.52, 0.02);
            foreGroup.add(hand);
            armRoot.add(foreGroup);
            return armRoot;
        }
        root.add(makeArm(true));
        root.add(makeArm(false));

        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
        renderer.setSize(600, 720);
        renderer.setPixelRatio(2);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.05;

        THREE.DefaultLoadingManager.onLoad = () => {
            renderer.render(scene, camera);
            window.__RENDER_DONE__ = true;
        };
    </script>
</body>
</html>`;

fs.writeFileSync(path.resolve(projectRoot, 'temp_sculpt.html'), html);

const server = http.createServer((req, res) => {
    let reqUrl = req.url.split('?')[0];
    const filePath = path.join(projectRoot, reqUrl);
    if (fs.existsSync(filePath) && fs.statSync(filePath).isFile()) {
        const ext = path.extname(filePath).toLowerCase();
        const mime = ext === '.html' ? 'text/html' : (ext === '.png' ? 'image/png' : (ext === '.js' ? 'text/javascript' : 'application/octet-stream'));
        res.writeHead(200, { 'Content-Type': mime });
        fs.createReadStream(filePath).pipe(res);
    } else {
        res.writeHead(404);
        res.end();
    }
});

server.listen(0, async () => {
    const port = server.address().port;
    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--enable-webgl', '--use-gl=angle', '--use-angle=swiftshader']
        });
        const page = await browser.newPage();
        await page.setViewport({ width: 600, height: 720 });
        await page.goto(`http://localhost:${port}/temp_sculpt.html`, { waitUntil: 'networkidle0' });
        await page.waitForFunction('window.__RENDER_DONE__ === true', { timeout: 12000 });
        const buf = await page.screenshot();
        fs.writeFileSync(path.resolve(projectRoot, 'preview/test_sculpt_render.png'), buf);
        console.log('Saved preview/test_sculpt_render.png');
        await browser.close();
    } catch(e) {
        console.error('Error:', e);
    } finally {
        server.close();
        try { fs.unlinkSync(path.resolve(projectRoot, 'temp_sculpt.html')); } catch(e){}
    }
});
