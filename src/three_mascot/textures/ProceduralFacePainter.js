/**
 * ProceduralFacePainter.js
 * 
 * Programmatically paints the Senior Developer Lego mascot ("Brick Dev") face
 * onto an HTML5 Canvas (or OffscreenCanvas).
 * 
 * Accurately calibrated to the concept art reference (brick_dev_perfect_cutout.png):
 * - Almond-shaped eyes with heavy upper eyelid folds, clipping the top of the dark espresso iris.
 * - Upper-right specular catchlights (1:30 position) with soft halo.
 * - Lower eyelid bags / creases and realistic brow bone highlights.
 * - Expressive arched tapered eyebrows close to eyes.
 * - Stylized 3D bulbous nose tip, nostrils, and bridge.
 * - Full sculpted lips with Cupid's bow and warm fleshy terracotta tones.
 * - Split mustache at philtrum with micro-hair texture.
 * - Triangular soul patch and curved chin goatee with micro-curls.
 * - Parametric mouth viseme lip-sync engine (REST, A_I, E, O, U, M_B_P, F_V, L_TH, W_Q, SMILE_OPEN).
 * - Procedural eyelid blinking (0.0 to 1.0) and directional gaze tracking.
 */

export const EMOTIONS = {
    NEUTRAL: {
        browLeft:  { yOffset: 0, slant: 0, arch: 1.0 },
        browRight: { yOffset: 0, slant: 0, arch: 1.0 },
        eyeLeft:   { scaleY: 1.0, squint: 0.0 },
        eyeRight:  { scaleY: 1.0, squint: 0.0 },
        mouthSmile: 0.85,
    },
    HAPPY: {
        browLeft:  { yOffset: -14, slant: -0.05, arch: 1.18 },
        browRight: { yOffset: -14, slant: 0.05, arch: 1.18 },
        eyeLeft:   { scaleY: 0.90, squint: 0.35 },
        eyeRight:  { scaleY: 0.90, squint: 0.35 },
        mouthSmile: 1.20,
    },
    THINKING: {
        // Senior dev pondering code: left brow furrowed down, right brow arched high
        browLeft:  { yOffset: 10, slant: 0.12, arch: 0.90 },
        browRight: { yOffset: -22, slant: 0.08, arch: 1.30 },
        eyeLeft:   { scaleY: 0.82, squint: 0.30 },
        eyeRight:  { scaleY: 1.05, squint: 0.05 },
        mouthSmile: 0.50,
        defaultGaze: { yawDeg: -22, pitchDeg: 16 },
    },
    SURPRISED: {
        browLeft:  { yOffset: -28, slant: 0.0, arch: 1.35 },
        browRight: { yOffset: -28, slant: 0.0, arch: 1.35 },
        eyeLeft:   { scaleY: 1.26, squint: 0.0 },
        eyeRight:  { scaleY: 1.26, squint: 0.0 },
        mouthSmile: 0.70,
    },
    SKEPTICAL: {
        browLeft:  { yOffset: 14, slant: -0.08, arch: 0.85 },
        browRight: { yOffset: -18, slant: 0.10, arch: 1.25 },
        eyeLeft:   { scaleY: 0.78, squint: 0.40 },
        eyeRight:  { scaleY: 1.02, squint: 0.0 },
        mouthSmile: 0.40,
    },
    FOCUSED: {
        browLeft:  { yOffset: 12, slant: -0.10, arch: 0.95 },
        browRight: { yOffset: 12, slant: 0.10, arch: 0.95 },
        eyeLeft:   { scaleY: 0.88, squint: 0.20 },
        eyeRight:  { scaleY: 0.88, squint: 0.20 },
        mouthSmile: 0.75,
    }
};

export class ProceduralFacePainter {
    constructor(options = {}) {
        this.width = options.width || 2048;
        this.height = options.height || 1024;
        
        // Calibrated palette from reference concept art
        this.colors = {
            skinBase: '#94532B',        // Rich warm brown ABS plastic
            skinHighlight: '#AD673A',   // Cheeks and forehead highlight
            skinShadow: '#733718',      // Chin, socket, and neck shadow
            eyeWhite: '#F3F4F8',        // Clean sclera
            irisOuter: '#1F1109',       // Deep dark espresso iris rim
            irisInner: '#381C0E',       // Warm espresso iris fill
            irisHighlight: '#5A2E16',   // Subtle amber iris bounce
            pupil: '#0A0503',           // Solid black pupil
            specular: '#FFFFFF',        // Specular catchlight
            upperLidLine: '#1E110A',    // Heavy upper lash line
            lidCrease: '#502613',       // Upper and lower lid skin folds
            eyebrow: '#180E08',         // Deep brown-black eyebrow
            noseShadow: '#522410',      // Soft nostril creases
            noseHighlight: '#D2854E',   // Nose tip plastic sheen
            mustache: '#180E09',        // Trimmed mustache hair
            mustacheStipple: '#2A170F', // Stubble texture
            upperLip: '#8D4A32',        // Warm terracotta upper lip
            lowerLip: '#B3644E',        // Fuller fleshy lower lip
            lipHighlight: '#C8785E',    // Gloss sheen on lower lip
            lipLine: '#38170B',         // Mouth closure seam
            mouthInterior: '#250808',   // Oral cavity for open visemes
            teeth: '#F5F7FA',           // Teeth row
            tongue: '#B44949',          // Tongue inside mouth
            soulPatch: '#180E08',       // Under-lip soul patch
            goatee: '#120A05',          // Chin goatee
            goateeCurl: '#24140A',      // Micro-curl texture
        };

        // Animation state
        this.state = {
            viseme: 'REST',       // REST, A_I, E, O, U, M_B_P, F_V, L_TH, W_Q, SMILE_OPEN
            blendViseme: null,
            blendWeight: 0.0,
            blink: 0.0,           // 0.0 (open) to 1.0 (closed)
            blinkLeft: null,      // Optional left eyelid override (e.g. winking)
            blinkRight: null,     // Optional right eyelid override
            gazeYawDeg: 0.0,      // -45 to +45 deg (positive = looking to his right)
            gazePitchDeg: 0.0,    // -30 to +30 deg (positive = looking up)
            eyeLookX: 0.0,        // Normalized -1.0 to 1.0
            eyeLookY: 0.0,        // Normalized -1.0 to 1.0
            emotion: 'NEUTRAL',   // NEUTRAL, HAPPY, THINKING, SURPRISED, SKEPTICAL, FOCUSED
            emotionIntensity: 1.0,
            smileAmount: 0.85,
        };

        // Feature landmarks (in 2048 x 1024 space, center front = 1024)
        this.landmarks = {
            centerX: 1024,
            eyeSpacing: 160,       // Lateral offset to eye centers
            eyeY: 480,             // Eye vertical center
            eyeRadiusX: 86,        // Fuller almond eye half-width
            eyeRadiusY: 52,        // Fuller almond eye half-height (calibrated 1.65:1 ratio)
            browY: 395,            // Eyebrow level intimately framing the eyes
            noseY: 575,            // Nose tip level
            mustacheY: 645,        // Mustache level
            mouthY: 695,           // Mouth line level
            soulPatchY: 748,       // Soul patch level
            goateeY: 825,          // Chin goatee level
        };

        this.canvas = null;
        this.ctx = null;
    }

