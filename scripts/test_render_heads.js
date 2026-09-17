import http from 'http';
import fs from 'fs';
import path from 'path';
import puppeteer from 'puppeteer-core';

const projectRoot = process.cwd();
const previewDir = path.join(projectRoot, 'preview');
const debugDir = path.join(previewDir, 'debug');

function generateHtml(viseme = 'REST', blink = 0.0) {
    const activeViseme = viseme === 'BLINK' ? 'REST' : viseme;
    const blinkVal = viseme === 'BLINK' ? 1.0 : blink;
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
        import { ProceduralFacePainter } from '/src/three_mascot/textures/ProceduralFacePainter.js';

        const canvas = document.getElementById('c');
        const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
        renderer.setSize(800, 800);
        renderer.setPixelRatio(2);
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.05;

        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x121218);

        // Studio Lighting matching concept art
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

        // 100% CODED PROCEDURAL VECTOR FACE (ZERO photo overlay / crop)
        const painter = new ProceduralFacePainter({ width: 2048, height: 1024 });
        const faceCanvas = painter.initCanvas();
        painter.setState({ viseme: '${activeViseme}', blink: ${blinkVal} });
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

        // Calibrated Molded Lego Afro Hair Piece (Part 21778 - Snug, low-profile dome)
        function createLegoAfroHair() {
            const group = new THREE.Group();
            group.name = 'afro_hair';
            const hairMat = new THREE.MeshStandardMaterial({
                color: 0x1a1715,
                roughness: 0.82,
                metalness: 0.02
            });

            // 1. Parametric Molded Hair Cap BufferGeometry
            const nTheta = 48;
            const nY = 24;
            const geom = new THREE.BufferGeometry();
            const positions = [];
            const uvs = [];
            const indices = [];

            // Forehead hairline contour function (smooth rounded arch, no sharp peak)
            function getBottomY(theta) {
                const zNorm = -Math.cos(theta); // -1 at back, +1 at front
                const xVal = 0.545 * Math.sin(theta);

                if (zNorm < -0.1) {
                    // Back of head: covers down to y = -0.12
                    return -0.12;
                } else if (zNorm < 0.35) {
                    // Sides & ears: transition smoothly up to sideburns
                    const t = (zNorm - (-0.1)) / 0.45;
                    return -0.12 + 0.10 * t;
                } else {
                    // Front forehead: gentle, rounded parabolic arch
                    const yForehead = 0.29 - 0.40 * (xVal * xVal);
                    const t = Math.min(1.0, (zNorm - 0.35) / 0.35);
                    return -0.02 * (1.0 - t) + yForehead * t;
                }
            }

            const yTop = 0.75;
            const capCenterY = 0.26;
            const capH = yTop - capCenterY; // 0.49

            // Generate grid of vertices (sealed top pole)
            for (let j = 0; j <= nY; j++) {
                const vFrac = j / nY;
                for (let i = 0; i <= nTheta; i++) {
                    const theta = -Math.PI + (2.0 * Math.PI * i) / nTheta;
                    const yBot = getBottomY(theta);
                    const y = yTop - vFrac * (yTop - yBot);

                    let px, py, pz;
                    if (j === 0) {
                        // Sealed top pole
                        px = 0;
                        py = yTop;
                        pz = 0;
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

            // Triangles
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

            // 2. Instanced micro-curls tightly hugging the outer surface
            const curlGeom = new THREE.SphereGeometry(0.034, 8, 8);
            const curlCount = 850;
            const curls = new THREE.InstancedMesh(curlGeom, hairMat, curlCount);
            const dummy = new THREE.Object3D();

            const phi = Math.PI * (Math.sqrt(5) - 1);
            let cIdx = 0;
            for (let i = 0; i < 1300; i++) {
                const u = i / 1299.0;
                const theta = phi * i;
                const normTheta = Math.atan2(Math.sin(theta), Math.cos(theta));
                const yBot = getBottomY(normTheta);

                const v = Math.sqrt(u);
                const py = yTop - v * (yTop - yBot);

                let r;
                if (py >= capCenterY) {
                    const relY = (py - capCenterY) / capH;
                    r = 0.552 * Math.sqrt(Math.max(0, 1.0 - relY * relY));
                } else {
                    r = 0.552;
                }

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

            // Hairline rim curls right along the forehead arch (scalloped afro hairline)
            const rimSteps = 36;
            for (let i = 0; i <= rimSteps; i++) {
                const t = -1.0 + (2.0 * i) / rimSteps; // -1 to +1 across front
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

        // Neck cylinder
        const neckGeom = new THREE.CylinderGeometry(0.24, 0.24, 0.18, 32);
        const neckMesh = new THREE.Mesh(neckGeom, matFactory.createSkinMaterial());
        neckMesh.position.set(0, 2.04 - 0.56, 0);

        scene.add(headGroup);
        scene.add(hair);
        scene.add(neckMesh);

        renderer.render(scene, camera);
        window.__READY__ = true;
    </script>
</body>
</html>`;
}

const server = http.createServer((req, res) => {
    let reqUrl = req.url.split('?')[0];
    if (reqUrl === '/') reqUrl = '/temp_render_heads.html';
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
    console.log(`Rendering clean 3D head on port ${port}...`);

    try {
        const browser = await puppeteer.launch({
            executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
            headless: 'new',
            args: ['--no-sandbox', '--disable-setuid-sandbox', '--enable-webgl']
        });

        const page = await browser.newPage();
        await page.setViewport({ width: 800, height: 800 });

        const visemes = ['REST', 'A_AH', 'O_OH', 'E_EE', 'M_B_P', 'SMILE_OPEN', 'BLINK'];
        for (const v of visemes) {
            fs.writeFileSync(path.join(projectRoot, 'temp_render_heads.html'), generateHtml(v));
            await page.goto(`http://localhost:${port}/temp_render_heads.html`, { waitUntil: 'networkidle0' });
            await page.waitForFunction('window.__READY__ === true', { timeout: 15000 });
            await new Promise(r => setTimeout(r, 200));
            const buf = await page.screenshot();
            
            const outName = `3d_viseme_${v.toLowerCase()}.png`;
            fs.writeFileSync(path.join(debugDir, outName), buf);
            console.log(`Saved debug/${outName}`);
            if (v === 'REST') {
                fs.writeFileSync(path.join(debugDir, 'head_3d_clean_molded.png'), buf);
            }
        }

        await browser.close();
        server.close();
        if (fs.existsSync(path.join(projectRoot, 'temp_render_heads.html'))) {
            fs.unlinkSync(path.join(projectRoot, 'temp_render_heads.html'));
        }
    } catch (err) {
        console.error('Error rendering clean 3D head:', err);
        server.close();
        process.exit(1);
    }
});
