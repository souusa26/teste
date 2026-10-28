"""Produz camadas screen com as diferenças positivas dos renders Blender."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

folder = Path(__file__).resolve().parent
def smooth(path):
    return Image.open(path).convert('RGB').filter(ImageFilter.MedianFilter(3))

base_image = smooth(folder / 'noite.png')
base = np.asarray(base_image, dtype=np.int16)
names = ['luz_sala_1','luz_sala_2','luz_cozinha','luz_corredor','luz_quarto','luz_quarto_1','tv_sala','tv_quarto']
for name in names:
    source = folder / ('_lit_' + name + '.png')
    image = np.asarray(smooth(source), dtype=np.int16)
    diff = np.maximum(image - base - 3, 0)
    diff = np.clip(diff * 1.6, 0, 255).astype(np.uint8)
    result = Image.fromarray(diff, 'RGB').filter(ImageFilter.GaussianBlur(.7)).convert('RGBA')
    result.save(folder / (name + '.png'), optimize=True)
    source.unlink()
smooth(folder / 'dia.png').save(folder / 'dia.png', optimize=True)
base_image.save(folder / 'noite.png', optimize=True)
