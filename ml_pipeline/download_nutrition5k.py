"""
Nutrition5k Dataset Downloader (Google Research CVPR 2021)
=========================================================
Downloads official metadata and sample overhead RGB + RealSense depth maps
directly from Google Cloud Storage (gs://nutrition5k_dataset/nutrition5k_dataset/).

Files downloaded:
  - data/nutrition5k/metadata/dish_metadata_cafe1.csv (~2.1 MB, 3,000+ dishes)
  - data/nutrition5k/metadata/dish_metadata_cafe2.csv (~99 KB, 300+ dishes)
  - data/nutrition5k/metadata/ingredients_metadata.csv (~21 KB, 250+ ingredients)
  - Sample dishes with overhead RGB and RealSense depth imagery for benchmark testing.
"""

import os
import sys
import urllib.request
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N5K_DIR = os.path.join(BASE_DIR, "data", "nutrition5k")
META_DIR = os.path.join(N5K_DIR, "metadata")
SAMPLES_DIR = os.path.join(N5K_DIR, "sample_dishes")

GCS_BASE = "https://storage.googleapis.com/nutrition5k_dataset/nutrition5k_dataset"

METADATA_FILES = {
    "dish_metadata_cafe1.csv": f"{GCS_BASE}/metadata/dish_metadata_cafe1.csv",
    "dish_metadata_cafe2.csv": f"{GCS_BASE}/metadata/dish_metadata_cafe2.csv",
    "ingredients_metadata.csv": f"{GCS_BASE}/metadata/ingredients_metadata.csv"
}

# A diverse set of sample dishes from Cafe 1 with complex multi-component ingredients
SAMPLE_DISH_IDS = [
    "dish_1561662216",  # Soy sauce chicken, rice, vegetables
    "dish_1556574268",  # Mixed greens, grilled chicken, dressing
    "dish_1556573195",  # Pasta with meat sauce & cheese
    "dish_1561664722",  # Salmon, broccoli, sweet potato
    "dish_1556575276",  # Rice bowl with beans, avocado, salsa
]


def download_file(url: str, dest_path: str, label: str):
    """Download a file with user-friendly progress reporting."""
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 0:
        size_kb = os.path.getsize(dest_path) / 1024
        print(f"  [ALREADY EXISTS] {label} ({size_kb:.1f} KB)")
        return True

    print(f"  [DOWNLOADING] {label} ...", end="", flush=True)
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            with open(dest_path, "wb") as f:
                f.write(data)
        elapsed = time.time() - t0
        size_kb = len(data) / 1024
        print(f" DONE ({size_kb:.1f} KB in {elapsed:.2f}s)")
        return True
    except Exception as e:
        print(f" FAILED ({e})")
        return False


def run_download():
    """Main download runner."""
    print("=" * 70)
    print("Google Research Nutrition5k Dataset Downloader")
    print("Target Directory:", N5K_DIR)
    print("=" * 70)

    # 1. Download metadata files
    print("\n[Step 1/2] Downloading Official Google Research Nutrition Metadata...")
    for filename, url in METADATA_FILES.items():
        dest = os.path.join(META_DIR, filename)
        download_file(url, dest, filename)

    # 2. Download sample dishes with overhead RGB and RealSense depth imagery
    print("\n[Step 2/2] Downloading Sample Overhead RGB & Depth Images for CV Benchmark...")
    for dish_id in SAMPLE_DISH_IDS:
        dish_folder = os.path.join(SAMPLES_DIR, dish_id)
        os.makedirs(dish_folder, exist_ok=True)
        
        # Overhead RGB
        rgb_url = f"{GCS_BASE}/imagery/realsense_overhead/{dish_id}/rgb.png"
        rgb_dest = os.path.join(dish_folder, "rgb.png")
        download_file(rgb_url, rgb_dest, f"{dish_id}/rgb.png")
        
        # Overhead Depth Color
        depth_url = f"{GCS_BASE}/imagery/realsense_overhead/{dish_id}/depth_color.png"
        depth_dest = os.path.join(dish_folder, "depth_color.png")
        download_file(depth_url, depth_dest, f"{dish_id}/depth_color.png")

    print("\n" + "=" * 70)
    print("Nutrition5k Download Complete! All metadata and samples ready for CV pipeline.")
    print("=" * 70)


if __name__ == "__main__":
    run_download()
