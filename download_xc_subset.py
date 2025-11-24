#!/usr/bin/env python3
r"""
download_xc_subset.py (temp-dir safe)

Same as the original downloader but adds an optional --temp-dir argument.
- Downloads originals into --temp-dir (outside Drive), converts there, then moves final WAVs into --output-dir.
- This avoids partial/intermediate files being synced into a Drive-synced folder.

Usage:
python download_xc_subset.py --output-dir "G:\My Drive\DSA598_Project\Data" --temp-dir "C:\Users\darcyme\AppData\Local\Temp\bird_xc_tmp" --per-species 120
"""
import argparse
import os
import sys
import time
import csv
from urllib.parse import quote_plus
import subprocess
import requests
from tqdm import tqdm
import pandas as pd
import shutil

XC_API = "https://xeno-canto.org/api/3/recordings"

DEFAULT_SPECIES = [
    ("Cardinalis_cardinalis", "Northern Cardinal"),
    ("Turdus_migratorius", "American Robin"),
    ("Poecile_atricapillus", "Black-capped Chickadee"),
    ("Cyanocitta-cristata", "Blue Jay"),
    ("Zonotrichia_albicollis", "White-throated Sparrow"),
    ("Junco_hyemalis", "Dark-eyed Junco"),
    ("Baeolophus_bicolor", "Tufted Titmouse"),
    ("Melospiza_melodia", "Song Sparrow"),
    ("Agelaius_phoeniceus", "Red-winged Blackbird"),
    ("Zenaida_macroura", "Mourning Dove"),
    ("Quiscalus_quiscula", "Common Grackle"),
    ("Haemorhous_mexicanus", "House Finch"),
    ("Spinus_tristis", "American Goldfinch"),
]

# Default: accept most Creative Commons licenses (excluding NC=NonCommercial, ND=NoDerivs if you want more open)
# For research/education, by-nc-sa is usually fine. For commercial use, use by, by-sa, cc0, publicdomain
DEFAULT_LICENSES = ["by-nc-sa", "by-nc-nd", "by-nc", "by-sa", "by", "cc0", "publicdomain"]

def parse_length_to_seconds(length_str):
    try:
        parts = length_str.strip().split(":")
        parts = [int(p) for p in parts]
        if len(parts) == 3:
            h, m, s = parts
            return h * 3600 + m * 60 + s
        elif len(parts) == 2:
            m, s = parts
            return m * 60 + s
        elif len(parts) == 1:
            return parts[0]
    except Exception:
        return None
    return None

def query_xc(species_query, page=1, api_key=None, max_retries=3):
    params = {"query": species_query, "page": page}
    if api_key:
        params["key"] = api_key
    
    for attempt in range(max_retries):
        try:
            r = requests.get(XC_API, params=params, timeout=60)
            r.raise_for_status()
            return r.json()
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            if attempt < max_retries - 1:
                wait_time = (attempt + 1) * 2
                print(f"  Connection issue, retrying in {wait_time}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
            else:
                raise
        except Exception as e:
            raise

def sanitize_species_folder(name):
    return "".join(c if (c.isalnum() or c in "_-") else "_" for c in name)

def download_file(url, dest_path, session=None):
    session = session or requests
    tmp_path = dest_path + ".part"
    with session.get(url, stream=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0))
        with open(tmp_path, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=os.path.basename(dest_path), leave=False) as pbar:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))
    os.replace(tmp_path, dest_path)

def convert_to_wav(input_path, output_path):
    cmd = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        input_path,
        "-ac",
        "1",
        "-ar",
        "32000",
        output_path,
    ]
    subprocess.run(cmd, check=True)

def safe_mkdir(path):
    os.makedirs(path, exist_ok=True)

