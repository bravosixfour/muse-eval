# MUSE Model Evaluation Framework

Testing framework for Qwen-Image-Edit-2509 interior design capabilities.

## Quick Start

```bash
cd /Users/thahirkareem/local/muze-model-eval

# 1. Set API token
export REPLICATE_API_TOKEN="r8_xxx"

# 2. Download test images (already done)
./download_test_images.sh

# 3. Run quick test
python3 quick_test.py "Your prompt here" test_images/living_room.jpg

# 4. Run full test suite
python3 muse_test_harness.py
```

---

## Notion Integration Setup

### Step 1: Create Notion Integration

1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name it "MUSE Test Results"
4. Select your workspace
5. Copy the **Internal Integration Token** (starts with `secret_`)

### Step 2: Create Database in Notion

Create a new page in Notion, then create a **database** with these columns:

| Column Name | Type | Options |
|-------------|------|---------|
| Test ID | Title | - |
| Category | Select | Precise Scale, Product Replication, Multi-Element, Photorealistic Integration, Consistency, Material Transfer, Style Transfer, Edge Cases |
| Name | Text | - |
| Difficulty | Select | medium, hard, very_hard |
| Status | Select | passed, failed, pending_review |
| Score | Number | - |
| Prompt | Text | - |
| Duration (s) | Number | - |
| Result Image | URL | - |
| Notes | Text | - |
| Date | Date | - |
| Success Criteria | Text | - |
| Failure Indicators | Text | - |

### Step 3: Share Database with Integration

1. Open your database in Notion
2. Click "..." menu → "Add connections"
3. Select your "MUSE Test Results" integration

### Step 4: Get Database ID

The database ID is in the URL:
```
https://www.notion.so/yourworkspace/DATABASE_ID?v=xxx
                                    ^^^^^^^^^^^^
```

### Step 5: Set Environment Variables

```bash
export NOTION_TOKEN="secret_xxx"
export NOTION_DATABASE_ID="xxx"
```

Or add to your `.zshrc` / `.bashrc`:
```bash
echo 'export NOTION_TOKEN="secret_xxx"' >> ~/.zshrc
echo 'export NOTION_DATABASE_ID="xxx"' >> ~/.zshrc
```

---

## Usage

### Push Test Results to Notion

```bash
# After running test harness
python3 notion_integration.py test_results/test_results.json

# Push a single quick test result
python3 push_to_notion.py "sofa_blue_001" "Material Transfer" "Change sofa to blue velvet" "https://replicate.delivery/..." 5
```

### Automated Integration

The test harness can auto-push to Notion. Set the environment variables and results will be logged automatically.

---

## Files

| File | Purpose |
|------|---------|
| `MUSE_system_prompt_v2.md` | System prompt for Open WebUI |
| `muse_edit_image_tool.py` | Open WebUI tool integration |
| `quick_test.py` | Single test runner |
| `muse_test_harness.py` | Full 14-test evaluation suite |
| `generate_comparison.py` | HTML comparison generator |
| `notion_integration.py` | Notion API integration |
| `push_to_notion.py` | Quick single-result push |
| `download_test_images.sh` | Test image downloader |

---

## Test Categories

| Category | Tests | What It Tests |
|----------|-------|---------------|
| Precise Scale | 2 | Proportional sizing, spatial relationships |
| Product Replication | 2 | Matching specific furniture from reference |
| Multi-Element | 2 | 4+ simultaneous changes |
| Photorealistic Integration | 2 | Shadows, reflections, material realism |
| Consistency | 1 | Same prompt 3x - variation check |
| Material Transfer | 2 | Applying material samples to surfaces |
| Style Transfer | 1 | Japandi transformation |
| Edge Cases | 2 | Preserve-all-but-one, clean removal |

---

## Scoring Guide

| Score | Meaning |
|-------|---------|
| 5 | Excellent - Production quality |
| 4 | Good - Minor issues, usable |
| 3 | Acceptable - Intent clear |
| 2 | Poor - Needs regeneration |
| 1 | Failed - Unusable |

---

## Example Workflow

```bash
# 1. Run a test
python3 quick_test.py "Replace countertops with Calacatta marble from reference" \
    test_images/kitchen.jpg test_images/marble_sample.jpg

# 2. Review the result (opens automatically on Mac)

# 3. Push to Notion with score
python3 push_to_notion.py \
    "marble_counter_001" \
    "Material Transfer" \
    "Replace countertops with Calacatta marble from reference" \
    "https://replicate.delivery/xxx/out-0.png" \
    4

# 4. Add notes in Notion UI
```
