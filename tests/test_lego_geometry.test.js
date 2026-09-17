import { LegoGeometryFactory } from '../src/three_mascot/geometry/LegoGeometryFactory.js';
import * as THREE from 'three';

console.log('--- Testing LegoGeometryFactory ---');

const factory = new LegoGeometryFactory();

// 1. Head Geometry
const head = factory.createHeadGeometry();
console.assert(head.group instanceof THREE.Group, 'Head should return a THREE.Group');
console.assert(head.headGeom.attributes.position.count > 0, 'Head geometry should have vertices');
console.assert(head.headGeom.attributes.uv !== undefined, 'Head geometry should have UV attributes');
console.assert(head.studGeom.attributes.position.count > 0, 'Stud geometry should have vertices');
console.log('✓ Head Geometry: PASSED');

// 2. Hair Geometry
const hair = factory.createHairGeometry();
console.assert(hair.group instanceof THREE.Group, 'Hair should return a THREE.Group');
console.assert(hair.bumps.count >= 140, 'Hair should have at least 140 instanced curls');
console.log('✓ Hair Geometry: PASSED');

// 3. Torso Geometry
const torso = factory.createTorsoGeometry();
console.assert(torso.group instanceof THREE.Group, 'Torso should return a THREE.Group');
console.assert(torso.torsoGeom.attributes.position.count > 0, 'Torso should have vertices');
console.assert(torso.neckGeom.attributes.position.count > 0, 'Torso neck should have vertices');
console.log('✓ Torso Geometry: PASSED');

// 4. Arm Geometry
const armL = factory.createArmGeometry(true);
const armR = factory.createArmGeometry(false);
console.assert(armL.group.name === 'arm_left_assembly', 'Left arm name match');
console.assert(armR.group.name === 'arm_right_assembly', 'Right arm name match');
console.log('✓ Arm Geometry: PASSED');

// 5. Hand Geometry
const handL = factory.createHandGeometry(true);
console.assert(handL.group instanceof THREE.Group, 'Hand should return a THREE.Group');
console.assert(handL.handGeom.attributes.position.count > 0, 'Hand geometry should have vertices');
console.log('✓ Hand Geometry: PASSED');

// 6. Waist Geometry
const waist = factory.createWaistGeometry();
console.assert(waist.group instanceof THREE.Group, 'Waist should return a THREE.Group');
console.log('✓ Waist Geometry: PASSED');

console.log('--- All LegoGeometryFactory tests PASSED successfully! ---');
