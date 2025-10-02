from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Union

import torch
from PIL import Image
from py_real_esrgan.model import RealESRGAN

_PathLike = Union[str, Path]

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"PyTorch is using device: {_device}")
if _device.type == "cpu":
    print("GPU is not being used. To use GPU, make sure you have:")
    print("1. An NVIDIA GPU")
    print("2. CUDA installed (https://developer.nvidia.com/cuda-downloads)")
    print("3. PyTorch with CUDA support installed")
_model = RealESRGAN(_device, scale=4)


@contextmanager
def _torch_load_weights_compat() -> Iterator[None]:
    original_load = torch.load

    def patched_load(*args, **kwargs):
        kwargs.setdefault("weights_only", False)
        return original_load(*args, **kwargs)

    torch.load = patched_load
    try:
        yield
    finally:
        torch.load = original_load


with _torch_load_weights_compat():
    _model.load_weights("weights/RealESRGAN_x4.pth", download=True)


def upscale_image(input_path: _PathLike, output_path: _PathLike) -> Path:
    """Upscale an image and write it to ``output_path``.

    Args:
        input_path: Path to the source RGB image.
        output_path: Destination path that will contain the upscaled result.

    Returns:
        The ``Path`` object for ``output_path``.
    """

    input_path = Path(input_path)
    output_path = Path(output_path)

    img = Image.open(input_path).convert("RGB")
    sr_img = _model.predict(img)
    sr_img.save(output_path)
    return output_path

    output_path.parent.mkdir(parents=True, exist_ok=True)
    sr_img.save(output_path)

    return output_path
