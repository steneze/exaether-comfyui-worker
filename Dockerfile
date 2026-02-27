FROM runpod/worker-comfyui:5.2.0-base

# ============================================================================
# ExAether ComfyUI Worker — RunPod Serverless
# Essential custom nodes for ArchIA workflows (inpainting, generation)
# Base image provides: ComfyUI at /comfyui, Python 3.11, CUDA, PyTorch
# Models are on RunPod Network Volume (mounted at /runpod-volume)
# ============================================================================

# Update core ComfyUI to latest (for comfy_extras: CFGNorm, nodes_qwen, etc.)
RUN cd /comfyui && git pull --ff-only || git fetch --all && git reset --hard origin/master

WORKDIR /comfyui/custom_nodes

# ----------------------------------------------------------------------------
# 1. Essential nodes for Flux Fill inpainting workflow
#    - ComfyUI_experiments: CLIPTextEncodeFlux, DifferentialDiffusion, FluxGuidance
#    - comfyui_essentials: MaskBlur+, ImageScaleToTotalPixels
#    - comfyui-impact-pack: LoadImageOptional
# ----------------------------------------------------------------------------
RUN git clone --depth 1 https://github.com/comfyanonymous/ComfyUI_experiments && \
    git clone --depth 1 https://github.com/cubiq/ComfyUI_essentials comfyui_essentials && \
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Pack comfyui-impact-pack && \
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Subpack comfyui-impact-subpack

# ----------------------------------------------------------------------------
# 2. Common utility nodes (useful for future workflows)
# ----------------------------------------------------------------------------
RUN git clone --depth 1 https://github.com/city96/ComfyUI-GGUF && \
    git clone --depth 1 https://github.com/cubiq/ComfyUI_IPAdapter_plus comfyui_ipadapter_plus && \
    git clone --depth 1 https://github.com/Fannovel16/comfyui_controlnet_aux && \
    git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes comfyui-kjnodes && \
    git clone --depth 1 https://github.com/yolain/ComfyUI-Easy-Use comfyui-easy-use

# ----------------------------------------------------------------------------
# 3. Install pip requirements for nodes that have them
# ----------------------------------------------------------------------------
RUN for dir in /comfyui/custom_nodes/*/; do \
        if [ -f "$dir/requirements.txt" ]; then \
            echo "Installing requirements for $(basename $dir)..." && \
            pip install --no-cache-dir -r "$dir/requirements.txt" || \
            echo "WARNING: Failed to install requirements for $(basename $dir)"; \
        fi; \
    done

# Impact Pack needs a special install step
RUN cd /comfyui/custom_nodes/comfyui-impact-pack && \
    python install.py || echo "WARNING: Impact Pack install.py failed (may need models at runtime)"

# ----------------------------------------------------------------------------
# 4. Custom _STT_* nodes (ExAether proprietary)
# ----------------------------------------------------------------------------
COPY custom_nodes/_STT_QWEN /comfyui/custom_nodes/_STT_QWEN
COPY custom_nodes/_STT_UTILS /comfyui/custom_nodes/_STT_UTILS
COPY custom_nodes/_STT_scene_selector /comfyui/custom_nodes/_STT_scene_selector
COPY custom_nodes/_STT_wardrobe_selector /comfyui/custom_nodes/_STT_wardrobe_selector

# ----------------------------------------------------------------------------
# 5. Extra model paths — replace with our own that includes diffusion_models
# ----------------------------------------------------------------------------
COPY extra_model_paths.yaml /comfyui/extra_model_paths.yaml

# Also create a startup script that symlinks diffusion_models into the
# ComfyUI models dir at runtime (when the volume is mounted)
RUN echo '#!/bin/bash' > /comfyui/link_models.sh && \
    echo 'if [ -d "/runpod-volume/models/diffusion_models" ]; then' >> /comfyui/link_models.sh && \
    echo '  ln -sfn /runpod-volume/models/diffusion_models /comfyui/models/diffusion_models' >> /comfyui/link_models.sh && \
    echo '  echo "Linked diffusion_models from network volume"' >> /comfyui/link_models.sh && \
    echo 'fi' >> /comfyui/link_models.sh && \
    chmod +x /comfyui/link_models.sh

WORKDIR /comfyui