    initCanvas(existingCanvas = null) {
        if (existingCanvas) {
            this.canvas = existingCanvas;
        } else if (typeof document !== 'undefined') {
            this.canvas = document.createElement('canvas');
            this.canvas.width = this.width;
            this.canvas.height = this.height;
        } else if (typeof OffscreenCanvas !== 'undefined') {
            this.canvas = new OffscreenCanvas(this.width, this.height);
        }
        if (this.canvas) {
            this.ctx = this.canvas.getContext('2d');
        }
        return this.canvas;
    }

    setState(newState) {
        Object.assign(this.state, newState);
    }

    setGazeAngle(yawDeg, pitchDeg = 0) {
        this.state.gazeYawDeg = yawDeg;
        this.state.gazePitchDeg = pitchDeg;
        this.state.eyeLookX = 0;
        this.state.eyeLookY = 0;
    }

    setEmotion(emotionName, intensity = 1.0) {
        if (EMOTIONS[emotionName]) {
            this.state.emotion = emotionName;
            this.state.emotionIntensity = intensity;
        }
    }

    getGazePixelOffsets() {
        let yaw = this.state.gazeYawDeg;
        let pitch = this.state.gazePitchDeg;

        // If emotion defines a default gaze (e.g. THINKING looking up-left) and no explicit angle is set
        if (yaw === 0 && pitch === 0 && this.state.eyeLookX === 0 && this.state.eyeLookY === 0) {
            const em = EMOTIONS[this.state.emotion];
            if (em && em.defaultGaze) {
                yaw = em.defaultGaze.yawDeg * this.state.emotionIntensity;
                pitch = em.defaultGaze.pitchDeg * this.state.emotionIntensity;
            }
        }

        let offsetX, offsetY;
        if (this.state.eyeLookX !== 0 || this.state.eyeLookY !== 0) {
            offsetX = this.state.eyeLookX * 42;
            offsetY = this.state.eyeLookY * 22;
        } else {
            const yawRad = (yaw * Math.PI) / 180;
            const pitchRad = (pitch * Math.PI) / 180;
            // 45 deg maps to ~44px lateral offset on 2048x1024 canvas
            offsetX = 56 * Math.sin(yawRad);
            // Positive pitch (looking up) moves iris up in 3D (-Y in 2D canvas coordinates)
            offsetY = -34 * Math.sin(pitchRad);
        }

        // Clamp to sclera safe interior bounds
        const maxDistX = 46;
        const maxDistY = 22;
        offsetX = Math.max(-maxDistX, Math.min(maxDistX, offsetX));
        offsetY = Math.max(-maxDistY, Math.min(maxDistY, offsetY));

        return { offsetX, offsetY };
    }

    render(targetCtx = null) {
        const ctx = targetCtx || this.ctx;
        if (!ctx) return;

        const w = this.width;
        const h = this.height;

        // 1. Base ABS Plastic skin tone
        ctx.fillStyle = this.colors.skinBase;
        ctx.fillRect(0, 0, w, h);

        // 2. Soft ambient 3D facial shading & cheek warmth
        this.drawSubtleSkinShading(ctx);

        // 3. Eyebrows
        this.drawEyebrows(ctx);

        // 4. Eyes (almond contour, clipped iris, dual catchlights, eyelid folds)
        this.drawEyes(ctx);

        // 5. Stylized 3D Nose
        this.drawNose(ctx);

        // 6. Dynamic Mouth (visemes / speech)
        this.drawMouth(ctx);

        // 7. Mustache (split philtrum, stippled stubble)
        this.drawMustache(ctx);

        // 8. Soul patch & Chin Goatee
        this.drawBeard(ctx);
    }

