import * as THREE from 'three';

/**
 * LegoMaterialFactory
 * Photorealistic PBR ABS Plastic materials and texture mapping for Brick Dev.
 */
export class LegoMaterialFactory {
    constructor() {
        this.colors = {
            skin: 0x9a572e,
            hair: 0x181615,
            poloSides: 0x9bc3ea,
            waist: 0x1c2b46,
        };
    }

    /**
     * Creates authentic ABS plastic skin material for neck, hands, and pin joints.
     */
    createSkinMaterial(overrides = {}) {
        return new THREE.MeshPhysicalMaterial({
            color: this.colors.skin,
            roughness: 0.25,
            metalness: 0.0,
            clearcoat: 0.45,
            clearcoatRoughness: 0.15,
            ...overrides,
        });
    }

    /**
     * Creates head material with 2K cylindrical face texture.
     */
    createHeadMaterial(faceTexture, overrides = {}) {
        if (faceTexture) {
            faceTexture.colorSpace = THREE.SRGBColorSpace;
        }
        return new THREE.MeshPhysicalMaterial({
            map: faceTexture,
            roughness: 0.25,
            metalness: 0.0,
            clearcoat: 0.45,
            clearcoatRoughness: 0.15,
            ...overrides,
        });
    }

    /**
     * Creates matte ABS plastic material for curly afro hair piece.
     */
    createHairMaterial(overrides = {}) {
        return new THREE.MeshStandardMaterial({
            color: this.colors.hair,
            roughness: 0.78,
            metalness: 0.02,
            ...overrides,
        });
    }

    /**
     * Creates torso front print material with polo stripes and placket.
     */
    createTorsoMaterial(torsoTexture, overrides = {}) {
        if (torsoTexture) {
            torsoTexture.colorSpace = THREE.SRGBColorSpace;
        }
        return new THREE.MeshPhysicalMaterial({
            map: torsoTexture,
            roughness: 0.28,
            metalness: 0.0,
            clearcoat: 0.38,
            clearcoatRoughness: 0.20,
            ...overrides,
        });
    }

    /**
     * Creates smooth light-blue plastic material for extruded torso sides and bevels.
     */
    createTorsoSidesMaterial(overrides = {}) {
        return new THREE.MeshPhysicalMaterial({
            color: this.colors.poloSides,
            roughness: 0.28,
            metalness: 0.0,
            clearcoat: 0.38,
            clearcoatRoughness: 0.20,
            ...overrides,
        });
    }

    /**
     * Creates sleeve and forearm materials.
     */
    createArmMaterials(sleeveTexture, forearmTexture, overrides = {}) {
        if (sleeveTexture) {
            sleeveTexture.colorSpace = THREE.SRGBColorSpace;
            sleeveTexture.wrapS = THREE.RepeatWrapping;
            sleeveTexture.wrapT = THREE.RepeatWrapping;
            sleeveTexture.repeat.set(1, 2);
        }
        if (forearmTexture) {
            forearmTexture.colorSpace = THREE.SRGBColorSpace;
        }

        const upperArmMat = new THREE.MeshPhysicalMaterial({
            map: sleeveTexture,
            roughness: 0.28,
            metalness: 0.0,
            clearcoat: 0.38,
            clearcoatRoughness: 0.20,
            ...overrides,
        });

        const forearmMat = new THREE.MeshPhysicalMaterial({
            map: forearmTexture,
            roughness: 0.26,
            metalness: 0.0,
            clearcoat: 0.42,
            clearcoatRoughness: 0.18,
            ...overrides,
        });

        return { upperArmMat, forearmMat };
    }

    /**
     * Creates dark navy plastic material for waist/pants block.
     */
    createWaistMaterial(overrides = {}) {
        return new THREE.MeshPhysicalMaterial({
            color: this.colors.waist,
            roughness: 0.30,
            metalness: 0.0,
            clearcoat: 0.35,
            clearcoatRoughness: 0.22,
            ...overrides,
        });
    }

    /**
     * Asynchronously loads all 4 mascot textures.
     */
    loadTextures(loader, basePath = '/assets/mascots/brick_dev/textures/') {
        const face = loader.load(`${basePath}brick_dev_face_2k.png`);
        const torso = loader.load(`${basePath}brick_dev_torso_1k.png`);
        const sleeve = loader.load(`${basePath}brick_dev_sleeve_1k.png`);
        const forearm = loader.load(`${basePath}brick_dev_forearm_1k.png`);

        return { face, torso, sleeve, forearm };
    }
}