def main():
    parser = argparse.ArgumentParser(description="Download a small Xeno-canto subset (temp-dir safe)")
    parser.add_argument("--output-dir", required=True, help="Final directory for WAVs (e.g., your Drive path)")
    parser.add_argument("--temp-dir", required=False, help="Temp/cache directory for downloads and conversion (recommended outside Drive)")
    parser.add_argument("--api-key", required=False, help="Xeno-canto API key (get from xeno-canto.org/account)")
    parser.add_argument("--per-species", type=int, default=120)
    parser.add_argument("--licenses", type=str, default=",".join(DEFAULT_LICENSES))
    parser.add_argument("--max-length", type=int, default=30)
    parser.add_argument("--species", type=str, default=None)
    parser.add_argument("--sleep-between-requests", type=float, default=1.0)
    args = parser.parse_args()

    output_dir = os.path.abspath(args.output_dir)
    temp_dir = os.path.abspath(args.temp_dir) if args.temp_dir else None
    api_key = args.api_key or os.environ.get("XENOCANTO_API_KEY")
    if not api_key:
        print("Error: API key required. Provide via --api-key or XENOCANTO_API_KEY environment variable.")
        print("Get your free API key at: https://xeno-canto.org/account")
        sys.exit(1)
    per_species = args.per_species
    allowed_licenses = [x.strip() for x in args.licenses.split(",") if x.strip()]
    max_length = args.max_length
    sleep_between_requests = float(args.sleep_between_requests)

    if args.species:
        user_specs = []
        for s in args.species.split(","):
            s = s.strip()
            if not s:
                continue
            if ":" in s:
                code, common = s.split(":", 1)
                user_specs.append((code.strip(), common.strip()))
            else:
                user_specs.append((s, s.replace("_", " ")))
        species_list = user_specs
    else:
        species_list = DEFAULT_SPECIES

    print("Output dir:", output_dir)
    if temp_dir:
        print("Temp dir:", temp_dir)
        safe_mkdir(temp_dir)
    print("Per species:", per_species)
    print("Allowed licenses:", allowed_licenses)
    print("Max clip length (s):", max_length)

    safe_mkdir(output_dir)

    manifest_rows = []
    session = requests.Session()
    headers = {"User-Agent": "bird-pam-capstone-subset-downloader/1.0 (contact: SUNY-Poly-Mark)"}
    session.headers.update(headers)

    for code, common in species_list:
        # Convert species code to API v3 tag format
        # e.g., "Cardinalis_cardinalis" -> "gen:Cardinalis sp:cardinalis"
        parts = code.replace("-", "_").split("_")
        if len(parts) >= 2:
            genus = parts[0]
            species = parts[1]
            query_name = f"gen:{genus} sp:{species}"
        else:
            # Fallback for single-word entries
            query_name = f"gen:{parts[0]}"
        
        print(f"\nFetching recordings for {common} ({query_name}) ...")
        species_folder_name = sanitize_species_folder(code)
        species_out_dir = os.path.join(output_dir, species_folder_name)
        safe_mkdir(species_out_dir)

        found = 0
        page = 1
        seen_ids = set()

        while found < per_species:
            try:
                data = query_xc(query_name, page=page, api_key=api_key)
            except Exception as e:
                print(f"API request failed for {query_name} page {page}: {e}")
                break

            recordings = data.get("recordings", [])
            if not recordings:
                break

            for rec in recordings:
                if found >= per_species:
                    break
                try:
                    xc_id = rec.get("id") or rec.get("recording-id") or rec.get("xcid")
                    if not xc_id:
                        continue
                    if xc_id in seen_ids:
                        continue

                    length_str = rec.get("length", "").strip()
                    length_s = parse_length_to_seconds(length_str) if length_str else None
                    if length_s is None:
                        continue
                    if length_s > max_length:
                        continue

                    license_url = (rec.get("lic") or "").strip()
                    # Extract license type from URL (e.g., "by-nc-sa" from ".../licenses/by-nc-sa/4.0/")
                    license_type = ""
                    if "creativecommons.org" in license_url:
                        parts = license_url.split("/")
                        for i, part in enumerate(parts):
                            if part == "licenses" and i + 1 < len(parts):
                                license_type = parts[i + 1].lower()
                                break
                    elif "publicdomain" in license_url.lower():
                        license_type = "publicdomain"
                    
                    # Check if license matches any allowed types
                    if not any(lic.lower() in license_type for lic in allowed_licenses):
                        continue

                    file_url_rel = rec.get("file") or rec.get("file-name") or ""
                    if not file_url_rel:
                        continue
                    file_url = file_url_rel if file_url_rel.startswith("http") else ("https:" + file_url_rel)

                    recordist = rec.get("rec") or rec.get("recordist") or ""
                    safe_recorder = "".join(c if (c.isalnum() or c in "_-") else "_" for c in (recordist or "rec"))
                    original_fname = os.path.basename(file_url.split("?")[0])
                    ext = os.path.splitext(original_fname)[1] or ".mp3"
                    fname_root = f"{xc_id}_{safe_recorder}_{int(length_s)}s"
                    # download path goes to temp_dir (if provided) else to species_out_dir
                    if temp_dir:
                        species_tmp_dir = os.path.join(temp_dir, species_folder_name)
                        safe_mkdir(species_tmp_dir)
                        downloaded_path = os.path.join(species_tmp_dir, fname_root + ext)
                        wav_tmp_path = os.path.join(species_tmp_dir, fname_root + ".wav")
                        final_wav_path = os.path.join(species_out_dir, fname_root + ".wav")
                    else:
                        downloaded_path = os.path.join(species_out_dir, fname_root + ext)
                        wav_tmp_path = os.path.join(species_out_dir, fname_root + ".wav")
                        final_wav_path = wav_tmp_path

                    if os.path.exists(final_wav_path):
                        seen_ids.add(xc_id)
                        found += 1
                        manifest_rows.append({
                            "filepath": os.path.relpath(final_wav_path, output_dir),
                            "species_code": code,
                            "species_name": common,
                            "xc_id": xc_id,
                            "url": file_url,
                            "license": license_url,
                            "length_s": length_s,
                            "original_file": original_fname,
                            "recordist": recordist,
                        })
                        continue

                    try:
                        print(f"Downloading {file_url} -> {downloaded_path}")
                        download_file(file_url, downloaded_path, session=session)
                    except Exception as e:
                        print("Download failed:", e)
                        if os.path.exists(downloaded_path):
                            try:
                                os.remove(downloaded_path)
                            except Exception:
                                pass
                        continue

                    try:
                        print(f"Converting to WAV: {downloaded_path} -> {wav_tmp_path}")
                        convert_to_wav(downloaded_path, wav_tmp_path)
                    except subprocess.CalledProcessError as e:
                        print("ffmpeg conversion failed:", e)
                        if os.path.exists(wav_tmp_path):
                            os.remove(wav_tmp_path)
                        if os.path.exists(downloaded_path):
                            os.remove(downloaded_path)
                        continue

                    # remove downloaded original
                    try:
                        if os.path.exists(downloaded_path):
                            os.remove(downloaded_path)
                    except Exception:
                        pass

                    # move final wav into output_dir if using temp_dir
                    if temp_dir and not os.path.exists(final_wav_path):
                        shutil.move(wav_tmp_path, final_wav_path)

                    elif not temp_dir:
                        final_wav_path = wav_tmp_path

                    seen_ids.add(xc_id)
                    found += 1

                    manifest_rows.append({
                        "filepath": os.path.relpath(final_wav_path, output_dir),
                        "species_code": code,
                        "species_name": common,
                        "xc_id": xc_id,
                        "url": file_url,
                        "license": license_url,
                        "length_s": length_s,
                        "original_file": original_fname,
                        "recordist": recordist,
                    })

                except Exception as e:
                    print("Error processing recording:", e)
                    continue

            num_pages = int(data.get("numPages") or data.get("numPages", 0) or 0)
            if page >= num_pages:
                break
            page += 1
            time.sleep(sleep_between_requests)

        print(f"Collected {found} recordings for {common}.")
        time.sleep(0.5)

    manifest_path = os.path.join(output_dir, "manifest.csv")
    print("Writing manifest to", manifest_path)
    df = pd.DataFrame(manifest_rows)
    if not df.empty:
        df.to_csv(manifest_path, index=False)
    else:
        with open(manifest_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["filepath", "species_code", "species_name", "xc_id", "url", "license", "length_s", "original_file", "recordist"])

    print("Done. Manifest rows:", len(manifest_rows))
    print("You can now sync the output directory with Google Drive (if not already placed in your Drive folder).")

if __name__ == "__main__":
    main()