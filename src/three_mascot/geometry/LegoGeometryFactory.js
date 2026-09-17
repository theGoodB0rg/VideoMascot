import * as THREE from 'three';

/**
 * LegoGeometryFactory
 * Procedural 3D Lego Minifigure geometry generator adhering to standard Lego aspect ratios.
 */
export class LegoGeometryFactory {
    constructor() {
        // Standard normalized Lego unit dimensions (Waist-up scale)
        this.units = {
            headDiameter: 1.04,
            headHeight: 1.06,
            studDiameter: 0.48,
            studHeight: 0.16,
            neckDiameter: 0.48,
            neckHeight: 0.05,
            torsoTopWidth: 1.48,
            torsoBottomWidth: 1.96,
            torsoHeight: 1.28,
            torsoDepth: 0.82,
            armLength: 0.90,
            armRadius: 0.22,
            handRadius: 0.24,
            handThickness: 0.13,
            handOpening: 0.20,
            waistWidth: 1.96,
            waistHeight: 0.36,
            waistDepth: 0.82,
        };
    }

    /**
     * Creates the Lego Minifigure head cylinder with rounded top/bottom bevels, stud, and cylindrical UVs.
     */
    createHeadGeometry() {
        const group = new THREE.Group();
        group.name = 'head_assembly';

        const r = this.units.headDiameter / 2.0; // 0.52
        const h = this.units.headHeight;        // 1.06
        const bevelR = 0.08;
        const bevelSegments = 6;

        const points = [];
        points.push(new THREE.Vector2(0.24, -h / 2));
        for (let i = 0; i <= bevelSegments; i++) {
            const angle = (Math.PI / 2) * (1 - i / bevelSegments);
            const px = r - bevelR + Math.cos(angle) * bevelR;
            const py = -h / 2 + bevelR - Math.sin(angle) * bevelR;
            points.push(new THREE.Vector2(px, py));
        }
        points.push(new THREE.Vector2(r, h / 2 - bevelR));
        for (let i = 0; i <= bevelSegments; i++) {
            const angle = (Math.PI / 2) * (i / bevelSegments);
            const px = r - bevelR + Math.cos(angle) * bevelR;
            const py = h / 2 - bevelR + Math.sin(angle) * bevelR;
            points.push(new THREE.Vector2(px, py));
        }
        points.push(new THREE.Vector2(this.units.studDiameter / 2.0, h / 2));
        points.push(new THREE.Vector2(0, h / 2));

        const headGeom = new THREE.LatheGeometry(points, 64, -Math.PI, Math.PI * 2);

        // Custom Cylindrical UV mapping directly derived from physical Y height and 3D angle
        const hPos = headGeom.attributes.position;
        const hUv = headGeom.attributes.uv;
        for (let i = 0; i < hPos.count; i++) {
            const px = hPos.getX(i);
            const py = hPos.getY(i);
            const pz = hPos.getZ(i);
            const theta = Math.atan2(px, pz);
            hUv.setXY(i, 0.5 + theta / (Math.PI * 2), (py + h / 2) / h);
        }
        hUv.needsUpdate = true;
        headGeom.computeVertexNormals();

        // Top stud
        const studR = this.units.studDiameter / 2.0;
        const studH = this.units.studHeight;
        const studGeom = new THREE.CylinderGeometry(studR, studR, studH, 32);
        studGeom.translate(0, h / 2 + studH / 2, 0);

        const headMesh = new THREE.Mesh(headGeom);
        headMesh.name = 'head_main';
        const studMesh = new THREE.Mesh(studGeom);
        studMesh.name = 'head_stud';

        group.add(headMesh);
        group.add(studMesh);

        return { group, headGeom, studGeom };
    }

