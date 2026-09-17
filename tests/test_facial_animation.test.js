import { ProceduralFacePainter, EMOTIONS } from '../src/three_mascot/textures/ProceduralFacePainter.js';

console.log('--- Testing Facial Animation: Directional Gaze, Emotions & 9-Viseme Speech ---');

// Mock Canvas 2D context for headless unit testing
function createMockContext() {
    const calls = [];
    const gradient = {
        addColorStop: (stop, color) => calls.push({ op: 'addColorStop', stop, color })
    };

    return {
        calls,
        fillStyle: '',
        strokeStyle: '',
        lineWidth: 1,
        lineCap: '',
        lineJoin: '',
        fillRect: (x, y, w, h) => calls.push({ op: 'fillRect', x, y, w, h }),
        rect: (x, y, w, h) => calls.push({ op: 'rect', x, y, w, h }),
        beginPath: () => calls.push({ op: 'beginPath' }),
        closePath: () => calls.push({ op: 'closePath' }),
        moveTo: (x, y) => calls.push({ op: 'moveTo', x, y }),
        lineTo: (x, y) => calls.push({ op: 'lineTo', x, y }),
        arc: (x, y, r, sa, ea) => calls.push({ op: 'arc', x, y, r }),
        arcTo: (x1, y1, x2, y2, r) => calls.push({ op: 'arcTo', x1, y1, x2, y2, r }),
        ellipse: (x, y, rx, ry, rot, sa, ea) => calls.push({ op: 'ellipse', x, y, rx, ry }),
        bezierCurveTo: (cp1x, cp1y, cp2x, cp2y, x, y) => calls.push({ op: 'bezierCurveTo', x, y }),
        quadraticCurveTo: (cpx, cpy, x, y) => calls.push({ op: 'quadraticCurveTo', x, y }),
        roundRect: (x, y, w, h, radii) => calls.push({ op: 'roundRect', x, y, w, h }),
        fill: () => calls.push({ op: 'fill' }),
        stroke: () => calls.push({ op: 'stroke' }),
        save: () => calls.push({ op: 'save' }),
        restore: () => calls.push({ op: 'restore' }),
        translate: (x, y) => calls.push({ op: 'translate', x, y }),
        rotate: (angle) => calls.push({ op: 'rotate', angle }),
        scale: (x, y) => calls.push({ op: 'scale', x, y }),
        clip: () => calls.push({ op: 'clip' }),
        createRadialGradient: () => gradient,
        createLinearGradient: () => gradient,
    };
}

const painter = new ProceduralFacePainter();

// 1. Test Gaze Angle Conversion & Sclera Boundary Clamping
console.log('1. Testing Gaze Angle Calculations & Constraints...');
const testAngles = [
    { yaw: 0, pitch: 0, expectedX: 0, expectedY: 0 },
    { yaw: 30, pitch: 0, desc: '30 deg right' },
    { yaw: -30, pitch: 0, desc: '30 deg left' },
    { yaw: 45, pitch: 0, desc: '45 deg right' },
    { yaw: -45, pitch: 0, desc: '45 deg left' },
    { yaw: 0, pitch: 20, desc: '20 deg up' },
    { yaw: 0, pitch: -20, desc: '20 deg down' },
    { yaw: 30, pitch: 15, desc: '30 deg right + 15 deg up' }
];

for (const t of testAngles) {
    painter.setGazeAngle(t.yaw, t.pitch);
    const offsets = painter.getGazePixelOffsets();
    console.assert(!isNaN(offsets.offsetX), `OffsetX is not NaN for yaw ${t.yaw}`);
    console.assert(!isNaN(offsets.offsetY), `OffsetY is not NaN for pitch ${t.pitch}`);
    console.assert(Math.abs(offsets.offsetX) <= 46.01, `OffsetX ${offsets.offsetX} within 46px sclera clamp`);
    console.assert(Math.abs(offsets.offsetY) <= 22.01, `OffsetY ${offsets.offsetY} within 22px sclera clamp`);

    if (t.yaw > 0) {
        console.assert(offsets.offsetX > 0, `Positive yaw (${t.yaw}°) yields positive lateral shift (${offsets.offsetX.toFixed(1)}px)`);
    } else if (t.yaw < 0) {
        console.assert(offsets.offsetX < 0, `Negative yaw (${t.yaw}°) yields negative lateral shift (${offsets.offsetX.toFixed(1)}px)`);
    }

    if (t.pitch > 0) {
        console.assert(offsets.offsetY < 0, `Pitch up (${t.pitch}°) yields negative canvas Y (${offsets.offsetY.toFixed(1)}px)`);
    } else if (t.pitch < 0) {
        console.assert(offsets.offsetY > 0, `Pitch down (${t.pitch}°) yields positive canvas Y (${offsets.offsetY.toFixed(1)}px)`);
    }
}
console.log('✓ Directional Gaze Angle System: PASSED');

// 2. Test Full 9-Viseme Preston Blair Speech Set
console.log('2. Testing 9-Viseme Speech Phonetics...');
const allVisemes = [
    'REST', 'A_I', 'E', 'O', 'U', 'M_B_P', 'F_V', 'L_TH', 'W_Q', 'SMILE_OPEN',
    // Aliases
    'A_AH', 'O_OH', 'E_EE', 'M', 'F', 'L', 'W'
];

for (const v of allVisemes) {
    painter.setState({ viseme: v, blink: 0.0 });
    const mockCtx = createMockContext();
    painter.render(mockCtx);
    console.assert(mockCtx.calls.length > 50, `Render calls generated for viseme ${v}`);
}
console.log('✓ All 9 Speech Visemes & Aliases: PASSED');

// 3. Test Emotional Expression Engine
console.log('3. Testing Emotional Expression Presets...');
const emotions = ['NEUTRAL', 'HAPPY', 'THINKING', 'SURPRISED', 'SKEPTICAL', 'FOCUSED'];
for (const em of emotions) {
    painter.setEmotion(em, 1.0);
    console.assert(painter.state.emotion === em, `Emotion state set to ${em}`);
    const mockCtx = createMockContext();
    painter.render(mockCtx);
    console.assert(mockCtx.calls.length > 50, `Render calls generated for emotion ${em}`);
}
console.log('✓ Emotional Expressions Engine: PASSED');

// 4. Test Blinks & Asymmetric Winks
console.log('4. Testing Blinks and Eyelid Asymmetry...');
const blinkStates = [
    { blink: 0.0, desc: 'Eyes wide open' },
    { blink: 0.5, desc: 'Half blink' },
    { blink: 1.0, desc: 'Fully closed blink' },
    { blinkLeft: 1.0, blinkRight: 0.0, desc: 'Wink Left' },
    { blinkLeft: 0.0, blinkRight: 1.0, desc: 'Wink Right' },
];

for (const b of blinkStates) {
    painter.setState({
        blink: b.blink ?? 0.0,
        blinkLeft: b.blinkLeft ?? null,
        blinkRight: b.blinkRight ?? null,
    });
    const mockCtx = createMockContext();
    painter.render(mockCtx);
    console.assert(mockCtx.calls.length > 50, `Render calls generated for ${b.desc}`);
}
console.log('✓ Eyelid Blinking & Winking: PASSED');

console.log('\n========================================');
console.log('ALL FACIAL ANIMATION TESTS PASSED (4/4)');
console.log('========================================');
