from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import threading
import uuid
import requests
 
app = FastAPI(title="Preset & Model Downloader")
 
download_status = {}
 
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
 
# ─────────────── КАТЕГОРИИ ───────────────
PRESET_CATEGORIES = {
    "Wan": {"name": "Wan", "icon": "🎬"},
    "ZImage": {"name": "Z-Image", "icon": "🖼️"},
}
 
# ─────────────── ПРЕСЕТЫ (описания) ───────────────
PRESETS = {
    "WAN_ANIMATE_I2V": {
        "name": "Wan Animate I2V",
        "description": "Анимация из изображения",
        "size": "~4 файла",
        "time": "10-20 мин",
        "category": "Wan",
        "video_guide": "",
    },
    "WAN_ANIMATE_V2V": {
        "name": "Wan Animate V2V",
        "description": "Анимация видео из видео",
        "size": "~16 файлов",
        "time": "20-40 мин",
        "category": "Wan",
        "video_guide": "",
    },
    "WAN_ANIMATE_I2V_NSFW": {
        "name": "Wan Animate I2V NSFW",
        "description": "Анимация из изображения (NSFW)",
        "size": "~18 файлов",
        "time": "20-40 мин",
        "category": "Wan",
        "video_guide": "",
    },
    "ZIMAGE_TURBO_T2I_I2I": {
        "name": "Z-Image Turbo T2I/I2I",
        "description": "Генерация и улучшение изображений",
        "size": "~7 файлов",
        "time": "10-15 мин",
        "category": "ZImage",
        "video_guide": "",
    },
    "ZIMAGE_SDXL_T2I_NSFW": {
        "name": "Z-Image SDXL T2I NSFW",
        "description": "Генерация изображений SDXL (NSFW)",
        "size": "~14 файлов",
        "time": "15-25 мин",
        "category": "ZImage",
        "video_guide": "",
    },
    "ZIMAGE_BODY_SWAP_I2I": {
        "name": "Z-image Swap I2I",
        "description": "Генерация изображений через SWAP",
        "size": "~3 файла",
        "time": "5-10 мин",
        "category": "ZImage",
        "video_guide": "",
    },
}
 