    drawSubtleSkinShading(ctx) {
        const cx = this.landmarks.centerX;
        const ey = this.landmarks.eyeY;

        // Soft cheek warmth
        const cheekGradL = ctx.createRadialGradient(cx - 180, ey + 90, 15, cx - 180, ey + 90, 130);
        cheekGradL.addColorStop(0, 'rgba(188, 96, 48, 0.40)');
        cheekGradL.addColorStop(1, 'rgba(148, 83, 43, 0)');
        ctx.fillStyle = cheekGradL;
        ctx.beginPath();
        ctx.arc(cx - 180, ey + 90, 130, 0, Math.PI * 2);
        ctx.fill();

        const cheekGradR = ctx.createRadialGradient(cx + 180, ey + 90, 15, cx + 180, ey + 90, 130);
        cheekGradR.addColorStop(0, 'rgba(188, 96, 48, 0.40)');
        cheekGradR.addColorStop(1, 'rgba(148, 83, 43, 0)');
        ctx.fillStyle = cheekGradR;
        ctx.beginPath();
        ctx.arc(cx + 180, ey + 90, 130, 0, Math.PI * 2);
        ctx.fill();

        // Forehead center highlight
        const foreheadGrad = ctx.createRadialGradient(cx, 320, 10, cx, 320, 200);
        foreheadGrad.addColorStop(0, 'rgba(195, 120, 72, 0.32)');
        foreheadGrad.addColorStop(1, 'rgba(148, 83, 43, 0)');
        ctx.fillStyle = foreheadGrad;
        ctx.beginPath();
        ctx.arc(cx, 320, 200, 0, Math.PI * 2);
        ctx.fill();
    }

    drawEyes(ctx) {
        const cx = this.landmarks.centerX;
        const ey = this.landmarks.eyeY;
        const spacing = this.landmarks.eyeSpacing;
        const rx = this.landmarks.eyeRadiusX;
        const ry = this.landmarks.eyeRadiusY;

        const baseBlink = Math.max(0, Math.min(1, this.state.blink));
        const blinkL = this.state.blinkLeft !== null ? Math.max(0, Math.min(1, this.state.blinkLeft)) : baseBlink;
        const blinkR = this.state.blinkRight !== null ? Math.max(0, Math.min(1, this.state.blinkRight)) : baseBlink;

        const em = EMOTIONS[this.state.emotion] || EMOTIONS.NEUTRAL;
        const intensity = this.state.emotionIntensity ?? 1.0;

        const eyeLeftParams = {
            scaleY: 1.0 + ((em.eyeLeft?.scaleY ?? 1.0) - 1.0) * intensity,
            squint: (em.eyeLeft?.squint ?? 0.0) * intensity,
        };

        const eyeRightParams = {
            scaleY: 1.0 + ((em.eyeRight?.scaleY ?? 1.0) - 1.0) * intensity,
            squint: (em.eyeRight?.squint ?? 0.0) * intensity,
        };

        const gaze = this.getGazePixelOffsets();

        this.drawSingleEye(ctx, cx - spacing, ey, rx, ry, blinkL, false, eyeLeftParams, gaze);
        this.drawSingleEye(ctx, cx + spacing, ey, rx, ry, blinkR, true, eyeRightParams, gaze);
    }

