#!/usr/bin/env python3
"""Gera os ícones maskable (disco dentro da zona segura de 80%) e o apple-touch-icon. Requer Pillow."""
import os
from PIL import Image, ImageDraw

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
BG, RIM, VINYL, LABEL = (20, 18, 26), (46, 42, 58), (30, 27, 39), (30, 215, 96)


def disc(size, scale):
    """scale = raio externo do disco / lado do ícone (o original usa ~0.40)."""
    ss = 4
    S = size * ss
    im = Image.new('RGB', (S, S), BG)
    d = ImageDraw.Draw(im)
    c = S / 2

    def circle(r, fill):
        d.ellipse((c - r, c - r, c + r, c + r), fill=fill)

    R = S * scale
    circle(R, (27, 24, 34))           # halo
    circle(R * 0.905, RIM)            # borda
    circle(R * 0.75, VINYL)           # vinil
    circle(R * 0.35, LABEL)           # selo
    circle(R * 0.10, BG)              # furo
    return im.resize((size, size), Image.LANCZOS)


if __name__ == '__main__':
    # zona segura maskable = círculo de raio 0.40; o disco fica em 0.30 com folga
    for n in (192, 512):
        disc(n, 0.30).save(os.path.join(ROOT, f'icon-maskable-{n}.png'), optimize=True)
    disc(180, 0.36).save(os.path.join(ROOT, 'apple-touch-icon.png'), optimize=True)
    print('ok')
