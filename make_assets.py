from PIL import Image, ImageDraw

# 1) Background resized to the 160x120 framebuffer
bg = Image.open("social_battery.png").convert("RGB").resize((160, 120), Image.LANCZOS)
bg.save("social_battery/assets/background.png")

# 2) Diamond sprite (RGBA, transparent background)
D = 24
dia = Image.new("RGBA", (D, D), (0, 0, 0, 0))
dd = ImageDraw.Draw(dia)
c = D / 2
pts = [(c, 1), (D - 1, c), (c, D - 1), (1, c)]
# gem body + white outline
dd.polygon(pts, fill=(90, 200, 255, 255), outline=(255, 255, 255, 255))
dd.polygon(pts, outline=(255, 255, 255, 255))
# facet highlight lines
dd.line([(c, 1), (c, D - 1)], fill=(255, 255, 255, 200), width=1)
dd.line([(1, c), (D - 1, c)], fill=(255, 255, 255, 160), width=1)
# top sparkle
dd.polygon([(c, 1), (c - 4, c - 2), (c, c), (c + 4, c - 2)], fill=(200, 240, 255, 255))
dia.save("social_battery/assets/diamond.png")

# 24x24 icon = the background scaled down
bg.resize((24, 24), Image.LANCZOS).save("social_battery/icon.png")

print("assets written")