    drawSingleEye(ctx, x, y, rx, ry, blink, isRight, eyeParams = {}, gaze = { offsetX: 0, offsetY: 0 }) {
        ctx.save();
        ctx.translate(x, y);

        const apertureScale = eyeParams.scaleY || 1.0;
        const squint = eyeParams.squint || 0.0;
        const scaleY = Math.max(0.04, (1.0 - blink * 0.96) * apertureScale);
        const squintOffset = squint * 14 * scaleY;

        if (blink > 0.82) {
            // Closed eye: gentle curved lash line
            ctx.strokeStyle = this.colors.upperLidLine;
            ctx.lineWidth = 9;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(-rx, 0);
            ctx.quadraticCurveTo(0, ry * 0.4, rx, -2);
            ctx.stroke();

            // Upper lid crease above closed eye
            ctx.strokeStyle = 'rgba(80, 38, 19, 0.5)';
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(-rx * 0.85, -12);
            ctx.quadraticCurveTo(0, -18, rx * 0.85, -14);
            ctx.stroke();

            ctx.restore();
            return;
        }

        // --- 1. Sclera Aperture (Almond Shape) ---
        // Distinct Lego almond contour: curved top, gentle bottom
        ctx.save();
        ctx.beginPath();
        // Start at inner corner
        ctx.moveTo(-rx, 2);
        // Top eyelid curve (arches up and slightly outward)
        ctx.bezierCurveTo(-rx * 0.5, -ry * 1.35 * scaleY, rx * 0.5, -ry * 1.30 * scaleY, rx, -2);
        // Bottom eyelid curve (raised if squinting with smiling emotion)
        ctx.bezierCurveTo(rx * 0.5, (ry * 0.95 - squintOffset) * scaleY, -rx * 0.5, (ry * 0.90 - squintOffset) * scaleY, -rx, 2);
        ctx.closePath();
        ctx.clip();

        // Fill white sclera
        ctx.fillStyle = this.colors.eyeWhite;
        ctx.fillRect(-rx - 25, -ry * scaleY - 25, (rx + 25) * 2, (ry * scaleY + 25) * 2);

        // Soft upper eyelid cast shadow on the eyeball
        const eyeShadow = ctx.createLinearGradient(0, -ry * scaleY, 0, ry * scaleY * 0.5);
        eyeShadow.addColorStop(0, 'rgba(80, 60, 50, 0.35)');
        eyeShadow.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.fillStyle = eyeShadow;
        ctx.fillRect(-rx, -ry * scaleY, rx * 2, ry * scaleY * 1.5);

        // --- 2. Iris & Pupil with Gaze Tracking ---
        const irisX = gaze.offsetX;
        const irisY = gaze.offsetY + ry * 0.12 * scaleY;
        const irisR = ry * 1.35; // Fuller iris matching reference

        // Dark espresso outer iris
        ctx.fillStyle = this.colors.irisOuter;
        ctx.beginPath();
        ctx.arc(irisX, irisY, irisR, 0, Math.PI * 2);
        ctx.fill();

        // Warm espresso gradient
        const irisGrad = ctx.createRadialGradient(irisX, irisY, irisR * 0.25, irisX, irisY, irisR);
        irisGrad.addColorStop(0, this.colors.irisHighlight);
        irisGrad.addColorStop(0.65, this.colors.irisInner);
        irisGrad.addColorStop(1, this.colors.irisOuter);
        ctx.fillStyle = irisGrad;
        ctx.beginPath();
        ctx.arc(irisX, irisY, irisR * 0.94, 0, Math.PI * 2);
        ctx.fill();

        // Black Pupil
        const pupilR = irisR * 0.54;
        ctx.fillStyle = this.colors.pupil;
        ctx.beginPath();
        ctx.arc(irisX, irisY, pupilR, 0, Math.PI * 2);
        ctx.fill();

        // Specular Catchlight (at 1:30 position, upper-right of pupil)
        // Cornea dome reflection: stays anchored to upper-right key light with subtle optical parallax
        const specAngle = -Math.PI * 0.28; // ~50 degrees up-right
        const specDist = pupilR * 0.55;
        const specX = irisX * 0.15 + Math.cos(specAngle) * specDist;
        const specY = irisY * 0.15 + Math.sin(specAngle) * specDist;
        const specR = pupilR * 0.40;

        // Diffuse halo
        const haloGrad = ctx.createRadialGradient(specX, specY, specR * 0.4, specX, specY, specR * 2.2);
        haloGrad.addColorStop(0, 'rgba(255, 255, 255, 0.65)');
        haloGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.fillStyle = haloGrad;
        ctx.beginPath();
        ctx.arc(specX, specY, specR * 2.2, 0, Math.PI * 2);
        ctx.fill();

        // Sharp white catchlight (primary 1:30)
        ctx.fillStyle = this.colors.specular;
        ctx.beginPath();
        ctx.arc(specX, specY, specR, 0, Math.PI * 2);
        ctx.fill();

        // Secondary subtle specular catchlight (7:30 position)
        const specAngle2 = Math.PI * 0.72;
        const specDist2 = pupilR * 0.62;
        const specX2 = irisX * 0.15 + Math.cos(specAngle2) * specDist2;
        const specY2 = irisY * 0.15 + Math.sin(specAngle2) * specDist2;
        const specR2 = pupilR * 0.22;
        ctx.fillStyle = 'rgba(255, 255, 255, 0.75)';
        ctx.beginPath();
        ctx.arc(specX2, specY2, specR2, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore(); // Restore clip

        // --- 3. Eyelid Contours & Creases (Unclipped) ---
        // Heavy upper lash line
        ctx.strokeStyle = this.colors.upperLidLine;
        ctx.lineWidth = 9.0;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-rx, 2);
        ctx.bezierCurveTo(-rx * 0.5, -ry * 1.38 * scaleY, rx * 0.5, -ry * 1.33 * scaleY, rx, -2);
        ctx.stroke();

        // Delicate lower lash line
        ctx.strokeStyle = 'rgba(30, 17, 10, 0.45)';
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(rx, -2);
        ctx.bezierCurveTo(rx * 0.5, (ry * 0.95 - squintOffset) * scaleY, -rx * 0.5, (ry * 0.90 - squintOffset) * scaleY, -rx, 2);
        ctx.stroke();

        // Upper eyelid crease (double eyelid fold)
        ctx.strokeStyle = 'rgba(75, 35, 18, 0.60)';
        ctx.lineWidth = 5;
        ctx.beginPath();
        ctx.moveTo(-rx * 0.85, -ry * scaleY - 14);
        ctx.quadraticCurveTo(0, -ry * scaleY - 26, rx * 0.85, -ry * scaleY - 18);
        ctx.stroke();

        // Lower eyelid soft crease (eye bag / fold)
        ctx.strokeStyle = 'rgba(95, 45, 22, 0.38)';
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(-rx * 0.75, (ry + 12 - squintOffset) * scaleY);
        ctx.quadraticCurveTo(0, (ry + 20 - squintOffset) * scaleY, rx * 0.75, (ry + 14 - squintOffset) * scaleY);
        ctx.stroke();

        ctx.restore();
    }

    drawEyebrows(ctx) {
        const cx = this.landmarks.centerX;
        const by = this.landmarks.browY;
        const spacing = this.landmarks.eyeSpacing;

        const em = EMOTIONS[this.state.emotion] || EMOTIONS.NEUTRAL;
        const intensity = this.state.emotionIntensity ?? 1.0;

        const leftParams = {
            yOffset: (em.browLeft?.yOffset ?? 0) * intensity,
            slant: (em.browLeft?.slant ?? 0) * intensity,
            arch: 1.0 + ((em.browLeft?.arch ?? 1.0) - 1.0) * intensity,
        };

        const rightParams = {
            yOffset: (em.browRight?.yOffset ?? 0) * intensity,
            slant: (em.browRight?.slant ?? 0) * intensity,
            arch: 1.0 + ((em.browRight?.arch ?? 1.0) - 1.0) * intensity,
        };

        this.drawSingleEyebrow(ctx, cx - spacing, by, false, leftParams);
        this.drawSingleEyebrow(ctx, cx + spacing, by, true, rightParams);
    }

