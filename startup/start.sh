#!/bin/bash
# ============================================================
# Vast.ai Startup Script
# ComfyUI + JupyterLab + Загрузчик пресетов
# ============================================================

set -e

WORKSPACE=${WORKSPACE:-/workspace}
COMFYUI_DIR="${WORKSPACE}/ComfyUI"
SERVICES_DIR="${WORKSPACE}/services"
VENV="${WORKSPACE}/venv"
NODES_RAW="https://raw.githubusercontent.com/lehych-sol/Start-Command/refs/heads/main/all-in-one"
SERVICES_REPO="https://github.com/lehych-sol/comfy-services"  # <-- замени на свой репо

# ─────────────── ЦВЕТА ───────────────
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[STARTUP]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# ─────────────── VENV ───────────────
log "Активируем venv..."
if [[ -f "${VENV}/bin/activate" ]]; then
    source "${VENV}/bin/activate"
else
    log "Создаём venv..."
    python3 -m venv "${VENV}"
    source "${VENV}/bin/activate"
fi

# ─────────────── APT ───────────────
log "Устанавливаем системные пакеты..."
apt-get update -qq
apt-get install -y -qq git git-lfs

# ─────────────── PIP ЗАВИСИМОСТИ ───────────────
log "Устанавливаем pip зависимости для сервисов..."
pip install -q fastapi uvicorn requests huggingface_hub aiofiles python-multipart

# ─────────────── COMFYUI ───────────────
log "Проверяем ComfyUI..."
if [[ ! -d "${COMFYUI_DIR}" ]]; then
    log "Клонируем ComfyUI..."
    git clone https://github.com/comfyanonymous/ComfyUI.git "${COMFYUI_DIR}"
fi
cd "${COMFYUI_DIR}"
git pull --ff-only 2>/dev/null || true
pip install -q -r requirements.txt

# ─────────────── НОДЫ ───────────────
log "Загружаем и устанавливаем ноды с GitHub..."
NODES_SCRIPT=$(curl -fsSL "${NODES_RAW}")

# Извлекаем массив NODES из raw файла и клонируем
mkdir -p "${COMFYUI_DIR}/custom_nodes"
cd "${COMFYUI_DIR}/custom_nodes"

NODES=(
    "https://github.com/ltdrdata/ComfyUI-Manager"
    "https://github.com/kijai/ComfyUI-WanVideoWrapper"
    "https://github.com/ltdrdata/ComfyUI-Impact-Pack"
    "https://github.com/pythongosssss/ComfyUI-Custom-Scripts"
    "https://github.com/chflame163/ComfyUI_LayerStyle"
    "https://github.com/lehych-sol/geek-nodes"
    "https://github.com/lehych-sol/custom-nodes"
    "https://github.com/thatboymentor/ofmtechclip"
    "https://github.com/rgthree/rgthree-comfy"
    "https://github.com/yolain/ComfyUI-Easy-Use"
    "https://github.com/teskor-hub/comfyui-teskors-utils"
    "https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler"
    "https://github.com/cubiq/ComfyUI_essentials"
    "https://github.com/ClownsharkBatwing/RES4LYF"
    "https://github.com/jnxmx/ComfyUI_HuggingFace_Downloader"
    "https://github.com/chrisgoringe/cg-use-everywhere"
    "https://github.com/ltdrdata/ComfyUI-Impact-Subpack"
    "https://github.com/Smirnov75/ComfyUI-mxToolkit"
    "https://github.com/TheLustriVA/ComfyUI-Image-Size-Tools"
    "https://github.com/ZhiHui6/zhihui_nodes_comfyui"
    "https://github.com/kijai/ComfyUI-KJNodes"
    "https://github.com/crystian/ComfyUI-Crystools"
    "https://github.com/plugcrypt/CRT-Nodes"
    "https://github.com/EllangoK/ComfyUI-post-processing-nodes"
    "https://github.com/Fannovel16/comfyui_controlnet_aux"
    "https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite"
    "https://github.com/kijai/ComfyUI-WanAnimatePreprocess"
    "https://github.com/GACLove/ComfyUI-VFI"
)

for repo in "${NODES[@]}"; do
    dir="${repo##*/}"
    if [[ -d "./${dir}/.git" ]]; then
        (cd "./${dir}" && git pull --ff-only 2>/dev/null) || warn "Не удалось обновить ${dir}"
    else
        git clone "${repo}" "./${dir}" --recursive 2>/dev/null || warn "Не удалось клонировать ${dir}"
    fi
    if [[ -f "./${dir}/requirements.txt" ]]; then
        pip install -q -r "./${dir}/requirements.txt" || true
    fi
done
log "Ноды установлены!"

# ─────────────── СЕРВИСЫ ───────────────
log "Устанавливаем сервисы..."
if [[ ! -d "${SERVICES_DIR}" ]]; then
    git clone "${SERVICES_REPO}" "${SERVICES_DIR}" 2>/dev/null || {
        warn "Не удалось клонировать сервисы, копируем локально..."
        mkdir -p "${SERVICES_DIR}"
    }
else
    (cd "${SERVICES_DIR}" && git pull --ff-only 2>/dev/null) || true
fi

# ─────────────── JUPYTERLAB ───────────────
log "Устанавливаем JupyterLab..."
pip install -q jupyterlab

# ─────────────── ЗАПУСК СЕРВИСОВ ───────────────
log "Запускаем сервисы..."

# ComfyUI на порту 8188
log "Запуск ComfyUI (порт 8188)..."
cd "${COMFYUI_DIR}"
python main.py --listen 0.0.0.0 --port 8188 &
COMFYUI_PID=$!

# JupyterLab на порту 8888
log "Запуск JupyterLab (порт 8888)..."
jupyter lab \
    --allow-root \
    --no-browser \
    --port=8888 \
    --ip=0.0.0.0 \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --FileContentsManager.delete_to_trash=False \
    --notebook-dir="${WORKSPACE}" &
JUPYTER_PID=$!

# Загрузчик пресетов на порту 8081
log "Запуск загрузчика пресетов (порт 8081)..."
cd "${WORKSPACE}"
uvicorn services.preset_downloader:app --host 0.0.0.0 --port 8081 &
PRESET_PID=$!

log "✅ Все сервисы запущены!"
log "  ComfyUI:           http://localhost:8188"
log "  JupyterLab:        http://localhost:8888"
log "  Загрузчик моделей: http://localhost:8081"

# Ждём ComfyUI (основной процесс)
wait $COMFYUI_PID
