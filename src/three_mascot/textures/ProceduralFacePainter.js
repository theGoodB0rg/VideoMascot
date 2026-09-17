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
        
        // Calibrated master palette from blueprint & reference concept art
        this.colors = {
            skinBase: '#9A572E',        // Rich warm caramel-brown ABS plastic
            skinHighlight: '#B56F42',   // Cheeks, forehead, and chin highlight
            skinShadow: '#733718',      // Jawline, chin bevel, and socket shadow
            skinCrease: '#5A2711',      // Deep eyelid crease & nostril shadow
            eyeWhite: '#F0F2F6',        // Clean warm white sclera
            sclera: '#F0F2F6',          // Clean warm white sclera
            irisOuter: '#1A0F09',       // Deep dark espresso iris rim
            irisInner: '#3D1E0F',       // Warm espresso iris fill
            irisHighlight: '#5E311A',   // Lower iris ambient bounce glow
            pupil: '#090503',           // Solid deep black pupil
            specular: '#FFFFFF',        // Primary studio catchlight
            catchlightMajor: '#FFFFFF', // Single brilliant circular studio catchlight (1:00 position)
            catchlightMinor: 'rgba(255, 255, 255, 0.0)', // Ultra-subtle ambient bounce
            upperLidLine: '#1E0F08',    // Upper lash contour line
            lidCrease: '#582712',       // Double-fold upper eyelid crease
            eyebrow: '#190E08',         // Espresso-black feathered brow
            noseShadow: '#522410',      // Fleshy curved nostril cavities
            noseHighlight: 'rgba(255, 235, 215, 0.65)', // Tip specular highlight
            noseBridgeSheen: 'rgba(225, 150, 95, 0.35)', // Bridge vertical gradient
            mustache: '#180E09',        // Trimmed mustache hair
            mustacheStipple: '#2B180F', // Edge hair feathering
            upperLip: '#8D4A32',        // Warm terracotta upper lip
            lowerLip: '#B3644E',        // Fuller fleshy lower lip
            lipHighlight: 'rgba(255, 205, 185, 0.70)',   // Gloss sheen on lower lip
            lipSheen: 'rgba(255, 205, 185, 0.70)',
            lipLine: '#38170B',         // Mouth closure seam
            mouthInterior: '#250808',   // Oral cavity for open visemes
            mouthInside: '#250808',
            teeth: '#F5F7FA',           // Clean white teeth
            tongue: '#B44949',          // Warm red tongue
            soulPatch: '#180E08',       // Under-lip soul patch
            goatee: '#1E100A',          // Chin goatee base
            goateeBase: '#1E100A',
            goateeCurl: '#120804',      // Stippled micro-curl ringlets
            goateePebble: '#2C180E',
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
            eyeSpacing: 168,       // Lateral offset to eye centers in isotropic face space
            eyeY: 520,             // Eye vertical center
            eyeRadiusX: 92,        // Calibrated almond eye half-width in isotropic space (184px total)
            eyeRadiusY: 70,        // Calibrated almond eye half-height (140px total)
            browY: 420,            // Eyebrow level framing the eyes
            noseY: 620,            // Nose tip level
            mustacheY: 710,        // Mustache level (snugly above upper lip)
            mouthY: 748,           // Mouth line level
            soulPatchY: 795,       // Soul patch level
            goateeY: 855,          // Chin goatee level (hugging chin contour)
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
        const cx = this.landmarks.centerX;

        // 1. Base ABS Plastic skin tone
        ctx.fillStyle = this.colors.skinBase;
        ctx.fillRect(0, 0, w, h);

        // Aspect compensation: Minifigure head cylinder has circumference 3.267 and height 1.06.
        // On a 2048 x 1024 canvas, horizontal pixels are stretched in 3D by 1.541x.
        // Applying scale(0.6489, 1.0) around cx renders isotropic 1:1 facial anatomy in 3D!
        ctx.save();
        ctx.translate(cx, 0);
        ctx.scale(0.6489, 1.0);
        ctx.translate(-cx, 0);

        // 2. Soft ambient 3D facial shading & cheek warmth
        this.drawSubtleSkinShading(ctx);

        // 3. Eyebrows
        this.drawEyebrows(ctx);

        // 4. Eyes (almond contour, clipped iris, studio catchlight, eyelid folds)
        this.drawEyes(ctx);

        // 5. Stylized 3D Nose
        this.drawNose(ctx);

        // 6. Dynamic Mouth (visemes / speech)
        this.drawMouth(ctx);

        // 7. Mustache (split philtrum, stippled stubble)
        this.drawMustache(ctx);

        // 8. Soul patch & Chin Goatee
        this.drawBeard(ctx);

        ctx.restore();
    }

    drawSubtleSkinShading(ctx) {
        const cx = this.landmarks.centerX;
        const ey = this.landmarks.eyeY;

        // Soft warm cheek glow centered under eyes
        const cheekGradL = ctx.createRadialGradient(cx - 185, ey + 85, 10, cx - 185, ey + 85, 125);
        cheekGradL.addColorStop(0, 'rgba(198, 110, 60, 0.45)');
        cheekGradL.addColorStop(1, 'rgba(154, 87, 46, 0)');
        ctx.fillStyle = cheekGradL;
        ctx.beginPath();
        ctx.arc(cx - 185, ey + 85, 125, 0, Math.PI * 2);
        ctx.fill();

        const cheekGradR = ctx.createRadialGradient(cx + 185, ey + 85, 10, cx + 185, ey + 85, 125);
        cheekGradR.addColorStop(0, 'rgba(198, 110, 60, 0.45)');
        cheekGradR.addColorStop(1, 'rgba(154, 87, 46, 0)');
        ctx.fillStyle = cheekGradR;
        ctx.beginPath();
        ctx.arc(cx + 185, ey + 85, 125, 0, Math.PI * 2);
        ctx.fill();

        // Forehead center ambient highlight
        const foreheadGrad = ctx.createRadialGradient(cx, 340, 10, cx, 340, 180);
        foreheadGrad.addColorStop(0, 'rgba(215, 138, 88, 0.35)');
        foreheadGrad.addColorStop(1, 'rgba(154, 87, 46, 0)');
        ctx.fillStyle = foreheadGrad;
        ctx.beginPath();
        ctx.arc(cx, 340, 180, 0, Math.PI * 2);
        ctx.fill();

        // Chin subtle highlight (beneath goatee)
        const chinGrad = ctx.createRadialGradient(cx, 890, 8, cx, 890, 95);
        chinGrad.addColorStop(0, 'rgba(205, 125, 75, 0.28)');
        chinGrad.addColorStop(1, 'rgba(154, 87, 46, 0)');
        ctx.fillStyle = chinGrad;
        ctx.beginPath();
        ctx.arc(cx, 890, 95, 0, Math.PI * 2);
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
        const squintOffset = squint * 10 * scaleY;

        if (blink > 0.82) {
            // Closed eye: gentle curved lash line
            ctx.strokeStyle = this.colors.upperLidLine;
            ctx.lineWidth = 6;
            ctx.lineCap = 'round';
            ctx.beginPath();
            ctx.moveTo(-rx * 0.95, 0);
            ctx.quadraticCurveTo(0, ry * 0.35, rx * 0.95, -2);
            ctx.stroke();

            // Upper lid crease above closed eye
            ctx.strokeStyle = 'rgba(80, 38, 19, 0.45)';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(-rx * 0.85, -10);
            ctx.quadraticCurveTo(0, -14, rx * 0.85, -12);
            ctx.stroke();

            ctx.restore();
            return;
        }

        // Medial side (towards nose/center) is -sign * rx; lateral side (towards temple) is +sign * rx
        const sign = isRight ? 1 : -1;
        const innerX = -sign * rx * 0.90;
        const outerX = sign * rx * 0.90;

        // --- 1. Sclera Aperture (Generous open almond eye matching Image 1) ---
        ctx.save();
        ctx.beginPath();
        ctx.moveTo(innerX, 0);
        // Top eyelid dome: smooth majestic arch, peaks slightly medial of center
        ctx.bezierCurveTo(-sign * rx * 0.40, -ry * 1.25 * scaleY, sign * rx * 0.20, -ry * 1.20 * scaleY, outerX, -2);
        // Outer corner rounded sweep
        ctx.bezierCurveTo(outerX + sign * 6, 2 * scaleY, outerX + sign * 2, 8 * scaleY, sign * rx * 0.70, (ry * 0.70 - squintOffset) * scaleY);
        // Bottom eyelid: generous downward curve revealing rounded sclera
        ctx.bezierCurveTo(sign * rx * 0.30, (ry * 1.05 - squintOffset) * scaleY, -sign * rx * 0.30, (ry * 1.00 - squintOffset) * scaleY, -sign * rx * 0.70, (ry * 0.60 - squintOffset) * scaleY);
        // Inner corner rounded nook
        ctx.bezierCurveTo(innerX - sign * 4, 6 * scaleY, innerX - sign * 6, 2 * scaleY, innerX, 0);
        ctx.closePath();
        ctx.clip();

        // Fill warm white sclera
        ctx.fillStyle = this.colors.eyeWhite;
        ctx.fillRect(-rx - 25, -ry * scaleY - 25, (rx + 25) * 2, (ry * scaleY + 25) * 2);

        // Eyeball 3D spherical depth shading
        const eye3D = ctx.createRadialGradient(0, -ry * 0.2, ry * 0.3, 0, 0, rx * 1.1);
        eye3D.addColorStop(0, 'rgba(255, 255, 255, 0.0)');
        eye3D.addColorStop(0.75, 'rgba(255, 255, 255, 0.0)');
        eye3D.addColorStop(1.0, 'rgba(180, 160, 150, 0.25)');
        ctx.fillStyle = eye3D;
        ctx.fillRect(-rx - 25, -ry * scaleY - 25, (rx + 25) * 2, (ry * scaleY + 25) * 2);

        // Soft upper eyelid cast shadow on sclera
        const eyeShadow = ctx.createLinearGradient(0, -ry * scaleY, 0, ry * scaleY * 0.4);
        eyeShadow.addColorStop(0, 'rgba(60, 30, 15, 0.38)');
        eyeShadow.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.fillStyle = eyeShadow;
        ctx.fillRect(-rx, -ry * scaleY, rx * 2, ry * scaleY * 1.4);

        // --- 2. Iris & Pupil with Gaze Tracking ---
        // Sits slightly high so top is clipped by upper eyelid
        const irisX = gaze.offsetX;
        const irisY = gaze.offsetY - ry * 0.10 * scaleY;
        const irisR = ry * 0.82; // Fills ~80% of vertical height

        // Dark espresso outer iris rim
        ctx.fillStyle = this.colors.irisOuter;
        ctx.beginPath();
        ctx.arc(irisX, irisY, irisR, 0, Math.PI * 2);
        ctx.fill();

        // Warm chestnut espresso radial gradient
        const irisGrad = ctx.createRadialGradient(irisX, irisY, irisR * 0.20, irisX, irisY, irisR);
        irisGrad.addColorStop(0, this.colors.irisHighlight);
        irisGrad.addColorStop(0.60, this.colors.irisInner);
        irisGrad.addColorStop(1.0, this.colors.irisOuter);
        ctx.fillStyle = irisGrad;
        ctx.beginPath();
        ctx.arc(irisX, irisY, irisR * 0.95, 0, Math.PI * 2);
        ctx.fill();

        // Ambient bounce glow at 7:30 (lower-left iris reflection from cheek)
        const bounceGrad = ctx.createRadialGradient(irisX - irisR * 0.45, irisY + irisR * 0.45, 2, irisX - irisR * 0.45, irisY + irisR * 0.45, irisR * 0.55);
        bounceGrad.addColorStop(0, 'rgba(215, 140, 90, 0.35)');
        bounceGrad.addColorStop(1, 'rgba(61, 30, 15, 0)');
        ctx.fillStyle = bounceGrad;
        ctx.beginPath();
        ctx.arc(irisX - irisR * 0.45, irisY + irisR * 0.45, irisR * 0.55, 0, Math.PI * 2);
        ctx.fill();

        // Black Pupil
        const pupilR = irisR * 0.50;
        ctx.fillStyle = this.colors.pupil;
        ctx.beginPath();
        ctx.arc(irisX, irisY, pupilR, 0, Math.PI * 2);
        ctx.fill();

        // --- SINGLE DOMINANT STUDIO SOFTBOX CATCHLIGHT AT 1:00 ---
        // (Matching Image 1: brilliant circular softbox reflection with soft halo bloom)
        const specX = irisX + irisR * 0.34;
        const specY = irisY - irisR * 0.36;
        const specR = 10.5;

        // Soft radiant bloom halo
        const haloGrad = ctx.createRadialGradient(specX, specY, specR * 0.25, specX, specY, specR * 2.4);
        haloGrad.addColorStop(0, 'rgba(255, 255, 255, 0.65)');
        haloGrad.addColorStop(0.5, 'rgba(255, 255, 255, 0.20)');
        haloGrad.addColorStop(1, 'rgba(255, 255, 255, 0)');
        ctx.fillStyle = haloGrad;
        ctx.beginPath();
        ctx.arc(specX, specY, specR * 2.4, 0, Math.PI * 2);
        ctx.fill();

        // Crisp brilliant white circular studio catchlight
        ctx.fillStyle = '#FFFFFF';
        ctx.beginPath();
        ctx.arc(specX, specY, specR, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore(); // Restore sclera clip

        // --- 3. Eyelid Contours & Fleshy Upper Crease (Unclipped) ---
        // Heavy upper lash line (smooth rounded arch covering top of iris)
        ctx.strokeStyle = this.colors.upperLidLine;
        ctx.lineWidth = 8.5;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.beginPath();
        ctx.moveTo(innerX, 0);
        ctx.bezierCurveTo(-sign * rx * 0.40, -ry * 1.27 * scaleY, sign * rx * 0.20, -ry * 1.22 * scaleY, outerX, -2);
        ctx.stroke();

        // Delicate lower lash line (tracing bottom eyelid contour cleanly)
        ctx.strokeStyle = 'rgba(40, 20, 12, 0.42)';
        ctx.lineWidth = 3.2;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(outerX, -2);
        ctx.bezierCurveTo(outerX + sign * 6, 2 * scaleY, outerX + sign * 2, 8 * scaleY, sign * rx * 0.70, (ry * 0.70 - squintOffset) * scaleY);
        ctx.bezierCurveTo(sign * rx * 0.30, (ry * 1.05 - squintOffset) * scaleY, -sign * rx * 0.30, (ry * 1.00 - squintOffset) * scaleY, -sign * rx * 0.70, (ry * 0.60 - squintOffset) * scaleY);
        ctx.bezierCurveTo(innerX - sign * 4, 6 * scaleY, innerX - sign * 6, 2 * scaleY, innerX, 0);
        ctx.stroke();

        // --- 4. Prominent Fleshy Upper Eyelid Hood / Crease ---
        const socketGrad = ctx.createLinearGradient(0, -ry * scaleY - 26, 0, -ry * scaleY);
        socketGrad.addColorStop(0, 'rgba(90, 42, 18, 0.0)');
        socketGrad.addColorStop(0.5, 'rgba(90, 42, 18, 0.30)');
        socketGrad.addColorStop(1, 'rgba(90, 42, 18, 0.0)');
        ctx.fillStyle = socketGrad;
        ctx.beginPath();
        ctx.moveTo(innerX, -ry * scaleY - 12);
        ctx.quadraticCurveTo(0, -ry * scaleY - 26, outerX, -ry * scaleY - 16);
        ctx.lineTo(outerX, -ry * scaleY);
        ctx.quadraticCurveTo(0, -ry * scaleY, innerX, -ry * scaleY);
        ctx.closePath();
        ctx.fill();

        // Crisp double-fold eyelid crease line
        ctx.strokeStyle = this.colors.lidCrease || '#582712';
        ctx.lineWidth = 3.6;
        ctx.beginPath();
        ctx.moveTo(innerX + sign * 5, -ry * scaleY - 12);
        ctx.quadraticCurveTo(0, -ry * scaleY - 22, outerX - sign * 5, -ry * scaleY - 15);
        ctx.stroke();

        // Lower eyelid soft contour crease (eye bag fold)
        ctx.strokeStyle = 'rgba(95, 45, 22, 0.28)';
        ctx.lineWidth = 2.2;
        ctx.beginPath();
        ctx.moveTo(-rx * 0.70, (ry + 8 - squintOffset) * scaleY);
        ctx.quadraticCurveTo(0, (ry + 14 - squintOffset) * scaleY, rx * 0.70, (ry + 8 - squintOffset) * scaleY);
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

        // 1. Brow bone ambient highlight (warm ridge glow above the brow)
        const boneGrad = ctx.createRadialGradient(sign * 10, -36 * arch, 5, sign * 10, -36 * arch, 65);
        boneGrad.addColorStop(0, 'rgba(215, 140, 88, 0.35)');
        boneGrad.addColorStop(1, 'rgba(154, 87, 46, 0.0)');
        ctx.fillStyle = boneGrad;
        ctx.beginPath();
        ctx.arc(sign * 10, -36 * arch, 65, 0, Math.PI * 2);
        ctx.fill();

        // 2. Solid, sculpted Lego eyebrow body framing large almond eye
        ctx.fillStyle = this.colors.eyebrow;
        ctx.beginPath();
        // Inner head medial start (rounded, confident)
        ctx.moveTo(-sign * 96, 10);
        // Arching upward along the superior crest
        ctx.bezierCurveTo(-sign * 50, -26 * arch, sign * 18, -32 * arch, sign * 75, -18 * arch);
        // Tapering to outer tail
        ctx.quadraticCurveTo(sign * 110, -7 * arch, sign * 118, 4);
        // Tail rounded tip
        ctx.quadraticCurveTo(sign * 108, 6, sign * 94, 4);
        // Inferior contour returning above eye socket
        ctx.bezierCurveTo(sign * 40, -9 * arch, -sign * 30, -7 * arch, -sign * 92, 16);
        // Medial head rounded finish
        ctx.quadraticCurveTo(-sign * 100, 14, -sign * 96, 10);
        ctx.closePath();
        ctx.fill();

        // 3. Natural micro-hair grain along the flow of the brow
        ctx.strokeStyle = '#0F0704';
        ctx.lineWidth = 1.8;
        ctx.lineCap = 'round';
        const headHairs = [
            [-94, 12, -90, 4],
            [-84, 6, -80, -3],
            [-74, 1, -68, -9],
            [-62, -6, -54, -15],
            [-48, -13, -38, -20],
            [-32, -18, -20, -23],
            [-14, -22, -2, -25],
            [6, -23, 22, -25],
            [32, -21, 48, -20],
            [58, -17, 72, -14],
            [82, -11, 96, -6]
        ];
        for (const [x1, y1, x2, y2] of headHairs) {
            ctx.beginPath();
            ctx.moveTo(sign * x1, y1 * arch);
            ctx.lineTo(sign * x2, y2 * arch);
            ctx.stroke();
        }

        ctx.restore();
    }

    drawNose(ctx) {
        const cx = this.landmarks.centerX;
        const ny = this.landmarks.noseY;

        ctx.save();

        // 1. Dorsal Bridge Lateral Shadows (giving the bridge 3D elevation from the face plane)
        const bridgeShadowL = ctx.createLinearGradient(cx - 24, 0, cx - 10, 0);
        bridgeShadowL.addColorStop(0, 'rgba(80, 36, 16, 0.25)');
        bridgeShadowL.addColorStop(1, 'rgba(154, 87, 46, 0.0)');
        ctx.fillStyle = bridgeShadowL;
        ctx.fillRect(cx - 24, ny - 90, 14, 80);

        const bridgeShadowR = ctx.createLinearGradient(cx + 24, 0, cx + 10, 0);
        bridgeShadowR.addColorStop(0, 'rgba(80, 36, 16, 0.25)');
        bridgeShadowR.addColorStop(1, 'rgba(154, 87, 46, 0.0)');
        ctx.fillStyle = bridgeShadowR;
        ctx.fillRect(cx + 10, ny - 90, 14, 80);

        // 2. Dorsal Bridge Vertical Ridge Highlight
        const bridgeGrad = ctx.createLinearGradient(cx, ny - 90, cx, ny - 10);
        bridgeGrad.addColorStop(0, 'rgba(215, 140, 90, 0.0)');
        bridgeGrad.addColorStop(0.5, 'rgba(225, 155, 105, 0.40)');
        bridgeGrad.addColorStop(1, 'rgba(235, 165, 115, 0.55)');
        ctx.fillStyle = bridgeGrad;
        ctx.beginPath();
        ctx.moveTo(cx - 11, ny - 90);
        ctx.lineTo(cx + 11, ny - 90);
        ctx.lineTo(cx + 16, ny - 10);
        ctx.lineTo(cx - 16, ny - 10);
        ctx.closePath();
        ctx.fill();

        // 3. Left and Right Nostril Wings (curving fleshy lateral flares)
        const wingGradL = ctx.createRadialGradient(cx - 28, ny, 3, cx - 28, ny + 2, 20);
        wingGradL.addColorStop(0, 'rgba(225, 145, 95, 0.65)');
        wingGradL.addColorStop(0.7, 'rgba(175, 95, 52, 0.40)');
        wingGradL.addColorStop(1, 'rgba(120, 55, 25, 0.0)');
        ctx.fillStyle = wingGradL;
        ctx.beginPath();
        ctx.arc(cx - 28, ny + 2, 20, 0, Math.PI * 2);
        ctx.fill();

        const wingGradR = ctx.createRadialGradient(cx + 28, ny, 3, cx + 28, ny + 2, 20);
        wingGradR.addColorStop(0, 'rgba(225, 145, 95, 0.65)');
        wingGradR.addColorStop(0.7, 'rgba(175, 95, 52, 0.40)');
        wingGradR.addColorStop(1, 'rgba(120, 55, 25, 0.0)');
        ctx.fillStyle = wingGradR;
        ctx.beginPath();
        ctx.arc(cx + 28, ny + 2, 20, 0, Math.PI * 2);
        ctx.fill();

        // Nostril wing lateral crease line
        ctx.strokeStyle = 'rgba(95, 42, 18, 0.38)';
        ctx.lineWidth = 2.2;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.arc(cx - 28, ny + 2, 17, Math.PI * 0.65, Math.PI * 1.35);
        ctx.stroke();
        ctx.beginPath();
        ctx.arc(cx + 28, ny + 2, 17, -Math.PI * 0.35, Math.PI * 0.35);
        ctx.stroke();

        // 4. Central Bulbous Nose Tip (spherical 3D volumetric highlight)
        const tipGrad = ctx.createRadialGradient(cx, ny - 4, 4, cx, ny + 2, 32);
        tipGrad.addColorStop(0, 'rgba(242, 168, 120, 0.75)');
        tipGrad.addColorStop(0.55, 'rgba(205, 125, 75, 0.45)');
        tipGrad.addColorStop(0.85, 'rgba(150, 78, 40, 0.20)');
        tipGrad.addColorStop(1, 'rgba(100, 45, 20, 0.0)');
        ctx.fillStyle = tipGrad;
        ctx.beginPath();
        ctx.arc(cx, ny + 2, 32, 0, Math.PI * 2);
        ctx.fill();

        // Under-tip ambient shadow (separates nose from mustache)
        const underTipGrad = ctx.createLinearGradient(cx, ny + 8, cx, ny + 22);
        underTipGrad.addColorStop(0, 'rgba(75, 32, 14, 0.45)');
        underTipGrad.addColorStop(1, 'rgba(75, 32, 14, 0.0)');
        ctx.fillStyle = underTipGrad;
        ctx.beginPath();
        ctx.ellipse(cx, ny + 14, 26, 8, 0, 0, Math.PI * 2);
        ctx.fill();

        // 5. Nostril Base Cavities (dark curved espresso apertures)
        ctx.fillStyle = this.colors.noseShadow;
        ctx.beginPath();
        ctx.ellipse(cx - 18, ny + 13, 11, 5.5, -0.25, 0, Math.PI * 2);
        ctx.ellipse(cx + 18, ny + 13, 11, 5.5, 0.25, 0, Math.PI * 2);
        ctx.fill();

        // 6. Crisp Specular Dot on Nose Tip (matching 1:00 key light)
        const specX = cx + 4;
        const specY = ny - 6;
        const specGrad = ctx.createRadialGradient(specX, specY, 1.5, specX, specY, 9);
        specGrad.addColorStop(0, 'rgba(255, 245, 235, 0.85)');
        specGrad.addColorStop(0.5, 'rgba(255, 235, 215, 0.35)');
        specGrad.addColorStop(1, 'rgba(255, 235, 215, 0.0)');
        ctx.fillStyle = specGrad;
        ctx.beginPath();
        ctx.arc(specX, specY, 9, 0, Math.PI * 2);
        ctx.fill();

        // 7. Subtle Philtrum Column Furrows
        ctx.strokeStyle = 'rgba(85, 38, 16, 0.22)';
        ctx.lineWidth = 2.0;
        ctx.beginPath();
        ctx.moveTo(cx - 7, ny + 16);
        ctx.lineTo(cx - 8, ny + 32);
        ctx.moveTo(cx + 7, ny + 16);
        ctx.lineTo(cx + 8, ny + 32);
        ctx.stroke();

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
        const gap = 9; // 18px total gap across philtrum center

        // 1. Mustache Solid Body Fill
        ctx.fillStyle = this.colors.mustache;
        ctx.beginPath();
        // Inner philtrum top
        ctx.moveTo(sign * gap, 2);
        // Arching smoothly over upper lip
        ctx.bezierCurveTo(sign * 28, -16, sign * 64, -14, sign * 98, 8);
        // Graceful drape over mouth corner
        ctx.bezierCurveTo(sign * 106, 16, sign * 88, 20, sign * 70, 13);
        // Bottom contour returning closely along upper lip
        ctx.bezierCurveTo(sign * 46, 8, sign * 24, 6, sign * gap, 8);
        // Philtrum vertical inner border
        ctx.closePath();
        ctx.fill();

        // 2. Subtle 3D Volume Ridge Highlight (warm dark brown sheen along the crest)
        ctx.strokeStyle = 'rgba(72, 42, 26, 0.45)';
        ctx.lineWidth = 4.0;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(sign * (gap + 6), 4);
        ctx.bezierCurveTo(sign * 32, -10, sign * 62, -8, sign * 92, 9);
        ctx.stroke();

        // 3. Delicate Micro-Stubble & Feathered Edge Hairs
        ctx.strokeStyle = this.colors.mustacheStipple;
        ctx.lineWidth = 1.6;
        ctx.lineCap = 'round';

        // Feathered hairs along upper contour
        const topHairs = [
            [12, 0, 14, -5],
            [22, -8, 26, -14],
            [34, -13, 39, -19],
            [48, -15, 54, -20],
            [62, -14, 68, -18],
            [76, -8, 82, -12],
            [88, 1, 94, -2]
        ];
        for (const [x1, y1, x2, y2] of topHairs) {
            ctx.beginPath();
            ctx.moveTo(sign * x1, y1);
            ctx.lineTo(sign * x2, y2);
            ctx.stroke();
        }

        // Soft micro-stipples inside the mustache body
        ctx.fillStyle = '#0D0604';
        const stipples = [
            [16, 4], [26, -3], [42, -6], [58, -4], [72, 2], [84, 8],
            [20, 7], [36, 5], [52, 4], [66, 8], [30, 1], [46, -1], [60, 2]
        ];
        for (const [dx, dy] of stipples) {
            ctx.beginPath();
            ctx.arc(sign * dx, dy, 1.4, 0, Math.PI * 2);
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
        const mw = 118; // Confident, warm smile half-width (matching calibrated face proportions)

        // 1. Upper Lip (Warm terracotta with sculpted Cupid's bow)
        ctx.fillStyle = this.colors.upperLip;
        ctx.beginPath();
        // Cupid's bow top
        ctx.moveTo(-mw, -8);
        ctx.quadraticCurveTo(-mw * 0.45, -18, -20, -14);
        ctx.lineTo(0, -6); // Center notch dip
        ctx.lineTo(20, -14);
        ctx.quadraticCurveTo(mw * 0.45, -18, mw, -8);
        // Returning along smile seam
        ctx.bezierCurveTo(mw * 0.55, 3, mw * 0.2, 2, 0, 2);
        ctx.bezierCurveTo(-mw * 0.2, 2, -mw * 0.55, 3, -mw, -8);
        ctx.closePath();
        ctx.fill();

        // 2. Lower Lip (Fuller fleshy warm rose with smooth rounded contour)
        ctx.fillStyle = this.colors.lowerLip;
        ctx.beginPath();
        ctx.moveTo(-mw * 0.86, -6);
        ctx.quadraticCurveTo(-mw * 0.48, 30, 0, 32);
        ctx.quadraticCurveTo(mw * 0.48, 30, mw * 0.86, -6);
        // Hugging smile seam
        ctx.bezierCurveTo(mw * 0.45, 3, mw * 0.2, 2, 0, 2);
        ctx.bezierCurveTo(-mw * 0.2, 2, -mw * 0.45, 3, -mw * 0.86, -6);
        ctx.closePath();
        ctx.fill();

        // Fleshy Lower Lip 3D Volume Gradient
        const lipDepth = ctx.createLinearGradient(0, 2, 0, 32);
        lipDepth.addColorStop(0, 'rgba(140, 58, 40, 0.35)');
        lipDepth.addColorStop(0.5, 'rgba(255, 255, 255, 0.0)');
        lipDepth.addColorStop(1, 'rgba(100, 38, 22, 0.40)');
        ctx.fillStyle = lipDepth;
        ctx.beginPath();
        ctx.moveTo(-mw * 0.86, -6);
        ctx.quadraticCurveTo(-mw * 0.48, 30, 0, 32);
        ctx.quadraticCurveTo(mw * 0.48, 30, mw * 0.86, -6);
        ctx.closePath();
        ctx.fill();

        // Brilliant Gloss Highlight on Lower Lip (matching concept art specular reflection)
        const glossGrad = ctx.createLinearGradient(0, 10, 0, 26);
        glossGrad.addColorStop(0, 'rgba(255, 215, 195, 0.80)');
        glossGrad.addColorStop(0.65, 'rgba(240, 175, 145, 0.35)');
        glossGrad.addColorStop(1, 'rgba(200, 120, 95, 0.0)');
        ctx.fillStyle = glossGrad;
        ctx.beginPath();
        ctx.ellipse(0, 17, mw * 0.44, 7.5, 0, 0, Math.PI * 2);
        ctx.fill();

        // 3. Mouth Seam (Dark, confident upturned smile line)
        ctx.strokeStyle = this.colors.lipLine;
        ctx.lineWidth = 5.2;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-mw, -8);
        ctx.bezierCurveTo(-mw * 0.55, 3, -mw * 0.2, 2, 0, 2);
        ctx.bezierCurveTo(mw * 0.2, 2, mw * 0.55, 3, mw, -8);
        ctx.stroke();

        // Confident Smile Corner Dimples & Creases
        ctx.strokeStyle = 'rgba(65, 26, 12, 0.55)';
        ctx.lineWidth = 3.2;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(-mw - 2, -13);
        ctx.quadraticCurveTo(-mw, -8, -mw + 6, -5);
        ctx.moveTo(mw + 2, -13);
        ctx.quadraticCurveTo(mw, -8, mw - 6, -5);
        ctx.stroke();
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

        // 1. Soul Patch (soft triangular wedge under lower lip with micro-strands)
        ctx.fillStyle = this.colors.soulPatch;
        ctx.beginPath();
        ctx.moveTo(cx - 10, spy - 16);
        ctx.lineTo(cx + 10, spy - 16);
        ctx.lineTo(cx + 5, spy + 12);
        ctx.lineTo(cx - 5, spy + 12);
        ctx.closePath();
        ctx.fill();

        // Soul patch vertical micro-strands
        ctx.strokeStyle = '#0E0603';
        ctx.lineWidth = 1.5;
        ctx.lineCap = 'round';
        for (let sx = -7; sx <= 7; sx += 3.5) {
            ctx.beginPath();
            ctx.moveTo(cx + sx, spy - 14);
            ctx.lineTo(cx + sx * 0.6, spy + 9);
            ctx.stroke();
        }

        // 2. Chin Goatee (composed of textured micro-curls hugging chin bevel)
        ctx.translate(cx, gy);

        // Soft semi-translucent base undertone (lets warm skin breathe through)
        const baseGrad = ctx.createRadialGradient(0, 16, 12, 0, 16, 62);
        baseGrad.addColorStop(0, 'rgba(28, 14, 8, 0.70)');
        baseGrad.addColorStop(0.7, 'rgba(28, 14, 8, 0.45)');
        baseGrad.addColorStop(1, 'rgba(28, 14, 8, 0.0)');
        ctx.fillStyle = baseGrad;
        ctx.beginPath();
        ctx.ellipse(0, 16, 62, 42, 0, 0, Math.PI * 2);
        ctx.fill();

        // Layer 1: Base curly ringlets (deep espresso #120804)
        ctx.strokeStyle = this.colors.goateeCurl;
        ctx.lineWidth = 2.2;
        ctx.lineCap = 'round';
        const curlsLayer1 = [
            [-44, -2], [-28, -6], [-12, -8], [0, -8], [12, -8], [28, -6], [44, -2],
            [-50, 8], [-34, 5], [-16, 3], [0, 3], [16, 3], [34, 5], [50, 8],
            [-48, 18], [-32, 15], [-16, 13], [0, 12], [16, 13], [32, 15], [48, 18],
            [-42, 28], [-26, 25], [-10, 23], [10, 23], [26, 25], [42, 28],
            [-30, 36], [-14, 34], [0, 34], [14, 34], [30, 36],
            [-16, 44], [0, 44], [16, 44]
        ];
        for (const [xc, yc] of curlsLayer1) {
            ctx.beginPath();
            ctx.arc(xc, yc, 3.8, 0.2, Math.PI * 1.6);
            ctx.stroke();
        }

        // Layer 2: Interlocking micro-curls (warm dark brown #28150D)
        ctx.strokeStyle = '#28150D';
        ctx.lineWidth = 1.8;
        const curlsLayer2 = [
            [-36, 0], [-20, -3], [-5, -4], [9, -3], [25, 0], [36, 2],
            [-40, 12], [-24, 10], [-8, 7], [9, 7], [25, 10], [40, 12],
            [-34, 22], [-18, 19], [-2, 17], [14, 18], [30, 21],
            [-22, 32], [-7, 29], [7, 29], [22, 32],
            [-9, 39], [7, 39]
        ];
        for (const [xc, yc] of curlsLayer2) {
            ctx.beginPath();
            ctx.arc(xc, yc, 3.2, Math.PI * 0.8, Math.PI * 2.2);
            ctx.stroke();
        }

        // Layer 3: Subtle surface highlight curls (#3E2215)
        ctx.strokeStyle = '#3E2215';
        ctx.lineWidth = 1.5;
        const curlsLayer3 = [
            [-24, 4], [-10, 2], [5, 2], [18, 4],
            [-28, 14], [-12, 12], [2, 11], [16, 12], [28, 14],
            [-18, 24], [-2, 21], [12, 22]
        ];
        for (const [xc, yc] of curlsLayer3) {
            ctx.beginPath();
            ctx.arc(xc, yc, 2.8, 0.4, Math.PI * 1.7);
            ctx.stroke();
        }

        // Layer 4: Organic edge feathering / stipples around the chin perimeter
        ctx.fillStyle = this.colors.goateePebble || '#2C180E';
        for (let i = 0; i < 48; i++) {
            const ang = (i * 2.3999);
            const rad = Math.sqrt((i + 0.5) / 48);
            const px = Math.cos(ang) * 54 * rad;
            const py = 18 + Math.sin(ang) * 32 * rad;
            ctx.beginPath();
            ctx.arc(px, py, 1.4, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.restore();
    }
}
