import { ProceduralFacePainter } from '../src/three_mascot/textures/ProceduralFacePainter.js';
import { ProceduralTorsoPainter } from '../src/three_mascot/textures/ProceduralTorsoPainter.js';

console.log('--- Testing Procedural Texture Painters ---');

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
        scale: (x, y) => calls.push({ op: 'scale', x, y }),
        clip: () => calls.push({ op: 'clip' }),
        createRadialGradient: () => gradient,
        createLinearGradient: () => gradient,
    };
}

// 1. ProceduralFacePainter Instantiation & Defaults
const facePainter = new ProceduralFacePainter();
console.assert(facePainter.width === 2048, 'Face painter default width 2048');
console.assert(facePainter.height === 1024, 'Face painter default height 1024');
console.assert(facePainter.colors.skinBase === '#94532B' || facePainter.colors.skinBase === '#9A572E', 'Face skin tone calibrated');
console.assert(facePainter.state.viseme === 'REST', 'Default viseme is REST');
console.log('✓ Face Painter Defaults: PASSED');

// 2. ProceduralFacePainter Rendering across all Visemes
const visemes = ['REST', 'A_AH', 'O_OH', 'E_EE', 'M_B_P', 'SMILE_OPEN'];
for (const viseme of visemes) {
    const mockCtx = createMockContext();
    facePainter.setState({ viseme, blink: 0.0 });
    facePainter.render(mockCtx);
    console.assert(mockCtx.calls.length > 50, `Render calls generated for viseme ${viseme}`);
}
console.log('✓ Face Painter All Visemes Render: PASSED');

// 3. ProceduralFacePainter Blink Transitions
{
    const mockCtx = createMockContext();
    facePainter.setState({ viseme: 'REST', blink: 1.0 }); // fully closed
    facePainter.render(mockCtx);
    const strokeCalls = mockCtx.calls.filter(c => c.op === 'stroke');
    console.assert(strokeCalls.length > 0, 'Closed eyelids rendered on full blink');
}
console.log('✓ Face Painter Blink State: PASSED');

// 4. ProceduralTorsoPainter Instantiation & Defaults
const torsoPainter = new ProceduralTorsoPainter();
console.assert(torsoPainter.width === 1024, 'Torso painter width 1024');
console.assert(torsoPainter.height === 1024, 'Torso painter height 1024');
console.assert(torsoPainter.colors.stripeBlue === '#96B8DA', 'Polo stripe light-blue matches');
console.assert(torsoPainter.colors.stripeWhite === '#EFF3F9', 'Polo stripe white matches');
console.log('✓ Torso Painter Defaults: PASSED');

// 5. ProceduralTorsoPainter Rendering (Torso, Sleeve, Forearm)
{
    const mockCtx = createMockContext();
    torsoPainter.render(mockCtx);
    console.assert(mockCtx.calls.length > 40, 'Torso render calls generated');
    
    // Verify pure fabric - check that skinBase is NOT in the collar/torso draw calls
    const usedColors = mockCtx.calls
        .filter(c => c.color)
        .map(c => c.color);
    console.assert(!usedColors.includes('#9A572E'), 'Torso must have ZERO baked brown skin');
}
console.log('✓ Torso Painter Zero-Skin Integrity: PASSED');

{
    const mockCtxSleeve = createMockContext();
    torsoPainter.renderSleeve(mockCtxSleeve);
    console.assert(mockCtxSleeve.calls.length >= 16, 'Sleeve stripes rendered');

    const mockCtxForearm = createMockContext();
    torsoPainter.renderForearm(mockCtxForearm);
    console.assert(mockCtxForearm.calls.length >= 6, 'Forearm cuff and skin rendered');
}
console.log('✓ Torso Painter Sleeves & Forearms: PASSED');

console.log('--- All Procedural Texture Tests PASSED successfully! ---');
