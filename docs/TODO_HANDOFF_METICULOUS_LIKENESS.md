# TODO HANDOFF: METICULOUS 1:1 LIKENESS BLUEPRINT (BRICK DEV)

**File Location**: `docs/TODO_HANDOFF_METICULOUS_LIKENESS.md`  
**Target Reference**: `preview/brick_dev_perfect_cutout.png` (1024x1024 RGBA)  
**Strict Mandate**: 100% Procedural Handcrafted PBR in Three.js & Canvas 2D.  
**ZERO Photo Decals. ZERO Texture Projections. ZERO Lazy Overlaying.**  

---

## 1. Executive Summary & Why Previous Attempts Failed

The goal is to render the Senior Developer Lego Minifigure ("Brick Dev", waist-up, zero props) in Three.js so faithfully that it is virtually indistinguishable in size, contouring, dimensions, and lighting from the concept art (`preview/brick_dev_perfect_cutout.png`).

### Why Previous Attempts Diverged:
1. **The Lazy Overlay Trap (`build_textures.py`)**:
   Attempted to crop pixels from the 2D concept art and project them onto cylinder UVs.
   *Result*: Severe cylindrical distortion, perspective flattening, blurry edges, and 2D shadows clashing with Three.js lights.
2. **The Crude Cartoon Fallback (`head_3d_clean_molded.png`)**:
   Attempted basic canvas primitives (rigid circles, flat black ovals, single-pixel lines).
   *Result*: Looked like a crude Minecraft head or Mii with anime eyes, lacking all the organic subtlety of the concept art.
3. **The Sunken Neck & Mushroom Hair Bug**:
   - The head was positioned too low on the torso, burying the **65px cylindrical neck pedestal** inside the collar.
   - The afro hair piece was oversized ($R=0.552$), ballooned outwards like a mushroom cap, and drooped over the eyebrows with large bead rows ($R=0.034$) forming concentric cornrow rings.
   - Torso shoulders had sharp knife edges instead of rounded molded fillets.

---

## 2. Concept Art Forensic Blueprint (Pixel-Calibrated Measurements)

All measurements calibrated against `preview/brick_dev_perfect_cutout.png` (1024×1024, Center Axis $X_0 = 512$):

```
                  Y=28  +--------------------+ (Top of Afro Hair)
                        |    Afro Helmet     | (Height: 92px at center)
                 Y=120  +---\------------/---+ (Forehead Hairline Arch)
                        |    Forehead (75px) | (Open, wide, dignified)
                 Y=195  |   ~ Eyebrows ~     | (Arched, feathered, X: 387-479 & 551-607)
                 Y=245  |    (O)    (O)      | Eyes (Almond, Double Studio Catchlight)
                 Y=316  |        *           | Nose Tip (X=525) & Nostril Shading
                 Y=345  |      {===}         | Mustache (Split 18px Philtrum Gap)
                 Y=375  |      (---)         | Terracotta Lips (Cupid's Bow, Gloss Sheen)
                 Y=425  |       ###          | Chin Goatee (Micro-Stippled Pebble Noise)
                 Y=480  +--------------------+ (Chin Bottom / Jaw Bevel)
                        |    Neck Pedestal   | (Height: 65px - VISIBLE ELEVATION)
                 Y=545  +---\____________/---+ (Polo Collar V-Neck)
                        |  |   Placket [o]   |
                 Y=575  |=== White Stripe ===| (Torso Stripe 1)
                 Y=615  |=== Sky-Blue Stripe=| (Torso Stripe 2)
                 Y=675  |=== White Stripe ===| (Torso Stripe 3)
                 Y=715  |=== Sky-Blue Stripe=| (Torso Stripe 4)
                 Y=755  |=== White Stripe ===| (Torso Stripe 5)
                 Y=795  |=== Sky-Blue Stripe=| (Torso Stripe 6)
                 Y=855  |=== White Stripe ===| (Torso Stripe 7 - Hem)
                 Y=915  +====================+ (Waist Seam)
                        |  Dark Navy Waist   | (Waistband / Hips, RGB: 20, 36, 72)
                Y=1023  +--------------------+ (Waist-Up Minifigure Crop)
```

### Proportional Relationships:
- **Total Mascot Height**: 995px ($Y = 28 \to 1023$).
- **Head Height (Hair Top to Chin Bottom)**: 452px ($Y = 28 \to 480$).
- **Visible Face Height (Hairline to Chin)**: 360px ($Y = 120 \to 480$).
- **Neck Height**: 65px ($Y = 480 \to 545$) $\rightarrow$ **Must never be sunken into the collar!**
- **Torso Height**: 370px ($Y = 545 \to 915$).
- **Head Width across Eyes**: 359px ($X = 332 \to 691$).
- **Eye Dimensions**: Width 136px, Height 84px (in 2048x1024 texture space); Spacing $\pm 155\text{px}$ from midline.

