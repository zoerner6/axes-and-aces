"""Render every page of the book into 4-up contact sheets for eyeballing.

Run: python sheets.py <pdf> <outdir> [per_sheet]
"""
import os, sys
import pymupdf
from PIL import Image, ImageDraw

PDF = sys.argv[1]
OUT = sys.argv[2]
PER = int(sys.argv[3]) if len(sys.argv) > 3 else 4

COLS = 2
PAGE_W = 720                      # px per page across
GAP = 14
LABEL = 18

os.makedirs(OUT, exist_ok=True)
doc = pymupdf.open(PDF)
zoom = PAGE_W / doc[0].rect.width
page_h = int(doc[0].rect.height * zoom)
rows = (PER + COLS - 1) // COLS

sheet_w = COLS * PAGE_W + (COLS + 1) * GAP
sheet_h = rows * (page_h + LABEL) + (rows + 1) * GAP

made = []
for start in range(0, doc.page_count, PER):
    sheet = Image.new('RGB', (sheet_w, sheet_h), (64, 64, 70))
    drw = ImageDraw.Draw(sheet)
    for k in range(PER):
        i = start + k
        if i >= doc.page_count:
            break
        pm = doc[i].get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        img = Image.frombytes('RGB', (pm.width, pm.height), pm.samples)
        cx, cy = k % COLS, k // COLS
        x = GAP + cx * (PAGE_W + GAP)
        y = GAP + cy * (page_h + LABEL + GAP)
        drw.text((x + 2, y + 3), 'page %d' % (i + 1), fill=(255, 255, 255))
        sheet.paste(img, (x, y + LABEL))
    p = os.path.join(OUT, 'sheet_%03d.png' % (start // PER + 1))
    sheet.save(p, optimize=True)
    made.append(p)

print('%d sheets, %d pages' % (len(made), doc.page_count))
for p in made:
    print(p)
