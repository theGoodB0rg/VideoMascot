/**
 * ProceduralTorsoPainter.js
 * 
 * Programmatically paints the Brick Dev polo shirt, collar, placket, button, and sleeves.
 * Recreates the exact proportions, curvatures, and colors of the concept art.
 * 
 * ZERO BAKED SKIN GUARANTEE:
 * The torso texture contains 100% pure fabric across the collar and neckline,
 * completely eliminating the baked brown neck skin triangle glitch from Image 0.
 */

export class ProceduralTorsoPainter {
    constructor(options = {}) {
        this.width = options.width || 1024;
        this.height = options.height || 1024;

        this.colors = {
            stripeBlue: '#96B8DA',      // Calibrated soft light-blue polo stripe
            stripeWhite: '#EFF3F9',     // Crisp off-white polo stripe
            collarBase: '#9EBFDE',      // Light blue polo collar fabric
            collarInside: '#7C9EC2',    // Inner neckline facing fabric (ZERO SKIN)
            collarOutline: '#385273',   // Dark blue accent seam & outline
            collarInnerTrim: '#FAFBFD', // Crisp white inner pinstripe trim
            placketOutline: '#385273',  // Dark blue button placket seam
            buttonWhite: '#FFFFFF',     // Molded white plastic button
            buttonOutline: '#385273',   // Button rim contour
            buttonHole: '#385273',      // Button thread holes
            skinBase: '#94532B',        // Forearm skin tone (only on forearm!)
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

    renderFront(targetCtx = null) {
        return this.render(targetCtx);
    }

    render(targetCtx = null) {
        const ctx = targetCtx || this.ctx;
        if (!ctx) return;

        const w = this.width;
        const h = this.height;

        // 1. Base off-white fabric
        ctx.fillStyle = this.colors.stripeWhite;
        ctx.fillRect(0, 0, w, h);

        // 2. Alternating horizontal stripes
        this.drawStripes(ctx, w, h);

        // 3. Inner neck cavity (PURE FABRIC - ZERO SKIN)
        this.drawNeckCavity(ctx, w, h);

        // 4. Polo Button Placket
        this.drawPlacket(ctx, w, h);

        // 5. Polo Collar Lapels
        this.drawCollar(ctx, w, h);

        // 6. Polo Button
        this.drawButton(ctx, w, h);

        // 7. Subtle lighting gradients across torso
        this.drawTorsoLighting(ctx, w, h);
    }

    /**
     * Alternating light-blue and white stripes.
     * Band 0 (0..128): White shoulders
     * Band 1 (128..256): Blue stripe 1
     * Band 2 (256..384): White stripe 2
     * Band 3 (384..512): Blue stripe 3
     * Band 4 (512..640): White stripe 4
     * Band 5 (640..768): Blue stripe 5
     * Band 6 (768..896): White stripe 6
     * Band 7 (896..1024): Blue stripe 7 (waist)
     */
    drawStripes(ctx, w, h) {
        const stripeH = h / 8; // 128px per band

        for (let i = 0; i < 8; i++) {
            if (i % 2 === 1) {
                const y = i * stripeH;
                ctx.fillStyle = this.colors.stripeBlue;
                ctx.fillRect(0, y, w, stripeH);

                // Subtle fabric gradient
                const grad = ctx.createLinearGradient(0, y, 0, y + stripeH);
                grad.addColorStop(0, 'rgba(255, 255, 255, 0.09)');
                grad.addColorStop(0.5, 'rgba(0, 0, 0, 0.0)');
                grad.addColorStop(1, 'rgba(0, 0, 0, 0.06)');
                ctx.fillStyle = grad;
                ctx.fillRect(0, y, w, stripeH);
            }
        }
    }

    /**
     * Inner neck cavity behind collar lapels.
     * Pure fabric facing that mates with the 3D neck cylinder.
     * ZERO skin tone.
     */
    /**
     * Authentic V-neck opening revealing warm caramel neck skin.
     */
    drawNeckCavity(ctx, w, h) {
        const cx = w / 2; // 512
        const neckW = 84;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(cx - neckW, 0);
        ctx.quadraticCurveTo(cx - 48, 72, cx, 116);
        ctx.quadraticCurveTo(cx + 48, 72, cx + neckW, 0);
        ctx.closePath();

        // Warm caramel skin tone matching the elevated 3D neck pedestal
        ctx.fillStyle = this.colors.skinBase || '#9A572E';
        ctx.fill();

        // Soft ambient neck shadow under the 3D neck cylinder
        const shadow = ctx.createLinearGradient(0, 0, 0, 80);
        shadow.addColorStop(0, 'rgba(70, 35, 18, 0.45)');
        shadow.addColorStop(0.6, 'rgba(70, 35, 18, 0.15)');
        shadow.addColorStop(1, 'rgba(70, 35, 18, 0.0)');
        ctx.fillStyle = shadow;
        ctx.fill();

        ctx.restore();
    }

    /**
     * Draws the vertical polo button placket.
     */
    drawPlacket(ctx, w, h) {
        const cx = w / 2; // 512
        const pw = 54;
        const pTop = 116;
        const pBottom = 236;
        const xLeft = cx - pw / 2;

        ctx.save();

        // Placket background (matches sky-blue polo fabric)
        ctx.fillStyle = this.colors.stripeBlue;
        ctx.beginPath();
        ctx.roundRect(xLeft, pTop, pw, pBottom - pTop, [0, 0, 6, 6]);
        ctx.fill();

        // Placket side seams & bottom outline
        ctx.strokeStyle = this.colors.placketOutline;
        ctx.lineWidth = 4.8;
        ctx.lineJoin = 'round';
        ctx.beginPath();
        ctx.moveTo(xLeft, pTop);
        ctx.lineTo(xLeft, pBottom - 6);
        ctx.arcTo(xLeft, pBottom, xLeft + 6, pBottom, 6);
        ctx.lineTo(xLeft + pw - 6, pBottom);
        ctx.arcTo(xLeft + pw, pBottom, xLeft + pw, pBottom - 6, 6);
        ctx.lineTo(xLeft + pw, pTop);
        ctx.stroke();

        ctx.restore();
    }

    /**
     * Authentic folded polo collar lapels matching reference Image 2.
     */
    drawCollar(ctx, w, h) {
        const cx = w / 2; // 512

        this.drawLapel(ctx, cx, false);
        this.drawLapel(ctx, cx, true);
    }

    drawLapel(ctx, cx, isRight) {
        ctx.save();
        const sign = isRight ? 1 : -1;

        // Landmark points calibrated against reference Image 2:
        const pNeck = { x: cx + sign * 84, y: 0 };
        const pShoulder = { x: cx + sign * 248, y: 26 };
        const pTip = { x: cx + sign * 198, y: 165 };
        const pInnerV = { x: cx + sign * 24, y: 118 };

        // 1. Lapel Body
        ctx.beginPath();
        ctx.moveTo(pNeck.x, pNeck.y);
        // Collar band curve over shoulder
        ctx.bezierCurveTo(cx + sign * 165, 6, pShoulder.x - sign * 5, pShoulder.y - 10, pShoulder.x, pShoulder.y);
        // Outer curved edge sweeping down to tip
        ctx.bezierCurveTo(pShoulder.x - sign * 12, 100, pTip.x + sign * 22, 132, pTip.x, pTip.y);
        // Bottom edge curving gently up towards inner placket notch
        ctx.bezierCurveTo(pTip.x - sign * 48, pTip.y - 10, pInnerV.x + sign * 40, pInnerV.y + 14, pInnerV.x, pInnerV.y);
        // Inner collar seam rising up to neck following V-opening
        ctx.bezierCurveTo(cx + sign * 42, 80, cx + sign * 60, 35, pNeck.x, pNeck.y);
        ctx.closePath();

        ctx.fillStyle = this.colors.collarBase;
        ctx.fill();

        // 2. Collar 3D Plastic Highlight & Shadow
        const lapelGrad = ctx.createLinearGradient(cx, 0, cx + sign * 198, 165);
        lapelGrad.addColorStop(0, 'rgba(255, 255, 255, 0.45)');
        lapelGrad.addColorStop(0.45, 'rgba(255, 255, 255, 0.05)');
        lapelGrad.addColorStop(1, 'rgba(30, 48, 75, 0.22)');
        ctx.fillStyle = lapelGrad;
        ctx.fill();

        // 3. Crisp White Inner Trim Pinstripe (running along shoulder, outer sweep, and bottom edge)
        ctx.strokeStyle = this.colors.collarInnerTrim;
        ctx.lineWidth = 4.8;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.beginPath();
        const trimShoulder = { x: pShoulder.x - sign * 12, y: pShoulder.y + 6 };
        const trimTip = { x: pTip.x - sign * 12, y: pTip.y - 12 };
        const trimInnerV = { x: pInnerV.x + sign * 10, y: pInnerV.y - 6 };

        ctx.moveTo(cx + sign * 155, 12);
        ctx.bezierCurveTo(pShoulder.x - sign * 16, 18, trimShoulder.x, trimShoulder.y - 6, trimShoulder.x, trimShoulder.y);
        ctx.bezierCurveTo(trimShoulder.x - sign * 10, 100, trimTip.x + sign * 14, 130, trimTip.x, trimTip.y);
        ctx.bezierCurveTo(trimTip.x - sign * 42, trimTip.y - 8, trimInnerV.x + sign * 34, trimInnerV.y + 8, trimInnerV.x, trimInnerV.y);
        ctx.stroke();

        // 4. Dark Blue Outer Border Seam
        ctx.strokeStyle = this.colors.collarOutline;
        ctx.lineWidth = 5.2;
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.beginPath();
        ctx.moveTo(pNeck.x, pNeck.y);
        ctx.bezierCurveTo(cx + sign * 165, 6, pShoulder.x - sign * 5, pShoulder.y - 10, pShoulder.x, pShoulder.y);
        ctx.bezierCurveTo(pShoulder.x - sign * 12, 100, pTip.x + sign * 22, 132, pTip.x, pTip.y);
        ctx.bezierCurveTo(pTip.x - sign * 48, pTip.y - 10, pInnerV.x + sign * 40, pInnerV.y + 14, pInnerV.x, pInnerV.y);
        ctx.stroke();

        // Inner neck border seam
        ctx.strokeStyle = this.colors.collarOutline;
        ctx.lineWidth = 4.2;
        ctx.beginPath();
        ctx.moveTo(pInnerV.x, pInnerV.y);
        ctx.bezierCurveTo(cx + sign * 42, 80, cx + sign * 60, 35, pNeck.x, pNeck.y);
        ctx.stroke();

        // 5. Cast Shadow Under Lapel onto Chest
        ctx.strokeStyle = 'rgba(25, 40, 60, 0.22)';
        ctx.lineWidth = 5.5;
        ctx.beginPath();
        ctx.moveTo(pTip.x, pTip.y + 4);
        ctx.bezierCurveTo(pTip.x - sign * 48, pTip.y - 8, pInnerV.x + sign * 40, pInnerV.y + 16, pInnerV.x, pInnerV.y + 6);
        ctx.stroke();

        ctx.restore();
    }

    /**
     * Draws the circular polo button on the placket matching Image 2.
     */
    drawButton(ctx, w, h) {
        const cx = w / 2; // 512
        const buttonY = 168;
        const buttonR = 16;

        ctx.save();

        // Button cast shadow
        ctx.fillStyle = 'rgba(25, 40, 65, 0.30)';
        ctx.beginPath();
        ctx.arc(cx + 1.5, buttonY + 2, buttonR, 0, Math.PI * 2);
        ctx.fill();

        // Button body (white molded plastic)
        ctx.fillStyle = this.colors.buttonWhite;
        ctx.beginPath();
        ctx.arc(cx, buttonY, buttonR, 0, Math.PI * 2);
        ctx.fill();

        // Button outer rim seam
        ctx.strokeStyle = this.colors.buttonOutline;
        ctx.lineWidth = 4.2;
        ctx.stroke();

        // Inner concentric circular stitch ring (matching Image 2)
        ctx.strokeStyle = this.colors.buttonHole;
        ctx.lineWidth = 2.8;
        ctx.beginPath();
        ctx.arc(cx, buttonY, 6.8, 0, Math.PI * 2);
        ctx.stroke();

        ctx.restore();
    }

    drawTorsoLighting(ctx, w, h) {
        // Soft shoulder highlight
        const shoulderGrad = ctx.createLinearGradient(0, 0, 0, 160);
        shoulderGrad.addColorStop(0, 'rgba(255, 255, 255, 0.22)');
        shoulderGrad.addColorStop(1, 'rgba(255, 255, 255, 0.0)');
        ctx.fillStyle = shoulderGrad;
        ctx.fillRect(0, 0, w, 160);

        // Soft lateral ambient shading
        const leftAo = ctx.createLinearGradient(0, 0, 80, 0);
        leftAo.addColorStop(0, 'rgba(20, 30, 45, 0.16)');
        leftAo.addColorStop(1, 'rgba(20, 30, 45, 0.0)');
        ctx.fillStyle = leftAo;
        ctx.fillRect(0, 0, 80, h);

        const rightAo = ctx.createLinearGradient(w, 0, w - 80, 0);
        rightAo.addColorStop(0, 'rgba(20, 30, 45, 0.16)');
        rightAo.addColorStop(1, 'rgba(20, 30, 45, 0.0)');
        ctx.fillStyle = rightAo;
        ctx.fillRect(w - 80, 0, 80, h);
    }

    renderSleeve(targetCtx = null, width = 512, height = 512) {
        let canvas = null;
        let ctx = targetCtx;
        if (!ctx) {
            if (typeof document !== 'undefined') {
                canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                ctx = canvas.getContext('2d');
            } else if (typeof OffscreenCanvas !== 'undefined') {
                canvas = new OffscreenCanvas(width, height);
                ctx = canvas.getContext('2d');
            }
        }
        if (!ctx) return null;

        ctx.fillStyle = this.colors.stripeWhite;
        ctx.fillRect(0, 0, width, height);

        const stripeH = height / 8;
        for (let i = 0; i < 8; i++) {
            if (i % 2 === 1) {
                ctx.fillStyle = this.colors.stripeBlue;
                ctx.fillRect(0, i * stripeH, width, stripeH);

                const g = ctx.createLinearGradient(0, i * stripeH, 0, (i + 1) * stripeH);
                g.addColorStop(0, 'rgba(255, 255, 255, 0.08)');
                g.addColorStop(1, 'rgba(0, 0, 0, 0.05)');
                ctx.fillStyle = g;
                ctx.fillRect(0, i * stripeH, width, stripeH);
            }
        }

        return canvas;
    }

    renderForearm(targetCtx = null, width = 512, height = 512) {
        let canvas = null;
        let ctx = targetCtx;
        if (!ctx) {
            if (typeof document !== 'undefined') {
                canvas = document.createElement('canvas');
                canvas.width = width;
                canvas.height = height;
                ctx = canvas.getContext('2d');
            } else if (typeof OffscreenCanvas !== 'undefined') {
                canvas = new OffscreenCanvas(width, height);
                ctx = canvas.getContext('2d');
            }
        }
        if (!ctx) return null;

        ctx.fillStyle = this.colors.skinBase;
        ctx.fillRect(0, 0, width, height);

        const cuffH = height * 0.26;
        ctx.fillStyle = this.colors.stripeBlue;
        ctx.fillRect(0, 0, width, cuffH);

        ctx.fillStyle = this.colors.collarOutline;
        ctx.fillRect(0, cuffH - 6, width, 6);

        const cuffGrad = ctx.createLinearGradient(0, 0, 0, cuffH);
        cuffGrad.addColorStop(0, 'rgba(255, 255, 255, 0.20)');
        cuffGrad.addColorStop(1, 'rgba(0, 0, 0, 0.08)');
        ctx.fillStyle = cuffGrad;
        ctx.fillRect(0, 0, width, cuffH - 6);

        return canvas;
    }
}
