import * as THREE from 'three';
import { LegoMaterialFactory } from '../src/three_mascot/materials/LegoMaterialFactory.js';
import { LegoMinifigure } from '../src/three_mascot/rig/LegoMinifigure.js';

console.log('--- Testing LegoMaterialFactory & PBR Minifigure ---');

const materialFactory = new LegoMaterialFactory();

// 1. Skin Material
const skinMat = materialFactory.createSkinMaterial();
console.assert(skinMat instanceof THREE.MeshPhysicalMaterial, 'Skin should be MeshPhysicalMaterial');
console.assert(skinMat.roughness === 0.25, 'Skin roughness should be 0.25');
console.assert(skinMat.clearcoat === 0.45, 'Skin clearcoat should be 0.45');
console.log('✓ Skin Material: PASSED');

// 2. Head Material
const mockTex = new THREE.Texture();
const headMat = materialFactory.createHeadMaterial(mockTex);
console.assert(headMat.map === mockTex, 'Head material should have mapped texture');
console.assert(headMat.clearcoat === 0.45, 'Head clearcoat should be 0.45');
console.log('✓ Head Material: PASSED');

// 3. Hair Material
const hairMat = materialFactory.createHairMaterial();
console.assert(hairMat instanceof THREE.MeshStandardMaterial, 'Hair should be MeshStandardMaterial');
console.assert(hairMat.roughness === 0.78, 'Hair roughness should be 0.78');
console.log('✓ Hair Material: PASSED');

// 4. Torso Materials
const torsoMat = materialFactory.createTorsoMaterial(mockTex);
const sidesMat = materialFactory.createTorsoSidesMaterial();
console.assert(torsoMat.map === mockTex, 'Torso front should have mapped texture');
console.assert(sidesMat.color.getHex() === 0x9bc3ea, 'Torso sides should match polo light-blue');
console.log('✓ Torso Materials: PASSED');

// 5. Arm Materials
const armMats = materialFactory.createArmMaterials(mockTex, mockTex);
console.assert(armMats.upperArmMat instanceof THREE.MeshPhysicalMaterial, 'Upper arm should be MeshPhysicalMaterial');
console.assert(armMats.forearmMat instanceof THREE.MeshPhysicalMaterial, 'Forearm should be MeshPhysicalMaterial');
console.log('✓ Arm Materials: PASSED');

// 6. Waist Material
const waistMat = materialFactory.createWaistMaterial();
console.assert(waistMat.color.getHex() === 0x1c2b46, 'Waist color should match dark navy');
console.log('✓ Waist Material: PASSED');

// 7. LegoMinifigure in PBR Mode
const figurePbr = new LegoMinifigure({
    materialMode: 'pbr',
    textures: { face: mockTex, torso: mockTex, sleeve: mockTex, forearm: mockTex }
});
console.assert(figurePbr.root.children.length === 6, 'Figure should have 6 top-level parts (waist, torso, head, hair, armL, armR)');
console.assert(figurePbr.parts.head.position.y > 2.0, 'Head should sit proudly on neck (y > 2.0)');
console.log('✓ LegoMinifigure PBR Assembly: PASSED');

console.log('--- All LegoMaterialFactory & PBR tests PASSED successfully! ---');
