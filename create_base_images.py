from PIL import Image, ImageDraw

def draw_tree(filename, sky_color, ground_color, trunk_color, leaf_color, style="round"):
    img = Image.new("RGB", (600, 500), sky_color)
    draw = ImageDraw.Draw(img)

    # Ground
    draw.rectangle([0, 380, 600, 500], fill=ground_color)

    # Trunk
    draw.rectangle([275, 280, 325, 390], fill=trunk_color)

    # Branches
    draw.line([300, 290, 220, 200], fill=trunk_color, width=10)
    draw.line([300, 310, 380, 210], fill=trunk_color, width=10)
    draw.line([300, 300, 260, 170], fill=trunk_color, width=8)

    if style == "round":
        draw.ellipse([170, 80, 430, 300], fill=leaf_color)
        draw.ellipse([150, 120, 350, 280], fill=leaf_color)
        draw.ellipse([250, 60, 450, 260], fill=leaf_color)

    elif style == "tall":
        draw.polygon([(300,50),(170,280),(430,280)], fill=leaf_color)
        draw.polygon([(300,80),(190,260),(410,260)], fill=leaf_color)

    elif style == "wide":
        draw.ellipse([100, 130, 500, 310], fill=leaf_color)
        draw.ellipse([130, 100, 470, 290], fill=leaf_color)

    elif style == "sparse":
        for x, y, r in [(220,180,55),(370,200,60),(290,140,65),(240,240,45),(360,150,50)]:
            draw.ellipse([x-r, y-r, x+r, y+r], fill=leaf_color)

    img.save(f"base_images/{filename}")
    print(f"✅ Created: base_images/{filename}")


# 5 different tree styles
trees = [
    ("tree_01.jpg", (135,185,220), (85,130,60),  (101,67,33),  (60,140,60),  "round"),
    ("tree_02.jpg", (200,220,255), (100,145,70),  (90,55,25),   (40,120,40),  "tall"),
    ("tree_03.jpg", (255,240,200), (110,150,65),  (120,80,40),  (180,160,30), "wide"),
    ("tree_04.jpg", (170,210,240), (75,120,55),   (85,50,20),   (50,160,70),  "sparse"),
    ("tree_05.jpg", (220,235,250), (90,135,60),   (95,60,28),   (35,100,35),  "round"),
]

for fname, sky, ground, trunk, leaf, style in trees:
    draw_tree(fname, sky, ground, trunk, leaf, style)

print("\n🎉 All 5 base images created in base_images/ folder!")
