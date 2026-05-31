import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import random

random.seed(42)
np.random.seed(42)

# ── Absolute output path ──────────────────────────────────────────────────────
OUTPUT_DIR = Path(r"D:\MOST IMPORTANT\RegiosAnalysis\data")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "transactions.csv"

# ── Config ────────────────────────────────────────────────────────────────────
N = 50000
START = datetime(2023, 1, 1)
END   = datetime(2024, 12, 31)

REGIONS = ['Jakarta', 'Yogyakarta', 'Surabaya', 'Medan', 'Bali']
CATEGORIES = ['F&B', 'Electronics', 'Fashion', 'Grocery', 'Healthcare',
              'Home & Living', 'Travel', 'Education']
CHANNELS = ['online', 'offline']
AGE_GROUPS = ['18-24', '25-34', '35-44', '45+']

REGION_PROFILE = {
    'Jakarta': {
        'category_weights': [0.20, 0.20, 0.18, 0.10, 0.08, 0.10, 0.08, 0.06],
        'channel_weights':  [0.70, 0.30],
        'age_weights':      [0.25, 0.38, 0.25, 0.12],
        'spend_multiplier': 1.45,
    },
    'Yogyakarta': {
        'category_weights': [0.25, 0.10, 0.18, 0.15, 0.10, 0.08, 0.05, 0.09],
        'channel_weights':  [0.40, 0.60],
        'age_weights':      [0.38, 0.30, 0.20, 0.12],
        'spend_multiplier': 0.70,
    },
    'Surabaya': {
        'category_weights': [0.20, 0.18, 0.17, 0.13, 0.10, 0.10, 0.07, 0.05],
        'channel_weights':  [0.55, 0.45],
        'age_weights':      [0.22, 0.35, 0.28, 0.15],
        'spend_multiplier': 1.20,
    },
    'Medan': {
        'category_weights': [0.28, 0.12, 0.15, 0.18, 0.10, 0.08, 0.05, 0.04],
        'channel_weights':  [0.45, 0.55],
        'age_weights':      [0.25, 0.32, 0.28, 0.15],
        'spend_multiplier': 1.00,
    },
    'Bali': {
        'category_weights': [0.28, 0.08, 0.15, 0.10, 0.07, 0.08, 0.20, 0.04],
        'channel_weights':  [0.55, 0.45],
        'age_weights':      [0.20, 0.30, 0.30, 0.20],
        'spend_multiplier': 1.30,
    },
}

CATEGORY_SPEND = {
    'F&B':           (15000, 350000),
    'Electronics':   (200000, 8000000),
    'Fashion':       (80000, 2500000),
    'Grocery':       (30000, 600000),
    'Healthcare':    (50000, 1500000),
    'Home & Living': (100000, 3000000),
    'Travel':        (200000, 5000000),
    'Education':     (100000, 2000000),
}

AGE_MULTIPLIER = {
    '18-24': 0.75,
    '25-34': 1.20,
    '35-44': 1.10,
    '45+':   0.95,
}

HOUR_WEIGHTS = [
    0.5, 0.3, 0.2, 0.2, 0.2, 0.4,
    0.8, 1.2, 1.5, 1.3, 1.2, 1.4,
    1.6, 1.4, 1.3, 1.4, 1.5, 1.7,
    2.0, 2.2, 2.0, 1.8, 1.4, 0.9,
]
HOUR_WEIGHTS = np.array(HOUR_WEIGHTS)
HOUR_WEIGHTS /= HOUR_WEIGHTS.sum()

DOW_WEIGHTS = np.array([0.90, 0.88, 0.92, 0.95, 1.10, 1.35, 1.30])
DOW_WEIGHTS /= DOW_WEIGHTS.sum()

records = []
transaction_id = 1
REGION_VOLUME = {
    'Jakarta': 0.30,
    'Yogyakarta': 0.14,
    'Surabaya': 0.25,
    'Medan': 0.16,
    'Bali': 0.15
}

total_days = (END - START).days
day_offsets = np.arange(total_days)
dow_of_each_day = (START.weekday() + day_offsets) % 7
day_probs = DOW_WEIGHTS[dow_of_each_day]
day_probs /= day_probs.sum()

for region, vol_share in REGION_VOLUME.items():
    n_region = int(N * vol_share)
    profile = REGION_PROFILE[region]

    for _ in range(n_region):
        day_offset = np.random.choice(day_offsets, p=day_probs)
        hour = np.random.choice(24, p=HOUR_WEIGHTS)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)

        timestamp = START + timedelta(
            days=int(day_offset),
            hours=int(hour),
            minutes=minute,
            seconds=second
        )

        category = np.random.choice(CATEGORIES, p=profile['category_weights'])
        channel = np.random.choice(CHANNELS, p=profile['channel_weights'])
        age_group = np.random.choice(AGE_GROUPS, p=profile['age_weights'])

        low, high = CATEGORY_SPEND[category]
        base_amount = np.random.lognormal(
            mean=np.log((low + high) / 2),
            sigma=0.55
        )
        base_amount = np.clip(base_amount, low, high)

        amount = (
            base_amount
            * profile['spend_multiplier']
            * AGE_MULTIPLIER[age_group]
        )

        if channel == 'online':
            amount *= random.uniform(1.02, 1.15)

        amount = round(amount / 500) * 500

        records.append({
            'transaction_id': f'TXN{transaction_id:06d}',
            'region': region,
            'category': category,
            'amount_idr': int(amount),
            'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'channel': channel,
            'age_group': age_group,
        })
        transaction_id += 1

df = pd.DataFrame(records).sample(frac=1, random_state=42).reset_index(drop=True)

df.to_csv(OUTPUT_FILE, index=False)

print(f"✅ Dataset saved to: {OUTPUT_FILE}")
print(f"Rows: {len(df):,}")
print(df.head())