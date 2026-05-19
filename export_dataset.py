import os
import json
import zipfile
import argparse
from datetime import datetime

parser = argparse.ArgumentParser(description="Export augmented images only as ZIP")
parser.add_argument("--output",     type=str, default=None)
parser.add_argument("--species",    type=str, default=None)
parser.add_argument("--aug-type",  type=str, default=None,
                    help="Filter by augmentation type e.g. brightness, season_spring")
args = parser.parse_args()

with open("config.json") as f:
    config = json.load(f)

SPECIES    = args.species or config.get("species_label", "unknown")
OUTPUT_DIR = config["output_dir"]
MANIFEST   = config["manifest_file"]

timestamp  = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
ZIP_NAME   = args.output or f"augmented_images_{SPECIES}_{timestamp}.zip"

print(f"\n📦 FloCard — Augmented Images Exporter")
print(f"   Species      : {SPECIES}")
print(f"   Filter type  : {args.aug_type or 'all'}")
print(f"   Output ZIP   : {ZIP_NAME}")
print("=" * 50)

# ── Load manifest ──
entries = []
if os.path.isfile(MANIFEST):
    with open(MANIFEST) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))

# ── Apply filters ──
if args.aug_type:
    entries = [e for e in entries if e.get("augmentation_type") == args.aug_type]

print(f"\n   Total entries in manifest : {len(entries)}")

# ── Build ZIP ──
packed   = 0
skipped  = 0
missing  = 0

with zipfile.ZipFile(ZIP_NAME, "w", zipfile.ZIP_DEFLATED) as zf:

    # Write filtered manifest
    filtered_manifest = "\n".join(json.dumps(e) for e in entries)
    zf.writestr("manifest.jsonl", filtered_manifest)
    print(f"  ✅ manifest.jsonl ({len(entries)} entries)")

    # Pack images
    print(f"\n  📸 Packing images...\n")
    for e in entries:
        fname = e.get("generated_image_id", "")
        fpath = os.path.join(OUTPUT_DIR, fname)
        if os.path.isfile(fpath):
            zf.write(fpath, fname)
            packed += 1
        else:
            missing += 1

    print(f"  ✅ {packed} images packed")
    if missing:
        print(f"  ⚠️  {missing} files not found on disk")

zip_size = os.path.getsize(ZIP_NAME)

print(f"\n{'=' * 50}")
print(f"✅ Export complete!")
print(f"   ZIP file     : {ZIP_NAME}")
print(f"   Images packed: {packed}")
print(f"   ZIP size     : {round(zip_size / 1024 / 1024, 2)} MB")
print(f"{'=' * 50}")
print(f"\n💡 Tips:")
print(f"   Export only brightness images:")
print(f"   python export_dataset.py --aug-type brightness")
print(f"   Export for different species:")
print(f"   python export_dataset.py --species neem")