# ─────────────── ФАЙЛЫ ПРЕСЕТОВ (заполни сам) ───────────────
PRESET_FILES = {
    "WAN_ANIMATE_I2V": [
        ("https://huggingface.co/lehychh/Wan-animate-i2v/resolve/main/diffusion_models/High.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Wan-animate-i2v/resolve/main/diffusion_models/Low.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Wan-animate-i2v/resolve/main/text_encoders/umt5.safetensors", "text_encoders", None),
        ("https://huggingface.co/lehychh/Wan-animate-i2v/resolve/main/vae/variational_encoder_primary.safetensors", "vae", None),
    ],
    "WAN_ANIMATE_V2V": [
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/diffusion_models/Wan2_2-Animate-14B_fp8_scaled_e4m3fn_KJ_v2.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/vae/wan_2.1_vae.safetensors", "vae", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/clip/umt5_xxl_fp16.safetensors", "text_encoders", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/loras/wan2.2_i2v_lightx2v_4steps_lora_v1_high_noise.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/loras/lightx2v_I2V_14B_480p_cfg_step_distill_rank256_bf16.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/loras/Wan21_PusaV1_LoRA_14B_rank512_bf16.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/loras/Wan2.2-Fun-A14B-InP-low-noise-HPS2.1.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/loras/Wan2.2%20SolarFlint_L2.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/loras/BounceHighWan2_2.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/upscale_models/005_colorDN_DFWB_s128w8_SwinIR-M_noise15.pth", "upscale_models", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/upscale_models/low.pt", "upscale_models", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/detection/vitpose_h_wholebody_data.bin", "detection", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/detection/vitpose_h_wholebody_model.onnx", "detection", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/detection/yolov10m.onnx", "detection", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/controlnet/Wan21_Uni3C_controlnet_fp16.safetensors", "controlnet", None),
        ("https://huggingface.co/lehychh/Wan-animate-v2v/resolve/main/clip_vision/clip_vision_h.safetensors", "clip_vision", None),
    ],
    "WAN_ANIMATE_I2V_NSFW": [
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/diffusion_models/Wan2.2_Remix_NSFW_i2v_14b_high_lighting_fp16_v2.1.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/diffusion_models/Wan2.2_Remix_NSFW_i2v_14b_low_lighting_fp16_v2.1.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/vae/wan_2.1_vae.safetensors", "vae", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/text_encoders/nsfw_wan_umt5-xxl_fp8_scaled.safetensors", "text_encoders", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/SVI_v2_PRO_Wan2.2-I2V-A14B_HIGH_lora_rank_128_fp16.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/SVI_v2_PRO_Wan2.2-I2V-A14B_LOW_lora_rank_128_fp16.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Sensual_fingering_v1_high_noise.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Sensual_fingering_v1_low_noise.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Wan2.2%20-%20T2V%20-%20Dildo%20-%20HIGH%2014B.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Wan2.2%20-%20T2V%20-%20Dildo%20-%20LOW%2014B.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Wan2.2%20-%20T2V%20-%20Dildo%20Ride%20v2%20-%20HIGH%2014B.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Wan2.2%20-%20T2V%20-%20Dildo%20Ride%20v2%20-%20LOW%2014B.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Wan2.2%20-%20T2V%20-%20Jiggle%20Tits%20v2%20-%20HIGH%2014B.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/Wan2.2%20-%20T2V%20-%20Jiggle%20Tits%20v2%20-%20LOW%2014B.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/wan22-i2v-rub-pussy-os-high.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/wan22-i2v-rub-pussy-os-low.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/wan_fingering_pussy_i2v2.2hi_v10.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Wan-animate-I2V-18/resolve/main/loras/wan_fingering_pussy_i2v2.2lo_v10.safetensors", "loras", None),
    ],
    "ZIMAGE_TURBO_T2I_I2I": [
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/z-image-turbo.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/x_gen_weights.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/nice_girls_z-image.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/vae.safetensors", "vae", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/qwen.safetensors", "text_encoders", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/2x_PureVision.pth", "upscale_models", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/face_yolov8m.pt", "ultralytics/bbox", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/person_yolov8m-seg.pt", "ultralytics/segm", None),
    ],
    "ZIMAGE_SDXL_T2I_NSFW": [
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/z-image-turbo.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/lustifySDXLNSFW_V7.safetensors", "checkpoints", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/vae.safetensors", "vae", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/qwen.safetensors", "text_encoders", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/pussy_lily_v5_XL.safetensors", "loras", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/2x_PureVision.pth", "upscale_models", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/face_yolov8m.pt", "ultralytics/bbox", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/nipple.pt", "ultralytics/bbox", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/vagina-v4.2.pt", "ultralytics/bbox", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/Eyes.pt", "ultralytics/bbox", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/hand_yolov8s.pt", "ultralytics/bbox", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/assdetailer-seg.pt", "ultralytics/bbox", None),
        ("https://huggingface.co/lehychh/Z-image-Turbo/resolve/main/person_yolov8m-seg.pt", "ultralytics/segm", None),
    ],
    "ZIMAGE_BODY_SWAP_I2I": [
        ("https://huggingface.co/lehychh/Flux-swap-i2i/resolve/main/diffusion_models/flux4b.safetensors", "diffusion_models", None),
        ("https://huggingface.co/lehychh/Flux-swap-i2i/resolve/main/text_encoders/qwen.safetensors", "text_encoders", None),
        ("https://huggingface.co/lehychh/Flux-swap-i2i/resolve/main/vae/flux2-vae.safetensors", "vae", None),
    ],
}
 
