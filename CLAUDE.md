# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MUSE Model Evaluation Framework - a testing suite for evaluating Qwen-Image-Edit-2509 (an AI image editing model) for interior design use cases. The framework tests the model's ability to handle tasks like furniture placement, material transfer, style transformation, and multi-element edits.

## Commands

```bash
# Set API token (required)
export REPLICATE_API_TOKEN="r8_xxx"

# Run a quick single test
python3 quick_test.py "Change the sofa to blue velvet" test_images/living_room.jpg

# Multi-image test (material transfer)
python3 quick_test.py "Apply this marble to countertops" test_images/kitchen.jpg test_images/marble_sample.jpg

# Run full 14-test evaluation suite (interactive menu)
python3 muse_test_harness.py

# Generate HTML comparison view of results
python3 generate_comparison.py test_results/

# Create formatted Notion page with all results (requires NOTION_TOKEN and NOTION_PARENT_PAGE_ID)
python3 create_notion_page.py

# Push batch results to Notion database (requires NOTION_TOKEN and NOTION_DATABASE_ID)
python3 notion_integration.py test_results/test_results.json

# Quick single-result push to Notion
python3 push_to_notion.py "test_id" "Category" "prompt" "image_url" score
```

## Architecture

### Test Framework Flow
```
quick_test.py        → Single ad-hoc test → result_TIMESTAMP.png
muse_test_harness.py → Full suite (14 tests) → test_results/
                                             → test_results.json
                                             → evaluation_sheet.md
generate_comparison.py → test_results/ → comparison.html (interactive scoring)
```

### Core Scripts
- `muse_test_harness.py` - Main test runner with 14 test cases across 8 categories. Interactive menu for running all/category/single tests. Handles API calls to Replicate, polling for results, saving outputs by category to `test_results/`, and generating evaluation sheets.
- `quick_test.py` - Lightweight single-test runner for ad-hoc testing. Saves results as `result_TIMESTAMP.png` and auto-opens on macOS.
- `generate_comparison.py` - Creates interactive HTML comparison grid with scoring UI and JSON export.

### Open WebUI Tools
- `muse_edit_image_tool.py` - Async tool for Open WebUI integration. Uses pydantic Valves for configuration. Extracts images from chat messages automatically, calls Replicate API, returns HTML-embedded results.
- `replicate_qwen_image_edit.py` - Alternative Open WebUI tool with similar functionality.

### Notion Integration
- `create_notion_page.py` - Creates a full presentable Notion page with images, prompts, and organized sections. Uses hardcoded test results data.
- `notion_integration.py` - Pushes test_results.json to a Notion database.
- `push_to_notion.py` - CLI wrapper for quick single-result pushes.

### Supporting Files
- `MUSE_system_prompt_v2.md` - System prompt for the MUSE assistant with deep interior design domain knowledge.
- `download_test_images.sh` - Downloads sample test images.

## Test Categories

| Category | Tests | Focus |
|----------|-------|-------|
| Precise Scale | 2 | Proportional sizing, furniture-to-wall relationships |
| Product Replication | 2 | Matching specific furniture from reference images |
| Multi-Element | 2 | 4+ simultaneous changes in one edit |
| Photorealistic Integration | 2 | Shadows, reflections, material realism |
| Consistency | 1 (3 runs) | Same prompt 3x - variation analysis |
| Material Transfer | 2 | Applying material samples to surfaces |
| Style Transfer | 1 | Full room aesthetic transformation |
| Edge Cases | 2 | Preserve-all-but-one, clean object removal |

## Test Images Required

Place in `test_images/`:
- `living_room.jpg` - Primary test room with sofa, coffee table
- `dining_room.jpg` - Dining room with table and chairs
- `kitchen.jpg` - Kitchen with countertops and cabinets
- `chair_reference.jpg` - Reference chair for product replication
- `marble_sample.jpg` - Material sample for transfer tests
- `fabric_sample.jpg` - Fabric swatch for upholstery tests
- `japandi_reference.png` - Style reference for Japandi transformation

## Replicate API Details

All scripts use the `qwen/qwen-image-edit-plus` model on Replicate:
- Images must be base64-encoded with data URI prefix (`data:image/jpeg;base64,...`)
- Images passed as arrays: `{"image": ["data:image/jpeg;base64,..."]}`
- Supports up to 3 images: `image` (primary), `image_2` (reference), `image_3` (additional context)
- `go_fast=True` uses 8-step Lightning mode (~12s); `False` uses 40-step high-fidelity (~35s)
- API returns prediction ID; scripts poll `/predictions/{id}` until status is `succeeded`/`failed`/`canceled`
- Typical generation time: 10-15s (Lightning), 30-40s (high-fidelity)

## Scoring Guide

| Score | Meaning |
|-------|---------|
| 5 | Excellent - Production quality |
| 4 | Good - Minor issues, usable |
| 3 | Acceptable - Intent clear |
| 2 | Poor - Needs regeneration |
| 1 | Failed - Unusable |

## MUSE System Prompt

`MUSE_system_prompt_v2.md` defines the MUSE assistant's behavior:
- Deep interior design domain knowledge (styles, materials, lighting, historical movements)
- Prompt crafting guidelines for the image model
- Image slot strategy (which image goes in which slot)
- Use proportional language ("60% of wall width") instead of exact measurements
- Material expertise (Calacatta vs Carrara, wood species, textile types)
