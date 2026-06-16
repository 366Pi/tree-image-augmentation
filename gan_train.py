"""
GAN Training Script — FloCard Tree Image Augmentation
Trains a DCGAN (Deep Convolutional GAN) on base tree images.
Saves the trained Generator model for later use in gan_generate.py

Usage:
    python gan_train.py
    python gan_train.py --epochs 100 --image-size 64
"""

import os
import json
import time
import argparse
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from PIL import Image
from datetime import datetime

# ─────────────────────────────────────────
# Arguments
# ─────────────────────────────────────────
parser = argparse.ArgumentParser(description="Train DCGAN on tree images")
parser.add_argument("--epochs",     type=int, default=200,  help="Number of training epochs")
parser.add_argument("--image-size", type=int, default=64,   help="Image size (64 recommended)")
parser.add_argument("--batch-size", type=int, default=4,    help="Batch size (keep small for few images)")
parser.add_argument("--latent-dim", type=int, default=100,  help="Size of the noise vector")
parser.add_argument("--lr",         type=float, default=0.0002, help="Learning rate")
parser.add_argument("--input-dir",  type=str, default="base_images", help="Folder with seed images")
parser.add_argument("--model-dir",  type=str, default="gan_models",  help="Folder to save trained models")
args = parser.parse_args()

IMAGE_SIZE  = args.image_size
LATENT_DIM  = args.latent_dim
BATCH_SIZE  = args.batch_size
EPOCHS      = args.epochs
LR          = args.lr
INPUT_DIR   = args.input_dir
MODEL_DIR   = args.model_dir

os.makedirs(MODEL_DIR, exist_ok=True)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n🌳 FloCard GAN Trainer")
print(f"   Device      : {DEVICE}")
print(f"   Image size  : {IMAGE_SIZE}×{IMAGE_SIZE}")
print(f"   Epochs      : {EPOCHS}")
print(f"   Batch size  : {BATCH_SIZE}")
print(f"   Input dir   : {INPUT_DIR}/")
print(f"   Model dir   : {MODEL_DIR}/")
print("=" * 55)