---

## 3. Master Color Palette & PBR Shading Parameters

```javascript
export const BRICK_DEV_PALETTE = {
    // Skin & Plastic Base (Warm rich caramel-brown ABS plastic)
    skinBase:          '#94532B', // Main facial skin tone (RGB: 148, 83, 43)
    skinHighlight:     '#AD673A', // Forehead, cheekbone, and chin highlight
    skinShadow:        '#733718', // Jawline, chin bevel, and socket shadow
    skinCrease:        '#5A2711', // Deep eyelid crease and nostril shadow
    
    // Eyes & Gaze
    sclera:            '#F0F2F6', // Clean warm white sclera
    irisOuter:         '#1A0F09', // Dark espresso outer iris border
    irisInner:         '#3D1E0F', // Rich warm brown iris core
    irisGlow:          '#5E311A', // Lower iris ambient bounce
    pupil:             '#090503', // Solid deep black pupil
    catchlightMajor:   '#FFFFFF', // Primary sharp circular studio catchlight (1:30 position)
    catchlightMinor:   'rgba(255, 255, 255, 0.65)', // Secondary smaller catchlight dot
    eyelidLine:        '#1E0F08', // Upper lash contour line
    eyelidCrease:      '#582712', // Double-fold upper eyelid crease
    
    // Brows & Hair
    eyebrow:           '#190E08', // Espresso-black feathered brow
    hairPlastic:       0x181615,  // Deep espresso-black ABS hair helmet
    hairSpecular:      0x44403c,  // Soft warm hair specular
    
    // Nose
    nostrilShadow:     'rgba(82, 36, 16, 0.75)', // Soft curved nostril crescents
    noseTipHighlight:  'rgba(247, 200, 182, 0.40)', // Soft radial tip highlight
    noseBridgeSheen:   'rgba(173, 103, 58, 0.35)', // Bridge vertical gradient
    
    // Facial Hair
    mustache:          '#180E09', // Trimmed mustache
    mustacheStipple:   '#2B180F', // Edge hair feathering
    soulPatch:         '#180E08', // Sub-lip soul patch
    goateeBase:        '#120A05', // Chin goatee base shape
    goateePebble:      '#24140B', // Stippled micro-curl ringlets
    
    // Mouth & Lips
    upperLip:          '#8D4A32', // Terracotta upper lip
    lowerLip:          '#B3644E', // Fuller fleshy lower lip
    lipSheen:          'rgba(200, 120, 94, 0.60)', // Lower lip gloss arc
    lipLine:           '#38170B', // Mouth seam line
    mouthInside:       '#250808', // Oral cavity (visemes)
    teeth:             '#F5F7FA', // Clean white teeth
    tongue:            '#B44949', // Warm red tongue
    
    // Torso Polo & Clothing
    poloSkyBlue:       '#96B4D6', // Sky blue stripes & collar (RGB: 150, 180, 214)
    poloWhite:         '#D6DCE6', // Crisp white stripes (RGB: 214, 220, 230)
    poloCollarTrim:    '#4E729A', // Darker blue seam stitch outline
    poloButton:        '#FFFFFF', // Placket button
    poloButtonHole:    '#7A9ABF', // Button center stitch
    waistNavy:         0x142448,  // Minifigure hips/pants dark navy blue
};
```

---

## 4. Phased Implementation Roadmap

### Phase 1: Overhaul Geometry & Proportions (`LegoGeometryFactory.js` & `LegoMinifigure.js`)
1. **Elevate Neck Pedestal**:
   - In `LegoMinifigure.js`, set head Y position to $Y = 2.18$ so that $0.12$ units of cylindrical neck cylinder are visible between the torso collar and the chin bevel.
2. **Organic Head Lathe Profile**:
   - In `LegoGeometryFactory.js`: Diameter $1.04$, Height $1.06$, Bevel Radius $0.10$.
   - Organic lower cheek bulge (+1.5% radius) tapering gently to temples.
3. **Sculpt Low-Profile Afro Helmet (Part 21778)**:
   - Cap geometry: Low cranial dome hugging cranium ($R = 0.535$, top height $0.68$).
   - Hairline arch: High parabolic arch ($Y = 0.38$ at center, curving to $Y = 0.08$ at sides) leaving $75\text{px}$ of open forehead.
   - Micro-pebbles: Replace large beads ($R=0.034$) with 1,200 fine bumps ($R=0.022$) in Fibonacci distribution, eliminating concentric ring artifacts.
