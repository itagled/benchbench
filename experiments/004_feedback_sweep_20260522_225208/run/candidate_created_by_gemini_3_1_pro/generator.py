import argparse
import json
import os
import random
import hashlib
from typing import List

def crc16(data: bytes) -> bytes:
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return bytes([crc >> 8, crc & 0xFF])

def compress(data: bytes) -> bytes:
    out = bytearray()
    i = 0
    while i < len(data):
        control_byte_idx = len(out)
        out.append(0)
        control_byte = 0

        for bit in range(8):
            if i >= len(data):
                break

            match_len = 0
            match_dist = 0
            start_window = max(0, i - 4095)
            for j in range(start_window, i):
                l = 0
                while l < 18 and i + l < len(data) and data[j + l] == data[i + l]:
                    l += 1
                if l > match_len:
                    match_len = l
                    match_dist = i - j

            if match_len >= 3:
                control_byte |= (1 << (7 - bit))
                out.append(match_dist & 0xFF)
                out.append(((match_dist >> 8) << 4) | (match_len - 3))
                i += match_len
            else:
                out.append(data[i])
                i += 1

        out[control_byte_idx] = control_byte
    return bytes(out)

def generate_payload(rng) -> bytes:
    prefixes = [b"[SYS] OK  ", b"[NET] ERR ", b"[APP] WARN", b"[DB]  INFO"]
    suffixes = [b" 001", b" 002", b" 003", b" 004"]
    payload = rng.choice(prefixes) + rng.choice(suffixes)
    return payload

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample-count', type=int, required=True)
    parser.add_argument('--seed', type=int, required=True)
    parser.add_argument('--out-dir', type=str, required=True)
    args = parser.parse_args()

    rng = random.Random(args.seed)

    solver_dir = os.path.join(args.out_dir, "solver_bundle")
    os.makedirs(solver_dir, exist_ok=True)

    gold_items = []
    bundle_items = []

    for i in range(args.sample_count):
        item_id = f"item_{i:03d}"

        # Generate 100 blocks of 16 bytes
        uncompressed = bytearray()
        for _ in range(100):
            payload = generate_payload(rng)
            uncompressed.extend(payload)
            uncompressed.extend(crc16(payload))

        uncompressed_bytes = bytes(uncompressed)
        gold_hash = hashlib.sha256(uncompressed_bytes).hexdigest()

        compressed_bytes = compress(uncompressed_bytes)
        corrupted = bytearray(compressed_bytes)

        # Flips exactly 3 bytes
        flips = rng.sample(range(len(corrupted)), 3)
        for idx in flips:
            old = corrupted[idx]
            while True:
                new = rng.randint(0, 255)
                if new != old:
                    corrupted[idx] = new
                    break

        filename = f"corrupted_{i:03d}.bin"
        filepath = os.path.join(solver_dir, filename)
        with open(filepath, "wb") as f:
            f.write(corrupted)

        gold_items.append({
            "id": item_id,
            "answer": gold_hash
        })

        bundle_items.append({
            "id": item_id,
            "filename": filename,
            "uncompressed_size": 1600
        })

    with open(os.path.join(args.out_dir, "gold_private_sample.jsonl"), "w") as f:
        for g in gold_items:
            f.write(json.dumps(g) + "\n")

    with open(os.path.join(solver_dir, "items_private_sample.jsonl"), "w") as f:
        for b in bundle_items:
            f.write(json.dumps(b) + "\n")

if __name__ == "__main__":
    main()
