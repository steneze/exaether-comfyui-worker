FROM runpod/worker-comfyui:5.2.0-base

# ============================================================================
# ExAether ComfyUI Worker — RunPod Serverless
# All custom nodes for ArchIA workflows (inpainting, generation, etc.)
# Base image provides: ComfyUI at /comfyui, Python 3.11, CUDA, PyTorch
# Models are on RunPod Network Volume (mounted at /runpod-volume)
# ============================================================================

WORKDIR /comfyui/custom_nodes

# ----------------------------------------------------------------------------
# 1. Git-tracked community nodes
# ----------------------------------------------------------------------------
RUN git clone --depth 1 https://github.com/M1kep/ComfyLiterals && \
    git clone --depth 1 https://github.com/liusida/ComfyUI-AutoCropFaces && \
    git clone --depth 1 https://github.com/MinusZoneAI/ComfyUI-FluxExt-MZ && \
    git clone --depth 1 https://github.com/kael558/ComfyUI-GGUF-FantasyTalking && \
    git clone --depth 1 https://github.com/SeaArtLab/ComfyUI-Long-CLIP && \
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Manager.git && \
    git clone --depth 1 https://github.com/blepping/ComfyUI-bleh && \
    git clone --depth 1 https://github.com/kaibioinfo/ComfyUI_AdvancedRefluxControl && \
    git clone --depth 1 https://github.com/Suzie1/ComfyUI_Comfyroll_CustomNodes && \
    git clone --depth 1 https://github.com/comfyanonymous/ComfyUI_experiments && \
    git clone --depth 1 https://github.com/ClownsharkBatwing/RES4LYF && \
    git clone --depth 1 https://github.com/laksjdjf/cgem156-ComfyUI && \
    git clone --depth 1 https://github.com/florestefano1975/comfyui-prompt-composer

# ----------------------------------------------------------------------------
# 2. Manager-installed community nodes (no .git upstream)
# ----------------------------------------------------------------------------
RUN git clone --depth 1 https://github.com/chengzeyi/Comfy-WaveSpeed && \
    git clone --depth 1 https://github.com/crystian/ComfyUI-Crystools && \
    git clone --depth 1 https://github.com/DonutsDelivery/ComfyUI-DonutNodes && \
    git clone --depth 1 https://github.com/city96/ComfyUI-GGUF && \
    git clone --depth 1 https://github.com/chrisgoringe/cg-use-everywhere && \
    git clone --depth 1 https://github.com/PowerHouseMan/ComfyUI-AdvancedLivePortrait comfyui-advancedliveportrait && \
    git clone --depth 1 https://github.com/Extraltodeus/ComfyUI-AutomaticCFG comfyui-automaticcfg && \
    git clone --depth 1 https://github.com/Jonseed/ComfyUI-Detail-Daemon comfyui-detail-daemon && \
    git clone --depth 1 https://github.com/yolain/ComfyUI-Easy-Use comfyui-easy-use && \
    git clone --depth 1 https://github.com/kijai/ComfyUI-Florence2 comfyui-florence2 && \
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Pack comfyui-impact-pack && \
    git clone --depth 1 https://github.com/ltdrdata/ComfyUI-Impact-Subpack comfyui-impact-subpack && \
    git clone --depth 1 https://github.com/CY-CHENYUE/ComfyUI-InpaintEasy comfyui-inpainteasy && \
    git clone --depth 1 https://github.com/kijai/ComfyUI-KJNodes comfyui-kjnodes

RUN git clone --depth 1 https://github.com/Smirnov75/ComfyUI-mxToolkit comfyui-mxtoolkit && \
    git clone --depth 1 https://github.com/1038lab/ComfyUI-RMBG comfyui-rmbg && \
    git clone --depth 1 https://github.com/Fannovel16/comfyui_controlnet_aux && \
    git clone --depth 1 https://github.com/cubiq/ComfyUI_essentials comfyui_essentials && \
    git clone --depth 1 https://github.com/cubiq/ComfyUI_InstantID comfyui_instantid && \
    git clone --depth 1 https://github.com/cubiq/ComfyUI_IPAdapter_plus comfyui_ipadapter_plus && \
    git clone --depth 1 https://github.com/chflame163/ComfyUI_LayerStyle comfyui_layerstyle && \
    git clone --depth 1 https://github.com/lldacing/ComfyUI_PuLID_Flux_ll comfyui_pulid_flux_ll && \
    git clone --depth 1 https://github.com/ssitu/ComfyUI_UltimateSDUpscale comfyui_ultimatesdupscale && \
    git clone --depth 1 https://github.com/vuongminh1907/ComfyUI_ZenID comfyui_zenid && \
    git clone --depth 1 https://github.com/gseth/ControlAltAI-Nodes controlaltai-nodes && \
    git clone --depth 1 https://github.com/Derfuu/Derfuu_ComfyUI_ModdedNodes derfuu_comfyui_moddednodes && \
    git clone --depth 1 https://github.com/jitcoder/lora-info && \
    git clone --depth 1 https://github.com/bash-j/mikey_nodes && \
    git clone --depth 1 https://github.com/rgthree/rgthree-comfy && \
    git clone --depth 1 https://github.com/numz/ComfyUI-SeedVR2_VideoUpscaler seedvr2_videoupscaler && \
    git clone --depth 1 https://github.com/ltdrdata/was-node-suite-comfyui was-node-suite-comfyui

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
# 5. Extra model paths — add diffusion_models mapping
#    Base image maps unet → models/unet/ but our volume uses models/diffusion_models/
# ----------------------------------------------------------------------------
RUN YAML_FILE=$(find / -name "extra_model_paths.yaml" -path "*/src/*" 2>/dev/null | head -1) && \
    if [ -n "$YAML_FILE" ]; then \
        echo "  diffusion_models: models/diffusion_models/" >> "$YAML_FILE" && \
        echo "Patched $YAML_FILE with diffusion_models path"; \
    else \
        echo "WARNING: extra_model_paths.yaml not found, creating custom one"; \
        cat > /comfyui/extra_model_paths.yaml <<'EOF'
runpod_worker_comfy:
  base_path: /runpod-volume
  checkpoints: models/checkpoints/
  clip: models/clip/
  clip_vision: models/clip_vision/
  configs: models/configs/
  controlnet: models/controlnet/
  embeddings: models/embeddings/
  loras: models/loras/
  upscale_models: models/upscale_models/
  vae: models/vae/
  unet: models/unet/
  diffusion_models: models/diffusion_models/
EOF
    fi

WORKDIR /comfyui
