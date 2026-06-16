"""
Gallery Generator
Reads manifest.jsonl and builds a visual HTML review page in gallery/index.html
"""

import os
import json

MANIFEST    = "manifest.jsonl"
GALLERY_DIR = "gallery"
OUTPUT_DIR  = "augmented_output"

# ─────────────────────────────────────────
# Load manifest
# ─────────────────────────────────────────
entries = []
with open(MANIFEST) as f:
    for line in f:
        line = line.strip()
        if line:
            entries.append(json.loads(line))

# Group by source image
groups = {}
for e in entries:
    sid = e["source_image_id"]
    groups.setdefault(sid, []).append(e)

# Collect all aug types for filter buttons
all_types = sorted(set(e["augmentation_type"] for e in entries))

# ─────────────────────────────────────────
# Build cards HTML
# ─────────────────────────────────────────
cards_html = ""
for source_id, items in groups.items():
    cards_html += f"""
    <div class="source-group">
      <h2 class="source-title">🌳 {source_id}</h2>
      <div class="card-grid">
    """
    for e in items:
        img_rel  = os.path.join("..", OUTPUT_DIR, e["generated_image_id"]).replace("\\", "/")
        aug_type = e["augmentation_type"]
        params   = json.dumps(e["augmentation_params"], separators=(",", ":"))
        ts       = e["generation_timestamp"][:19].replace("T", " ")
        cards_html += f"""
        <div class="card" data-aug="{aug_type}">
          <img src="{img_rel}" alt="{aug_type}" loading="lazy"/>
          <div class="card-body">
            <span class="badge">{aug_type}</span>
            <p class="params">{params}</p>
            <p class="ts">{ts}</p>
          </div>
        </div>
        """
    cards_html += "</div></div>"

# ─────────────────────────────────────────
# Filter buttons
# ─────────────────────────────────────────
btn_html = '<button class="filter-btn active" onclick="filter(\'all\')">All</button>\n'
for t in all_types:
    btn_html += f'<button class="filter-btn" onclick="filter(\'{t}\')">{t}</button>\n'

# ─────────────────────────────────────────
# Full HTML page
# ─────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Tree Augmentation Gallery</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: system-ui, sans-serif; background: #f0f4f0; color: #222; }}

  header {{
    background: #2d5a27;
    color: #fff;
    padding: 24px 32px;
  }}
  header h1 {{ font-size: 24px; font-weight: 600; }}
  header p  {{ font-size: 14px; opacity: 0.8; margin-top: 4px; }}

  .stats {{
    display: flex;
    gap: 24px;
    padding: 20px 32px;
    background: #fff;
    border-bottom: 1px solid #dde8dd;
    flex-wrap: wrap;
  }}
  .stat {{ text-align: center; }}
  .stat-num {{ font-size: 28px; font-weight: 700; color: #2d5a27; }}
  .stat-label {{ font-size: 12px; color: #666; }}

  .filters {{
    padding: 16px 32px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    background: #fff;
    border-bottom: 1px solid #dde8dd;
  }}
  .filter-btn {{
    padding: 6px 14px;
    border: 1.5px solid #2d5a27;
    border-radius: 20px;
    background: #fff;
    color: #2d5a27;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.15s;
  }}
  .filter-btn:hover, .filter-btn.active {{
    background: #2d5a27;
    color: #fff;
  }}

  .source-group {{ padding: 24px 32px 8px; }}
  .source-title {{
    font-size: 18px;
    font-weight: 600;
    color: #2d5a27;
    margin-bottom: 16px;
    padding-bottom: 8px;
    border-bottom: 2px solid #c8e0c5;
  }}

  .card-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }}

  .card {{
    background: #fff;
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    transition: transform 0.15s, box-shadow 0.15s;
  }}
  .card:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 16px rgba(0,0,0,0.13);
  }}
  .card img {{
    width: 100%;
    height: 160px;
    object-fit: cover;
    display: block;
  }}
  .card-body {{ padding: 10px 12px 12px; }}
  .badge {{
    display: inline-block;
    background: #e8f5e5;
    color: #2d5a27;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 600;
    padding: 2px 8px;
    margin-bottom: 6px;
  }}
  .params {{
    font-size: 11px;
    color: #555;
    font-family: monospace;
    word-break: break-all;
    margin-bottom: 4px;
  }}
  .ts {{ font-size: 10px; color: #999; }}

  .hidden {{ display: none !important; }}

  footer {{
    text-align: center;
    padding: 24px;
    font-size: 12px;
    color: #888;
  }}
</style>
</head>
<body>

<header>
  <h1>🌳 Tree Augmentation Gallery</h1>
  <p>Visual review of all generated image variations</p>
</header>

<div class="stats">
  <div class="stat">
    <div class="stat-num">{len(entries)}</div>
    <div class="stat-label">Total Images</div>
  </div>
  <div class="stat">
    <div class="stat-num">{len(groups)}</div>
    <div class="stat-label">Base Images</div>
  </div>
  <div class="stat">
    <div class="stat-num">{len(all_types)}</div>
    <div class="stat-label">Augmentation Types</div>
  </div>
  <div class="stat">
    <div class="stat-num">{round(len(entries)/len(groups)) if groups else 0}</div>
    <div class="stat-label">Avg Variations Each</div>
  </div>
</div>

<div class="filters">
  {btn_html}
</div>

{cards_html}

<footer>Generated by Tree Augmentation Pipeline &mdash; open-source synthetic data only</footer>

<script>
function filter(type) {{
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');

  document.querySelectorAll('.card').forEach(card => {{
    if (type === 'all' || card.dataset.aug === type) {{
      card.classList.remove('hidden');
    }} else {{
      card.classList.add('hidden');
    }}
  }});
}}
</script>
</body>
</html>
"""

out_path = os.path.join(GALLERY_DIR, "index.html")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"\n🎨 Gallery built!")
print(f"   Total images : {len(entries)}")
print(f"   Base images  : {len(groups)}")
print(f"   Aug types    : {len(all_types)}")
print(f"\n✅ Open this file in your browser:")
print(f"   {os.path.abspath(out_path)}")
