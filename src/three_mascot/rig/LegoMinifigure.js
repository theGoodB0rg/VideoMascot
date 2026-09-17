import * as THREE from 'three';
import { LegoGeometryFactory } from '../geometry/LegoGeometryFactory.js';
import { LegoMaterialFactory } from '../materials/LegoMaterialFactory.js';

/**
 * LegoMinifigure
 * Assembles the full procedural 3D Lego Minifigure hierarchy supporting both Clay and PBR modes.
 */
export class LegoMinifigure {
    constructor(options = {}) {
        this.factory = new LegoGeometryFactory();
        this.materialFactory = new LegoMaterialFactory();
        this.root = new THREE.Group();
        this.root.name = 'minifigure_root';
        this.materialMode = options.materialMode || 'clay'; // 'clay' or 'pbr'
        this.textures = options.textures || {};

        this.parts = {};
        this.buildHierarchy();
    }

    createClayMaterial() {
        return new THREE.MeshStandardMaterial({
            color: 0x94a3b8, // Neutral studio clay grey
            roughness: 0.45,
            metalness: 0.05,
        });
    }

    buildHierarchy() {
        const isPbr = this.materialMode === 'pbr';
        const clayMat = this.createClayMaterial();

        // 1. Waist (Base of waist-up figure)
        const waistData = this.factory.createWaistGeometry();
        this.waist = waistData.group;
        this.waist.position.set(0, 0.18, 0);
        if (isPbr) {
            this.applyMaterial(this.waist, this.materialFactory.createWaistMaterial());
        } else {
            this.applyMaterial(this.waist, clayMat);
        }
        this.root.add(this.waist);

        // 2. Torso
        const torsoData = this.factory.createTorsoGeometry();
        this.torso = torsoData.group;
        this.torso.position.set(0, 0.18 + 0.64, 0); // y = 0.82
        if (isPbr) {
            const torsoMainMesh = this.torso.getObjectByName('torso_main');
            if (torsoMainMesh) {
                const frontMat = this.materialFactory.createTorsoMaterial(this.textures.torso);
                const sidesMat = this.materialFactory.createTorsoSidesMaterial();
                torsoMainMesh.material = [frontMat, sidesMat];
            }
            const torsoNeckMesh = this.torso.getObjectByName('torso_neck');
            if (torsoNeckMesh) {
                torsoNeckMesh.material = this.materialFactory.createSkinMaterial();
            }
        } else {
            this.applyMaterial(this.torso, clayMat);
        }
        this.root.add(this.torso);

        // 3. Head & Neck
        const neckH = this.factory.units.neckHeight;
        const headH = this.factory.units.headHeight;
        const headData = this.factory.createHeadGeometry();
        this.head = headData.group;
        // Head sits on neck cylinder
        this.head.position.set(0, 0.82 + 0.64 + neckH + headH / 2.0, 0); // y = 2.04
        if (isPbr) {
            const headMain = this.head.getObjectByName('head_main');
            if (headMain) {
                headMain.material = this.materialFactory.createHeadMaterial(this.textures.face);
            }
            const headStud = this.head.getObjectByName('head_stud');
            if (headStud) {
                headStud.material = this.materialFactory.createSkinMaterial();
            }
        } else {
            this.applyMaterial(this.head, clayMat);
        }
        this.root.add(this.head);

        // 4. Afro Hair
        const hairMat = isPbr
            ? this.materialFactory.createHairMaterial()
            : new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.65 });
        const hairData = this.factory.createHairGeometry(hairMat);
        this.hair = hairData.group;
        this.hair.position.add(this.head.position);
        this.root.add(this.hair);

        // Arm materials
        let armMaterials = { upperArmMat: clayMat, forearmMat: clayMat, skinMat: clayMat };
        if (isPbr) {
            const mats = this.materialFactory.createArmMaterials(this.textures.sleeve, this.textures.forearm);
            armMaterials = {
                upperArmMat: mats.upperArmMat,
                forearmMat: mats.forearmMat,
                skinMat: this.materialFactory.createSkinMaterial(),
            };
        }

        // 5. Left Arm (positioned outside torso with 18.5° outward flare and forward drape)
        const armLData = this.factory.createArmGeometry(true);
        this.armL = armLData.group;
        this.armL.position.set(-0.98, 1.30, 0);
        this.armL.rotation.z = THREE.MathUtils.degToRad(-18.5);
        this.armL.rotation.x = THREE.MathUtils.degToRad(-8);
        this.setupArmMaterials(this.armL, armMaterials, isPbr);
        this.root.add(this.armL);

        // Left Hand
        const handLData = this.factory.createHandGeometry(true);
        this.handL = handLData.group;
        this.handL.position.set(-0.02, -1.14, 0.04);
        this.handL.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(15), 0);
        this.applyMaterial(this.handL, armMaterials.skinMat);
        this.armL.add(this.handL);

        // 6. Right Arm (positioned outside torso with 18.5° outward flare and forward drape)
        const armRData = this.factory.createArmGeometry(false);
        this.armR = armRData.group;
        this.armR.position.set(0.98, 1.30, 0);
        this.armR.rotation.z = THREE.MathUtils.degToRad(18.5);
        this.armR.rotation.x = THREE.MathUtils.degToRad(-8);
        this.setupArmMaterials(this.armR, armMaterials, isPbr);
        this.root.add(this.armR);

        // Right Hand
        const handRData = this.factory.createHandGeometry(false);
        this.handR = handRData.group;
        this.handR.position.set(0.02, -1.14, 0.04);
        this.handR.rotation.set(THREE.MathUtils.degToRad(15), THREE.MathUtils.degToRad(165), 0);
        this.applyMaterial(this.handR, armMaterials.skinMat);
        this.armR.add(this.handR);

        this.parts = {
            waist: this.waist,
            torso: this.torso,
            head: this.head,
            hair: this.hair,
            armL: this.armL,
            handL: this.handL,
            armR: this.armR,
            handR: this.handR,
        };
    }

    setupArmMaterials(armGroup, materials, isPbr) {
        if (!isPbr) {
            this.applyMaterial(armGroup, materials.upperArmMat);
            return;
        }
        const shoulder = armGroup.getObjectByName('shoulder_pivot');
        if (shoulder) shoulder.material = materials.upperArmMat;
        const upper = armGroup.getObjectByName('upper_arm');
        if (upper) upper.material = materials.upperArmMat;
        const elbow = armGroup.getObjectByName('elbow_joint');
        if (elbow) elbow.material = materials.forearmMat;
        const fore = armGroup.getObjectByName('forearm');
        if (fore) fore.material = materials.forearmMat;
    }

    applyMaterial(group, material) {
        group.traverse((child) => {
            if (child.isMesh) {
                child.material = material;
                child.castShadow = true;
                child.receiveShadow = true;
            }
        });
    }

    setMaterialMode(mode, textures = {}) {
        this.materialMode = mode;
        this.textures = textures;
        while (this.root.children.length > 0) {
            this.root.remove(this.root.children[0]);
        }
        this.buildHierarchy();
    }

    setFacePainter(facePainter, faceTexture) {
        this.facePainter = facePainter;
        this.faceTexture = faceTexture;
    }

    setGaze(options = {}) {
        if (!this.facePainter) return;
        const yawDeg = options.yawDeg ?? 0;
        const pitchDeg = options.pitchDeg ?? 0;
        this.facePainter.setGazeAngle(yawDeg, pitchDeg);
        this.facePainter.render();
        if (this.faceTexture) this.faceTexture.needsUpdate = true;
    }

    setEmotion(emotionName, intensity = 1.0) {
        if (!this.facePainter) return;
        this.facePainter.setEmotion(emotionName, intensity);
        this.facePainter.render();
        if (this.faceTexture) this.faceTexture.needsUpdate = true;
    }

    setBlink(amount, blinkLeft = null, blinkRight = null) {
        if (!this.facePainter) return;
        this.facePainter.setState({
            blink: amount,
            blinkLeft: blinkLeft,
            blinkRight: blinkRight,
        });
        this.facePainter.render();
        if (this.faceTexture) this.faceTexture.needsUpdate = true;
    }

    speakViseme(visemeId) {
        if (!this.facePainter) return;
        this.facePainter.setState({ viseme: visemeId });
        this.facePainter.render();
        if (this.faceTexture) this.faceTexture.needsUpdate = true;
    }
}