    drawSingleEyebrow(ctx, x, y, isRight, params = {}) {
        ctx.save();
        const yOffset = params.yOffset || 0;
        const slant = params.slant || 0;
        const arch = params.arch !== undefined ? params.arch : 1.0;

        ctx.translate(x, y + yOffset);
        if (slant !== 0) {
            ctx.rotate(slant);
        }
        const sign = isRight ? 1 : -1;

        ctx.fillStyle = this.colors.eyebrow;
        ctx.beginPath();
        // Sleek, solid, beautifully arched Lego eyebrow
        // Medial start: rounded, thick
        ctx.moveTo(-sign * 78, 16);
        // Arch rising up to apex
        ctx.quadraticCurveTo(-sign * 25, -28 * arch, sign * 28, -26 * arch);
        // Tapering down towards temple
        ctx.quadraticCurveTo(sign * 82, -8, sign * 96, 6);
        // Bottom contour returning
        ctx.quadraticCurveTo(sign * 75, 2, sign * 22, -10);
        ctx.quadraticCurveTo(-sign * 28, -10, -sign * 78, 16);
        ctx.closePath();
        ctx.fill();

        ctx.restore();
    }

    drawNose(ctx) {
        const cx = this.landmarks.centerX;
        const ny = this.landmarks.noseY;

        ctx.save();

        // 1. Nose Bridge highlight
        const bridgeGrad = ctx.createLinearGradient(cx, ny - 60, cx, ny);
        bridgeGrad.addColorStop(0, 'rgba(195, 120, 75, 0.0)');
        bridgeGrad.addColorStop(1, 'rgba(215, 140, 90, 0.35)');
        ctx.fillStyle = bridgeGrad;
        ctx.beginPath();
        ctx.moveTo(cx - 16, ny - 60);
        ctx.lineTo(cx + 16, ny - 60);
        ctx.lineTo(cx + 24, ny);
        ctx.lineTo(cx - 24, ny);
        ctx.closePath();
        ctx.fill();

        // 2. Central Bulbous Tip (smooth Lego rounded nose)
        const tipGrad = ctx.createRadialGradient(cx, ny - 4, 4, cx, ny, 32);
        tipGrad.addColorStop(0, 'rgba(225, 148, 98, 0.55)');
        tipGrad.addColorStop(0.65, 'rgba(180, 100, 55, 0.25)');
        tipGrad.addColorStop(1, 'rgba(148, 83, 43, 0)');
        ctx.fillStyle = tipGrad;
        ctx.beginPath();
        ctx.arc(cx, ny, 32, 0, Math.PI * 2);
        ctx.fill();

        // 3. Left and Right Nostril Bulbs
        ctx.fillStyle = 'rgba(175, 95, 50, 0.35)';
        ctx.beginPath();
        ctx.arc(cx - 32, ny + 4, 16, 0, Math.PI * 2);
        ctx.arc(cx + 32, ny + 4, 16, 0, Math.PI * 2);
        ctx.fill();

        // 4. Nostril Under-Creases / Holes (dark curved slits)
        ctx.fillStyle = this.colors.noseShadow;
        ctx.beginPath();
        ctx.ellipse(cx - 22, ny + 14, 11, 5, -0.25, 0, Math.PI * 2);
        ctx.ellipse(cx + 22, ny + 14, 11, 5, 0.25, 0, Math.PI * 2);
        ctx.fill();

        // 5. Specular highlight on nose tip
        ctx.fillStyle = 'rgba(255, 230, 205, 0.40)';
        ctx.beginPath();
        ctx.arc(cx, ny - 6, 8, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }

    drawMustache(ctx) {
        const cx = this.landmarks.centerX;
        const my = this.landmarks.mustacheY;

        ctx.save();
        ctx.translate(cx, my);

        // Split mustache with distinct philtrum gap in the center
        this.drawMustacheHalf(ctx, false);
        this.drawMustacheHalf(ctx, true);

        ctx.restore();
    }

    drawMustacheHalf(ctx, isRight) {
        ctx.save();
        const sign = isRight ? 1 : -1;

        // Gap from center: 9px
        const gap = 9;
        ctx.fillStyle = this.colors.mustache;

        ctx.beginPath();
        // Start at philtrum inner top
        ctx.moveTo(sign * gap, 0);
        // Arch up across upper lip
        ctx.bezierCurveTo(sign * 28, -16, sign * 68, -12, sign * 105, 12);
        // Curve down over corner of mouth
        ctx.bezierCurveTo(sign * 116, 22, sign * 95, 26, sign * 75, 18);
        // Bottom contour returning
        ctx.bezierCurveTo(sign * 48, 10, sign * 25, 6, sign * gap, 10);
        ctx.closePath();
        ctx.fill();

        // Micro-stubble texture
        ctx.fillStyle = this.colors.mustacheStipple;
        const dots = [
            [20, 2], [35, -4], [55, -2], [75, 6], [90, 14],
            [25, 6], [45, 4], [65, 8], [80, 14], [35, 8]
        ];
        for (const [dx, dy] of dots) {
            ctx.beginPath();
            ctx.arc(sign * dx, dy, 2.5, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }

    drawMouth(ctx) {
        const cx = this.landmarks.centerX;
        const my = this.landmarks.mouthY;
        const viseme = (this.state.viseme || 'REST').toUpperCase();

        ctx.save();
        ctx.translate(cx, my);

        switch (viseme) {
            case 'REST':
            case 'IDLE':
                this.drawMouthRest(ctx);
                break;
            case 'A':
            case 'A_AH':
            case 'A_I':
            case 'AH':
                this.drawMouthA(ctx);
                break;
            case 'E':
            case 'E_EE':
            case 'EE':
                this.drawMouthE(ctx);
                break;
            case 'O':
            case 'O_OH':
            case 'OH':
                this.drawMouthO(ctx);
                break;
            case 'U':
            case 'OO':
                this.drawMouthU(ctx);
                break;
            case 'M':
            case 'B':
            case 'P':
            case 'M_B_P':
                this.drawMouthM(ctx);
                break;
            case 'F':
            case 'V':
            case 'F_V':
                this.drawMouthFV(ctx);
                break;
            case 'L':
            case 'TH':
            case 'L_TH':
                this.drawMouthLTH(ctx);
                break;
            case 'W':
            case 'Q':
            case 'W_Q':
                this.drawMouthWQ(ctx);
                break;
            case 'SMILE_OPEN':
            case 'LAUGH':
                this.drawMouthSmileOpen(ctx);
                break;
            default:
                this.drawMouthRest(ctx);
        }

        ctx.restore();
    }

    drawMouthRest(ctx) {
        const mw = 106; // Mouth half-width (confident, warm smile)

        // 1. Upper Lip (Warm terracotta with subtle Cupid's bow)
        ctx.fillStyle = this.colors.upperLip;
        ctx.beginPath();
        // Cupid's bow top
        ctx.moveTo(-mw, -2);
        ctx.quadraticCurveTo(-mw * 0.45, -16, -16, -12);
        ctx.lineTo(0, -7); // Center notch
        ctx.lineTo(16, -12);
        ctx.quadraticCurveTo(mw * 0.45, -16, mw, -2);
        // Mouth line bottom
        ctx.quadraticCurveTo(mw * 0.45, 5, 0, 6);
        ctx.quadraticCurveTo(-mw * 0.45, 5, -mw, -2);
        ctx.closePath();
        ctx.fill();

        // 2. Lower Lip (Fuller fleshy warm rose with rounded contour)
        ctx.fillStyle = this.colors.lowerLip;
        ctx.beginPath();
        ctx.moveTo(-mw * 0.88, 0);
        ctx.quadraticCurveTo(-mw * 0.45, 28, 0, 30);
        ctx.quadraticCurveTo(mw * 0.45, 28, mw * 0.88, 0);
        ctx.quadraticCurveTo(mw * 0.45, 5, 0, 6);
        ctx.quadraticCurveTo(-mw * 0.45, 5, -mw * 0.88, 0);
        ctx.closePath();
        ctx.fill();

        // Gloss highlight on lower lip
        const lipGloss = ctx.createLinearGradient(0, 10, 0, 26);
        lipGloss.addColorStop(0, 'rgba(238, 160, 130, 0.75)');
        lipGloss.addColorStop(1, 'rgba(185, 100, 78, 0.0)');
        ctx.fillStyle = lipGloss;
        ctx.beginPath();
        ctx.ellipse(0, 15, mw * 0.48, 7, 0, 0, Math.PI * 2);
        ctx.fill();

        // 3. Mouth Seam (Dark confident closed smile line)
        ctx.strokeStyle = this.colors.lipLine;
        ctx.lineWidth = 5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-mw, -3);
        ctx.quadraticCurveTo(-mw * 0.45, 6, 0, 6);
        ctx.quadraticCurveTo(mw * 0.45, 6, mw, -3);
        ctx.stroke();

        // Subtle smile corner dimple indents
        ctx.fillStyle = 'rgba(56, 23, 11, 0.65)';
        ctx.beginPath();
        ctx.arc(-mw, -3, 3.5, 0, Math.PI * 2);
        ctx.arc(mw, -3, 3.5, 0, Math.PI * 2);
        ctx.fill();
    }

    /**
     * A_AH: Open mouth talking viseme. Jaw drops downwards from stable upper lip.
     */
    drawMouthA(ctx) {
        const mw = 84;
        const drop = 36;

        ctx.save();
        // Oral cavity opening
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.moveTo(-mw, 0);
        ctx.quadraticCurveTo(0, -4, mw, 0);
        ctx.quadraticCurveTo(mw * 0.7, drop, 0, drop);
        ctx.quadraticCurveTo(-mw * 0.7, drop, -mw, 0);
        ctx.closePath();
        ctx.fill();
        ctx.clip();

        // Upper teeth hanging from top lip
        ctx.fillStyle = this.colors.teeth;
        ctx.beginPath();
        ctx.rect(-mw * 0.7, -4, mw * 1.4, 14);
        ctx.fill();

        // Tongue resting in lower jaw
        ctx.fillStyle = this.colors.tongue;
        ctx.beginPath();
        ctx.ellipse(0, drop + 2, mw * 0.58, 16, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // Upper and lower lip contours
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-mw, 0);
        ctx.quadraticCurveTo(0, -4, mw, 0);
        ctx.stroke();

        ctx.strokeStyle = this.colors.lowerLip;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.moveTo(-mw, 0);
        ctx.quadraticCurveTo(-mw * 0.7, drop, 0, drop);
        ctx.quadraticCurveTo(mw * 0.7, drop, mw, 0);
        ctx.stroke();
    }

    /**
     * O_OH: Rounded mouth talking viseme opening downwards.
     */
    drawMouthO(ctx) {
        const rx = 36;
        const ry = 22;
        const cy = 18;

        ctx.save();
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.ellipse(0, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.clip();

        // Tongue
        ctx.fillStyle = this.colors.tongue;
        ctx.beginPath();
        ctx.ellipse(0, cy + ry * 0.6, rx * 0.7, ry * 0.45, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // Rounded lip contour
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.ellipse(0, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.stroke();
    }

    /**
     * E_EE: Wide talking smile with upper and lower teeth.
     */
    drawMouthE(ctx) {
        const mw = 96;
        const drop = 24;

        ctx.save();
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.moveTo(-mw, -2);
        ctx.quadraticCurveTo(0, 0, mw, -2);
        ctx.quadraticCurveTo(mw * 0.8, drop, 0, drop);
        ctx.quadraticCurveTo(-mw * 0.8, drop, -mw, -2);
        ctx.closePath();
        ctx.fill();
        ctx.clip();

        // Upper teeth
        ctx.fillStyle = this.colors.teeth;
        ctx.fillRect(-mw * 0.8, -4, mw * 1.6, 11);

        // Lower teeth
        ctx.fillRect(-mw * 0.65, drop - 9, mw * 1.3, 10);

        ctx.restore();

        // Lip border
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 4.5;
        ctx.beginPath();
        ctx.moveTo(-mw, -2);
        ctx.quadraticCurveTo(0, 0, mw, -2);
        ctx.quadraticCurveTo(mw * 0.8, drop, 0, drop);
        ctx.quadraticCurveTo(-mw * 0.8, drop, -mw, -2);
        ctx.closePath();
        ctx.stroke();
    }

    /**
     * M_B_P: Compressed closed lips for bilabials.
     */
    drawMouthM(ctx) {
        const mw = 76;
        ctx.strokeStyle = this.colors.lipLine;
        ctx.lineWidth = 4.5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-mw, 2);
        ctx.lineTo(mw, 2);
        ctx.stroke();

        ctx.fillStyle = this.colors.upperLip;
        ctx.beginPath();
        ctx.ellipse(0, -2, mw * 0.72, 3.5, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.fillStyle = this.colors.lowerLip;
        ctx.beginPath();
        ctx.ellipse(0, 6, mw * 0.72, 4.5, 0, 0, Math.PI * 2);
        ctx.fill();
    }

    /**
     * SMILE_OPEN: Broad animated talking smile.
     */
    drawMouthSmileOpen(ctx) {
        const mw = 102;
        const drop = 32;

        ctx.save();
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.moveTo(-mw, -4);
        ctx.quadraticCurveTo(0, 2, mw, -4);
        ctx.quadraticCurveTo(mw * 0.75, drop, 0, drop + 4);
        ctx.quadraticCurveTo(-mw * 0.75, drop, -mw, -4);
        ctx.closePath();
        ctx.fill();
        ctx.clip();

        // Upper teeth
        ctx.fillStyle = this.colors.teeth;
        ctx.fillRect(-mw * 0.82, -6, mw * 1.64, 14);

        // Tongue
        ctx.fillStyle = this.colors.tongue;
        ctx.beginPath();
        ctx.ellipse(0, drop + 4, mw * 0.6, 16, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // Lip border
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 4.5;
        ctx.beginPath();
        ctx.moveTo(-mw, -4);
        ctx.quadraticCurveTo(0, 2, mw, -4);
        ctx.quadraticCurveTo(mw * 0.75, drop, 0, drop + 4);
        ctx.quadraticCurveTo(-mw * 0.75, drop, -mw, -4);
        ctx.closePath();
        ctx.stroke();
    }

    /**
     * U / OO: Small rounded forward pucker viseme.
     */
    drawMouthU(ctx) {
        const rx = 24;
        const ry = 18;
        const cy = 16;

        ctx.save();
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.ellipse(0, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.clip();

        // Tongue depth
        ctx.fillStyle = this.colors.tongue;
        ctx.beginPath();
        ctx.ellipse(0, cy + ry * 0.5, rx * 0.6, ry * 0.4, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // Puckered lip border with terracotta depth
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 7;
        ctx.beginPath();
        ctx.ellipse(0, cy, rx + 2, ry + 2, 0, 0, Math.PI * 2);
        ctx.stroke();

        // Lip gloss highlight on lower pucker
        ctx.fillStyle = 'rgba(238, 160, 130, 0.8)';
        ctx.beginPath();
        ctx.ellipse(0, cy + ry * 0.7, rx * 0.45, 3.5, 0, 0, Math.PI * 2);
        ctx.fill();
    }

    /**
     * F_V: Labiodental fricative viseme. Upper teeth resting visibly on tucked lower lip.
     */
    drawMouthFV(ctx) {
        const mw = 80;
        const drop = 22;

        ctx.save();
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.moveTo(-mw, 0);
        ctx.quadraticCurveTo(0, -2, mw, 0);
        ctx.quadraticCurveTo(mw * 0.7, drop, 0, drop);
        ctx.quadraticCurveTo(-mw * 0.7, drop, -mw, 0);
        ctx.closePath();
        ctx.fill();
        ctx.clip();

        // Upper teeth row prominent and clean
        ctx.fillStyle = this.colors.teeth;
        ctx.beginPath();
        ctx.rect(-mw * 0.65, -4, mw * 1.3, 14);
        ctx.fill();

        ctx.restore();

        // Upper lip contour
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-mw, 0);
        ctx.quadraticCurveTo(0, -2, mw, 0);
        ctx.stroke();

        // Lower lip tucked upward against bottom of teeth
        ctx.fillStyle = this.colors.lowerLip;
        ctx.beginPath();
        ctx.moveTo(-mw * 0.8, 6);
        ctx.quadraticCurveTo(0, 10, mw * 0.8, 6);
        ctx.quadraticCurveTo(mw * 0.65, drop + 4, 0, drop + 6);
        ctx.quadraticCurveTo(-mw * 0.65, drop + 4, -mw * 0.8, 6);
        ctx.closePath();
        ctx.fill();

        ctx.strokeStyle = this.colors.lipLine;
        ctx.lineWidth = 3.5;
        ctx.beginPath();
        ctx.moveTo(-mw * 0.7, 7);
        ctx.quadraticCurveTo(0, 10, mw * 0.7, 7);
        ctx.stroke();
    }

    /**
     * L_TH: Lingua-dental viseme. Open aperture with tongue tip raised behind teeth.
     */
    drawMouthLTH(ctx) {
        const mw = 84;
        const drop = 28;

        ctx.save();
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.moveTo(-mw, -2);
        ctx.quadraticCurveTo(0, 0, mw, -2);
        ctx.quadraticCurveTo(mw * 0.7, drop, 0, drop);
        ctx.quadraticCurveTo(-mw * 0.7, drop, -mw, -2);
        ctx.closePath();
        ctx.fill();
        ctx.clip();

        // Upper teeth row
        ctx.fillStyle = this.colors.teeth;
        ctx.beginPath();
        ctx.rect(-mw * 0.65, -4, mw * 1.3, 11);
        ctx.fill();

        // Tongue tip pressing up behind teeth
        ctx.fillStyle = this.colors.tongue;
        ctx.beginPath();
        ctx.ellipse(0, 11, mw * 0.38, 10, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // Lip borders
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 4.5;
        ctx.beginPath();
        ctx.moveTo(-mw, -2);
        ctx.quadraticCurveTo(0, 0, mw, -2);
        ctx.stroke();

        ctx.strokeStyle = this.colors.lowerLip;
        ctx.lineWidth = 5.5;
        ctx.beginPath();
        ctx.moveTo(-mw, -2);
        ctx.quadraticCurveTo(-mw * 0.7, drop, 0, drop);
        ctx.quadraticCurveTo(mw * 0.7, drop, mw, -2);
        ctx.stroke();
    }

    /**
     * W_Q: Narrow forward rounded pucker viseme (between O and U).
     */
    drawMouthWQ(ctx) {
        const rx = 28;
        const ry = 20;
        const cy = 16;

        ctx.save();
        ctx.fillStyle = this.colors.mouthInterior;
        ctx.beginPath();
        ctx.ellipse(0, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.clip();

        // Tongue
        ctx.fillStyle = this.colors.tongue;
        ctx.beginPath();
        ctx.ellipse(0, cy + ry * 0.55, rx * 0.65, ry * 0.45, 0, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();

        // Pucker lip contour
        ctx.strokeStyle = this.colors.upperLip;
        ctx.lineWidth = 6;
        ctx.beginPath();
        ctx.ellipse(0, cy, rx, ry, 0, 0, Math.PI * 2);
        ctx.stroke();

        // Highlight
        ctx.fillStyle = 'rgba(238, 160, 130, 0.7)';
        ctx.beginPath();
        ctx.ellipse(0, cy + ry * 0.65, rx * 0.5, 4, 0, 0, Math.PI * 2);
        ctx.fill();
    }

    drawBeard(ctx) {
        const cx = this.landmarks.centerX;
        const spy = this.landmarks.soulPatchY;
        const gy = this.landmarks.goateeY;

        ctx.save();

        // 1. Soul Patch (neat triangular wedge under lower lip)
        ctx.fillStyle = this.colors.soulPatch;
        ctx.beginPath();
        ctx.moveTo(cx - 12, spy - 20);
        ctx.lineTo(cx + 12, spy - 20);
        ctx.lineTo(cx + 5, spy + 12);
        ctx.lineTo(cx - 5, spy + 12);
        ctx.closePath();
        ctx.fill();

        // 2. Goatee (chin patch wrapping authentic chin contour)
        ctx.translate(cx, gy);

        // Solid dark base - authentic wide rounded chin dome
        ctx.fillStyle = this.colors.goatee;
        ctx.beginPath();
        ctx.ellipse(0, 16, 78, 48, 0, 0, Math.PI * 2);
        ctx.fill();

        // Organic curly loops & micro-stippling
        ctx.strokeStyle = this.colors.goateeCurl;
        ctx.lineWidth = 2.4;
        const curlyCoords = [
            [-60, 2], [-40, -4], [-20, -6], [0, -6], [20, -6], [40, -4], [60, 2],
            [-65, 16], [-45, 14], [-25, 10], [0, 10], [25, 10], [45, 14], [65, 16],
            [-55, 30], [-35, 28], [-15, 28], [0, 28], [15, 28], [35, 28], [55, 30],
            [-40, 42], [-20, 44], [0, 46], [20, 44], [40, 42],
            [-15, 54], [0, 56], [15, 54]
        ];
        for (const [x_c, y_c] of curlyCoords) {
            ctx.beginPath();
            ctx.arc(x_c, y_c, 5.5, 0, Math.PI * 1.5);
            ctx.stroke();
        }

        // Faint specular stipples (subtle hair sheen)
        ctx.fillStyle = 'rgba(255, 255, 255, 0.18)';
        for (let i = 0; i < curlyCoords.length; i += 2) {
            const [x_c, y_c] = curlyCoords[i];
            ctx.beginPath();
            ctx.arc(x_c + 1.5, y_c - 1.5, 1.8, 0, Math.PI * 2);
            ctx.fill();
        }

        // Soft rim light along chin contour
        ctx.strokeStyle = 'rgba(180, 100, 50, 0.35)';
        ctx.lineWidth = 3.2;
        ctx.beginPath();
        ctx.arc(0, 10, 78, Math.PI * 0.2, Math.PI * 0.8);
        ctx.stroke();

        ctx.restore();
    }
}
