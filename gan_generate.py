"""
GAN Image Generation Script — FloCard Tree Image Augmentation
Loads a trained Generator model and produces new synthetic tree images.
Records every generated image in manifest.jsonl for full traceability.

Usage:
    python gan_generate.py
    python gan_generate.py --count 50 --model gan_models/generator_final.pth
"""

import os
import json
import argparse
import torch
import torch.nn as nn
from PIL import Image
from datetime import datetime

# ─────────────────────────────────────────
# Arguments
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Generate tree images using trained GAN")
parser.add_argument("--count",      type=int,   default=20,   help="Number of images to generate")
parser.add_argument("--model",      type=str,   default="gan_models/generator_final.pth")
parser.add_argument("--config",     type=str,   default="gan_models/gan_config.json")
parser.add_argument("--output-dir", type=str,   default="augmented_output")
parser.add_argument("--manifest",   type=str,   default="manifest.jsonl")
args = parser.parse_args()

# ─────────────────────────────────────────
# Load GAN config
# ─────────────────────────────────────────
if not os.path.isfile(args.config):
    print(f"❌ GAN config not found: {args.config}")
    print("   Run python gan_train.py first.")
    exit(1)

with open(args.config) as f:
    gan_cfg = json.load(f)

LATENT_DIM  = gan_cfg["latent_dim"]
IMAGE_SIZE  = gan_cfg["image_size"]
OUTPUT_DIR  = args.output_dir
MANIFEST    = args.manifest
COUNT       = args.count

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load species from main config if available
species = "unknown"
growth  = "unknown"
if os.path.isfile("config.json"):
    with open("config.json") as f:
        cfg     = json.load(f)
        species = cfg.get("species_label", "unknown")
        growth  = cfg.get("growth_stage",  "unknown")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

print(f"\n🌳 FloCard GAN Image Generator")
print(f"   Model       : {args.model}")
print(f"   Device      : {DEVICE}")
print(f"   Image size  : {IMAGE_SIZE}×{IMAGE_SIZE}")
print(f"   Generating  : {COUNT} images")
print(f"   Species     : {species}")
print(f"   Output dir  : {OUTPUT_DIR}/")
print("=" * 55)


# ─────────────────────────────────────────
# Generator architecture (must match gan_train.py)
# ─────────────────────────────────────────
class Generator(nn.Module):
    """DCGAN Generator — must match the architecture used during training."""

    def __init__(self, latent_dim, image_size):
        super().__init__()
        self.init_size = image_size // 16
        self.fc        = nn.Linear(latent_dim, 512 * self.init_size * self.init_size)

        self.model = nn.Sequential(
            nn.BatchNorm2d(512),
            nn.Upsample(scale_factor=2),
            nn.Conv2d(512, 256, 3, stride=1, padding=1),
            nn.BatchNorm2d(256),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Upsample(scale_factor=2),
            nn.Conv2d(256, 128, 3, stride=1, padding=1),
            nn.BatchNorm2d(128),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Upsample(scale_factor=2),
            nn.Conv2d(128, 64, 3, stride=1, padding=1),
            nn.BatchNorm2d(64),
            nn.LeakyReLU(0.2, inplace=True),

            nn.Upsample(scale_factor=2),
            nn.Conv2d(64, 3, 3, stride=1, padding=1),
            nn.Tanh()
        )

    def forward(self, z):
        out = self.fc(z)
        out = out.view(out.shape[0], 512, self.init_size, self.init_size)
        return self.model(out)


# ─────────────────────────────────────────
# Load trained model
# ─────────────────────────────────────────
if not os.path.isfile(args.model):
    print(f"❌ Model not found: {args.model}")
    print("   Run python gan_train.py first.")
    exit(1)

G = Generator(LATENT_DIM, IMAGE_SIZE).to(DEVICE)
G.load_state_dict(torch.load(args.model, map_location=DEVICE))
G.eval()
print(f"\n✅ Model loaded: {args.model}")


# ─────────────────────────────────────────
# Generate images
# ─────────────────────────────────────────
manifest_entries = []
generated = 0
failed    = 0

print(f"\n📸 Generating {COUNT} images...\n")

with torch.no_grad():
    for i in range(COUNT):
        try:
            z         = torch.randn(1, LATENT_DIM).to(DEVICE)
            fake_img  = G(z)

            # Convert from tensor [-1,1] → PIL image [0,255]
            fake_img  = fake_img.squeeze(0).cpu()
            fake_img  = (fake_img * 0.5 + 0.5).clamp(0, 1)
            fake_img  = (fake_img.permute(1, 2, 0).numpy() * 255).astype("uint8")
            pil_img   = Image.fromarray(fake_img)

            # Scale up to a more usable resolution
            pil_img = pil_img.resize((256, 256), Image.LANCZOS)

            # Save image
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f")
            out_name  = f"gan_generated__{timestamp}.jpg"
            out_path  = os.path.join(OUTPUT_DIR, out_name)
            pil_img.save(out_path, quality=92)

            # Manifest entry
            entry = {
                "source_image_id"    : "gan_generator",
                "source_license"     : "gan-generated/synthetic",
                "species_label"      : species,
                "growth_stage"       : growth,
                "original_dimensions": [IMAGE_SIZE, IMAGE_SIZE],
                "generated_image_id" : out_name,
                "augmentation_type"  : "gan_generated",
                "augmentation_params": {
                    "latent_dim" : LATENT_DIM,
                    "image_size" : IMAGE_SIZE,
                    "model"      : args.model,
                    "sample_idx" : i + 1
                },
                "capture_quality"      : "synthetic_gan",
                "season"               : None,
                "time_of_day"          : None,
                "health_condition"     : None,
                "location_tag"         : None,
                "output_file_path"     : out_path,
                "generation_timestamp" : datetime.utcnow().isoformat() + "Z"
            }
            manifest_entries.append(entry)
            generated += 1
            print(f"  ✅ [{i+1:3d}/{COUNT}] {out_name}")

        except Exception as e:
            print(f"  ❌ [{i+1:3d}/{COUNT}] Failed — {e}")
            failed += 1

# ─────────────────────────────────────────
# Append to manifest
# ─────────────────────────────────────────
with open(MANIFEST, "a") as f:
    for entry in manifest_entries:
        f.write(json.dumps(entry) + "\n")

print(f"\n{'=' * 55}")
print(f"✅ Generation complete!")
print(f"   Images generated : {generated}")
print(f"   Failed           : {failed}")
print(f"   Manifest updated : {MANIFEST}")
print(f"   Output folder    : {OUTPUT_DIR}/")
print(f"{'=' * 55}")
print(f"\n▶  Run  python gallery.py  to see GAN images in the gallery.")