4. **Torso Shoulder Bevel**:
   - Add $0.06$ fillet radius with 6 segments to eliminate knife-edge shoulders.

### Phase 2: Procedural Pad-Printed Face Overhaul (`ProceduralFacePainter.js`)
1. **Almond Eyes with Dual Studio Catchlights**:
   - Espresso-to-brown radial gradient iris (`#1A0F09` to `#3D1E0F`) with centered black pupil.
   - **Double Studio Catchlight at 1:30**:
     - Major Catchlight: Pure white circle, radius $14\text{px}$ at $(X+16, Y-14)$.
     - Minor Catchlight: $65\%$ opacity white dot, radius $6\text{px}$ at $(X+26, Y+12)$.
   - Upper eyelid fold crease ($24\text{px}$ above lash line) and lower lid crease.
2. **Tapered Arched Eyebrows**:
   - Espresso-black with soft feathered upper edge at $Y=410$, angled confident and friendly.
3. **Soft Volumetric Nose**:
   - Curved radial gradient nostril crescents and warm tip highlight ($X=525, Y=316$).
4. **Mustache & Philtrum**:
   - Trimmed mustache with **$18\text{px}$ center philtrum gap** and feathered hair edges.
5. **Terracotta Lips & Stippled Goatee**:
   - Upper lip (`#8D4A32`) with Cupid's bow; Lower lip (`#B3644E`) with gloss highlight.
   - Goatee at $Y=810$ with dense micro-stipple pebble noise.
6. **Dynamic Visemes**:
   - Preston Blair 9-viseme set deforming the mouth opening cleanly without distorting mustache or chin.

### Phase 3: Procedural Polo & Sleeve Painter (`ProceduralTorsoPainter.js`)
1. **Crisp 6-Band Horizontal Stripes**:
   - Alternate Sky-Blue (`#96B4D6`) and White (`#D6DCE6`) across torso and sleeves.
2. **Polo Collar & Placket**:
   - Folded sky-blue collar flaps with dark-blue stitch trim (`#4E729A`).
   - Rectangular placket through Stripe 1 with circular button.

### Phase 4: PBR ABS Materials & Studio Lighting (`LegoMaterialFactory.js`)
1. **Three.js `MeshPhysicalMaterial`**:
   - Clearcoat $0.42$, Roughness $0.24$, Clearcoat Roughness $0.14$.
2. **3-Point Studio Lighting**:
   - Key Light: Warm daylight directional from upper-right ($X=3.2, Y=5.0, Z=4.0$, intensity $2.0$).
   - Fill Light: Soft sky-blue directional from left ($X=-3.5, Y=2.5, Z=2.5$, intensity $0.85$).
   - Rim Light: Warm directional from rear ($X=0.5, Y=4.0, Z=-3.5$, intensity $1.3$).

---

## 5. Verification Gate & Acceptance Criteria

1. **Automated Test Suites**:
   ```bash
   node tests/test_facial_animation.test.js
   node tests/test_lego_geometry.test.js
   node tests/test_lego_materials.test.js
   node tests/test_procedural_textures.test.js
   ```
2. **Visual Verification Render**:
   - Generate high-resolution 4-column gate comparison render:
     - Col 1: Ground Truth Concept Art (`brick_dev_perfect_cutout.png`).
     - Col 2: Procedural 3D Front View.
     - Col 3: Procedural 3D 45° Perspective View.
     - Col 4: Close-up Head & Expression View.
3. **Rigorous Self-Review Checklist (using `view_file`)**:
   - [ ] Head is properly elevated; $65\text{px}$ neck pedestal is clearly visible above collar.
   - [ ] Hair is low-profile cranial helmet; forehead is open; no concentric cornrow rings.
   - [ ] Eyes have authentic almond shape, eyelid fold, and signature dual catchlights at 1:30.
   - [ ] Mustache has clean $18\text{px}$ philtrum gap in center.
   - [ ] Lips are warm terracotta with Cupid's bow and lower lip gloss.
   - [ ] Goatee has dense curly pebble texture.
   - [ ] Polo shirt has rounded shoulder caps and crisp 6-band sky-blue/white stripes.
   - [ ] ZERO photo overlaying, zero decal projection.
4. **Live Inspector Sync**:
   - Updated live on `http://localhost:3000` with real-time gaze tracking and emotion sliders.
