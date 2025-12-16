#!/usr/bin/env python3
"""
Create a presentable Notion page with MUSE test results.
Creates a full page with images, prompts, and organized sections.

Usage:
    python create_notion_page.py

Requires:
    NOTION_TOKEN - Your Notion integration token
    NOTION_PARENT_PAGE_ID - The page ID where you want to create the results page
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_PARENT_PAGE_ID = os.environ.get("NOTION_PARENT_PAGE_ID", "")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"

# Test results data
TEST_RESULTS = {
    "run_timestamp": "2025-12-15T02:08:45",
    "model": "qwen/qwen-image-edit-plus",
    "total_tests": 16,
    "successful": 16,
    "categories": [
        {
            "name": "Precise Scale",
            "icon": "📐",
            "tests": [
                {
                    "id": "scale_001",
                    "name": "Sofa Sizing - Specific Dimensions",
                    "difficulty": "hard",
                    "prompt": "Replace the sofa with a large sectional that fills approximately 70% of the wall width. The sectional should be L-shaped, facing right, in warm gray bouclé fabric. Maintain proper scale relative to the coffee table and rug.",
                    "duration": 12.9,
                    "result_url": "https://replicate.delivery/xezq/wQP6xryFv3JpKxHZfyeU63232MwkyeV28hAT6l76qMWcycmrA/out-0.png",
                    "success_criteria": ["Sofa proportionally sized to wall", "L-shape orientation correct", "Scale relationship maintained", "Fabric texture visible"],
                },
                {
                    "id": "scale_002",
                    "name": "Pendant Light Height",
                    "difficulty": "hard",
                    "prompt": "Add a large globe pendant light centered above the dining table. The pendant should hang at standard dining height - low enough to illuminate the table but high enough to not obstruct views. Warm brass finish, frosted glass globe approximately 50cm diameter.",
                    "duration": 12.9,
                    "result_url": "https://replicate.delivery/xezq/IIABuwwC305hDpEmdcSXhg7JxaaJf3H0GG9TZL6AiKhvMn5KA/out-0.png",
                    "success_criteria": ["Pendant centered over table", "Height appropriate for dining", "Scale proportional to table size", "Brass/glass materials visible"],
                },
            ]
        },
        {
            "name": "Product Replication",
            "icon": "🪑",
            "tests": [
                {
                    "id": "product_001",
                    "name": "Chair from Reference",
                    "difficulty": "very_hard",
                    "prompt": "Place the tufted accent chair from the reference image in the corner by the window, replacing the existing armchair. Match the exact design - button tufting, curved back, turned legs.",
                    "duration": 15.5,
                    "result_url": "https://replicate.delivery/xezq/h9CFMvzXcJoDNl4YT7WJj5kE45xTxbYXqekWpR8J4Zq2Mn5KA/out-0.png",
                    "multi_image": True,
                },
                {
                    "id": "product_002",
                    "name": "Chair Style in Dining Room",
                    "difficulty": "very_hard",
                    "prompt": "Replace the dining chairs with chairs matching the style from the reference image - elegant tufted design with turned legs. Keep the same count of chairs.",
                    "duration": 13.9,
                    "result_url": "https://replicate.delivery/xezq/sCHtYk6veJXfnE3vE6s86psmfR19X56U9a3eXbLt91G8n5MXB/out-0.png",
                    "multi_image": True,
                },
            ]
        },
        {
            "name": "Multi-Element",
            "icon": "🎨",
            "tests": [
                {
                    "id": "complex_001",
                    "name": "Full Room Transformation - 4 Changes",
                    "difficulty": "very_hard",
                    "prompt": "Transform this space: 1) Change wall color to deep forest green, 2) Replace sofa with cream linen sectional, 3) Add a large vintage Persian rug in reds and blues, 4) Swap the coffee table for a round marble-top table with brass base.",
                    "duration": 12.1,
                    "result_url": "https://replicate.delivery/xezq/fXSv4MtbgwRGdqTk7YNNbSV9PxylJGVKwbxQwp8nCNtINn5KA/out-0.png",
                },
                {
                    "id": "complex_002",
                    "name": "Kitchen Renovation - Surfaces + Hardware",
                    "difficulty": "very_hard",
                    "prompt": "Renovate this kitchen: Replace countertops with white Calacatta marble with dramatic gray veining. Change cabinet color to deep navy blue with satin finish. Replace all hardware with unlacquered brass pulls.",
                    "duration": 10.5,
                    "result_url": "https://replicate.delivery/xezq/p56fRwh5RE3LNCNeVnIQAwHRemQgcbSCxJBFXwewyeIwTzZuC/out-0.png",
                },
            ]
        },
        {
            "name": "Photorealistic Integration",
            "icon": "✨",
            "tests": [
                {
                    "id": "realism_001",
                    "name": "Shadow and Lighting Consistency",
                    "difficulty": "hard",
                    "prompt": "Add a tall floor lamp with a linen drum shade in the corner to the right of the sofa. The lamp should cast realistic shadows consistent with the existing lighting in the room.",
                    "duration": 13.1,
                    "result_url": "https://replicate.delivery/xezq/gkq6Y0F7Rk6XCJeMXKueuUe3BLVifiq5Rt42bCWmdx7Lr5MXB/out-0.png",
                },
                {
                    "id": "realism_002",
                    "name": "Reflection and Material Interaction",
                    "difficulty": "very_hard",
                    "prompt": "Replace the coffee table with a glass-top table with polished chrome legs. The glass should show realistic reflections of the room.",
                    "duration": 14.2,
                    "result_url": "https://replicate.delivery/xezq/HnadFCpQ4eWYBqj3S12Thu9zfvQxemlfwBOtW8fbvfySxmzcF/out-0.png",
                },
            ]
        },
        {
            "name": "Consistency",
            "icon": "🔄",
            "tests": [
                {
                    "id": "consistency_001",
                    "name": "Same Edit, Three Runs",
                    "difficulty": "hard",
                    "prompt": "Change the sofa to a mid-century modern style in mustard yellow velvet. Wooden tapered legs, clean lines, slightly angled back.",
                    "duration": 12.1,
                    "result_url": "https://replicate.delivery/xezq/8MdjNjYltMIZIFoQjPUNWf1ZPTzHF9WvbIFOHyffKobq2cmrA/out-0.png",
                    "extra_results": [
                        "https://replicate.delivery/xezq/hldqveNt8q1NdKvWhHTDmEwVOfgyH65UyYhJiiRXg0QlbOzVA/out-0.png",
                        "https://replicate.delivery/xezq/MtRRchCVsuKQD5LAKfoB8GGQMsh8UVxhfP5jodoAHek13cmrA/out-0.png",
                    ],
                },
            ]
        },
        {
            "name": "Material Transfer",
            "icon": "🪨",
            "tests": [
                {
                    "id": "material_001",
                    "name": "Stone Sample to Countertop",
                    "difficulty": "hard",
                    "prompt": "Replace the kitchen countertops with the marble from the reference image. Match the exact vein pattern, color, and finish.",
                    "duration": 11.4,
                    "result_url": "https://replicate.delivery/xezq/Gjqg2HEXGZr3FNyqvQCoZ88gEetyqsQDS9wIbeef3fQahzZuC/out-0.png",
                    "multi_image": True,
                },
                {
                    "id": "material_002",
                    "name": "Fabric Sample to Upholstery",
                    "difficulty": "hard",
                    "prompt": "Reupholster the sofa with the fabric from the reference image. Match the exact color, texture, and pattern.",
                    "duration": 19.0,
                    "result_url": "https://replicate.delivery/xezq/oI8ZoEY1UtqpFFlTdCyH6TRPgy4pNolXH0j4TDKlm1OHnzcF/out-0.png",
                    "multi_image": True,
                },
            ]
        },
        {
            "name": "Style Transfer",
            "icon": "🏠",
            "tests": [
                {
                    "id": "style_001",
                    "name": "Japandi Transformation",
                    "difficulty": "medium",
                    "prompt": "Transform this room to match the Japandi aesthetic from the reference image. Apply: low-profile furniture forms, warm light wood tones, neutral color palette with black accents.",
                    "duration": 34.5,
                    "result_url": "https://replicate.delivery/xezq/TdYBStsJXmZjGtG3zG2nvLo8lY1yVseApa21N9XFSK4lOn5KA/out-0.png",
                    "multi_image": True,
                },
            ]
        },
        {
            "name": "Edge Cases",
            "icon": "⚠️",
            "tests": [
                {
                    "id": "edge_001",
                    "name": "Preserve Specific Elements",
                    "difficulty": "hard",
                    "prompt": "Change ONLY the wall color to warm white. Keep absolutely everything else exactly as is - all furniture, art, lighting, flooring, window treatments, decor items.",
                    "duration": 10.8,
                    "result_url": "https://replicate.delivery/xezq/UhrRsGl4N4YANFnneXKeG2XkeFu7kkyVfeNrj3teJlcGXnzcF/out-0.png",
                },
                {
                    "id": "edge_002",
                    "name": "Remove Single Object Cleanly",
                    "difficulty": "medium",
                    "prompt": "Remove the coffee table completely. Fill the space naturally with continuous flooring matching the existing floor exactly.",
                    "duration": 11.3,
                    "result_url": "https://replicate.delivery/xezq/wVkUhObRgMp1MJQfmaAnxDh5UdzlsftyoYhfZR2Zshel25MXB/out-0.png",
                },
            ]
        },
    ]
}


def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }


def create_heading_block(text, level=1):
    """Create a heading block."""
    heading_type = f"heading_{level}"
    return {
        "object": "block",
        "type": heading_type,
        heading_type: {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def create_paragraph_block(text, bold=False, color="default"):
    """Create a paragraph block."""
    return {
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [{
                "type": "text",
                "text": {"content": text},
                "annotations": {"bold": bold, "color": color}
            }]
        }
    }


def create_callout_block(text, icon="💡", color="gray_background"):
    """Create a callout block."""
    return {
        "object": "block",
        "type": "callout",
        "callout": {
            "rich_text": [{"type": "text", "text": {"content": text}}],
            "icon": {"type": "emoji", "emoji": icon},
            "color": color
        }
    }


def create_quote_block(text):
    """Create a quote block."""
    return {
        "object": "block",
        "type": "quote",
        "quote": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def create_image_block(url):
    """Create an image block from URL."""
    return {
        "object": "block",
        "type": "image",
        "image": {
            "type": "external",
            "external": {"url": url}
        }
    }


def create_divider_block():
    """Create a divider block."""
    return {
        "object": "block",
        "type": "divider",
        "divider": {}
    }


def create_table_of_contents_block():
    """Create a table of contents block."""
    return {
        "object": "block",
        "type": "table_of_contents",
        "table_of_contents": {"color": "default"}
    }


def create_column_list_block(columns):
    """Create a column list with columns."""
    return {
        "object": "block",
        "type": "column_list",
        "column_list": {
            "children": columns
        }
    }


def create_column_block(children):
    """Create a column."""
    return {
        "object": "block",
        "type": "column",
        "column": {
            "children": children
        }
    }


def create_bulleted_list_block(text):
    """Create a bulleted list item."""
    return {
        "object": "block",
        "type": "bulleted_list_item",
        "bulleted_list_item": {
            "rich_text": [{"type": "text", "text": {"content": text}}]
        }
    }


def create_toggle_block(title, children):
    """Create a toggle block."""
    return {
        "object": "block",
        "type": "toggle",
        "toggle": {
            "rich_text": [{"type": "text", "text": {"content": title}}],
            "children": children
        }
    }


def build_page_content():
    """Build the full page content."""
    blocks = []

    # Header callout
    blocks.append(create_callout_block(
        f"Model: {TEST_RESULTS['model']} | Run: {TEST_RESULTS['run_timestamp'][:10]} | Tests: {TEST_RESULTS['total_tests']}/{TEST_RESULTS['total_tests']} passed",
        "🎯",
        "blue_background"
    ))

    blocks.append(create_divider_block())

    # Summary section
    blocks.append(create_heading_block("Summary", 2))
    blocks.append(create_paragraph_block(
        f"✅ {TEST_RESULTS['successful']} tests generated successfully (100% success rate)"
    ))
    blocks.append(create_paragraph_block(
        "📊 8 categories tested: Scale, Product Replication, Multi-Element, Photorealistic, Consistency, Material Transfer, Style Transfer, Edge Cases"
    ))
    blocks.append(create_paragraph_block(
        "⏱️ Average generation time: ~13 seconds | Longest: 34.5s (Style Transfer)"
    ))

    blocks.append(create_divider_block())

    # Table of contents
    blocks.append(create_heading_block("Categories", 2))
    blocks.append(create_table_of_contents_block())

    blocks.append(create_divider_block())

    # Each category
    for category in TEST_RESULTS["categories"]:
        # Category header
        blocks.append(create_heading_block(f"{category['icon']} {category['name']}", 2))

        for test in category["tests"]:
            # Test name as heading
            difficulty_emoji = {"medium": "🟢", "hard": "🟡", "very_hard": "🔴"}.get(test["difficulty"], "⚪")
            multi_img = " 📎" if test.get("multi_image") else ""
            blocks.append(create_heading_block(f"{test['name']} {difficulty_emoji}{multi_img}", 3))

            # Test ID and duration
            blocks.append(create_paragraph_block(
                f"ID: {test['id']} | Duration: {test['duration']}s | Difficulty: {test['difficulty'].replace('_', ' ').title()}"
            ))

            # Prompt as quote
            blocks.append(create_quote_block(test["prompt"]))

            # Result image
            blocks.append(create_paragraph_block("Result:", bold=True))
            blocks.append(create_image_block(test["result_url"]))

            # Extra results for consistency test
            if test.get("extra_results"):
                blocks.append(create_paragraph_block("Additional runs:", bold=True))
                for extra_url in test["extra_results"]:
                    blocks.append(create_image_block(extra_url))

            # Success criteria if available
            if test.get("success_criteria"):
                blocks.append(create_paragraph_block("Success Criteria:", bold=True))
                for criterion in test["success_criteria"]:
                    blocks.append(create_bulleted_list_block(criterion))

            blocks.append(create_divider_block())

    return blocks


def create_page(parent_page_id):
    """Create the Notion page."""

    # Create the page
    page_data = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "icon": {"type": "emoji", "emoji": "🎨"},
        "cover": {
            "type": "external",
            "external": {"url": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?w=1200"}
        },
        "properties": {
            "title": {
                "title": [{
                    "type": "text",
                    "text": {"content": "MUSE Model Evaluation Results"}
                }]
            }
        },
        "children": []  # Will add blocks after page creation
    }

    # Create the page first
    response = requests.post(
        f"{NOTION_API_URL}/pages",
        headers=notion_headers(),
        json=page_data
    )

    if response.status_code != 200:
        print(f"❌ Failed to create page: {response.status_code}")
        print(response.text)
        return None

    page_id = response.json()["id"]
    print(f"✅ Created page: {page_id}")

    # Now add content blocks in batches (Notion limit is 100 blocks per request)
    blocks = build_page_content()

    batch_size = 100
    for i in range(0, len(blocks), batch_size):
        batch = blocks[i:i + batch_size]

        response = requests.patch(
            f"{NOTION_API_URL}/blocks/{page_id}/children",
            headers=notion_headers(),
            json={"children": batch}
        )

        if response.status_code != 200:
            print(f"⚠️ Failed to add blocks {i}-{i+len(batch)}: {response.status_code}")
            print(response.text[:500])
        else:
            print(f"  Added blocks {i+1}-{i+len(batch)}")

    return page_id


def main():
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN not set")
        print("   export NOTION_TOKEN='secret_xxx'")
        return

    if not NOTION_PARENT_PAGE_ID:
        print("❌ NOTION_PARENT_PAGE_ID not set")
        print("   export NOTION_PARENT_PAGE_ID='your-page-id'")
        print("\n   To get a page ID:")
        print("   1. Open a Notion page where you want to create the results")
        print("   2. Click 'Share' → 'Copy link'")
        print("   3. The ID is in the URL: notion.so/PAGE_ID or notion.so/workspace/Page-Name-PAGE_ID")
        print("   4. Use just the 32-character ID (with or without dashes)")
        return

    print("🚀 Creating MUSE Evaluation Results page in Notion...")
    print(f"   Parent page: {NOTION_PARENT_PAGE_ID}")

    page_id = create_page(NOTION_PARENT_PAGE_ID)

    if page_id:
        print(f"\n✅ Done! Page created successfully")
        print(f"   https://notion.so/{page_id.replace('-', '')}")


if __name__ == "__main__":
    main()
