#!/usr/bin/env python3
"""
Generate HTML comparison grid for reviewing test results.
Creates a visual side-by-side view of original vs generated images.

Usage:
    python generate_comparison.py test_results/
"""

import json
import sys
from pathlib import Path
from datetime import datetime

HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>MUSE Test Results Comparison</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: #1a1a1a;
            color: #fff;
            padding: 20px;
        }}
        h1 {{
            text-align: center;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        .meta {{
            text-align: center;
            color: #888;
            margin-bottom: 30px;
            font-size: 14px;
        }}
        .category {{
            margin-bottom: 40px;
        }}
        .category h2 {{
            background: #333;
            padding: 10px 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-weight: 500;
        }}
        .test-card {{
            background: #2a2a2a;
            border-radius: 12px;
            margin-bottom: 20px;
            overflow: hidden;
        }}
        .test-header {{
            padding: 15px 20px;
            background: #333;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .test-title {{
            font-size: 16px;
            font-weight: 500;
        }}
        .test-meta {{
            display: flex;
            gap: 15px;
            font-size: 12px;
            color: #888;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 11px;
            text-transform: uppercase;
        }}
        .badge-hard {{ background: #f59e0b; color: #000; }}
        .badge-very_hard {{ background: #ef4444; color: #fff; }}
        .badge-medium {{ background: #3b82f6; color: #fff; }}
        .badge-success {{ background: #22c55e; color: #fff; }}
        .badge-fail {{ background: #ef4444; color: #fff; }}

        .test-content {{
            padding: 20px;
        }}
        .prompt-box {{
            background: #1a1a1a;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            font-size: 14px;
            line-height: 1.5;
            color: #ccc;
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
        }}
        .image-slot {{
            background: #1a1a1a;
            border-radius: 8px;
            overflow: hidden;
        }}
        .image-slot-header {{
            padding: 8px 12px;
            background: #333;
            font-size: 12px;
            color: #888;
            text-transform: uppercase;
        }}
        .image-slot img {{
            width: 100%;
            height: auto;
            display: block;
        }}
        .image-slot .placeholder {{
            height: 200px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #555;
            font-size: 14px;
        }}

        .criteria-section {{
            margin-top: 20px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 15px;
        }}
        .criteria-box {{
            background: #1a1a1a;
            padding: 15px;
            border-radius: 8px;
        }}
        .criteria-box h4 {{
            font-size: 12px;
            text-transform: uppercase;
            color: #888;
            margin-bottom: 10px;
        }}
        .criteria-box ul {{
            list-style: none;
            font-size: 13px;
        }}
        .criteria-box li {{
            padding: 5px 0;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .criteria-box li::before {{
            content: '○';
            color: #555;
        }}

        .score-section {{
            margin-top: 20px;
            padding: 15px;
            background: #1a1a1a;
            border-radius: 8px;
            display: flex;
            align-items: center;
            gap: 20px;
        }}
        .score-input {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .score-input label {{
            font-size: 14px;
            color: #888;
        }}
        .score-input select {{
            padding: 8px 12px;
            border-radius: 6px;
            border: 1px solid #444;
            background: #333;
            color: #fff;
            font-size: 14px;
        }}
        .notes-input {{
            flex: 1;
        }}
        .notes-input textarea {{
            width: 100%;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #444;
            background: #333;
            color: #fff;
            font-size: 13px;
            resize: vertical;
            min-height: 60px;
        }}

        .summary {{
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #333;
            padding: 15px 20px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}
        .summary button {{
            background: #3b82f6;
            color: #fff;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }}
        .summary button:hover {{
            background: #2563eb;
        }}

        @media (max-width: 768px) {{
            .criteria-section {{ grid-template-columns: 1fr; }}
            .score-section {{ flex-direction: column; align-items: stretch; }}
        }}
    </style>
</head>
<body>
    <h1>MUSE Model Capability Test Results</h1>
    <div class="meta">
        Generated: {timestamp} | Model: {model}
    </div>

    {content}

    <div class="summary">
        <button onclick="exportScores()">Export Scores</button>
    </div>

    <script>
        function exportScores() {{
            const scores = [];
            document.querySelectorAll('.test-card').forEach(card => {{
                const id = card.dataset.testId;
                const score = card.querySelector('select')?.value || '';
                const notes = card.querySelector('textarea')?.value || '';
                scores.push({{ id, score, notes }});
            }});

            const blob = new Blob([JSON.stringify(scores, null, 2)], {{type: 'application/json'}});
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'evaluation_scores.json';
            a.click();
        }}
    </script>
</body>
</html>
"""

TEST_CASES = [
    {"id": "scale_001", "category": "Precise Scale", "name": "Sofa sizing - specific dimensions", "difficulty": "hard",
     "success_criteria": ["Sofa proportionally sized to wall", "L-shape orientation correct", "Scale relationship maintained", "Fabric texture visible"],
     "failure_indicators": ["Sofa obviously wrong scale", "Floating or clipping", "Other furniture distorted"]},
    {"id": "scale_002", "category": "Precise Scale", "name": "Pendant light height", "difficulty": "hard",
     "success_criteria": ["Pendant centered over table", "Height appropriate for dining", "Scale proportional", "Materials visible"],
     "failure_indicators": ["Pendant too high or too low", "Wrong size", "Off-center"]},
    {"id": "product_001", "category": "Product Replication", "name": "Eames Lounge Chair from reference", "difficulty": "very_hard",
     "success_criteria": ["Recognizable as Eames", "Correct proportions", "Ottoman present", "Materials match", "Shadow correct"],
     "failure_indicators": ["Generic lounger", "Wrong proportions", "Missing ottoman", "Wrong materials"]},
    {"id": "product_002", "category": "Product Replication", "name": "Specific dining table from reference", "difficulty": "very_hard",
     "success_criteria": ["Design matches reference", "Base structure preserved", "Tabletop correct", "Material accurate", "Scale appropriate"],
     "failure_indicators": ["Generic table", "Features lost", "Wrong proportions"]},
    {"id": "complex_001", "category": "Multi-Element", "name": "Full room transformation - 4 changes", "difficulty": "very_hard",
     "success_criteria": ["Wall color changed", "Sofa replaced", "Rug added", "Coffee table changed", "Preserved elements intact"],
     "failure_indicators": ["Partial changes", "Preserved elements modified", "Visual chaos"]},
    {"id": "complex_002", "category": "Multi-Element", "name": "Kitchen renovation - surfaces + hardware", "difficulty": "very_hard",
     "success_criteria": ["Marble countertops", "Navy cabinets", "Brass hardware", "Backsplash unchanged", "Appliances unchanged"],
     "failure_indicators": ["Generic marble", "Hardware wrong", "Other elements modified"]},
    {"id": "realism_001", "category": "Photorealistic Integration", "name": "Shadow and lighting consistency", "difficulty": "hard",
     "success_criteria": ["Lamp placed correctly", "Shadow direction matches", "Light glow visible", "Materials realistic", "Clean edges"],
     "failure_indicators": ["No/wrong shadow", "Pasted appearance", "Harsh edges", "Fake materials"]},
    {"id": "realism_002", "category": "Photorealistic Integration", "name": "Reflection and material interaction", "difficulty": "very_hard",
     "success_criteria": ["Glass transparency", "Reflections visible", "Chrome reflects", "Natural integration", "Correct proportions"],
     "failure_indicators": ["Opaque glass", "No reflections", "Matte chrome", "Obvious fake"]},
    {"id": "consistency_001", "category": "Consistency", "name": "Same edit, three runs", "difficulty": "hard",
     "success_criteria": ["Mid-century style", "Mustard yellow", "Velvet texture", "Wooden legs"],
     "failure_indicators": ["Drastically different results", "Inconsistent style", "Color varies"]},
    {"id": "material_001", "category": "Material Transfer", "name": "Stone sample to countertop", "difficulty": "hard",
     "success_criteria": ["Marble resembles reference", "Vein pattern similar", "Color matches", "All surfaces covered", "Continuous slab"],
     "failure_indicators": ["Generic marble", "Veining wrong", "Color off", "Inconsistent"]},
    {"id": "material_002", "category": "Material Transfer", "name": "Fabric sample to upholstery", "difficulty": "hard",
     "success_criteria": ["Color matches", "Texture/pattern visible", "Scale appropriate", "Natural drape", "Consistent"],
     "failure_indicators": ["Color different", "Pattern wrong", "Flat application", "Inconsistent"]},
    {"id": "style_001", "category": "Style Transfer", "name": "Japandi transformation", "difficulty": "medium",
     "success_criteria": ["Japandi feel", "Low-profile furniture", "Warm neutrals", "Natural materials", "Minimal feel", "Architecture preserved"],
     "failure_indicators": ["Wrong style", "Too cluttered/empty", "Wrong colors", "Architecture modified"]},
    {"id": "edge_001", "category": "Edge Cases", "name": "Preserve specific elements", "difficulty": "hard",
     "success_criteria": ["Wall color changed", "Everything else identical", "No furniture moved", "Art unchanged", "Lighting unchanged"],
     "failure_indicators": ["Other elements modified", "Furniture moved", "Items changed"]},
    {"id": "edge_002", "category": "Edge Cases", "name": "Remove single object cleanly", "difficulty": "medium",
     "success_criteria": ["Table removed", "Floor natural", "Floor matches", "Nothing else changed", "No artifacts"],
     "failure_indicators": ["Partial table", "Floor obvious", "Other furniture moved", "Artifacts"]}
]


def find_images(results_dir: Path, test_id: str) -> dict:
    """Find original and result images for a test."""
    images = {"original": None, "reference": None, "result": None}
    
    # Look for result images
    for subdir in results_dir.iterdir():
        if subdir.is_dir():
            for img in subdir.glob(f"{test_id}*.png"):
                images["result"] = str(img)
                break
    
    # Original images would be in test_images/
    test_images = results_dir.parent / "test_images"
    if test_images.exists():
        for img in test_images.glob("*.jpg"):
            if "reference" not in img.name.lower() and "sample" not in img.name.lower():
                if images["original"] is None:
                    images["original"] = str(img)
            else:
                if images["reference"] is None:
                    images["reference"] = str(img)
    
    return images


def generate_card(test: dict, images: dict) -> str:
    """Generate HTML for a single test card."""
    
    difficulty_class = f"badge-{test['difficulty']}"
    status = "success" if images.get("result") else "fail"
    status_class = f"badge-{status}"
    
    # Image slots
    image_slots = ""
    
    if images.get("original"):
        image_slots += f"""
        <div class="image-slot">
            <div class="image-slot-header">Original</div>
            <img src="{images['original']}" alt="Original">
        </div>
        """
    
    if images.get("reference"):
        image_slots += f"""
        <div class="image-slot">
            <div class="image-slot-header">Reference</div>
            <img src="{images['reference']}" alt="Reference">
        </div>
        """
    
    if images.get("result"):
        image_slots += f"""
        <div class="image-slot">
            <div class="image-slot-header">Result</div>
            <img src="{images['result']}" alt="Result">
        </div>
        """
    else:
        image_slots += """
        <div class="image-slot">
            <div class="image-slot-header">Result</div>
            <div class="placeholder">No result generated</div>
        </div>
        """
    
    # Criteria
    success_items = "".join(f"<li>{c}</li>" for c in test.get("success_criteria", []))
    failure_items = "".join(f"<li>{c}</li>" for c in test.get("failure_indicators", []))
    
    return f"""
    <div class="test-card" data-test-id="{test['id']}">
        <div class="test-header">
            <div class="test-title">{test['name']}</div>
            <div class="test-meta">
                <span class="badge {difficulty_class}">{test['difficulty']}</span>
                <span class="badge {status_class}">{status}</span>
            </div>
        </div>
        <div class="test-content">
            <div class="prompt-box">
                {test.get('prompt', 'No prompt recorded')}
            </div>
            
            <div class="image-grid">
                {image_slots}
            </div>
            
            <div class="criteria-section">
                <div class="criteria-box">
                    <h4>✓ Success Criteria</h4>
                    <ul>{success_items}</ul>
                </div>
                <div class="criteria-box">
                    <h4>✗ Failure Indicators</h4>
                    <ul>{failure_items}</ul>
                </div>
            </div>
            
            <div class="score-section">
                <div class="score-input">
                    <label>Score:</label>
                    <select>
                        <option value="">-</option>
                        <option value="5">5 - Excellent</option>
                        <option value="4">4 - Good</option>
                        <option value="3">3 - Acceptable</option>
                        <option value="2">2 - Poor</option>
                        <option value="1">1 - Failed</option>
                    </select>
                </div>
                <div class="notes-input">
                    <textarea placeholder="Notes..."></textarea>
                </div>
            </div>
        </div>
    </div>
    """


def generate_html(results_dir: Path) -> str:
    """Generate full comparison HTML."""
    
    # Group tests by category
    categories = {}
    for test in TEST_CASES:
        cat = test["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(test)
    
    # Generate content
    content = ""
    for cat_name, tests in categories.items():
        content += f'<div class="category"><h2>{cat_name}</h2>'
        
        for test in tests:
            images = find_images(results_dir, test["id"])
            content += generate_card(test, images)
        
        content += '</div>'
    
    return HTML_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"),
        model="qwen/qwen-image-edit-plus",
        content=content
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: python generate_comparison.py <results_directory>")
        print("Example: python generate_comparison.py test_results/")
        sys.exit(1)
    
    results_dir = Path(sys.argv[1])
    
    if not results_dir.exists():
        print(f"Directory not found: {results_dir}")
        sys.exit(1)
    
    html = generate_html(results_dir)
    
    output_path = results_dir / "comparison.html"
    output_path.write_text(html)
    
    print(f"✅ Generated: {output_path}")
    print(f"   Open in browser to review and score results")
    
    # Try to open (macOS)
    if sys.platform == "darwin":
        import os
        os.system(f"open {output_path}")


if __name__ == "__main__":
    main()
