from __future__ import annotations
import base64
import json
from pathlib import Path


def generate_html_inspector(bundle_dir: Path, output_file: Path) -> Path:
    """Builds a standalone interactive HTML5 rig inspector for live browser inspection."""
    bundle_dir = Path(bundle_dir)
    manifest_path = bundle_dir / "manifest.json"
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest_data = json.load(f)

    # Encode all image assets into base64 for zero-CORS single-file viewing
    asset_base64: dict[str, str] = {}
    for slot_name, slot_cfg in manifest_data.get("slots", {}).items():
        for att_name, rel_path in slot_cfg.get("attachments", {}).items():
            if not rel_path:
                continue
            img_path = bundle_dir / rel_path
            if img_path.is_file():
                ext = img_path.suffix.lower().replace(".", "")
                if ext == "jpg":
                    ext = "jpeg"
                with open(img_path, "rb") as img_f:
                    b64 = base64.b64encode(img_f.read()).decode("utf-8")
                    asset_base64[rel_path] = f"data:image/{ext};base64,{b64}"

    manifest_json_str = json.dumps(manifest_data)
    assets_json_str = json.dumps(asset_base64)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>VideoMascot - Live Rig Inspector</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #0f172a;
            color: #f8fafc;
            display: flex;
            height: 100vh;
            overflow: hidden;
        }}
        #viewport-container {{
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            position: relative;
            background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
        }}
        #mascotCanvas {{
            background: #1e293b;
            border-radius: 16px;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.1);
            cursor: crosshair;
        }}
        #sidebar {{
            width: 380px;
            background: #1e293b;
            border-left: 1px solid #334155;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }}
        .header {{
            padding: 20px;
            border-bottom: 1px solid #334155;
            background: #0f172a;
        }}
        .header h1 {{ font-size: 18px; font-weight: 700; color: #38bdf8; }}
        .header p {{ font-size: 12px; color: #94a3b8; margin-top: 4px; }}
        .section {{
            padding: 16px 20px;
            border-bottom: 1px solid #334155;
        }}
        .section-title {{
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        .control-group {{
            margin-bottom: 12px;
        }}
        .control-label {{
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #cbd5e1;
            margin-bottom: 4px;
        }}
        .control-label span.val {{ color: #38bdf8; font-weight: 600; }}
        input[type="range"] {{
            width: 100%;
            accent-color: #38bdf8;
        }}
        .btn-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
        }}
        .btn {{
            background: #334155;
            color: #f8fafc;
            border: 1px solid #475569;
            padding: 8px 10px;
            border-radius: 8px;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.15s ease;
            text-align: center;
        }}
        .btn:hover {{ background: #475569; border-color: #38bdf8; color: #38bdf8; }}
        .btn.active {{ background: #0284c7; border-color: #38bdf8; color: #fff; }}
        .btn-primary {{
            background: #2563eb;
            border-color: #3b82f6;
            color: white;
            padding: 10px 14px;
            font-size: 13px;
        }}
        .btn-primary:hover {{ background: #1d4ed8; color: white; }}
        .toggle-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
            font-size: 13px;
            color: #e2e8f0;
        }}
        .badge {{
            font-size: 10px;
            background: #0284c7;
            padding: 2px 6px;
            border-radius: 4px;
            font-weight: 700;
        }}
        #badge-status {{
            position: absolute;
            top: 20px;
            left: 20px;
            background: rgba(15, 23, 42, 0.8);
            backdrop-filter: blur(8px);
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 12px;
            color: #94a3b8;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
    </style>
</head>
<body>

    <div id="viewport-container">
        <div id="badge-status">🎮 Live Rig: <span style="color:#38bdf8;" id="char-name">Chibi Tech Guide</span> • Target Gaze & Pointer</div>
        <canvas id="mascotCanvas" width="600" height="600"></canvas>
    </div>

    <div id="sidebar">
        <div class="header">
            <h1>VideoMascot Inspector</h1>
            <p>2.5D Layered Puppet & Kinematic Rig Tool</p>
        </div>

        <!-- Quick Poses -->
        <div class="section">
            <div class="section-title">Character Poses & Actions</div>
            <div class="btn-grid" style="grid-template-columns: repeat(2, 1fr);">
                <button class="btn" onclick="applyPose('point_up_right')">👉 Point Up-Right</button>
                <button class="btn" onclick="applyPose('point_up_left')">👈 Point Up-Left</button>
                <button class="btn" onclick="applyPose('happy_wave')">👋 Wave Hello</button>
                <button class="btn" onclick="applyPose('thumbs_up')">👍 Thumbs Up</button>
                <button class="btn" onclick="applyPose('thinking')">🤔 Thinking</button>
                <button class="btn" onclick="applyPose('surprised')">😲 Surprised</button>
                <button class="btn" onclick="applyPose('rest')">🧘 Neutral Rest</button>
            </div>
        </div>

        <!-- Emotional Expressions -->
        <div class="section">
            <div class="section-title">Facial Expressions <span class="badge">Mood</span></div>
            <div class="btn-grid">
                <button class="btn active" id="e-smile" onclick="setEmotion('smile')">😊 Smile</button>
                <button class="btn" id="e-open_smile" onclick="setEmotion('open_smile')">😃 Open Smile</button>
                <button class="btn" id="e-happy_eyes" onclick="setEmotion('happy_eyes')">✨ Happy ^^</button>
            </div>
        </div>

        <!-- Viseme Pad -->
        <div class="section">
            <div class="section-title">Speech Visemes (9-Set) <span class="badge">Lip-Sync</span></div>
            <div class="btn-grid">
                <button class="btn" id="v-smile" onclick="setViseme('smile')">/smile/</button>
                <button class="btn" id="v-A_I" onclick="setViseme('A_I')">/A_I/</button>
                <button class="btn" id="v-E" onclick="setViseme('E')">/E/</button>
                <button class="btn" id="v-O" onclick="setViseme('O')">/O/</button>
                <button class="btn" id="v-U" onclick="setViseme('U')">/U/</button>
                <button class="btn" id="v-M_B_P" onclick="setViseme('M_B_P')">/M_B_P/</button>
                <button class="btn" id="v-F_V" onclick="setViseme('F_V')">/F_V/</button>
                <button class="btn" id="v-L_D_T_N" onclick="setViseme('L_D_T_N')">/L_D_T_N/</button>
                <button class="btn" id="v-W_Q" onclick="setViseme('W_Q')">/W_Q/</button>
            </div>
            <button class="btn btn-primary" style="width:100%; margin-top:10px;" onclick="toggleSpeechSim()">
                <span id="speech-btn-label">▶ Play Lip-Sync Audio Simulation</span>
            </button>
        </div>

        <!-- Procedural & Overlays -->
        <div class="section">
            <div class="section-title">Procedural Physics & FX</div>
            <div class="toggle-row">
                <span>Dynamic Mouse Gaze Tracking</span>
                <input type="checkbox" id="chk-gaze" checked>
            </div>
            <div class="toggle-row">
                <span>Breathing / Subtle Bob</span>
                <input type="checkbox" id="chk-breathe" checked>
            </div>
            <div class="toggle-row">
                <span>Auto-Blink Cycle</span>
                <input type="checkbox" id="chk-blink" checked>
            </div>
            <div class="toggle-row">
                <span>Show Bone Skeleton</span>
                <input type="checkbox" id="chk-skeleton" onchange="render()">
            </div>
        </div>

        <!-- Kinematic Sliders -->
        <div class="section">
            <div class="section-title">Joint Kinematics</div>
            <div class="control-group">
                <div class="control-label"><span>Head Tilt</span><span class="val" id="val-head">0°</span></div>
                <input type="range" id="sld-head" min="-45" max="45" value="0" oninput="onSliderChange()">
            </div>
            <div class="control-group">
                <div class="control-label"><span>Right Shoulder (Aim)</span><span class="val" id="val-r-sh">0°</span></div>
                <input type="range" id="sld-r-sh" min="-180" max="180" value="0" oninput="onSliderChange()">
            </div>
            <div class="control-group">
                <div class="control-label"><span>Right Elbow</span><span class="val" id="val-r-el">0°</span></div>
                <input type="range" id="sld-r-el" min="-150" max="150" value="0" oninput="onSliderChange()">
            </div>
            <div class="control-group">
                <div class="control-label"><span>Left Shoulder (Wave)</span><span class="val" id="val-l-sh">0°</span></div>
                <input type="range" id="sld-l-sh" min="-180" max="180" value="0" oninput="onSliderChange()">
            </div>
            <div class="control-group">
                <div class="control-label"><span>Left Elbow</span><span class="val" id="val-l-el">0°</span></div>
                <input type="range" id="sld-l-el" min="-150" max="150" value="0" oninput="onSliderChange()">
            </div>
        </div>
    </div>

    <script>
        const MANIFEST = {manifest_json_str};
        const ASSETS = {assets_json_str};

        // Preload images
        const loadedImages = {{}};
        for (const [relPath, b64] of Object.entries(ASSETS)) {{
            const img = new Image();
            img.src = b64;
            loadedImages[relPath] = img;
        }}

        // Runtime Rig State
        const state = {{
            joints: {{
                head: 0,
                arm_l_upper: 0,
                arm_l_lower: 0,
                arm_r_upper: 0,
                arm_r_lower: 0,
                torso: 0
            }},
            attachments: {{
                hand_l: "rest",
                hand_r: "rest",
                eye_l_sclera: "default",
                eye_r_sclera: "default",
                prop_r: "none"
            }},
            viseme: "smile",
            gaze: {{ x: 0, y: 0 }},
            blink: 0,
            simulatingSpeech: false,
            time: 0
        }};

        const canvas = document.getElementById("mascotCanvas");
        const ctx = canvas.getContext("2d");

        // Gaze tracking listener
        canvas.addEventListener("mousemove", (e) => {{
            if (!document.getElementById("chk-gaze").checked) return;
            const rect = canvas.getBoundingClientRect();
            const mouseX = ((e.clientX - rect.left) / rect.width) * 800;
            const mouseY = ((e.clientY - rect.top) / rect.height) * 800;
            state.gaze.x = Math.max(-10, Math.min(10, (mouseX - 400) * 0.04));
            state.gaze.y = Math.max(-8, Math.min(8, (mouseY - 350) * 0.04));
        }});

        function setViseme(v) {{
            state.viseme = v;
            document.querySelectorAll('.section .btn').forEach(b => {{
                if (b.id && b.id.startsWith('v-')) b.classList.remove('active');
            }});
            const btn = document.getElementById('v-' + v);
            if (btn) btn.classList.add('active');
        }}

        function setEmotion(em) {{
            document.querySelectorAll('.section .btn').forEach(b => {{
                if (b.id && b.id.startsWith('e-')) b.classList.remove('active');
            }});
            const btn = document.getElementById('e-' + em);
            if (btn) btn.classList.add('active');

            if (em === "smile") {{
                state.viseme = "smile";
                state.attachments.eye_l_sclera = "default";
                state.attachments.eye_r_sclera = "default";
            }} else if (em === "open_smile") {{
                state.viseme = "open_smile";
                state.attachments.eye_l_sclera = "default";
                state.attachments.eye_r_sclera = "default";
            }} else if (em === "happy_eyes") {{
                state.viseme = "open_smile";
                state.attachments.eye_l_sclera = "happy";
                state.attachments.eye_r_sclera = "happy";
            }}
        }}

        function applyPose(name) {{
            // Reset to defaults
            state.joints = {{ head: 0, arm_l_upper: 0, arm_l_lower: 0, arm_r_upper: 0, arm_r_lower: 0, torso: 0 }};
            state.attachments = {{ hand_l: "rest", hand_r: "rest", eye_l_sclera: "default", eye_r_sclera: "default", prop_r: "none" }};
            state.viseme = "smile";

            if (name === "point_up_right") {{
                state.joints.torso = -3;
                state.joints.head = 6;
                // Right arm raises up-right towards target
                state.joints.arm_r_upper = -135;
                state.joints.arm_r_lower = 15;
                state.attachments.hand_r = "point";
                state.attachments.prop_r = "pointer_stick";
                // Left arm on hip
                state.joints.arm_l_upper = 25;
                state.joints.arm_l_lower = -30;
                state.viseme = "smile";
            }} else if (name === "point_up_left") {{
                state.joints.torso = 3;
                state.joints.head = -6;
                // Left arm raises up-left towards target
                state.joints.arm_l_upper = 135;
                state.joints.arm_l_lower = -15;
                state.attachments.hand_l = "point";
                // Right arm on hip
                state.joints.arm_r_upper = -25;
                state.joints.arm_r_lower = 30;
                state.viseme = "smile";
            }} else if (name === "happy_wave") {{
                state.joints.head = 8;
                // Left arm raises high outside the body (+125 deg)
                state.joints.arm_l_upper = 125;
                state.joints.arm_l_lower = 25;
                state.attachments.hand_l = "wave";
                state.attachments.eye_l_sclera = "happy";
                state.attachments.eye_r_sclera = "happy";
                state.viseme = "open_smile";
            }} else if (name === "thumbs_up") {{
                state.joints.head = -4;
                state.joints.arm_r_upper = -50;
                state.joints.arm_r_lower = -55;
                state.attachments.hand_r = "thumbs_up";
                state.viseme = "open_smile";
            }} else if (name === "thinking") {{
                state.joints.head = 12;
                state.joints.arm_r_upper = -115;
                state.joints.arm_r_lower = -90;
                state.attachments.hand_r = "rest";
                state.viseme = "smile";
            }} else if (name === "surprised") {{
                state.joints.head = 0;
                state.joints.arm_l_upper = 70;
                state.joints.arm_l_lower = 40;
                state.joints.arm_r_upper = -70;
                state.joints.arm_r_lower = -40;
                state.attachments.hand_l = "wave";
                state.attachments.hand_r = "wave";
                state.viseme = "O";
            }} else if (name === "rest") {{
                state.viseme = "smile";
            }}
            syncSliders();
        }}

        function syncSliders() {{
            document.getElementById("sld-head").value = state.joints.head;
            document.getElementById("val-head").innerText = state.joints.head + "°";
            document.getElementById("sld-r-sh").value = state.joints.arm_r_upper;
            document.getElementById("val-r-sh").innerText = state.joints.arm_r_upper + "°";
            document.getElementById("sld-r-el").value = state.joints.arm_r_lower;
            document.getElementById("val-r-el").innerText = state.joints.arm_r_lower + "°";
            document.getElementById("sld-l-sh").value = state.joints.arm_l_upper;
            document.getElementById("val-l-sh").innerText = state.joints.arm_l_upper + "°";
            document.getElementById("sld-l-el").value = state.joints.arm_l_lower;
            document.getElementById("val-l-el").innerText = state.joints.arm_l_lower + "°";
        }}

        function onSliderChange() {{
            state.joints.head = parseFloat(document.getElementById("sld-head").value);
            state.joints.arm_r_upper = parseFloat(document.getElementById("sld-r-sh").value);
            state.joints.arm_r_lower = parseFloat(document.getElementById("sld-r-el").value);
            state.joints.arm_l_upper = parseFloat(document.getElementById("sld-l-sh").value);
            state.joints.arm_l_lower = parseFloat(document.getElementById("sld-l-el").value);
            syncSliders();
        }}

        let speechTimer = null;
        function toggleSpeechSim() {{
            state.simulatingSpeech = !state.simulatingSpeech;
            const btn = document.getElementById("speech-btn-label");
            if (state.simulatingSpeech) {{
                btn.innerText = "⏹ Stop Simulation";
                const phonemes = ["smile", "A_I", "E", "O", "M_B_P", "L_D_T_N", "F_V", "open_smile", "W_Q", "smile"];
                let pIdx = 0;
                speechTimer = setInterval(() => {{
                    setViseme(phonemes[pIdx % phonemes.length]);
                    pIdx++;
                }}, 130);
            }} else {{
                btn.innerText = "▶ Play Lip-Sync Audio Simulation";
                clearInterval(speechTimer);
                setViseme("smile");
            }}
        }}

        // 2D Matrix Transforms
        function computeTransforms() {{
            const transforms = {{}};

            function solveBone(boneName) {{
                if (transforms[boneName]) return transforms[boneName];
                const cfg = MANIFEST.bones[boneName];
                let parentMat = [1, 0, 0, 1, 0, 0]; // Identity
                if (cfg.parent) {{
                    parentMat = solveBone(cfg.parent);
                }}

                const pos = cfg.position;
                const rotDeg = (cfg.rotation_deg || 0) + (state.joints[boneName] || 0);
                const rotRad = (rotDeg * Math.PI) / 180;
                const pivot = cfg.pivot || [0, 0];

                let extraY = 0;
                if (boneName === "torso" && document.getElementById("chk-breathe").checked) {{
                    extraY = Math.sin(state.time * 2.5) * 3;
                }}

                const c = Math.cos(rotRad);
                const s = Math.sin(rotRad);
                
                const a = c;
                const b = s;
                const d = -s;
                const e = c;
                const tx = pos[0] + pivot[0] - (c * pivot[0] - s * pivot[1]);
                const ty = pos[1] + extraY + pivot[1] - (s * pivot[0] + c * pivot[1]);

                const pa = parentMat[0], pb = parentMat[1], pd = parentMat[2], pe = parentMat[3], ptx = parentMat[4], pty = parentMat[5];
                const outA = pa * a + pd * b;
                const outB = pb * a + pe * b;
                const outD = pa * d + pd * e;
                const outE = pb * d + pe * e;
                const outTx = pa * tx + pd * ty + ptx;
                const outTy = pb * tx + pe * ty + pty;

                transforms[boneName] = [outA, outB, outD, outE, outTx, outTy];
                return transforms[boneName];
            }}

            for (const bName of Object.keys(MANIFEST.bones)) {{
                solveBone(bName);
            }}
            return transforms;
        }}

        // Main Animation & Render Loop (60fps)
        function loop() {{
            state.time += 0.016;

            if (document.getElementById("chk-blink").checked) {{
                const blinkCycle = state.time % 3.5;
                if (blinkCycle > 3.35) {{
                    state.blink = 1;
                }} else {{
                    state.blink = 0;
                }}
            }}

            render();
            requestAnimationFrame(loop);
        }}

        function render() {{
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const scale = canvas.width / MANIFEST.canvas_size[0];

            ctx.save();
            ctx.scale(scale, scale);

            const boneTransforms = computeTransforms();

            const slotList = [];
            for (const [slotName, slotCfg] of Object.entries(MANIFEST.slots)) {{
                const bone = MANIFEST.bones[slotCfg.bone];
                const z = (bone.z_index || 0) * 1000 + (slotCfg.z_index || 0);
                slotList.push({{ name: slotName, cfg: slotCfg, z: z }});
            }}
            slotList.sort((a, b) => a.z - b.z);

            for (const slot of slotList) {{
                const sName = slot.name;
                const cfg = slot.cfg;
                const mat = boneTransforms[cfg.bone];

                let attKey = cfg.default_attachment || "default";
                if (sName === MANIFEST.viseme_slot) {{
                    attKey = MANIFEST.visemes[state.viseme] || state.viseme || "smile";
                }} else if (state.attachments[sName]) {{
                    attKey = state.attachments[sName];
                }}

                if ((sName === "eye_l_sclera" || sName === "eye_r_sclera") && state.blink === 1) {{
                    attKey = "blink";
                }}

                const relPath = cfg.attachments[attKey];
                if (!relPath || !loadedImages[relPath]) continue;

                const img = loadedImages[relPath];

                ctx.save();
                ctx.transform(mat[0], mat[1], mat[2], mat[3], mat[4], mat[5]);

                let px = 0, py = 0;
                if (sName.includes("pupil")) {{
                    px = state.gaze.x;
                    py = state.gaze.y;
                }}

                ctx.drawImage(img, cfg.offset[0] + px, cfg.offset[1] + py);
                ctx.restore();
            }}

            // Draw skeleton gizmos if enabled
            if (document.getElementById("chk-skeleton").checked) {{
                ctx.lineWidth = 4;
                ctx.strokeStyle = "#38bdf8";
                ctx.fillStyle = "#f43f5e";

                for (const [bName, cfg] of Object.entries(MANIFEST.bones)) {{
                    const mat = boneTransforms[bName];
                    const x = mat[4];
                    const y = mat[5];

                    if (cfg.parent) {{
                        const pMat = boneTransforms[cfg.parent];
                        ctx.beginPath();
                        ctx.moveTo(pMat[4], pMat[5]);
                        ctx.lineTo(x, y);
                        ctx.stroke();
                    }}

                    ctx.beginPath();
                    ctx.arc(x, y, 6, 0, Math.PI * 2);
                    ctx.fill();
                }}
            }}

            ctx.restore();
        }}

        loop();
    </script>
</body>
</html>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_file
