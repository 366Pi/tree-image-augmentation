"""
Test Suite — Tree Augmentation Pipeline
Validates manifest completeness, image outputs, metadata fields, and error handling.
Run with: python test_pipeline.py
"""

import os
import json
import sys

MANIFEST      = "manifest.jsonl"
OUTPUT_DIR    = "augmented_output"
BASE_DIR      = "base_images"
CONFIG_FILE   = "config.json"

passed = 0
failed = 0

# ─────────────────────────────────────────
# Helper
# ─────────────────────────────────────────
def test(name, condition, detail=""):
    global passed, failed
    if condition:
        print(f"  ✅ PASS  {name}")
        passed += 1
    else:
        print(f"  ❌ FAIL  {name}")
        if detail:
            print(f"           → {detail}")
        failed += 1

# ─────────────────────────────────────────
# 1. Project structure checks
# ─────────────────────────────────────────
print("\n📁 1. Project structure")

test("base_images/ folder exists",
     os.path.isdir(BASE_DIR))

test("augmented_output/ folder exists",
     os.path.isdir(OUTPUT_DIR))

test("gallery/ folder exists",
     os.path.isdir("gallery"))

test("config.json exists",
     os.path.isfile(CONFIG_FILE))

test("manifest.jsonl exists",
     os.path.isfile(MANIFEST),
     "Run python augment.py first")

test("gallery/index.html exists",
     os.path.isfile(os.path.join("gallery", "index.html")),
     "Run python gallery.py first")

# ─────────────────────────────────────────
# 2. Base images checks
# ─────────────────────────────────────────
print("\n🌳 2. Base images")

base_files = [f for f in os.listdir(BASE_DIR)
              if f.lower().endswith((".jpg", ".jpeg", ".png"))] if os.path.isdir(BASE_DIR) else []

test("At least 1 base image exists",
     len(base_files) >= 1,
     f"Found {len(base_files)} images in {BASE_DIR}/")

test("At least 5 base images exist",
     len(base_files) >= 5,
     f"Found only {len(base_files)} — expected 5")

for fname in base_files:
    fpath = os.path.join(BASE_DIR, fname)
    test(f"Base image is not empty: {fname}",
         os.path.getsize(fpath) > 0,
         f"{fpath} is 0 bytes")

# ─────────────────────────────────────────
# 3. Config file checks
# ─────────────────────────────────────────
print("\n⚙️  3. Config file")

config = {}
if os.path.isfile(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)

REQUIRED_KEYS = ["input_dir", "output_dir", "gallery_dir",
                 "manifest_file", "augmentations"]

for key in REQUIRED_KEYS:
    test(f"config.json has '{key}'",
         key in config,
         f"Missing key: {key}")

test("At least 1 augmentation is enabled",
     any(v.get("enabled", False)
         for v in config.get("augmentations", {}).values()),
     "All augmentations are disabled in config.json")

# ─────────────────────────────────────────
# 4. Manifest checks
# ─────────────────────────────────────────
print("\n📄 4. Manifest (manifest.jsonl)")

entries = []
if os.path.isfile(MANIFEST):
    with open(MANIFEST) as f:
        for i, line in enumerate(f):
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"  ❌ FAIL  Line {i+1} is not valid JSON")
                    failed += 1

test("Manifest has at least 1 entry",
     len(entries) >= 1,
     "manifest.jsonl is empty")

REQUIRED_FIELDS = [
    "source_image_id",
    "source_license",
    "original_dimensions",
    "generated_image_id",
    "augmentation_type",
    "augmentation_params",
    "output_file_path",
    "generation_timestamp"
]

if entries:
    sample = entries[0]
    for field in REQUIRED_FIELDS:
        test(f"Manifest entry has field: '{field}'",
             field in sample,
             f"Missing field in manifest entries")

test("All manifest entries have unique generated_image_id",
     len(entries) == len(set(e.get("generated_image_id") for e in entries)),
     "Duplicate generated_image_id found")

# ─────────────────────────────────────────
# 5. Output image checks
# ─────────────────────────────────────────
print("\n🖼️  5. Output images")

output_files = set(os.listdir(OUTPUT_DIR)) if os.path.isdir(OUTPUT_DIR) else set()

test("At least 1 output image exists",
     len(output_files) >= 1,
     f"augmented_output/ is empty")

test("More output images than base images",
     len(output_files) > len(base_files),
     f"Expected more outputs than {len(base_files)} base images")

# Check every manifest entry points to a real file
missing_files = []
for e in entries:
    fname = e.get("generated_image_id", "")
    if fname not in output_files:
        missing_files.append(fname)

test("Every manifest entry has a matching image file",
     len(missing_files) == 0,
     f"{len(missing_files)} manifest entries have no matching file")

# Check no output image is 0 bytes
empty_files = [f for f in output_files
               if os.path.getsize(os.path.join(OUTPUT_DIR, f)) == 0]
test("No output images are 0 bytes",
     len(empty_files) == 0,
     f"{len(empty_files)} empty files found")

# ─────────────────────────────────────────
# 6. Augmentation type coverage
# ─────────────────────────────────────────
print("\n🔧 6. Augmentation coverage")

aug_types = set(e.get("augmentation_type") for e in entries)

EXPECTED_TYPES = [
    "brightness", "blur", "rotation", "crop",
    "contrast", "weather_rain", "weather_fog",
    "color_temp_warm", "color_temp_cool", "occlusion"
]

for atype in EXPECTED_TYPES:
    test(f"Augmentation type present: {atype}",
         atype in aug_types)

# ─────────────────────────────────────────
# Summary
# ─────────────────────────────────────────
total = passed + failed
print("\n" + "=" * 50)
print(f"  Tests passed : {passed} / {total}")
print(f"  Tests failed : {failed} / {total}")
print("=" * 50)

if failed == 0:
    print("  🎉 All tests passed! Project is ready.")
else:
    print("  ⚠️  Fix the failing tests before submitting.")

sys.exit(0 if failed == 0 else 1)
