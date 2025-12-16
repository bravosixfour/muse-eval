#!/usr/bin/env python3
"""
MUSE Model Capability Test Harness
Tests Qwen-Image-Edit-2509 on challenging interior design use cases

Usage:
    1. Set REPLICATE_API_TOKEN environment variable
    2. Place test images in ./test_images/
    3. Run: python muse_test_harness.py
    4. Review results in ./test_results/
"""

import os
import json
import time
import base64
import hashlib
import requests
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Optional, List

# ============================================================================
# CONFIGURATION
# ============================================================================

REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")
MODEL = "qwen/qwen-image-edit-plus"
OUTPUT_DIR = Path("./test_results")
IMAGE_DIR = Path("./test_images")

# ============================================================================
# TEST CASES - The Challenging Ones
# ============================================================================

TEST_CASES = [
    # -------------------------------------------------------------------------
    # CATEGORY 1: Precise Scale & Measurement
    # -------------------------------------------------------------------------
    {
        "id": "scale_001",
        "category": "Precise Scale",
        "name": "Sofa sizing - specific dimensions",
        "difficulty": "hard",
        "images_needed": ["living_room.jpg"],
        "prompt": "Replace the sofa with a large sectional that fills approximately 70% of the wall width. The sectional should be L-shaped, facing right, in warm gray bouclé fabric. Maintain proper scale relative to the coffee table and rug.",
        "success_criteria": [
            "Sofa proportionally sized to wall (not too big/small)",
            "L-shape orientation correct",
            "Scale relationship with other furniture maintained",
            "Fabric texture visible"
        ],
        "failure_indicators": [
            "Sofa obviously wrong scale",
            "Floating or clipping into floor",
            "Other furniture distorted"
        ]
    },
    {
        "id": "scale_002", 
        "category": "Precise Scale",
        "name": "Pendant light height",
        "difficulty": "hard",
        "images_needed": ["dining_room.jpg"],
        "prompt": "Add a large globe pendant light centered above the dining table. The pendant should hang at standard dining height - low enough to illuminate the table but high enough to not obstruct views across the table. Warm brass finish, frosted glass globe approximately 50cm diameter.",
        "success_criteria": [
            "Pendant centered over table",
            "Height looks appropriate for dining",
            "Scale proportional to table size",
            "Brass/glass materials visible"
        ],
        "failure_indicators": [
            "Pendant too high (near ceiling) or too low (in face)",
            "Dramatically wrong size",
            "Off-center placement"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CATEGORY 2: Specific Product Replication
    # -------------------------------------------------------------------------
    {
        "id": "product_001",
        "category": "Product Replication",
        "name": "Chair from reference",
        "difficulty": "very_hard",
        "images_needed": ["living_room.jpg", "chair_reference.jpg"],
        "prompt": "Place the tufted accent chair from the reference image in the corner by the window, replacing the existing armchair. Match the exact design - button tufting, curved back, turned legs. Position angled toward the room. The chair should integrate naturally with the room's lighting.",
        "success_criteria": [
            "Recognizable as the reference chair style",
            "Correct proportions and details",
            "Button tufting visible",
            "Turned legs present",
            "Natural lighting integration"
        ],
        "failure_indicators": [
            "Generic chair instead of reference style",
            "Wrong proportions or details",
            "Tufting missing",
            "Materials clearly wrong"
        ]
    },
    {
        "id": "product_002",
        "category": "Product Replication",
        "name": "Chair style in dining room",
        "difficulty": "very_hard",
        "images_needed": ["dining_room.jpg", "chair_reference.jpg"],
        "prompt": "Replace the dining chairs with chairs matching the style from the reference image - elegant tufted design with turned legs. Keep the same count of chairs and their positions around the table. Scale appropriately for dining height.",
        "success_criteria": [
            "Chair design matches reference style",
            "Tufting preserved",
            "Leg style accurate",
            "Correct count of chairs",
            "Scale appropriate for dining"
        ],
        "failure_indicators": [
            "Generic chairs generated",
            "Key design features lost",
            "Wrong proportions"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CATEGORY 3: Multi-Element Complex Edits
    # -------------------------------------------------------------------------
    {
        "id": "complex_001",
        "category": "Multi-Element",
        "name": "Full room transformation - 4 changes",
        "difficulty": "very_hard",
        "images_needed": ["living_room.jpg"],
        "prompt": "Transform this space: 1) Change wall color to deep forest green, 2) Replace sofa with cream linen sectional, 3) Add a large vintage Persian rug in reds and blues, 4) Swap the coffee table for a round marble-top table with brass base. Keep the existing lighting and artwork.",
        "success_criteria": [
            "Wall color changed to green",
            "Sofa replaced with cream sectional",
            "Persian rug added with correct colors",
            "Coffee table is round marble/brass",
            "Lighting and artwork preserved"
        ],
        "failure_indicators": [
            "Only some changes applied",
            "Elements that should be preserved were changed",
            "Incoherent result / visual chaos",
            "Items missing entirely"
        ]
    },
    {
        "id": "complex_002",
        "category": "Multi-Element", 
        "name": "Kitchen renovation - surfaces + hardware",
        "difficulty": "very_hard",
        "images_needed": ["kitchen.jpg"],
        "prompt": "Renovate this kitchen: Replace countertops with white Calacatta marble with dramatic gray veining. Change cabinet color to deep navy blue with satin finish. Replace all hardware with unlacquered brass pulls and knobs. Keep backsplash, appliances, and layout exactly as is.",
        "success_criteria": [
            "Countertops are white marble with veining",
            "Cabinets are navy blue",
            "Hardware appears brass",
            "Backsplash unchanged",
            "Appliances unchanged"
        ],
        "failure_indicators": [
            "Marble looks generic/plastic",
            "Hardware missing or wrong",
            "Backsplash or appliances modified",
            "Layout changed"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CATEGORY 4: Photorealistic Integration
    # -------------------------------------------------------------------------
    {
        "id": "realism_001",
        "category": "Photorealistic Integration",
        "name": "Shadow and lighting consistency",
        "difficulty": "hard",
        "images_needed": ["living_room.jpg"],
        "prompt": "Add a tall floor lamp with a linen drum shade in the corner to the right of the sofa. The lamp should cast realistic shadows consistent with the existing lighting in the room. Brushed nickel base, warm white light glowing through the shade.",
        "success_criteria": [
            "Floor lamp placed correctly",
            "Shadow direction matches room lighting",
            "Light glow through shade visible",
            "Materials look realistic",
            "Edges clean (not floating/clipping)"
        ],
        "failure_indicators": [
            "No shadow or wrong direction",
            "Lamp appears pasted/floating",
            "Harsh edges / obvious compositing",
            "Material looks CG/fake"
        ]
    },
    {
        "id": "realism_002",
        "category": "Photorealistic Integration",
        "name": "Reflection and material interaction",
        "difficulty": "very_hard",
        "images_needed": ["living_room.jpg"],
        "prompt": "Replace the coffee table with a glass-top table with polished chrome legs. The glass should show realistic reflections of the room - the ceiling, nearby furniture, windows. Chrome legs should reflect the floor and surroundings.",
        "success_criteria": [
            "Glass transparency correct",
            "Reflections visible on glass",
            "Chrome shows environmental reflections",
            "Table integrates naturally",
            "Proportions correct"
        ],
        "failure_indicators": [
            "Glass looks solid/opaque",
            "No reflections",
            "Chrome looks matte/painted",
            "Obvious fake integration"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CATEGORY 5: Consistency Across Iterations
    # -------------------------------------------------------------------------
    {
        "id": "consistency_001",
        "category": "Consistency",
        "name": "Same edit, three runs",
        "difficulty": "hard",
        "images_needed": ["living_room.jpg"],
        "prompt": "Change the sofa to a mid-century modern style in mustard yellow velvet. Wooden tapered legs, clean lines, slightly angled back. Keep everything else exactly the same.",
        "success_criteria": [
            "Sofa is mid-century style",
            "Color is mustard yellow",
            "Velvet texture visible",
            "Wooden legs present"
        ],
        "failure_indicators": [
            "Drastically different results each run",
            "Style inconsistent between runs",
            "Color varies significantly"
        ],
        "special_instructions": "RUN THIS 3 TIMES with same prompt, compare results"
    },
    
    # -------------------------------------------------------------------------
    # CATEGORY 6: Material Sample Application
    # -------------------------------------------------------------------------
    {
        "id": "material_001",
        "category": "Material Transfer",
        "name": "Stone sample to countertop",
        "difficulty": "hard",
        "images_needed": ["kitchen.jpg", "marble_sample.jpg"],
        "prompt": "Replace the kitchen countertops with the marble from the reference image. Match the exact vein pattern, color, and finish. Apply consistently across all counter surfaces including the island. Maintain edge profile and thickness.",
        "success_criteria": [
            "Marble resembles reference sample",
            "Vein pattern similar",
            "Color tone matches",
            "Applied to all counter surfaces",
            "Looks like continuous slab"
        ],
        "failure_indicators": [
            "Generic marble generated",
            "Veining doesn't match",
            "Color significantly off",
            "Inconsistent application"
        ]
    },
    {
        "id": "material_002",
        "category": "Material Transfer",
        "name": "Fabric sample to upholstery",
        "difficulty": "hard",
        "images_needed": ["living_room.jpg", "fabric_sample.jpg"],
        "prompt": "Reupholster the sofa with the fabric from the reference image. Match the exact color, texture, and pattern. The fabric should drape naturally showing the texture and any pattern at the correct scale for furniture.",
        "success_criteria": [
            "Fabric color matches reference",
            "Texture/pattern visible",
            "Scale appropriate for sofa",
            "Natural drape and folds",
            "Consistent across all cushions"
        ],
        "failure_indicators": [
            "Color significantly different",
            "Pattern missing or wrong scale",
            "Flat/unrealistic application",
            "Inconsistent across surfaces"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CATEGORY 7: Style Transfer Accuracy
    # -------------------------------------------------------------------------
    {
        "id": "style_001",
        "category": "Style Transfer",
        "name": "Japandi transformation",
        "difficulty": "medium",
        "images_needed": ["living_room.jpg", "japandi_reference.png"],
        "prompt": "Transform this room to match the Japandi aesthetic from the reference image. Apply: low-profile furniture forms, warm light wood tones, neutral color palette with black accents, natural textures (linen, wool, wood), deliberate negative space, minimal ornamentation. Preserve room architecture.",
        "success_criteria": [
            "Overall Japandi feel achieved",
            "Low-profile furniture",
            "Warm neutral palette",
            "Natural materials visible",
            "Space feels intentionally minimal",
            "Room architecture preserved"
        ],
        "failure_indicators": [
            "Style doesn't read as Japandi",
            "Too cluttered or too empty",
            "Colors wrong for style",
            "Architecture modified"
        ]
    },
    
    # -------------------------------------------------------------------------
    # CATEGORY 8: Edge Cases
    # -------------------------------------------------------------------------
    {
        "id": "edge_001",
        "category": "Edge Cases",
        "name": "Preserve specific elements",
        "difficulty": "hard",
        "images_needed": ["living_room.jpg"],
        "prompt": "Change ONLY the wall color to warm white. Keep absolutely everything else exactly as is - all furniture, art, lighting, flooring, window treatments, decor items. Nothing should move or change except the wall color.",
        "success_criteria": [
            "Wall color changed",
            "Every single other element identical",
            "No furniture moved",
            "Art/decor unchanged",
            "Lighting unchanged"
        ],
        "failure_indicators": [
            "Other elements modified",
            "Furniture positions changed",
            "Items removed or added",
            "Lighting/mood shifted"
        ]
    },
    {
        "id": "edge_002",
        "category": "Edge Cases",
        "name": "Remove single object cleanly",
        "difficulty": "medium",
        "images_needed": ["living_room.jpg"],
        "prompt": "Remove the coffee table completely. Fill the space naturally with continuous flooring matching the existing floor exactly. Do not add anything new. All other furniture and decor must remain exactly in place.",
        "success_criteria": [
            "Coffee table removed",
            "Floor filled in naturally",
            "Floor matches existing",
            "Nothing else changed",
            "No artifacts where table was"
        ],
        "failure_indicators": [
            "Table partially visible",
            "Floor fill obvious/wrong",
            "Other furniture moved",
            "Artifacts or smearing"
        ]
    }
]


# ============================================================================
# API FUNCTIONS
# ============================================================================

def encode_image(image_path: Path) -> str:
    """Encode image to base64."""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def get_mime_type(image_path: Path) -> str:
    """Get MIME type from file extension."""
    ext = image_path.suffix.lower()
    return {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg", 
        ".png": "image/png",
        ".webp": "image/webp"
    }.get(ext, "image/png")


def call_replicate(
    prompt: str,
    images: List[Path],
    go_fast: bool = True,
    seed: Optional[int] = None
) -> dict:
    """Call Replicate API and return result."""
    
    headers = {
        "Authorization": f"Bearer {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    
    # Build input
    input_data = {
        "prompt": prompt,
        "go_fast": go_fast,
        "aspect_ratio": "match_input_image",
        "output_format": "png",
        "output_quality": 95,
    }
    
    if seed is not None:
        input_data["seed"] = seed
    
    # Add images (API requires arrays)
    image_keys = ["image", "image_2", "image_3"]
    for i, img_path in enumerate(images[:3]):
        mime = get_mime_type(img_path)
        b64 = encode_image(img_path)
        input_data[image_keys[i]] = [f"data:{mime};base64,{b64}"]
    
    # Submit prediction
    response = requests.post(
        f"https://api.replicate.com/v1/models/{MODEL}/predictions",
        headers=headers,
        json={"input": input_data},
        timeout=60
    )
    
    if response.status_code not in (200, 201):
        return {"error": f"API error: {response.status_code}", "detail": response.text}
    
    result = response.json()
    prediction_id = result.get("id")
    
    # Poll for completion
    poll_url = f"https://api.replicate.com/v1/predictions/{prediction_id}"
    max_wait = 300
    elapsed = 0
    
    while elapsed < max_wait:
        poll_response = requests.get(poll_url, headers=headers)
        poll_data = poll_response.json()
        status = poll_data.get("status")
        
        if status == "succeeded":
            return {
                "success": True,
                "output": poll_data.get("output"),
                "metrics": poll_data.get("metrics", {}),
                "prediction_id": prediction_id
            }
        elif status in ("failed", "canceled"):
            return {
                "success": False,
                "error": poll_data.get("error", "Unknown error"),
                "prediction_id": prediction_id
            }
        
        time.sleep(2)
        elapsed += 2
    
    return {"success": False, "error": "Timeout", "prediction_id": prediction_id}


def download_image(url: str, save_path: Path) -> bool:
    """Download image from URL."""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            save_path.write_bytes(response.content)
            return True
    except Exception as e:
        print(f"Download error: {e}")
    return False


# ============================================================================
# TEST RUNNER
# ============================================================================

@dataclass
class TestResult:
    test_id: str
    category: str
    name: str
    difficulty: str
    prompt: str
    images_used: List[str]
    timestamp: str
    duration_seconds: float
    success: bool
    output_url: Optional[str]
    output_file: Optional[str]
    error: Optional[str]
    notes: str = ""
    scores: dict = None
    
    def __post_init__(self):
        if self.scores is None:
            self.scores = {}


def run_test(test_case: dict, run_number: int = 1) -> TestResult:
    """Run a single test case."""
    
    test_id = test_case["id"]
    if run_number > 1:
        test_id = f"{test_id}_run{run_number}"
    
    print(f"\n{'='*60}")
    print(f"Running: {test_case['name']}")
    print(f"Category: {test_case['category']} | Difficulty: {test_case['difficulty']}")
    print(f"{'='*60}")
    
    # Check for required images
    images_needed = test_case.get("images_needed", [])
    image_paths = []
    missing = []
    
    for img_name in images_needed:
        img_path = IMAGE_DIR / img_name
        if img_path.exists():
            image_paths.append(img_path)
        else:
            missing.append(img_name)
    
    if missing:
        print(f"⚠️  Missing images: {missing}")
        print(f"   Place them in {IMAGE_DIR}/")
        return TestResult(
            test_id=test_id,
            category=test_case["category"],
            name=test_case["name"],
            difficulty=test_case["difficulty"],
            prompt=test_case["prompt"],
            images_used=[],
            timestamp=datetime.now().isoformat(),
            duration_seconds=0,
            success=False,
            output_url=None,
            output_file=None,
            error=f"Missing images: {missing}"
        )
    
    print(f"Images: {[p.name for p in image_paths]}")
    print(f"Prompt: {test_case['prompt'][:100]}...")
    
    # Run the test
    start_time = time.time()
    result = call_replicate(test_case["prompt"], image_paths)
    duration = time.time() - start_time
    
    # Process result
    output_url = None
    output_file = None
    
    if result.get("success"):
        output = result.get("output")
        output_url = output[0] if isinstance(output, list) else output
        
        # Download result
        output_file = f"{test_id}_{datetime.now().strftime('%H%M%S')}.png"
        output_path = OUTPUT_DIR / test_case["category"].replace(" ", "_") / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if download_image(output_url, output_path):
            print(f"✅ Saved: {output_path}")
        else:
            print(f"⚠️  Could not download result")
            output_file = None
    else:
        print(f"❌ Failed: {result.get('error')}")
    
    return TestResult(
        test_id=test_id,
        category=test_case["category"],
        name=test_case["name"],
        difficulty=test_case["difficulty"],
        prompt=test_case["prompt"],
        images_used=[p.name for p in image_paths],
        timestamp=datetime.now().isoformat(),
        duration_seconds=round(duration, 2),
        success=result.get("success", False),
        output_url=output_url,
        output_file=output_file,
        error=result.get("error")
    )


def run_all_tests(categories: Optional[List[str]] = None) -> List[TestResult]:
    """Run all tests or filtered by category."""
    
    results = []
    
    for test_case in TEST_CASES:
        if categories and test_case["category"] not in categories:
            continue
        
        # Check for special instructions (like run 3 times)
        if "RUN THIS 3 TIMES" in test_case.get("special_instructions", ""):
            for i in range(1, 4):
                result = run_test(test_case, run_number=i)
                results.append(result)
                time.sleep(2)  # Brief pause between runs
        else:
            result = run_test(test_case)
            results.append(result)
        
        time.sleep(1)  # Rate limiting
    
    return results


def save_results(results: List[TestResult], filename: str = "test_results.json"):
    """Save results to JSON."""
    output_path = OUTPUT_DIR / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    data = {
        "run_timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "total_tests": len(results),
        "successful": sum(1 for r in results if r.success),
        "failed": sum(1 for r in results if not r.success),
        "results": [asdict(r) for r in results]
    }
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\n📊 Results saved to {output_path}")
    return output_path


def print_summary(results: List[TestResult]):
    """Print summary of test results."""
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    # By category
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = {"success": 0, "fail": 0}
        if r.success:
            categories[r.category]["success"] += 1
        else:
            categories[r.category]["fail"] += 1
    
    print(f"\n{'Category':<30} {'Pass':<8} {'Fail':<8} {'Rate':<10}")
    print("-"*56)
    
    for cat, counts in categories.items():
        total = counts["success"] + counts["fail"]
        rate = counts["success"] / total * 100 if total > 0 else 0
        print(f"{cat:<30} {counts['success']:<8} {counts['fail']:<8} {rate:.0f}%")
    
    # Overall
    total_success = sum(1 for r in results if r.success)
    total = len(results)
    print("-"*56)
    print(f"{'TOTAL':<30} {total_success:<8} {total - total_success:<8} {total_success/total*100:.0f}%")
    
    # Timing
    avg_time = sum(r.duration_seconds for r in results if r.success) / max(total_success, 1)
    print(f"\nAverage generation time: {avg_time:.1f}s")



def generate_evaluation_sheet(results: List[TestResult]):
    """Generate markdown evaluation sheet for manual scoring."""
    
    output_path = OUTPUT_DIR / "evaluation_sheet.md"
    
    lines = [
        "# MUSE Model Evaluation Sheet",
        f"\nGenerated: {datetime.now().isoformat()}",
        f"\nModel: {MODEL}",
        "\n---\n",
        "## Scoring Guide",
        "- **5**: Excellent - Meets all criteria, production quality",
        "- **4**: Good - Minor issues, usable for concept work", 
        "- **3**: Acceptable - Noticeable issues but intent clear",
        "- **2**: Poor - Major issues, needs regeneration",
        "- **1**: Failed - Unusable result",
        "\n---\n"
    ]
    
    current_category = None
    
    for r in results:
        if r.category != current_category:
            current_category = r.category
            lines.append(f"\n## {current_category}\n")
        
        lines.append(f"### {r.name}")
        lines.append(f"**Test ID:** {r.test_id}")
        lines.append(f"**Difficulty:** {r.difficulty}")
        lines.append(f"**Status:** {'✅ Generated' if r.success else '❌ Failed'}")
        
        if r.output_file:
            lines.append(f"**Output:** `{r.output_file}`")
        
        lines.append(f"\n**Prompt:**\n> {r.prompt}\n")
        
        # Find original test case for criteria
        original = next((t for t in TEST_CASES if t["id"] == r.test_id.split("_run")[0]), None)
        
        if original:
            lines.append("**Success Criteria:**")
            for criterion in original.get("success_criteria", []):
                lines.append(f"- [ ] {criterion}")
            
            lines.append("\n**Failure Indicators:**")
            for indicator in original.get("failure_indicators", []):
                lines.append(f"- [ ] {indicator}")
        
        lines.append("\n**Score:** ___/5")
        lines.append("\n**Notes:**\n```\n\n```")
        lines.append("\n---\n")
    
    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    
    print(f"📝 Evaluation sheet saved to {output_path}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point."""
    
    print("="*60)
    print("MUSE MODEL CAPABILITY TEST HARNESS")
    print("="*60)
    
    # Check API token
    if not REPLICATE_API_TOKEN:
        print("\n❌ Error: REPLICATE_API_TOKEN not set")
        print("   export REPLICATE_API_TOKEN='your-token-here'")
        return
    
    # Setup directories
    OUTPUT_DIR.mkdir(exist_ok=True)
    IMAGE_DIR.mkdir(exist_ok=True)
    
    # Check for test images
    existing_images = list(IMAGE_DIR.glob("*.jpg")) + list(IMAGE_DIR.glob("*.png"))
    
    if not existing_images:
        print(f"\n⚠️  No test images found in {IMAGE_DIR}/")
        print("\nRequired images:")
        all_images = set()
        for tc in TEST_CASES:
            all_images.update(tc.get("images_needed", []))
        for img in sorted(all_images):
            print(f"   - {img}")
        print("\nPlace your test images and run again.")
        
        # Create placeholder info
        readme = IMAGE_DIR / "README.md"
        readme.write_text("""# Test Images

Place the following images here:

## Primary room images (your own photos or stock):
- `living_room.jpg` - A living room with sofa, coffee table, visible walls
- `dining_room.jpg` - Dining room with table and chairs
- `kitchen.jpg` - Kitchen with visible countertops and cabinets

## Reference images:
- `eames_chair_reference.jpg` - Eames Lounge Chair product photo
- `table_reference.jpg` - Distinctive dining table product photo
- `marble_sample.jpg` - Marble material sample close-up
- `fabric_sample.jpg` - Fabric swatch (textured like bouclé or velvet)
- `japandi_reference.jpg` - Japandi style interior for reference

Tips:
- Use high-resolution images (1024px+ on shortest side)
- Room images should have good lighting
- Reference images should clearly show the material/product
""")
        print(f"\n📄 Created {readme} with image requirements")
        return
    
    print(f"\n✅ Found {len(existing_images)} images in {IMAGE_DIR}/")
    print("   " + ", ".join(img.name for img in existing_images[:5]))
    if len(existing_images) > 5:
        print(f"   ... and {len(existing_images) - 5} more")
    
    # Menu
    print("\n" + "-"*60)
    print("Options:")
    print("  1. Run ALL tests")
    print("  2. Run by category")
    print("  3. Run single test")
    print("  4. Generate evaluation sheet only")
    print("-"*60)
    
    choice = input("\nSelect option (1-4): ").strip()
    
    results = []
    
    if choice == "1":
        results = run_all_tests()
    
    elif choice == "2":
        categories = sorted(set(tc["category"] for tc in TEST_CASES))
        print("\nCategories:")
        for i, cat in enumerate(categories, 1):
            count = sum(1 for tc in TEST_CASES if tc["category"] == cat)
            print(f"  {i}. {cat} ({count} tests)")
        
        cat_choice = input("\nSelect category number: ").strip()
        try:
            selected_cat = categories[int(cat_choice) - 1]
            results = run_all_tests(categories=[selected_cat])
        except (ValueError, IndexError):
            print("Invalid selection")
            return
    
    elif choice == "3":
        print("\nTests:")
        for i, tc in enumerate(TEST_CASES, 1):
            print(f"  {i}. [{tc['category']}] {tc['name']}")
        
        test_choice = input("\nSelect test number: ").strip()
        try:
            selected_test = TEST_CASES[int(test_choice) - 1]
            result = run_test(selected_test)
            results = [result]
        except (ValueError, IndexError):
            print("Invalid selection")
            return
    
    elif choice == "4":
        # Generate sheet without running tests
        dummy_results = [TestResult(
            test_id=tc["id"],
            category=tc["category"],
            name=tc["name"],
            difficulty=tc["difficulty"],
            prompt=tc["prompt"],
            images_used=tc.get("images_needed", []),
            timestamp=datetime.now().isoformat(),
            duration_seconds=0,
            success=True,
            output_url=None,
            output_file=f"{tc['id']}_PLACEHOLDER.png",
            error=None
        ) for tc in TEST_CASES]
        generate_evaluation_sheet(dummy_results)
        return
    
    else:
        print("Invalid option")
        return
    
    # Save and summarize
    if results:
        save_results(results)
        print_summary(results)
        generate_evaluation_sheet(results)
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print(f"1. Review generated images in {OUTPUT_DIR}/")
        print(f"2. Fill out evaluation_sheet.md with scores")
        print("3. Note patterns in what works vs. what doesn't")


if __name__ == "__main__":
    main()