    /**
     * Creates the authentic molded Lego afro hair piece with open face cutout,
     * wide side lobes covering temples/ears, back neck drape, and tightly packed afro curls.
     */
    createHairGeometry(material = null) {
        const group = new THREE.Group();
        group.name = 'hair_assembly';

        const hairMat = material || new THREE.MeshStandardMaterial({
            color: 0x161413,
            roughness: 0.82,
            metalness: 0.02
        });

        // 1. Parametric Molded Hair Cap BufferGeometry (Lego Part 21778)
        const nTheta = 48;
        const nY = 24;
        const geom = new THREE.BufferGeometry();
        const positions = [];
        const uvs = [];
        const indices = [];

        function getBottomY(theta) {
            const zNorm = -Math.cos(theta); // -1 at back, +1 at front
            const xVal = 0.545 * Math.sin(theta);

            if (zNorm < -0.1) {
                return -0.12; // Back of head covers down towards neck
            } else if (zNorm < 0.35) {
                const t = (zNorm - (-0.1)) / 0.45;
                return -0.12 + 0.10 * t; // Sides over ears
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

        // Generate grid of vertices with sealed top pole
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

        // 2. Tightly packed micro-curls across outer surface (Lego Part 21778)
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

            const relY = py >= capCenterY ? (py - capCenterY) / capH : 0.0;
            const r = py >= capCenterY ? 0.552 * Math.sqrt(Math.max(0, 1.0 - relY * relY)) : 0.552;
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

        return { group, capGeom: geom, curls, bumps: curls };
    }

    /**
     * Creates the classic trapezoidal Lego torso with 10° sloped sides and rounded shoulder bevels.
     */
    createTorsoGeometry() {
        const group = new THREE.Group();
        group.name = 'torso_assembly';

        const topW = this.units.torsoTopWidth;       // 1.48
        const botW = this.units.torsoBottomWidth;    // 1.96
        const h = this.units.torsoHeight;            // 1.28
        const d = this.units.torsoDepth;             // 0.82

        // Create 2D trapezoid shape in XY plane
        const shape = new THREE.Shape();
        const halfTop = topW / 2.0;
        const halfBot = botW / 2.0;
        const halfH = h / 2.0;

        shape.moveTo(-halfBot, -halfH);
        shape.lineTo(halfBot, -halfH);
        shape.lineTo(halfTop, halfH);
        shape.lineTo(-halfTop, halfH);
        shape.closePath();

        // Extrude with slight bevel
        const extrudeSettings = {
            steps: 1,
            depth: d - 0.08,
            bevelEnabled: true,
            bevelThickness: 0.04,
            bevelSize: 0.04,
            bevelSegments: 4,
        };

        const torsoGeom = new THREE.ExtrudeGeometry(shape, extrudeSettings);
        torsoGeom.center(); // Center at (0, 0, 0)
        torsoGeom.computeVertexNormals();

        // Neck stud on top of torso
        const neckR = this.units.neckDiameter / 2.0;
        const neckH = this.units.neckHeight;
        const neckGeom = new THREE.CylinderGeometry(neckR, neckR, neckH, 32);
        neckGeom.translate(0, halfH + neckH / 2.0, 0);

        const torsoMesh = new THREE.Mesh(torsoGeom);
        torsoMesh.name = 'torso_main';
        const neckMesh = new THREE.Mesh(neckGeom);
        neckMesh.name = 'torso_neck';

        group.add(torsoMesh);
        group.add(neckMesh);

        return { group, torsoGeom, neckGeom };
    }

    /**
     * Creates an articulated arm segment with spherical shoulder pivot and forearm socket.
     */
    createArmGeometry(isLeft = true) {
        const group = new THREE.Group();
        group.name = isLeft ? 'arm_left_assembly' : 'arm_right_assembly';

        const armR = this.units.armRadius; // 0.22
        const armL = this.units.armLength; // 1.15

        // Shoulder ball/cap (fits inside torso socket seamlessly)
        const shoulderBall = new THREE.SphereGeometry(armR * 1.1, 24, 16);

        // Upper arm curved cylinder
        const upperArmGeom = new THREE.CylinderGeometry(armR * 1.05, armR * 0.95, armL * 0.55, 24);
        upperArmGeom.translate(0, -armL * 0.275, 0);

        // Forearm curved cylinder tapering down to wrist
        const forearmGeom = new THREE.CylinderGeometry(armR * 0.95, armR * 0.85, armL * 0.5, 24);
        forearmGeom.translate(0, -armL * 0.25, 0);

        // Elbow joint sphere for continuous rotation without severed seams
        const elbowBall = new THREE.SphereGeometry(armR * 0.98, 20, 14);

        const shoulderMesh = new THREE.Mesh(shoulderBall);
        shoulderMesh.name = 'shoulder_pivot';
        const upperArmMesh = new THREE.Mesh(upperArmGeom);
        upperArmMesh.name = 'upper_arm';
        const elbowMesh = new THREE.Mesh(elbowBall);
        elbowMesh.position.y = -armL * 0.55;
        elbowMesh.name = 'elbow_joint';
        const forearmMesh = new THREE.Mesh(forearmGeom);
        forearmMesh.position.y = -armL * 0.55;
        forearmMesh.name = 'forearm';

        group.add(shoulderMesh);
        group.add(upperArmMesh);
        group.add(elbowMesh);
        group.add(forearmMesh);

        return { group, shoulderBall, upperArmGeom, elbowBall, forearmGeom };
    }

    /**
     * Creates the classic Lego C-shaped clamp hand with rotating wrist shaft.
     */
    createHandGeometry(isLeft = true) {
        const group = new THREE.Group();
        group.name = isLeft ? 'hand_left_assembly' : 'hand_right_assembly';

        const cShape = new THREE.Shape();
        const cx = 0.07, cy = -0.14;
        const rOut = 0.17, rIn = 0.10;
        cShape.absarc(cx, cy, rOut, Math.PI * 0.25, Math.PI * 1.75, false);
        cShape.absarc(cx, cy, rIn, Math.PI * 1.75, Math.PI * 0.25, true);
        cShape.closePath();

        const extrudeSettings = {
            steps: 1,
            depth: 0.11,
            bevelEnabled: true,
            bevelThickness: 0.015,
            bevelSize: 0.015,
            bevelSegments: 3,
        };

        const handGeom = new THREE.ExtrudeGeometry(cShape, extrudeSettings);
        handGeom.computeBoundingBox();
        const zMid = (handGeom.boundingBox.min.z + handGeom.boundingBox.max.z) / 2;
        handGeom.translate(0, 0, -zMid);
        handGeom.computeVertexNormals();

        // Wrist pin shaft (rotates in forearm socket)
        const wristR = 0.07;
        const wristH = 0.08;
        const wristGeom = new THREE.CylinderGeometry(wristR, wristR, wristH, 16);
        wristGeom.translate(0, wristH / 2.0, 0);

        const handMesh = new THREE.Mesh(handGeom);
        handMesh.name = 'hand_clamp';
        const sign = isLeft ? -1 : 1;
        handMesh.scale.set(sign, 1, 1);

        const wristMesh = new THREE.Mesh(wristGeom);
        wristMesh.name = 'wrist_pin';

        group.add(handMesh);
        group.add(wristMesh);

        return { group, handGeom, wristGeom };
    }

    /**
     * Creates the waist/hips block matching the waist-up crop constraint.
     */
    createWaistGeometry() {
        const group = new THREE.Group();
        group.name = 'waist_assembly';

        const w = this.units.waistWidth;
        const h = this.units.waistHeight;
        const d = this.units.waistDepth;

        // Beveled rectangular block
        const waistGeom = new THREE.BoxGeometry(w, h, d, 2, 2, 2);
        const waistMesh = new THREE.Mesh(waistGeom);
        waistMesh.name = 'waist_block';

        group.add(waistMesh);
        return { group, waistGeom };
    }
}
