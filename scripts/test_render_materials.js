import puppeteer from 'puppeteer-core';
import http from 'http';
import fs from 'fs';
import path from 'path';

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
        body { margin: 0; background: #121218; display: flex; gap: 20px; justify-content: center; align-items: center; height: 100vh; }
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

        const camera = new THREE.PerspectiveCamera(35, 600 / 720, 0.1, 50);
        camera.position.set(0, 1.42, 5.2);
        camera.lookAt(0, 1.35, 0);

        // 3-Point Studio Lighting matching reference CGI render
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

        // Texture Loader
        const loader = new THREE.TextureLoader();
        const faceTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_face_2k.png');
        faceTex.colorSpace = THREE.SRGBColorSpace;

        const torsoTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_torso_1k.png');
        torsoTex.colorSpace = THREE.SRGBColorSpace;

        const sleeveTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_sleeve_1k.png');
        sleeveTex.colorSpace = THREE.SRGBColorSpace;
        sleeveTex.wrapS = THREE.RepeatWrapping;
        sleeveTex.wrapT = THREE.RepeatWrapping;
        sleeveTex.repeat.set(1, 2);

        const forearmTex = loader.load('/assets/mascots/brick_dev/textures/brick_dev_forearm_1k.png');
        forearmTex.colorSpace = THREE.SRGBColorSpace;

        // PBR ABS Materials
        const skinMat = new THREE.MeshPhysicalMaterial({
            color: 0x9a572e,
            roughness: 0.25,
            metalness: 0.0,
            clearcoat: 0.45,
            clearcoatRoughness: 0.15
        });

        const headMat = new THREE.MeshPhysicalMaterial({
            map: faceTex,
            roughness: 0.25,
            metalness: 0.0,
            clearcoat: 0.45,
            clearcoatRoughness: 0.15
        });

        const hairMat = new THREE.MeshStandardMaterial({
            color: 0x181615,
            roughness: 0.75,
            metalness: 0.02
        });

        const torsoMat = new THREE.MeshPhysicalMaterial({
            map: torsoTex,
            roughness: 0.28,
            metalness: 0.0,
            clearcoat: 0.38,
            clearcoatRoughness: 0.20
        });

        const upperArmMat = new THREE.MeshPhysicalMaterial({
            map: sleeveTex,
            roughness: 0.28,
            metalness: 0.0,
            clearcoat: 0.38,
            clearcoatRoughness: 0.20
        });

        const forearmMat = new THREE.MeshPhysicalMaterial({
            map: forearmTex,
            roughness: 0.26,
            metalness: 0.0,
            clearcoat: 0.42,
            clearcoatRoughness: 0.18
        });

        const waistMat = new THREE.MeshPhysicalMaterial({
            color: 0x1c2b46,
            roughness: 0.30,
            metalness: 0.0,
            clearcoat: 0.35,
            clearcoatRoughness: 0.22
        });

        const root = new THREE.Group();
        scene.add(root);

        // 1. Waist
        const waist = new THREE.Mesh(new THREE.BoxGeometry(1.96, 0.36, 0.82), waistMat);
        waist.position.y = 0.18;
        root.add(waist);

        // 2. Torso
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

        const posAttr = torsoGeom.attributes.position;
        const uvAttr = torsoGeom.attributes.uv;
        for (let i = 0; i < posAttr.count; i++) {
            const x = posAttr.getX(i);
            const y = posAttr.getY(i);
            const z = posAttr.getZ(i);
            if (z > 0.25) {
                const w = 0.96 - ((y + 0.64) / 1.28) * 0.24;
                const u = (x + w) / (2.0 * w);
                const v = (y + 0.64) / 1.28;
                uvAttr.setXY(i, Math.max(0, Math.min(1, u)), Math.max(0, Math.min(1, v)));
            }
        }
        uvAttr.needsUpdate = true;

        const torsoSidesMat = new THREE.MeshPhysicalMaterial({
            color: 0x9bc3ea,
            roughness: 0.28,
            metalness: 0.0,
            clearcoat: 0.38,
            clearcoatRoughness: 0.20
        });

        const torso = new THREE.Mesh(torsoGeom, [torsoMat, torsoSidesMat]);
        torso.position.y = 0.82;
        root.add(torso);

        // Neck: authentic Lego neck cylinder rising cleanly out of the torso collar
        const neckH = 0.16;
        const neckR = 0.25;
        const neck = new THREE.Mesh(new THREE.CylinderGeometry(neckR, neckR, neckH, 32), skinMat);
        neck.position.y = 0.82 + 0.64 + neckH / 2.0; // 1.54
        root.add(neck);

        // 3. Head: Sits on top of the neck cylinder
        const headH = 0.94;
        const headR = 0.51;
        const headGroup = new THREE.Group();
        headGroup.position.set(0, 0.82 + 0.64 + neckH + headH / 2.0, 0); // 2.09
        root.add(headGroup);

        const headPoints = [];
        const bR = 0.08;
        headPoints.push(new THREE.Vector2(0.25, -headH/2));
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
            const px = hPos.getX(i);
            const py = hPos.getY(i);
            const pz = hPos.getZ(i);
            const theta = Math.atan2(px, pz);
            let u = 0.5 + theta / (Math.PI * 2);
            let v = (py + headH / 2) / headH;
            hUv.setXY(i, u, v);
        }
        hUv.needsUpdate = true;

        const head = new THREE.Mesh(headGeom, headMat);
        headGroup.add(head);

        const stud = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.16, 32), skinMat);
        stud.position.y = headH/2 + 0.08;
        headGroup.add(stud);

        // 4. Authentic Lego Afro Hair Piece with Open Face Cutout
        // The hair wraps around top, back, and sides, leaving the face completely open
        const hairGroup = new THREE.Group();
        hairGroup.position.set(0, 0.08, -0.02);
        headGroup.add(hairGroup);

        // A. Top Crown Dome: covers top of head, stops cleanly at forehead hairline (theta = 0 to 0.36*PI)
        const crownGeom = new THREE.SphereGeometry(0.65, 32, 16, 0, Math.PI * 2, 0, Math.PI * 0.36);
        const crownMesh = new THREE.Mesh(crownGeom, hairMat);
        crownMesh.position.set(0, 0.22, -0.02);
        hairGroup.add(crownMesh);

        // B. Back & Sides Shell: covers temples, sideburns, and back of head, OPEN in the front 75 degrees
        // phiStart = 0.21*PI, phiLength = 1.58*PI (leaves [-38 deg, +38 deg] open in front)
        const sidesGeom = new THREE.SphereGeometry(0.64, 32, 16, Math.PI * 0.21, Math.PI * 1.58, Math.PI * 0.32, Math.PI * 0.36);
        const sidesMesh = new THREE.Mesh(sidesGeom, hairMat);
        sidesMesh.position.set(0, 0.20, -0.02);
        hairGroup.add(sidesMesh);

        // C. Lower Back Neck Drape
        const neckDrapeGeom = new THREE.CylinderGeometry(0.58, 0.54, 0.32, 24, 1, true, Math.PI * 0.60, Math.PI * 0.80);
        const neckDrapeMesh = new THREE.Mesh(neckDrapeGeom, hairMat);
        neckDrapeMesh.position.set(0, -0.08, -0.08);
        hairGroup.add(neckDrapeMesh);

        // D. Sideburn Cushions (tapered along sides of cheeks)
        const leftSideburn = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.08, 0.32, 16), hairMat);
        leftSideburn.position.set(-0.46, -0.04, 0.16);
        leftSideburn.rotation.z = THREE.MathUtils.degToRad(-12);
        hairGroup.add(leftSideburn);

        const rightSideburn = new THREE.Mesh(new THREE.CylinderGeometry(0.12, 0.08, 0.32, 16), hairMat);
        rightSideburn.position.set(0.46, -0.04, 0.16);
        rightSideburn.rotation.z = THREE.MathUtils.degToRad(12);
        hairGroup.add(rightSideburn);

        // E. Tight Curly Afro Pebbles distributed over the hair surface
        const bumpGeom = new THREE.SphereGeometry(0.080, 10, 10);
        const bumpCount = 420;
        const bumps = new THREE.InstancedMesh(bumpGeom, hairMat, bumpCount);
        const dummy = new THREE.Object3D();

        let bIdx = 0;
        // 1. Crown pebbles (Fibonacci lattice on top dome)
        const phi = Math.PI * (Math.sqrt(5) - 1);
        for (let i = 0; i < 220; i++) {
            const y = 1 - (i / 219) * 0.70; // top 70% of sphere
            const radius = Math.sqrt(Math.max(0, 1 - y * y));
            const theta = phi * i;
            const px = Math.cos(theta) * radius * 0.66;
            const py = 0.22 + y * 0.66;
            const pz = -0.02 + Math.sin(theta) * radius * 0.66;

            // Strict exclusion: NEVER enter face opening
            if (pz > 0.15 && py < 0.40) continue;

            if (bIdx < bumpCount) {
                dummy.position.set(px, py, pz);
                const s = 0.92 + (i % 3) * 0.12;
                dummy.scale.set(s, s, s);
                dummy.updateMatrix();
                bumps.setMatrixAt(bIdx++, dummy.matrix);
            }
        }

        // 2. Scalloped front hairline right above eyebrows
        const hairSteps = 11;
        for (let i = 0; i < hairSteps; i++) {
            const t = -1.0 + (2.0 * i) / (hairSteps - 1); // -1 to 1
            const hx = 0.36 * t;
            const cylR = 0.54;
            const hz = Math.sqrt(Math.max(0, cylR * cylR - hx * hx));
            // Scalloped hairline: peaks slightly higher in center, dips at temples
            const hy = 0.26 + 0.03 * (1.0 - t * t) + 0.015 * Math.cos(t * Math.PI * 4.0);
            if (bIdx < bumpCount) {
                dummy.position.set(hx, hy, hz);
                dummy.scale.set(1.05, 1.05, 1.05);
                dummy.updateMatrix();
                bumps.setMatrixAt(bIdx++, dummy.matrix);
            }
        }

        // 3. Sideburn pebbles along the cheeks down to eye/nose level
        const sideSteps = 7;
        for (let sign of [-1, 1]) {
            for (let i = 0; i < sideSteps; i++) {
                const sFrac = i / (sideSteps - 1); // 0 (top) to 1 (bottom)
                const sx = sign * (0.44 + 0.05 * (1.0 - sFrac));
                const sy = 0.22 - 0.30 * sFrac;
                const sz = 0.30 - 0.25 * sFrac;
                if (bIdx < bumpCount) {
                    dummy.position.set(sx, sy, sz);
                    dummy.scale.set(1.05, 1.05, 1.05);
                    dummy.updateMatrix();
                    bumps.setMatrixAt(bIdx++, dummy.matrix);
                }
            }
        }

        // 4. Back and side outer pebbles
        for (let i = 0; i < 90; i++) {
            const angle = Math.PI * 0.25 + (i / 89) * Math.PI * 1.50; // around sides and back
            const r = 0.65;
            const px = Math.cos(angle) * r;
            const pz = -0.02 + Math.sin(angle) * r;
            const py = 0.02 + ((i % 5) - 2) * 0.08;
            if (bIdx < bumpCount) {
                dummy.position.set(px, py, pz);
                dummy.scale.set(1.0, 1.0, 1.0);
                dummy.updateMatrix();
                bumps.setMatrixAt(bIdx++, dummy.matrix);
            }
        }

        bumps.count = bIdx;
        bumps.instanceMatrix.needsUpdate = true;
        hairGroup.add(bumps);

        // 5. Arms
        function makeArm(isLeft) {
            const sign = isLeft ? -1 : 1;
            const armRoot = new THREE.Group();
            armRoot.position.set(sign * 0.98, 1.30, 0);
            armRoot.rotation.z = sign * THREE.MathUtils.degToRad(18.5);
            armRoot.rotation.x = THREE.MathUtils.degToRad(-8);

            // Shoulder ball (matches shirt)
            const shoulder = new THREE.Mesh(new THREE.SphereGeometry(0.24, 24, 16), upperArmMat);
            armRoot.add(shoulder);

            // Upper arm (striped sleeve)
            const upper = new THREE.Mesh(new THREE.CylinderGeometry(0.23, 0.21, 0.48, 24), upperArmMat);
            upper.position.set(0, -0.24, 0);
            armRoot.add(upper);

            const foreGroup = new THREE.Group();
            foreGroup.position.set(0, -0.48, 0);
            foreGroup.rotation.x = THREE.MathUtils.degToRad(-18);

            // Elbow joint sphere
            const elbow = new THREE.Mesh(new THREE.SphereGeometry(0.21, 20, 14), forearmMat);
            foreGroup.add(elbow);

            // Forearm (cuff + brown skin)
            const fore = new THREE.Mesh(new THREE.CylinderGeometry(0.21, 0.18, 0.42, 24), forearmMat);
            fore.position.set(0, -0.21, 0);
            foreGroup.add(fore);

            // Wrist pin (brown skin)
            const wrist = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.12, 16), skinMat);
            wrist.position.set(0, -0.42, 0);
            foreGroup.add(wrist);

            // Hand (brown skin)
            const cShape = new THREE.Shape();
            const outerR = 0.24, innerR = 0.15;
            const gap = Math.PI * 0.46;
            cShape.absarc(0, 0, outerR, gap/2, Math.PI * 2 - gap/2, false);
            cShape.absarc(0, 0, innerR, Math.PI * 2 - gap/2, gap/2, true);
            cShape.closePath();

            const handGeom = new THREE.ExtrudeGeometry(cShape, {
                steps: 1, depth: 0.13, bevelEnabled: true, bevelThickness: 0.02, bevelSize: 0.02, bevelSegments: 3
            });
            handGeom.center();
            const hand = new THREE.Mesh(handGeom, skinMat);

            if (isLeft) {
                hand.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(15), 0);
            } else {
                hand.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(165), 0);
            }
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

        // Wait for textures to load then render
        THREE.DefaultLoadingManager.onLoad = () => {
            renderer.render(scene, camera);
            window.__MATERIAL_TEST_DONE__ = true;
        };
    </script>
</body>
</html>`;

fs.writeFileSync(path.resolve(projectRoot, 'test_materials.html'), html);

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
        await page.goto(`http://localhost:${port}/test_materials.html`, { waitUntil: 'networkidle0' });
        await page.waitForFunction('window.__MATERIAL_TEST_DONE__ === true', { timeout: 12000 });
        const buf = await page.screenshot();
        fs.writeFileSync(path.resolve(projectRoot, 'preview/test_material_render.png'), buf);
        console.log('Saved preview/test_material_render.png');
        await browser.close();
    } catch (e) {
        console.error('Error:', e);
    } finally {
        server.close();
        try { fs.unlinkSync(path.resolve(projectRoot, 'test_materials.html')); } catch(e){}
    }
});
