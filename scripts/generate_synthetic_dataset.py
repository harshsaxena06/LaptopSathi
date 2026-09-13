"""
Generates a realistic synthetic laptop knowledge-base CSV to seed the system,
standing in for the Kaggle datasets / manufacturer spec sheets described in
the PRD (no live scraping is used, by design).

Run:
    python scripts/generate_synthetic_dataset.py
"""
import random
from pathlib import Path

import numpy as np
import pandas as pd

RNG = random.Random(42)
NP_RNG = np.random.default_rng(42)

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_PATH = BASE_DIR / "data" / "raw" / "laptops_raw.csv"

BRANDS = ["Dell", "HP", "Lenovo", "Asus", "Acer", "Apple", "MSI", "Samsung", "LG", "Microsoft"]

CPUS = [
    ("Intel Core i3-1215U", 6, 8, 1.2, 4.4, 4800, 10500, 15),
    ("Intel Core i5-1240P", 12, 16, 1.7, 4.4, 8200, 17800, 28),
    ("Intel Core i5-13500H", 12, 16, 2.6, 4.7, 9500, 19500, 45),
    ("Intel Core i7-1355U", 10, 12, 1.7, 5.0, 9800, 18900, 15),
    ("Intel Core i7-13700H", 14, 20, 2.4, 5.0, 10800, 22300, 45),
    ("Intel Core i9-13900H", 14, 20, 2.6, 5.4, 11500, 23800, 45),
    ("AMD Ryzen 5 7530U", 6, 12, 2.0, 4.5, 7900, 16200, 15),
    ("AMD Ryzen 7 7735HS", 8, 16, 3.2, 4.75, 10200, 21200, 35),
    ("AMD Ryzen 9 7940HS", 8, 16, 4.0, 5.2, 11200, 23100, 45),
    ("Apple M2", 8, 8, 3.5, 3.5, 10500, 21900, 20),
    ("Apple M3 Pro", 12, 12, 4.0, 4.0, 12000, 26500, 30),
]

GPUS = [
    ("Intel Iris Xe Graphics", 0, False, False, 3200),
    ("Intel UHD Graphics", 0, False, False, 2100),
    ("AMD Radeon Graphics (Integrated)", 0, False, False, 3400),
    ("NVIDIA GeForce RTX 2050", 4, True, True, 9800),
    ("NVIDIA GeForce RTX 3050", 6, True, True, 12500),
    ("NVIDIA GeForce RTX 4050", 6, True, True, 15800),
    ("NVIDIA GeForce RTX 4060", 8, True, True, 19500),
    ("NVIDIA GeForce RTX 4070", 8, True, True, 24800),
    ("NVIDIA GeForce RTX 4080", 12, True, True, 29500),
    ("Apple M2 GPU (Integrated)", 0, False, False, 11000),
]

RESOLUTIONS = ["1366x768", "1920x1080", "1920x1200", "2560x1440", "2880x1800", "3840x2160"]
STORAGE_TYPES = ["SSD", "SSD", "SSD", "HDD", "Hybrid"]

MODEL_ADJECTIVES = ["Pro", "Air", "Slim", "Ultra", "Ideapad", "Vivobook", "Inspiron",
                     "Pavilion", "Nitro", "Predator", "ThinkPad", "Zenbook", "Legion",
                     "Swift", "Katana", "Galaxy Book", "Gram", "Surface Laptop"]


def make_row(idx: int) -> dict:
    brand = RNG.choice(BRANDS)
    cpu = RNG.choice(CPUS)
    cpu_name, cores, threads, base_clk, boost_clk, sc_score, mc_score, tdp = cpu

    # Apple brand should pair with Apple silicon / GPU for realism
    if brand == "Apple":
        cpu = RNG.choice([c for c in CPUS if "Apple" in c[0]])
        cpu_name, cores, threads, base_clk, boost_clk, sc_score, mc_score, tdp = cpu
        gpu = RNG.choice([g for g in GPUS if "Apple" in g[0]])
    else:
        gpu = RNG.choice([g for g in GPUS if "Apple" not in g[0]])

    gpu_name, vram, is_dedicated, cuda, gpu_bench = gpu

    ram_gb = RNG.choice([8, 8, 16, 16, 16, 32, 32, 64])
    storage_gb = RNG.choice([256, 512, 512, 1024, 2048])
    storage_type = RNG.choice(STORAGE_TYPES) if storage_gb <= 1024 else "SSD"

    display_size = round(RNG.choice([13.3, 14.0, 15.6, 16.0, 17.3]), 1)
    resolution = RNG.choice(RESOLUTIONS)
    refresh_rate = RNG.choice([60, 60, 60, 90, 120, 144, 165]) if is_dedicated else RNG.choice([60, 60, 90])

    battery_whr = round(RNG.uniform(40, 99), 1)
    battery_life = round(max(3.0, battery_whr / RNG.uniform(7, 13)), 1)
    weight_kg = round(RNG.uniform(1.1, 3.1) + (0.3 if is_dedicated else 0), 2)

    # Price model: base + component premiums + noise, roughly calibrated to INR market prices
    base_price = 28000
    price = (
        base_price
        + mc_score * 3.2
        + gpu_bench * 5.5
        + ram_gb * 550
        + (storage_gb * 6 if storage_type == "SSD" else storage_gb * 2)
        + (display_size - 13) * 2500
        + (5000 if brand == "Apple" else 0)
        + NP_RNG.normal(0, 4000)
    )
    price = round(max(22000, price), -2)  # round to nearest 100, floor at 22k

    release_year = RNG.choice([2022, 2023, 2023, 2024, 2024, 2025])
    model_name = f"{RNG.choice(MODEL_ADJECTIVES)} {RNG.randint(1, 16)}{RNG.choice(['', 'X', 'S', ' Plus'])}"

    return {
        "model_name": model_name,
        "brand": brand,
        "cpu_name": cpu_name,
        "cpu_cores": cores,
        "cpu_threads": threads,
        "cpu_base_clock_ghz": base_clk,
        "cpu_boost_clock_ghz": boost_clk,
        "cpu_single_core_score": sc_score,
        "cpu_multi_core_score": mc_score,
        "cpu_tdp_watts": tdp,
        "gpu_name": gpu_name,
        "gpu_vram_gb": vram,
        "gpu_is_dedicated": is_dedicated,
        "gpu_supports_cuda": cuda,
        "gpu_benchmark_score": gpu_bench,
        "ram_gb": ram_gb,
        "storage_gb": storage_gb,
        "storage_type": storage_type,
        "display_size_inch": display_size,
        "display_resolution": resolution,
        "refresh_rate_hz": refresh_rate,
        "battery_whr": battery_whr,
        "battery_life_hours": battery_life,
        "weight_kg": weight_kg,
        "price_inr": price,
        "release_year": release_year,
    }


def generate(n: int = 250) -> pd.DataFrame:
    rows = [make_row(i) for i in range(n)]
    df = pd.DataFrame(rows)
    # De-duplicate exact (brand, model_name) collisions by suffixing
    df["model_name"] = df["model_name"] + " (" + (df.groupby(["brand", "model_name"]).cumcount() + 1).astype(str) + ")"
    df["model_name"] = df["model_name"].str.replace(r" \(1\)$", "", regex=True)
    return df


if __name__ == "__main__":
    df = generate(250)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_PATH, index=False)
    print(f"Generated {len(df)} synthetic laptop records -> {OUT_PATH}")