# ─────────────── HTML ───────────────
INDEX_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Загрузчик пресетов и моделей</title>
  <style>
    :root { --bg:#0a0a0a; --text:#e8e8e8; --muted:#888; --accent:#fff; --card:#111; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: var(--bg); color: var(--text); font-family: system-ui, sans-serif; padding: 24px; }
    .wrap { max-width: 900px; margin: 0 auto; }
    .title { font-size: 28px; font-weight: 800; text-align: center; margin-bottom: 8px; }
    .subtitle { text-align: center; color: var(--muted); margin-bottom: 24px; }
    .card { background: var(--card); border: 1px solid #222; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
    .tabs { display: flex; gap: 8px; margin-bottom: 20px; justify-content: center; }
    .tab { padding: 8px 20px; background: #1a1a1a; border: 1px solid #333; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
    .tab.active { background: var(--accent); color: var(--bg); }
    .tab-content { display: none; }
    .tab-content.active { display: block; }
    .search-container { margin-bottom: 16px; }
    .search-input { width: 100%; padding: 10px 16px; background: #1a1a1a; border: 1px solid #333; color: var(--text); border-radius: 8px; font-size: 14px; }
    .category-filters { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
    .category-filter { padding: 6px 14px; background: #1a1a1a; border: 1px solid #333; border-radius: 8px; cursor: pointer; font-size: 13px; display: flex; align-items: center; gap: 4px; transition: all 0.2s; }
    .category-filter:hover { border-color: var(--accent); }
    .category-filter.active { background: var(--accent); color: var(--bg); border-color: var(--accent); }
    .preset-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; margin-bottom: 20px; }
    .preset-card { background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 8px; padding: 16px; cursor: pointer; transition: all 0.2s; position: relative; }
    .preset-card:hover { border-color: #555; }
    .preset-card.selected { border-color: var(--accent); background: #1e1e1e; }
    .preset-card.hidden { display: none; }
    .preset-name { font-weight: 700; margin-bottom: 6px; color: var(--accent); }
    .preset-desc { color: var(--muted); font-size: 13px; margin-bottom: 6px; }
    .preset-info { font-size: 12px; color: #555; }
    .btn { padding: 12px 24px; background: rgba(255,255,255,0.9); color: #000; font-weight: 700; border: none; border-radius: 8px; cursor: pointer; font-size: 14px; transition: all 0.2s; }
    .btn:hover { background: #fff; }
    .btn:disabled { opacity: 0.4; cursor: not-allowed; }
    .btn-hf { background: rgba(255,193,7,0.9); color: #000; }
    .btn-hf:hover { background: rgb(255,193,7); }
    .result { white-space: pre-wrap; background: #1a1a1a; border: 1px solid #2a2a2a; padding: 14px; border-radius: 8px; margin-top: 16px; min-height: 20px; font-size: 13px; }
    .progress { margin-top: 16px; }
    .progress-bar { width: 100%; height: 6px; background: #1a1a1a; border: 1px solid #2a2a2a; border-radius: 4px; overflow: hidden; }
    .progress-fill { height: 100%; background: var(--accent); width: 0%; transition: width 0.3s; }
    .progress-text { margin-top: 6px; color: var(--muted); font-size: 13px; text-align: center; }
    .row { margin-bottom: 14px; }
    label { display: block; margin-bottom: 6px; font-size: 13px; color: var(--muted); }
    input[type=text], input[type=password], select { width: 100%; padding: 10px 14px; background: #1a1a1a; border: 1px solid #333; color: var(--text); border-radius: 8px; font-size: 13px; }
  </style>
</head>
<body>
  <div class="wrap">
    <h1 class="title">Загрузчик пресетов и моделей</h1>
    <p class="subtitle">Скачивание пресетов и моделей с HuggingFace</p>
 
    <div class="tabs">
      <div class="tab active" onclick="switchTab('presets')">🎯 Пресеты</div>
      <div class="tab" onclick="switchTab('huggingface')">🤗 HuggingFace</div>
    </div>
 
    <!-- Пресеты -->
    <div class="card tab-content active" id="presets-tab">
      <h3 style="margin-bottom:16px;">Выберите пресеты для скачивания</h3>
      <div class="search-container">
        <input class="search-input" type="text" id="preset-search" placeholder="Поиск пресетов..." oninput="filterPresets()">
      </div>
      <div class="category-filters" id="category-filters">{{ category_filters_html }}</div>
      <div class="preset-grid" id="preset-grid">{{ presets_html }}</div>
      <button class="btn" onclick="downloadPresets()" id="download-presets-btn" disabled>📥 Скачать выбранные пресеты</button>
      <div class="result" id="preset-result"></div>
      <div class="progress" id="preset-progress" style="display:none;">
        <div class="progress-bar"><div class="progress-fill" id="preset-progress-fill"></div></div>
        <div class="progress-text" id="preset-progress-text">Загрузка...</div>
      </div>
    </div>
 
    <!-- HuggingFace -->
    <div class="card tab-content" id="huggingface-tab">
      <div class="tabs" style="margin-bottom:20px;">
        <div class="tab active" onclick="switchHFMethod('url')">🔗 Прямая ссылка</div>
        <div class="tab" onclick="switchHFMethod('repo')">🤗 HuggingFace Repo</div>
      </div>
      <form id="hf-url-form">
        <div class="row">
          <label>Прямая ссылка на файл</label>
          <input type="text" id="hf_url" placeholder="https://huggingface.co/.../file.safetensors">
        </div>
        <div class="row">
          <label>Папка назначения</label>
          <select id="hf_url_folder">
            <option value="diffusion_models">diffusion_models</option>
            <option value="loras">loras</option>
            <option value="vae">vae</option>
            <option value="text_encoders">text_encoders</option>
            <option value="checkpoints">checkpoints</option>
            <option value="clip_vision">clip_vision</option>
            <option value="upscale_models">upscale_models</option>
            <option value="controlnet">controlnet</option>
          </select>
        </div>
        <button class="btn btn-hf" type="submit">🔗 Скачать по ссылке</button>
      </form>
      <form id="hf-repo-form" style="display:none;">
        <div class="row">
          <label>Репозиторий</label>
          <input type="text" id="hf_repo" placeholder="username/model-name">
        </div>
        <div class="row">
          <label>Файл (опционально)</label>
          <input type="text" id="hf_file" placeholder="model.safetensors">
        </div>
        <div class="row">
          <label>API токен (опционально)</label>
          <input type="password" id="hf_token" placeholder="hf_...">
        </div>
        <div class="row">
          <label>Папка назначения</label>
          <select id="hf_folder">
            <option value="diffusion_models">diffusion_models</option>
            <option value="loras">loras</option>
            <option value="vae">vae</option>
            <option value="text_encoders">text_encoders</option>
            <option value="checkpoints">checkpoints</option>
            <option value="clip_vision">clip_vision</option>
            <option value="upscale_models">upscale_models</option>
            <option value="controlnet">controlnet</option>
          </select>
        </div>
        <button class="btn btn-hf" type="submit">🤗 Скачать с HuggingFace</button>
      </form>
      <div class="result" id="hf-result"></div>
      <div class="progress" id="hf-progress" style="display:none;">
        <div class="progress-bar"><div class="progress-fill" id="hf-progress-fill"></div></div>
        <div class="progress-text" id="hf-progress-text">Загрузка...</div>
      </div>
    </div>
  </div>
  <script src="/static/script.js"></script>
</body>
</html>"""
 
 
def generate_category_filters_html():
    html = '<div class="category-filter all active" onclick="filterByCategory(\'all\', event)">Все</div>'
    for cat_id, cat_info in PRESET_CATEGORIES.items():
        html += f'<div class="category-filter" onclick="filterByCategory(\'{cat_id}\', event)" data-category="{cat_id}"><span>{cat_info["icon"]}</span><span>{cat_info["name"]}</span></div>'
    return html
 
 
def generate_presets_html():
    html = ""
    for preset_id, preset_info in PRESETS.items():
        category = preset_info.get("category", "Wan")
        html += f'''
        <div class="preset-card" data-preset="{preset_id}" data-category="{category}" onclick="togglePreset('{preset_id}')">
          <div class="preset-name">{preset_info["name"]}</div>
          <div class="preset-desc">{preset_info["description"]}</div>
          <div class="preset-info">Размер: {preset_info["size"]} • Время: {preset_info["time"]}</div>
        </div>'''
    return html
 
 
@app.get("/", response_class=HTMLResponse)
def index():
    return HTMLResponse(
        INDEX_HTML
        .replace("{{ presets_html }}", generate_presets_html())
        .replace("{{ category_filters_html }}", generate_category_filters_html())
    )
 
 
@app.get("/health")
def health():
    return {"status": "ok"}
 
 
@app.get("/status/{task_id}")
def get_status(task_id: str):
    if task_id not in download_status:
        return {"status": "not_found", "message": "Задача не найдена"}
    return download_status[task_id]
 
 
@app.post("/download_presets")
def download_presets(presets: str = Form(...)):
    presets_list = [p.strip() for p in presets.split(",") if p.strip()]
    if not presets_list:
        return {"message": "❌ Не выбрано ни одного пресета"}
 
    task_id = str(uuid.uuid4())
 
    def run():
        try:
            all_files = []
            for pid in presets_list:
                if pid in PRESET_FILES:
                    all_files.extend(PRESET_FILES[pid])
 
            total = len(all_files)
            download_status[task_id] = {"status": "running", "message": f"🚀 Начато: {', '.join(presets_list)}\nФайлов: {total}", "progress": 0, "total_files": total, "current_file": 0}
 
            downloaded, skipped, failed = [], [], []
 
            for idx, (url, folder, custom_name) in enumerate(all_files, 1):
                dest = f"/workspace/ComfyUI/models/{folder}"
                os.makedirs(dest, exist_ok=True)
                filename = custom_name or url.split("/")[-1].split("?")[0]
                filepath = os.path.join(dest, filename)
 
                if os.path.isfile(filepath) and os.path.getsize(filepath) > 0:
                    skipped.append(filename)
                    download_status[task_id]["current_file"] = idx
                    download_status[task_id]["progress"] = idx / total * 100
                    download_status[task_id]["message"] = f"⏭️ Пропущено: {filename} ({idx}/{total})"
                    continue
 
                download_status[task_id]["message"] = f"📥 Скачивание {idx}/{total}: {filename}"
                try:
                    r = requests.get(url, stream=True, headers={"User-Agent": "Mozilla/5.0"}, timeout=600)
                    r.raise_for_status()
                    total_size = int(r.headers.get("content-length", 0))
                    dl = 0
                    with open(filepath, "wb") as f:
                        for chunk in r.iter_content(chunk_size=1024 * 1024):
                            if chunk:
                                f.write(chunk)
                                dl += len(chunk)
                                if total_size:
                                    pct = dl / total_size * 100
                                    overall = ((idx - 1) + pct / 100) / total * 100
                                    download_status[task_id]["progress"] = overall
                                    download_status[task_id]["message"] = f"📥 {filename} ({pct:.0f}%) [{idx}/{total}]"
                    downloaded.append(filename)
                except Exception as e:
                    if os.path.exists(filepath):
                        os.remove(filepath)
                    failed.append(filename)
 
            lines = [f"✅ Завершено: {', '.join(presets_list)}", ""]
            if downloaded:
                lines.append(f"📥 Скачано: {len(downloaded)}")
                lines += [f"  ✅ {f}" for f in downloaded]
            if skipped:
                lines.append(f"⏭️ Пропущено: {len(skipped)}")
                lines += [f"  ⏭️ {f}" for f in skipped]
            if failed:
                lines.append(f"❌ Ошибки: {len(failed)}")
                lines += [f"  ❌ {f}" for f in failed]
 
            download_status[task_id] = {
                "status": "error" if failed else "completed",
                "message": "\n".join(lines),
                "progress": 100,
                "total_files": total,
                "current_file": total,
            }
        except Exception as e:
            download_status[task_id] = {"status": "error", "message": f"❌ Ошибка: {e}", "progress": 0}
 
    download_status[task_id] = {"status": "running", "message": "🚀 Запускаем...", "progress": 0}
    threading.Thread(target=run, daemon=True).start()
    return {"message": f"🚀 Начато! ID: {task_id}", "task_id": task_id}
 
 
@app.post("/download_url")
def download_url_endpoint(url: str = Form(...), folder: str = Form("diffusion_models")):
    task_id = str(uuid.uuid4())
 
    def run():
        try:
            dest = f"/workspace/ComfyUI/models/{folder}"
            os.makedirs(dest, exist_ok=True)
            download_status[task_id] = {"status": "running", "message": "📥 Подключение...", "progress": 0}
            r = requests.get(url, stream=True, headers={"User-Agent": "Mozilla/5.0"}, timeout=600)
            r.raise_for_status()
            filename = url.split("/")[-1].split("?")[0]
            if "content-disposition" in r.headers:
                import re
                m = re.search(r'filename="?([^";\n]+)"?', r.headers["content-disposition"])
                if m:
                    filename = m.group(1).strip()
            filepath = os.path.join(dest, filename)
            total_size = int(r.headers.get("content-length", 0))
            dl = 0
            with open(filepath, "wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        dl += len(chunk)
                        if total_size:
                            pct = dl / total_size * 100
                            download_status[task_id] = {"status": "running", "message": f"📥 {filename} ({pct:.0f}%)", "progress": pct}
            size_mb = os.path.getsize(filepath) / 1024 / 1024
            download_status[task_id] = {"status": "completed", "message": f"✅ Скачано!\n📄 {filename}\n💾 {size_mb:.1f} MB\n📂 {dest}", "progress": 100}
        except Exception as e:
            download_status[task_id] = {"status": "error", "message": f"❌ Ошибка: {e}", "progress": 0}
 
    download_status[task_id] = {"status": "running", "message": "🚀 Запускаем...", "progress": 0}
    threading.Thread(target=run, daemon=True).start()
    return {"message": f"🚀 Начато! ID: {task_id}", "task_id": task_id}
 
 
@app.post("/download_hf")
def download_hf_endpoint(repo: str = Form(...), filename: str = Form(""), token: str = Form(""), folder: str = Form("diffusion_models")):
    task_id = str(uuid.uuid4())
 
    def run():
        try:
            dest = f"/workspace/ComfyUI/models/{folder}"
            os.makedirs(dest, exist_ok=True)
            headers = {"User-Agent": "Mozilla/5.0"}
            if token:
                headers["Authorization"] = f"Bearer {token}"
 
            if filename:
                url = f"https://huggingface.co/{repo}/resolve/main/{filename}"
                download_status[task_id] = {"status": "running", "message": "📥 Подключение к HuggingFace...", "progress": 0}
                r = requests.get(url, stream=True, headers=headers, timeout=600)
                r.raise_for_status()
                filepath = os.path.join(dest, filename)
                total_size = int(r.headers.get("content-length", 0))
                dl = 0
                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            f.write(chunk)
                            dl += len(chunk)
                            if total_size:
                                pct = dl / total_size * 100
                                download_status[task_id] = {"status": "running", "message": f"📥 {filename} ({pct:.0f}%)", "progress": pct}
                size_mb = os.path.getsize(filepath) / 1024 / 1024
                download_status[task_id] = {"status": "completed", "message": f"✅ Скачано!\n📄 {filename}\n💾 {size_mb:.1f} MB", "progress": 100}
            else:
                from huggingface_hub import snapshot_download, login as hf_login
                if token:
                    hf_login(token=token)
                download_status[task_id] = {"status": "running", "message": f"📥 Скачивание репозитория {repo}...", "progress": 0}
                snapshot_download(repo_id=repo, local_dir=dest, local_dir_use_symlinks=False)
                download_status[task_id] = {"status": "completed", "message": f"✅ Репозиторий {repo} скачан!\n📂 {dest}", "progress": 100}
        except Exception as e:
            download_status[task_id] = {"status": "error", "message": f"❌ Ошибка: {e}", "progress": 0}
 
    download_status[task_id] = {"status": "running", "message": "🚀 Запускаем...", "progress": 0}
    threading.Thread(target=run, daemon=True).start()
    return {"message": f"🚀 Начато! ID: {task_id}", "task_id": task_id}
