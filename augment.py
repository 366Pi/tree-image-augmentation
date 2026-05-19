"""
Tree Image Augmentation Pipeline — FloCard Edition
Reads config.json, applies visual transformations to base tree images,
saves outputs, and writes a metadata manifest.
"""

import os
import json
import time
import random
from datetime import datetime
from PIL import Image, ImageEnhance, ImageFilter, ImageDraw

# ─────────────────────────────────────────
# Load config
# ─────────────────────────────────────────
with open("config.json") as f:
    config = json.load(f)

INPUT_DIR    = config["input_dir"]
OUTPUT_DIR   = config["output_dir"]
GALLERY_DIR  = config["gallery_dir"]
MANIFEST     = config["manifest_file"]
AUG          = config["augmentations"]
SPECIES      = config.get("species_label", "unknown")
GROWTH       = config.get("growth_stage", "unknown")
LOC          = config.get("location_tag", {})

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GALLERY_DIR, exist_ok=True)

manifest_entries = []
generated = 0
failed    = 0
start_time = time.time()


# ─────────────────────────────────────────
# Helper: save image + write manifest entry
# ─────────────────────────────────────────
def save_image(img, source_id, aug_type, aug_params, orig_size,
               capture_quality="clean", season=None,
               time_of_day=None, health_condition=None):
    """Save generated image to disk and append a metadata record to the manifest."""
    global generated
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
    out_name  = f"{source_id}__{aug_type}__{timestamp}.jpg"
    out_path  = os.path.join(OUTPUT_DIR, out_name)
    img.save(out_path, quality=92)

    entry = {
        "source_image_id"    : source_id,
        "source_license"     : "synthetic/contributor-created",
        "species_label"      : SPECIES,
        "growth_stage"       : GROWTH,
        "original_dimensions": list(orig_size),
        "generated_image_id" : out_name,
        "augmentation_type"  : aug_type,
        "augmentation_params": aug_params,
        "capture_quality"    : capture_quality,
        "season"             : season,
        "time_of_day"        : time_of_day,
        "health_condition"   : health_condition,
        "location_tag"       : {
            "latitude" : LOC.get("latitude"),
            "longitude": LOC.get("longitude")
        } if LOC.get("enabled") else None,
        "output_file_path"      : out_path,
        "generation_timestamp"  : datetime.utcnow().isoformat() + "Z"
    }
    manifest_entries.append(entry)
    generated += 1
    print(f"  ✅ {aug_type:25s} → {out_name}")


# ─────────────────────────────────────────
# Original augmentation functions
# ─────────────────────────────────────────

def aug_brightness(img, source_id, orig_size):
    """Apply brightness variations — simulates different exposure levels."""
    if not AUG["brightness"]["enabled"]:
        return
    for factor in AUG["brightness"]["factors"]:
        out = ImageEnhance.Brightness(img).enhance(factor)
        save_image(out, source_id, "brightness", {"factor": factor}, orig_size)


def aug_blur(img, source_id, orig_size):
    """Apply gaussian blur — simulates out-of-focus captures."""
    if not AUG["blur"]["enabled"]:
        return
    for radius in AUG["blur"]["radius_values"]:
        out = img.filter(ImageFilter.GaussianBlur(radius=radius))
        save_image(out, source_id, "blur", {"radius": radius}, orig_size)


def aug_rotation(img, source_id, orig_size):
    """Rotate image — simulates tilted camera angles in the field."""
    if not AUG["rotation"]["enabled"]:
        return
    for angle in AUG["rotation"]["angles"]:
        out = img.rotate(angle, expand=False, fillcolor=(200, 220, 200))
        save_image(out, source_id, "rotation", {"angle_degrees": angle}, orig_size)


def aug_crop(img, source_id, orig_size):
    """Crop and resize — simulates zoomed-in field capture."""
    if not AUG["crop"]["enabled"]:
        return
    pct = AUG["crop"]["crop_percent"]
    w, h = img.size
    margin_x = int(w * pct)
    margin_y = int(h * pct)
    out = img.crop((margin_x, margin_y, w - margin_x, h - margin_y))
    out = out.resize((w, h), Image.LANCZOS)
    save_image(out, source_id, "crop", {"crop_percent": pct}, orig_size)


def aug_contrast(img, source_id, orig_size):
    """Apply contrast variations — simulates different camera settings."""
    if not AUG["contrast"]["enabled"]:
        return
    for factor in AUG["contrast"]["factors"]:
        out = ImageEnhance.Contrast(img).enhance(factor)
        save_image(out, source_id, "contrast", {"factor": factor}, orig_size)


