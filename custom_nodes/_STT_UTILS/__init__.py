import os
import hashlib
import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence
import folder_paths


class LoadImageOptional:

    @classmethod
    def INPUT_TYPES(s):
        files = sorted(
            f for f in os.listdir(folder_paths.get_input_directory())
            if os.path.isfile(os.path.join(folder_paths.get_input_directory(), f))
        )
        files.insert(0, "none")
        return {
            "required": {
                "image": (files, {"image_upload": True}),
            },
        }

    RETURN_TYPES = ("IMAGE", "MASK")
    OUTPUT_IS_LIST = (False, False)
    FUNCTION = "load"
    CATEGORY = "image"

    def load(self, image):
        if not image or image == "none":
            return (None, None)

        image_path = folder_paths.get_annotated_filepath(image)
        img = Image.open(image_path)
        frames, masks = [], []
        for frame in ImageSequence.Iterator(img):
            frame = ImageOps.exif_transpose(frame)
            if frame.mode == "I":
                frame = frame.point(lambda i: i * (1 / 255))
            rgba = frame.convert("RGBA")
            px = np.array(rgba).astype(np.float32) / 255.0
            frames.append(torch.from_numpy(px[..., :3]))
            masks.append(1.0 - torch.from_numpy(px[..., 3]))

        return (
            torch.stack(frames) if len(frames) > 1 else frames[0].unsqueeze(0),
            torch.stack(masks) if len(masks) > 1 else masks[0].unsqueeze(0),
        )

    @classmethod
    def IS_CHANGED(s, image, **kwargs):
        if not image or image == "none":
            return ""
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, "rb") as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image, **kwargs):
        return True


NODE_CLASS_MAPPINGS = {"LoadImageOptional": LoadImageOptional}
NODE_DISPLAY_NAME_MAPPINGS = {"LoadImageOptional": "Load Image (Optional)"}