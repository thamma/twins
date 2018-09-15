from PIL import Image, ImageDraw
from math import sqrt
import random
import colorsys
import itertools

H = 200

tri_mid = [(.5, 0), (.75, sqrt(1-.5**2) / 2), (.25, sqrt(1-.5**2) / 2)]
tri_a = [(0, 0), (.5, 0), (.25, sqrt(1-.5**2)/ 2)]
tri_b = [(.5, 0), (1, 0), (.75, sqrt(1-.5**2 ) / 2)]
tri_c = [(.75, sqrt(1-.5**2 ) / 2), (.5,sqrt(1-.5**2 )), (.25, sqrt(1-.5**2 ) / 2)]

def tr(a):
    return [(H * x, H * y) for x, y in a]

def tc(c):
    r, g, b = c
    return (int(r * 255), int(g * 255), int(b * 255))

colors = [colorsys.hsv_to_rgb(i/16, 1, 1) for i in range(16)]
random.shuffle(colors)

def gen_tri(fname, c0, c1, c2, c3):
    img = Image.new("RGB", (H, int(H*0.9)))
    draw = ImageDraw.Draw(img)

    draw.polygon(tr(tri_mid), tc(colors[c0]))
    draw.polygon(tr(tri_a), tc(colors[c1]))
    draw.polygon(tr(tri_b), tc(colors[c2]))
    draw.polygon(tr(tri_c), tc(colors[c3]))

    draw.line(tr([(.5, 0), (.25, sqrt(1-.5**2)/2)]), fill=(0,0,0), width=5)
    draw.line(tr([(.5, 0), (.75, sqrt(1-.5**2)/2)]), fill=(0,0,0), width=5)
    draw.line(tr([(.75, sqrt(1-.5**2)/2), (.25, sqrt(1-.5**2)/2)]), fill=(0,0,0), width=5)

    img.save(fname)

with open("aaa.txt", "r") as f:
    for line in f:
        rc, a, b, c = line.strip().split()
        mid = rc.split("_")[0]
        mid = int(mid)
        a = int(a)
        b = int(b)
        c = int(c)
        gen_tri(f"{rc}.png", mid, a, b, c)