def aug_weather(img, source_id, orig_size):
    """Overlay rain or fog — simulates field capture in bad weather."""
    if not AUG["weather"]["enabled"]:
        return
    for weather_type in AUG["weather"]["types"]:
        out  = img.copy()
        draw = ImageDraw.Draw(out)
        w, h = out.size

        if weather_type == "rain":
            for _ in range(1500):
                x      = random.randint(0, w)
                y      = random.randint(0, h)
                length = random.randint(15, 35)
                draw.line([(x, y), (x - 3, y + length)],
                    fill=(80, 100, 120), width=2)
                draw.line([(x+1, y), (x - 2, y + length)],
                    fill=(200, 220, 240), width=1)
        elif weather_type == "fog":
            fog = Image.new("RGBA", out.size, (220, 225, 230, 110))
            out = out.convert("RGBA")
            out = Image.alpha_composite(out, fog).convert("RGB")

        save_image(out, source_id, f"weather_{weather_type}",
                   {"weather_type": weather_type}, orig_size)


def aug_color_temperature(img, source_id, orig_size):
    """Shift color temperature — warm or cool lighting simulation."""
    if not AUG["color_temperature"]["enabled"]:
        return
    for mode in AUG["color_temperature"]["modes"]:
        r, g, b = img.split()
        if mode == "warm":
            r = r.point(lambda i: min(255, int(i * 1.2)))
            b = b.point(lambda i: int(i * 0.8))
        elif mode == "cool":
            r = r.point(lambda i: int(i * 0.8))
            b = b.point(lambda i: min(255, int(i * 1.2)))
        out = Image.merge("RGB", (r, g, b))
        save_image(out, source_id, f"color_temp_{mode}",
                   {"mode": mode}, orig_size)

def aug_occlusion(img, source_id, orig_size):
    """Add random black boxes — simulates partial obstruction of tree."""
    if not AUG["occlusion"]["enabled"]:
        return
    out  = img.copy()
    draw = ImageDraw.Draw(out)
    w, h = out.size
    n    = AUG["occlusion"]["num_boxes"]
    bmax = AUG["occlusion"]["max_box_size"]
    boxes = []
    for _ in range(n):
        bw = random.randint(20, bmax)
        bh = random.randint(20, bmax)
        bx = random.randint(0, w - bw)
        by = random.randint(0, h - bh)
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(0, 0, 0))
        boxes.append({"x": bx, "y": by, "w": bw, "h": bh})
    save_image(out, source_id, "occlusion", {"boxes": boxes}, orig_size)


# ─────────────────────────────────────────
# NEW FloCard augmentation functions
# ─────────────────────────────────────────

def aug_season(img, source_id, orig_size):
    """Apply seasonal color tint — spring/summer/monsoon/winter appearance."""
    if not AUG["season"]["enabled"]:
        return
    season_tints = {
        "spring"  : (0,  20,  0,  60),
        "summer"  : (20, 10,  0,  60),
        "monsoon" : (0,  10,  20, 80),
        "winter"  : (10, 10,  20, 70),
    }
    for season_type in AUG["season"]["types"]:
        tint    = season_tints.get(season_type, (0, 0, 0, 50))
        overlay = Image.new("RGBA", img.size,
                            (tint[0], tint[1], tint[2], tint[3]))
        out = img.convert("RGBA")
        out = Image.alpha_composite(out, overlay).convert("RGB")
        save_image(out, source_id, f"season_{season_type}",
                   {"season": season_type}, orig_size,
                   season=season_type)


def aug_time_of_day(img, source_id, orig_size):
    """Apply time-of-day tint — morning warm, noon neutral, evening cool blue."""
    if not AUG["time_of_day"]["enabled"]:
        return
    for time_type in AUG["time_of_day"]["types"]:
        r, g, b = img.split()
        if time_type == "morning":
            r = r.point(lambda i: min(255, int(i * 1.15)))
            b = b.point(lambda i: int(i * 0.85))
        elif time_type == "evening":
            r = r.point(lambda i: int(i * 0.85))
            b = b.point(lambda i: min(255, int(i * 1.2)))
        out = Image.merge("RGB", (r, g, b))
        save_image(out, source_id, f"time_{time_type}",
                   {"time_of_day": time_type}, orig_size,
                   time_of_day=time_type)


