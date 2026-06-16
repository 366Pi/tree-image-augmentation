# 🌳 Tree Image Augmentation Pipeline
### FloCard Tree Planters App — AI Training Dataset Generation

A hybrid image augmentation pipeline that takes a small set of real tree seed images and generates a large, labeled synthetic dataset using **classical augmentation** and **DCGAN** — built for training AI models to identify tree species, health conditions, and image quality.

---

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [What it generates](#what-it-generates)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [How to Clone and Run](#how-to-clone-and-run)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Augmentation Types](#augmentation-types)
- [GAN Pipeline](#gan-pipeline)
- [Output and Results](#output-and-results)
- [Assumptions and Limitations](#assumptions-and-limitations)

---

## Project Overview

FloCard's Tree Planters App allows field workers to capture tree photos in remote areas. These images are used to create blockchain-based tree records. To build an AI that automatically verifies tree species, health, and image quality — a large and diverse training dataset is needed.

This pipeline solves that by:
- Taking 5 real seed images
- Generating 1355+ labeled variations
- Training a DCGAN to create brand new synthetic tree images
- Packaging everything into a reviewable, exportable dataset

---

## What it generates

| Metric | Value |
|---|---|
| Seed images | 5 real tree photos |
| Augmentation types | 22 |
| Total images generated | 1355+ |
| GAN-generated images | 20+ |
| Metadata fields per image | 12 |
| Automated tests | 43 / 43 passing |

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3 | Main programming language |
| Pillow (PIL) | All image transformations |
| PyTorch | DCGAN training and generation |
| torchvision | Image loading and preprocessing |
| JSON / JSONL | Settings and metadata tracking |
| HTML + CSS + JS | Visual gallery for review |
| zipfile | Dataset packaging and export |

---

## Prerequisites

Make sure you have the following installed before cloning:

- **Python 3.8 or higher** — [Download here](https://www.python.org/downloads/)
- **Git** — [Download here](https://git-scm.com/downloads)
- **pip** — comes with Python

Check your versions:
```bash
python --version
git --version
pip --version
```

---

## How to Clone and Run

### Step 1 — Fork the repository
Click the **Fork** button at the top right of this page to create your own copy.

### Step 2 — Clone the forked repository
```bash
git clone https://github.com/YOUR-USERNAME/tree-image-augmentation
```
Replace `YOUR-USERNAME` with your GitHub username.

### Step 3 — Go into the project folder
```bash
cd tree-image-augmentation
```

### Step 4 — Install required libraries
```bash
pip install Pillow torch torchvision
```

### Step 5 — Add your seed images
Place your tree photos inside the `base_images/` folder.
Supported formats: `.jpg`, `.jpeg`, `.png`

> ⚠️ Do NOT commit private geo-tagged images or restricted-license photos.
> You can use the synthetic image generator instead:
> ```bash
> python create_base_images.py
> ```

### Step 6 — Run the augmentation pipeline
```bash
python augment.py
```
This generates all image variations and writes `manifest.jsonl`.

### Step 7 — Build the visual gallery
```bash
python gallery.py
```
Open `gallery/index.html` in your browser to review all outputs.

### Step 8 — Train the GAN (optional — takes ~70 min on CPU)
```bash
python gan_train.py
```
Saves trained model to `gan_models/generator_final.pth`.

### Step 9 — Generate new images using GAN
```bash
python gan_generate.py
```
Produces 20 new synthetic tree images added to `augmented_output/`.

### Step 10 — Run automated tests
```bash
python test_pipeline.py
```
Expected output:
```
Tests passed : 43 / 43
Tests failed : 0 / 43
🎉 All tests passed! Project is ready.
```

### Step 11 — Export the dataset
```bash
python export_dataset.py
```
Creates a ZIP file with all images and manifest — ready to share.

---

## Project Structure

```
tree-image-augmentation/
├── base_images/              # Place your seed images here
├── augmented_output/         # Generated images saved here (auto-created)
├── gallery/
│   └── index.html            # Visual review page (auto-created)
├── gan_models/               # Trained GAN model saved here (auto-created)
│   ├── generator_final.pth
│   ├── gan_config.json
│   └── training_log.jsonl
├── augment.py                # Main augmentation pipeline
├── config.json               # All settings — edit this to customize
├── create_base_images.py     # Generates synthetic placeholder trees
├── gallery.py                # Builds HTML gallery from manifest
├── gan_train.py              # Trains DCGAN on seed images
├── gan_generate.py           # Generates images using trained GAN
├── export_dataset.py         # Packages images + manifest as ZIP
├── test_pipeline.py          # 43 automated validation checks
├── manifest.jsonl            # Auto-generated metadata (one line per image)
└── README.md                 # This file
```

---

## Configuration

All settings are in `config.json` — no code changes needed:

```json
{
  "species_label": "mango",
  "growth_stage": "mature",
  "augmentations": {
    "brightness": { "enabled": true, "factors": [0.5, 0.75, 1.25, 1.5] },
    "season": { "enabled": true, "types": ["spring", "summer", "monsoon", "winter"] },
    "health": { "enabled": true, "conditions": ["healthy", "stressed", "diseased"] }
  }
}
```

**To change species:** update `species_label` to `"neem"`, `"banyan"`, `"peepal"` etc.
**To disable an augmentation:** set `"enabled": false`
**To add more brightness levels:** add values to `"factors"` list

---

## Augmentation Types

| Type | Variations | What it simulates |
|---|---|---|
| Brightness | 4 | Dark or overexposed capture |
| Blur | 3 | Out of focus camera |
| Rotation | 4 | Tilted phone angle |
| Crop | 1 | Zoomed in capture |
| Contrast | 4 | Camera contrast settings |
| Weather Rain | 1 | Rainy field capture |
| Weather Fog | 1 | Misty conditions |
| Color Temperature | 2 | Warm / cool lighting |
| Occlusion | 1 | Branch blocking camera |
| Season | 4 | Spring / Summer / Monsoon / Winter |
| Time of Day | 3 | Morning / Noon / Evening |
| Health | 3 | Healthy / Stressed / Diseased |
| Noise | 3 | Low quality mobile sensor |
| Motion Blur | 2 | Shaky hand capture |

---

## GAN Pipeline

The DCGAN consists of two competing networks:

**Generator** — takes 100 random numbers (noise) → outputs a 64×64 tree image
**Discriminator** — takes an image → outputs real or fake probability

After 200 training epochs they produce realistic synthetic tree images.

```bash
# Train
python gan_train.py --epochs 200 --image-size 64

# Generate
python gan_generate.py --count 20 --model gan_models/generator_final.pth
```

---

## Output and Results

- `augmented_output/` — all generated images
- `manifest.jsonl` — one JSON record per image with 12 metadata fields
- `gallery/index.html` — open in browser, filter by augmentation type
- `augmented_images_SPECIES_DATE.zip` — exportable dataset package

---

## Assumptions and Limitations

- GAN trained on 5 images — more seed images produce better quality
- Weather effects are overlay-based — not photorealistic on all image types
- GAN output is 64×64 upscaled to 256×256 — not full resolution
- Training runs on CPU — a GPU would be significantly faster
- Species label is set manually in config — not auto-detected

---

## Data

All synthetic images generated by this pipeline are open and freely reusable.
Real seed images used for training are provided by FloCard and are not committed to this repository.

For access to seed images contact: **abhijeet@366pitech.com**
