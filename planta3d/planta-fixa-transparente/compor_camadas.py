"""Compõe camadas screen preservando transparência das imagens-base.

Execute após renderizar.py com film_transparent=True. Requer Pillow e numpy.
"""
from pathlib import Path
import numpy as np
from PIL import Image, ImageFilter

folder = Path(__file__).resolve().parent
names = ['luz_sala_1','luz_sala_2','luz_cozinha','luz_corredor','luz_quarto','luz_quarto_1','tv_sala','tv_quarto']

def read_rgba(path):
    return Image.open(path).convert('RGBA')

def smooth_rgb(im):
    return im.convert('RGB').filter(ImageFilter.MedianFilter(3))

day = read_rgba(folder / 'dia.png')
night = read_rgba(folder / 'noite.png')
day_alpha = np.asarray(day.getchannel('A'), dtype=np.uint8)
night_alpha = np.asarray(night.getchannel('A'), dtype=np.uint8)
base_image = smooth_rgb(night)
base = np.asarray(base_image, dtype=np.int16)

# Na borda semitransparente, uma segunda camada source-over engrossaria o halo.
# Restrinja os efeitos a pixels quase opacos em ambos os estados solares.
mask = Image.fromarray(((day_alpha >= 250) & (night_alpha >= 250)).astype(np.uint8) * 255, 'L')
for name in names:
    source = folder / ('_lit_' + name + '.png')
    image = np.asarray(smooth_rgb(read_rgba(source)), dtype=np.int16)
    diff = np.maximum(image - base - 3, 0)
    diff = np.clip(diff * 1.6, 0, 255).astype(np.uint8)
    result = Image.fromarray(diff, 'RGB').filter(ImageFilter.GaussianBlur(.7)).convert('RGBA')
    result.putalpha(mask)
    result.save(folder / (name + '.png'), optimize=True)
    source.unlink()

# RGB com redução de ruído; canal alfa original conserva antisserrilhado.
for name, im in [('dia.png', day), ('noite.png', night)]:
    # Não filtrar RGB nas bordas: a mistura com pixels transparentes pode
    # escurecer o contorno ao usar fundos claros.
    original = np.asarray(im.convert('RGB'), dtype=np.uint8)
    filtered = np.asarray(smooth_rgb(im), dtype=np.uint8)
    alpha = np.asarray(im.getchannel('A'), dtype=np.uint8)
    rgb = np.where((alpha < 250)[:, :, None], original, filtered).astype(np.uint8)
    result = Image.fromarray(rgb, 'RGB').convert('RGBA')
    result.putalpha(im.getchannel('A'))
    result.save(folder / name, optimize=True)
