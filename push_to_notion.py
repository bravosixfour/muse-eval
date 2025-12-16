#!/usr/bin/env python3
"""
Quick push a single test result to Notion.
Use after running quick_test.py to log results.

Usage:
    python push_to_notion.py "test_id" "category" "prompt" "image_url" score
    
Example:
    python push_to_notion.py "sofa_blue_001" "Material Transfer" "Change sofa to blue velvet" "https://..." 5
"""

import os
import sys
from notion_integration import push_single_result, NOTION_TOKEN, NOTION_DATABASE_ID

def main():
    if not NOTION_TOKEN or not NOTION_DATABASE_ID:
        print("❌ Set NOTION_TOKEN and NOTION_DATABASE_ID environment variables")
        return
    
    if len(sys.argv) < 5:
        print(__doc__)
        return
    
    test_id = sys.argv[1]
    category = sys.argv[2]
    prompt = sys.argv[3]
    image_url = sys.argv[4] if len(sys.argv) > 4 else None
    score = int(sys.argv[5]) if len(sys.argv) > 5 else None
    
    success = push_single_result(
        test_id=test_id,
        category=category,
        name=test_id.replace("_", " ").title(),
        prompt=prompt,
        success=True,
        output_url=image_url,
        difficulty="medium"
    )
    
    if success:
        print(f"✅ Pushed to Notion: {test_id}")
    else:
        print(f"❌ Failed to push")

if __name__ == "__main__":
    main()
