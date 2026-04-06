# ComfyUI Vast.ai Template

## Структура репозиториев

Нужно два GitHub репо:

### 1. `comfy-services` (этот репо)
Содержит папку `services/` с загрузчиком пресетов.

```
services/
├── __init__.py
├── preset_downloader.py   ← здесь заполняешь свои пресеты
└── static/
    └── script.js
```

### 2. `Start-Command` (уже есть)
Содержит raw файл с нодами — уже готов.

---

## Настройка Vast.ai Template

### Docker Image
```
vastai/comfy:v0.15.1-cuda-13.1-py312
```

### Открытые порты
| Порт  | Сервис               |
|-------|----------------------|
| 8188  | ComfyUI              |
| 8888  | JupyterLab           |
| 8081  | Загрузчик пресетов   |

### On-Start Script (вставить в поле "On-start script" при создании темплейта)
```bash
bash <(curl -fsSL https://raw.githubusercontent.com/lehych-sol/comfy-services/main/startup/start.sh)
```

---

## Добавление моделей в пресеты

Открой `services/preset_downloader.py` и найди `PRESET_FILES`.

Для каждого пресета добавь кортежи вида:
```python
("https://huggingface.co/username/repo/resolve/main/file.safetensors", "папка_назначения", None),
```

Папки назначения:
- `diffusion_models`
- `loras`
- `vae`
- `text_encoders`
- `checkpoints`
- `clip_vision`
- `upscale_models`
- `controlnet`

---

## Пресеты

| ID                     | Название               |
|------------------------|------------------------|
| WAN_ANIMATE_I2V        | Wan Animate I2V        |
| WAN_ANIMATE_V2V        | Wan Animate V2V        |
| WAN_ANIMATE_I2V_NSFW   | Wan Animate I2V NSFW   |
| ZIMAGE_TURBO_T2I_I2I   | Z-Image Turbo T2I/I2I  |
| ZIMAGE_SDXL_T2I_NSFW   | Z-Image SDXL T2I NSFW  |
| FLUX_SWAP_I2I          | Flux Swap I2I          |
