import torch
from PIL import Image
from py_real_esrgan.model import RealESRGAN

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = RealESRGAN(device, scale=4)
model.load_weights('weights/RealESRGAN_x4.pth', download=True)

img = Image.open('source.png').convert('RGB')
sr_img = model.predict(img)
sr_img.save('output.png')

from __future__ import annotations

import argparse
from pathlib import Path

from processor import upscale_image


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Upscale an image using Real-ESRGAN (x4)")
	parser.add_argument(
		"input",
		nargs="?",
		default="source.png",
		help="Path to the source image (default: %(default)s)",
	)
	parser.add_argument(
		"output",
		nargs="?",
		default="output.png",
		help="Destination path for the upscaled image (default: %(default)s)",
	)
	return parser.parse_args()


def main() -> None:
	args = parse_args()

	input_path = Path(args.input)
	output_path = Path(args.output)

	if not input_path.exists():
		raise FileNotFoundError(f"Input image not found: {input_path}")

	upscale_image(input_path, output_path)

	print(f"Upscaled image saved to {output_path}")


if __name__ == "__main__":
	main()
