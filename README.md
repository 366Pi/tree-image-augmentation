# Tree Image Augmentation Pipeline

A simple, reusable pipeline that takes a small set of base tree images and generates
controlled visual variations for use in synthetic dataset preparation workflows.

---

## What It Does

Given a few base tree images, this pipeline:
- Applies 10 types of visual augmentations to each image
- Saves every generated image with a unique traceable filename
- Records full metadata for every output in `manifest.jsonl`
- Builds a visual HTML gallery for reviewing all outputs

---

## Project Structure

```
tree-augmentation/
├── base_images/            # Source tree images (input)
├── augmented_output/       # All generated images (output)
├── gallery/
│   └── index.html          # Visual review gallery (open in browser)
├── create_base_images.py   # Script to generate synthetic base images
├── augment.py              # Main augmentation pipeline
├── gallery.py              # Builds the HTML review gallery
├── config.json             # All settings and augmentation parameters
└── manifest.jsonl          # Auto-generated metadata for every image
```

---

## Setup

### Requirements
- Python 3.8 or higher
- Pillow library

### Install dependencies
```bash
pip install Pillow
```

### Clone or download the project
```bash
cd tree-augmentation
```

---

## How To Run

### Step 1 — Generate base images (only needed once)
```bash
python create_base_images.py
```

### Step 2 — Run the augmentation pipeline
```bash
python augment.py
```

### Step 3 — Build the visual gallery
```bash
python gallery.py
```

### Step 4 — Open the gallery
Open `gallery/index.html` in any browser to visually review all outputs.

> Always run in this order: `augment.py` first, then `gallery.py`

---

## Augmentation Types

| Type | What It Does |
|---|---|
| `brightness` | Makes image darker or brighter (factors: 0.5, 0.75, 1.25, 1.5) |
| `blur` | Applies gaussian blur (radius: 1, 2, 4) |
| `rotation` | Rotates image left or right (angles: -30, -15, 15, 30 degrees) |
| `crop` | Zooms in by cropping edges (15% margin) |
| `contrast` | Increases or decreases contrast (factors: 0.5, 0.75, 1.25, 1.5) |
| `weather_rain` | Overlays random rain streak lines |
| `weather_fog` | Adds a semi-transparent fog layer |
| `color_temp_warm` | Boosts red channel, reduces blue (warm/sunset look) |
| `color_temp_cool` | Boosts blue channel, reduces red (cool/cloudy look) |
| `occlusion` | Adds random black boxes to partially hide the tree |

---

## Configuration

All settings live in `config.json`. You can change them without touching the code.

```json
{
  "variations_per_image": 6,
  "augmentations": {
    "brightness": {
      "enabled": true,
      "factors": [0.5, 0.75, 1.25, 1.5]
    },
    "blur": {
      "enabled": true,
      "radius_values": [1, 2, 4]
    }
  }
}
```

To **disable** any augmentation, set `"enabled": false`.
To **add more values**, just add to the list (e.g. more rotation angles).

---

## Metadata Format

Every generated image is recorded in `manifest.jsonl` (one JSON object per line):

```json
{
  "source_image_id": "tree_01",
  "source_license": "synthetic/contributor-created",
  "species_label": "unknown",
  "original_dimensions": [600, 500],
  "generated_image_id": "tree_01__brightness__20260506_034255_800763.jpg",
  "augmentation_type": "brightness",
  "augmentation_params": {"factor": 0.5},
  "output_file_path": "augmented_output/tree_01__brightness__....jpg",
  "generation_timestamp": "2026-05-06T03:42:55Z"
}
```

Every output is fully traceable back to its source image.

---

## Sample Results

| Metric | Value |
|---|---|
| Base images | 5 |
| Total images generated | 105 |
| Augmentation types | 10 |
| Failed generations | 0 |
| Processing time | ~0.82 seconds |

---

## Data

All base images are **synthetically generated** using Python and Pillow.
No real, proprietary, or restricted-license images are used anywhere in this project.

---

## Assumptions and Limitations

- Base images must be `.jpg`, `.jpeg`, or `.png` format
- Weather effects are randomised so results vary slightly each run
- Occlusion boxes are placed randomly — not semantically targeted
- No botanical accuracy is guaranteed (images are synthetic placeholders)
- Not designed for production-scale datasets (no parallel processing)

---

## Scaling Notes

To scale this pipeline for larger datasets:
- Add `multiprocessing` to process images in parallel
- Store outputs in cloud storage (S3, GCS) by changing the output path in `config.json`
- Switch manifest format to a database for querying large manifests
- Add a job queue (e.g. Celery) for distributed processing

---

## Integration Notes

This pipeline can plug into a broader data preparation workflow by:
- Pointing `input_dir` to any image folder
- Reading `manifest.jsonl` downstream for dataset labelling tools
- Extending `augment.py` with new augmentation functions following the same pattern

---

## License

All code and synthetic images in this project are open and freely reusable.

cd tree-image-augmentation