# ─────────────────────────────────────────
# Dataset
# ─────────────────────────────────────────
class TreeDataset(Dataset):
    """Loads tree images from a folder and applies transforms."""

    def __init__(self, folder, image_size):
        self.paths = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ]
        if not self.paths:
            raise ValueError(f"No images found in {folder}/")

        self.transform = transforms.Compose([
            transforms.Resize((image_size, image_size)),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

    def __len__(self):
        # Repeat the small dataset to fill more batches
        return max(len(self.paths) * 40, 200)

    def __getitem__(self, idx):
        path = self.paths[idx % len(self.paths)]
        img  = Image.open(path).convert("RGB")
        return self.transform(img)


# ─────────────────────────────────────────
# Generator — creates fake images from noise
# ─────────────────────────────────────────
class Generator(nn.Module):
    """DCGAN Generator — takes random noise, outputs a fake tree image."""

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
        img = self.model(out)
        return img


# ─────────────────────────────────────────
# Discriminator — judges real vs fake
# ─────────────────────────────────────────
class Discriminator(nn.Module):
    """DCGAN Discriminator — takes an image, outputs real/fake probability."""

    def __init__(self, image_size):
        super().__init__()

        def block(in_ch, out_ch, bn=True):
            layers = [nn.Conv2d(in_ch, out_ch, 4, stride=2, padding=1)]
            if bn:
                layers.append(nn.BatchNorm2d(out_ch))
            layers.append(nn.LeakyReLU(0.2, inplace=True))
            return layers

        self.model = nn.Sequential(
            *block(3,   64,  bn=False),
            *block(64,  128),
            *block(128, 256),
            *block(256, 512),
        )
        ds = image_size // 16
        self.fc = nn.Sequential(
            nn.Linear(512 * ds * ds, 1),
            nn.Sigmoid()
        )

    def forward(self, img):
        out = self.model(img)
        out = out.view(out.shape[0], -1)
        return self.fc(out)


# ─────────────────────────────────────────
# Training loop
# ─────────────────────────────────────────
dataset    = TreeDataset(INPUT_DIR, IMAGE_SIZE)
dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, drop_last=True)

G = Generator(LATENT_DIM, IMAGE_SIZE).to(DEVICE)
D = Discriminator(IMAGE_SIZE).to(DEVICE)

optimizer_G = optim.Adam(G.parameters(), lr=LR, betas=(0.5, 0.999))
optimizer_D = optim.Adam(D.parameters(), lr=LR, betas=(0.5, 0.999))
criterion   = nn.BCELoss()

print(f"\n   Dataset size    : {len(dataset)} samples ({len(dataset.paths)} real images × repeats)")
print(f"   Generator params: {sum(p.numel() for p in G.parameters()):,}")
print(f"   Discriminator   : {sum(p.numel() for p in D.parameters()):,}")
print(f"\n🚀 Training started...\n")

start_time = time.time()
log_entries = []

for epoch in range(1, EPOCHS + 1):
    g_loss_total = 0.0
    d_loss_total = 0.0
    batches      = 0

    for real_imgs in dataloader:
        real_imgs = real_imgs.to(DEVICE)
        b         = real_imgs.size(0)

        real_labels = torch.ones(b, 1).to(DEVICE)
        fake_labels = torch.zeros(b, 1).to(DEVICE)

        # ── Train Discriminator ──
        optimizer_D.zero_grad()
        z         = torch.randn(b, LATENT_DIM).to(DEVICE)
        fake_imgs = G(z).detach()
        d_real    = D(real_imgs)
        d_fake    = D(fake_imgs)
        d_loss    = criterion(d_real, real_labels) + criterion(d_fake, fake_labels)
        d_loss.backward()
        optimizer_D.step()

        # ── Train Generator ──
        optimizer_G.zero_grad()
        z         = torch.randn(b, LATENT_DIM).to(DEVICE)
        fake_imgs = G(z)
        g_loss    = criterion(D(fake_imgs), real_labels)
        g_loss.backward()
        optimizer_G.step()

        g_loss_total += g_loss.item()
        d_loss_total += d_loss.item()
        batches      += 1

    avg_g = round(g_loss_total / batches, 4)
    avg_d = round(d_loss_total / batches, 4)

    log_entries.append({
        "epoch"  : epoch,
        "g_loss" : avg_g,
        "d_loss" : avg_d,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    })

    if epoch % 10 == 0 or epoch == 1:
        elapsed = round(time.time() - start_time, 1)
        print(f"  Epoch {epoch:4d}/{EPOCHS}  |  G_loss: {avg_g:.4f}  |  D_loss: {avg_d:.4f}  |  {elapsed}s")

    # Save checkpoint every 50 epochs
    if epoch % 50 == 0:
        ckpt_path = os.path.join(MODEL_DIR, f"generator_epoch_{epoch}.pth")
        torch.save(G.state_dict(), ckpt_path)
        print(f"  💾 Checkpoint saved: {ckpt_path}")

# ─────────────────────────────────────────
# Save final model
# ─────────────────────────────────────────
final_path = os.path.join(MODEL_DIR, "generator_final.pth")
torch.save(G.state_dict(), final_path)

config_path = os.path.join(MODEL_DIR, "gan_config.json")
with open(config_path, "w") as f:
    json.dump({
        "latent_dim"  : LATENT_DIM,
        "image_size"  : IMAGE_SIZE,
        "epochs"      : EPOCHS,
        "trained_on"  : len(dataset.paths),
        "device"      : str(DEVICE),
        "trained_at"  : datetime.utcnow().isoformat() + "Z"
    }, f, indent=2)

log_path = os.path.join(MODEL_DIR, "training_log.jsonl")
with open(log_path, "w") as f:
    for entry in log_entries:
        f.write(json.dumps(entry) + "\n")

total_time = round(time.time() - start_time, 1)
print(f"\n{'=' * 55}")
print(f"✅ Training complete!")
print(f"   Total time      : {total_time}s")
print(f"   Final model     : {final_path}")
print(f"   GAN config      : {config_path}")
print(f"   Training log    : {log_path}")
print(f"{'=' * 55}")
print(f"\n▶  Next: run  python gan_generate.py  to generate new images.")