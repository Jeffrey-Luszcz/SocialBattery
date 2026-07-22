from PIL import Image, ImageDraw, ImageFont

W, H = 320, 240
img = Image.new("RGB", (W, H), (30, 30, 40))
d = ImageDraw.Draw(img)

# 7 colors from red -> yellow (center) -> green
colors = [
    (220, 40, 40),    # red (very sad)
    (235, 110, 40),   # orange
    (240, 175, 45),   # amber
    (240, 220, 50),   # yellow (center, flat)
    (190, 215, 55),   # yellow-green
    (120, 200, 60),   # light green
    (50, 175, 70),    # green (very happy)
]

# Title
title = "My Social Battery"
try:
    font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 22)
except Exception:
    font = ImageFont.load_default()
tb = d.textbbox((0, 0), title, font=font)
tw = tb[2] - tb[0]
d.text(((W - tw) // 2, 6), title, fill=(255, 255, 255), font=font)

# Rectangle band
top = 40
bottom = 200
n = 7
seg = W / n

for i, c in enumerate(colors):
    x0 = int(i * seg)
    x1 = int((i + 1) * seg)
    d.rectangle([x0, top, x1, bottom], fill=c)

    cx = (x0 + x1) / 2
    cy = (top + bottom) / 2 - 5
    r = 16
    # face circle
    face = (255, 255, 210)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=face, outline=(40, 40, 40), width=2)
    # eyes
    ex = 6
    ey = 5
    er = 2.5
    for sx in (-ex, ex):
        d.ellipse([cx + sx - er, cy - ey - er, cx + sx + er, cy - ey + er], fill=(40, 40, 40))
    # mouth: interpolate curve from sad (left) to happy (right)
    # t: -1 = very sad, 0 = flat, 1 = very happy
    t = (i - (n - 1) / 2) / ((n - 1) / 2)
    mw = 9      # half mouth width
    my = cy + 7 # mouth baseline
    curve = int(t * 8)  # positive = smile
    # Happiest face: a nicer, bigger grin sitting a bit higher in the face
    if i == n - 1:
        mw = 10
        my = cy + 1
        curve = 8
    pts = []
    steps = 12
    for s in range(steps + 1):
        px = cx - mw + (2 * mw) * s / steps
        # parabola: at ends y=my, at center y=my-curve
        frac = (s / steps - 0.5) * 2  # -1..1
        py = my + curve * (1 - frac * frac)
        pts.append((px, py))
    d.line(pts, fill=(40, 40, 40), width=2, joint="curve")

# Bottom gray rounded rectangle line with white border
by0 = 155
by1 = 178
bx0 = 8
bx1 = W - 8
d.rounded_rectangle([bx0, by0, bx1, by1], radius=10,
                    fill=(110, 110, 120), outline=(255, 255, 255), width=3)

img.save("social_battery.png")
print("saved social_battery.png")