def aug_health(img, source_id, orig_size):
    """Simulate tree health — healthy, stressed (yellowing), diseased (brown patches)."""
    if not AUG["health"]["enabled"]:
        return
    for condition in AUG["health"]["conditions"]:
        out  = img.copy()
        draw = ImageDraw.Draw(out)
        w, h = out.size

        if condition == "stressed":
            r, g, b = out.split()
            r = r.point(lambda i: min(255, int(i * 1.05)))
            g = g.point(lambda i: int(i * 0.88))
            out = Image.merge("RGB", (r, g, b))

        elif condition == "diseased":
            r, g, b = out.split()
            r = r.point(lambda i: min(255, int(i * 1.08)))
            g = g.point(lambda i: int(i * 0.78))
            out = Image.merge("RGB", (r, g, b))
            for _ in range(8):
                px = random.randint(w // 4, 3 * w // 4)
                py = random.randint(h // 8, h // 2)
                pr = random.randint(6, 18)
                draw.ellipse([px - pr, py - pr, px + pr, py + pr],
                             fill=(101, 67, 10))

        save_image(out, source_id, f"health_{condition}",
                   {"condition": condition}, orig_size,
                   health_condition=condition)


def aug_noise(img, source_id, orig_size):
    """Add random pixel noise — simulates low quality mobile sensor capture."""
    if not AUG["noise"]["enabled"]:
        return
    for intensity in AUG["noise"]["intensity_values"]:
        out    = img.copy()
        pixels = out.load()
        w, h   = out.size
        for _ in range(int(w * h * 0.05)):
            px = random.randint(0, w - 1)
            py = random.randint(0, h - 1)
            nr = random.randint(-intensity, intensity)
            r, g, b = pixels[px, py]
            pixels[px, py] = (
                max(0, min(255, r + nr)),
                max(0, min(255, g + nr)),
                max(0, min(255, b + nr))
            )
        save_image(out, source_id, "noise",
                   {"intensity": intensity}, orig_size,
                   capture_quality="noisy")


def aug_motion_blur(img, source_id, orig_size):
    """Directional motion blur — simulates shaky hand capture in the field."""
    if not AUG["motion_blur"]["enabled"]:
        return
    for strength in AUG["motion_blur"]["strengths"]:
        out = img.filter(ImageFilter.GaussianBlur(radius=strength))
        save_image(out, source_id, "motion_blur",
                   {"strength": strength}, orig_size,
                   capture_quality="motion_blur")


# ─────────────────────────────────────────
# Main pipeline
# ─────────────────────────────────────────
image_files = [f for f in os.listdir(INPUT_DIR)
               if f.lower().endswith((".jpg", ".jpeg", ".png"))]

if not image_files:
    print("❌ No images found in base_images/. Run create_base_images.py first.")
    exit(1)

print(f"\n🌳 Tree Augmentation Pipeline — FloCard Edition")
print(f"   Species          : {SPECIES}")
print(f"   Growth stage     : {GROWTH}")
print(f"   Base images      : {len(image_files)}")
print(f"   Output directory : {OUTPUT_DIR}/")
print("=" * 60)

for img_file in image_files:
    source_id = os.path.splitext(img_file)[0]
    img_path  = os.path.join(INPUT_DIR, img_file)

    try:
        img = Image.open(img_path).convert("RGB")
        orig_size = img.size
        print(f"\n📷 Processing: {img_file}  ({orig_size[0]}×{orig_size[1]})")

        aug_brightness(img, source_id, orig_size)
        aug_blur(img, source_id, orig_size)
        aug_rotation(img, source_id, orig_size)
        aug_crop(img, source_id, orig_size)
        aug_contrast(img, source_id, orig_size)
        aug_weather(img, source_id, orig_size)
        aug_color_temperature(img, source_id, orig_size)
        aug_occlusion(img, source_id, orig_size)
        aug_season(img, source_id, orig_size)
        aug_time_of_day(img, source_id, orig_size)
        aug_health(img, source_id, orig_size)
        aug_noise(img, source_id, orig_size)
        aug_motion_blur(img, source_id, orig_size)

    except Exception as e:
        print(f"  ❌ Failed: {img_file} — {e}")
        failed += 1

# ─────────────────────────────────────────
# Write manifest
# ─────────────────────────────────────────
with open(MANIFEST, "w") as f:
    for entry in manifest_entries:
        f.write(json.dumps(entry) + "\n")

elapsed = round(time.time() - start_time, 2)

print("\n" + "=" * 60)
print(f"✅ Done!")
print(f"   Images generated  : {generated}")
print(f"   Failed            : {failed}")
print(f"   Time taken        : {elapsed}s")
print(f"   Manifest saved    : {MANIFEST}")
print(f"   Output folder     : {OUTPUT_DIR}/")
print("=" * 60)
print("\n▶  Next: run  python gallery.py  to rebuild the visual review page.")