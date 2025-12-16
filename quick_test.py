#!/usr/bin/env python3
"""
Quick test script for MUSE image editing.
Simpler than full harness - just run one edit and see results.

Usage:
    python quick_test.py "your prompt here" image1.jpg [image2.jpg] [image3.jpg]
    
Example:
    python quick_test.py "Change the sofa to blue velvet" living_room.jpg
    python quick_test.py "Apply this marble to countertops" kitchen.jpg marble_sample.jpg
"""

import os
import sys
import base64
import time
import requests
from pathlib import Path
from datetime import datetime

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
MODEL = "qwen/qwen-image-edit-plus"


def encode_image(path: str) -> tuple[str, str]:
    """Return (base64_data, mime_type)."""
    ext = Path(path).suffix.lower()
    mime = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode(), mime


def run_edit(prompt: str, images: list[str], go_fast: bool = True) -> dict:
    """Run single edit."""
    
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    input_data = {
        "prompt": prompt,
        "go_fast": go_fast,
        "aspect_ratio": "match_input_image",
        "output_format": "png",
        "output_quality": 95,
    }
    
    # Primary image as array with data URI
    b64, mime = encode_image(images[0])
    input_data["image"] = [f"data:{mime};base64,{b64}"]
    
    # Additional reference images
    if len(images) > 1:
        b64_2, mime_2 = encode_image(images[1])
        input_data["image_2"] = [f"data:{mime_2};base64,{b64_2}"]
    if len(images) > 2:
        b64_3, mime_3 = encode_image(images[2])
        input_data["image_3"] = [f"data:{mime_3};base64,{b64_3}"]
    
    print(f"🚀 Submitting to {MODEL}...")
    start = time.time()
    
    resp = requests.post(
        f"https://api.replicate.com/v1/models/{MODEL}/predictions",
        headers=headers,
        json={"input": input_data},
        timeout=60
    )
    
    if resp.status_code not in (200, 201):
        return {"error": f"API error {resp.status_code}: {resp.text}"}
    
    pred_id = resp.json().get("id")
    poll_url = f"https://api.replicate.com/v1/predictions/{pred_id}"
    
    print(f"⏳ Waiting for result (ID: {pred_id})...")
    
    while True:
        poll = requests.get(poll_url, headers=headers).json()
        status = poll.get("status")
        
        if status == "succeeded":
            duration = time.time() - start
            output = poll.get("output")
            url = output[0] if isinstance(output, list) else output
            return {"success": True, "url": url, "duration": duration}
        
        if status in ("failed", "canceled"):
            return {"error": poll.get("error", "Failed")}
        
        print(".", end="", flush=True)
        time.sleep(2)


def download(url: str, save_path: str):
    """Download result image."""
    resp = requests.get(url, timeout=30)
    if resp.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(resp.content)
        return True
    return False


def main():
    if not REPLICATE_API_TOKEN:
        print("❌ Set REPLICATE_API_TOKEN environment variable")
        sys.exit(1)
    
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    
    prompt = sys.argv[1]
    images = sys.argv[2:]
    
    # Validate images exist
    for img in images:
        if not Path(img).exists():
            print(f"❌ Image not found: {img}")
            sys.exit(1)
    
    print(f"\n{'='*60}")
    print(f"Prompt: {prompt[:80]}{'...' if len(prompt) > 80 else ''}")
    print(f"Images: {images}")
    print(f"{'='*60}\n")
    
    result = run_edit(prompt, images)
    
    if result.get("error"):
        print(f"\n❌ Error: {result['error']}")
        sys.exit(1)
    
    print(f"\n\n✅ Done in {result['duration']:.1f}s")
    print(f"🔗 URL: {result['url']}")
    
    # Save locally
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"result_{timestamp}.png"
    
    if download(result["url"], output_file):
        print(f"💾 Saved: {output_file}")
        
        # Try to open (macOS)
        if sys.platform == "darwin":
            os.system(f"open {output_file}")
    
    print("\n" + "="*60)
    print("EVALUATE:")
    print("  - Does it match your intent?")
    print("  - Are preserved elements actually preserved?")
    print("  - Is the scale/proportion reasonable?")
    print("  - Are materials/textures realistic?")
    print("  - Any artifacts or obvious AI tells?")
    print("="*60)


if __name__ == "__main__":
    main()
