#!/usr/bin/env python3
"""
MUSE Test Results → Notion Integration
Pushes test results to a Notion database for tracking and scoring.

Setup:
1. Create integration at https://www.notion.so/my-integrations
2. Create a database in Notion with these properties:
   - Test ID (title)
   - Category (select)
   - Name (text)
   - Difficulty (select: medium, hard, very_hard)
   - Status (select: passed, failed, pending_review)
   - Score (number 1-5)
   - Prompt (text)
   - Duration (number)
   - Image URL (url)
   - Original Image (url)
   - Notes (text)
   - Date (date)
3. Share the database with your integration
4. Set environment variables:
   - NOTION_TOKEN=secret_xxx
   - NOTION_DATABASE_ID=xxx

Usage:
    python notion_integration.py                    # Push latest results
    python notion_integration.py test_results.json  # Push specific file
    python notion_integration.py --setup            # Create database template
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path

NOTION_TOKEN = os.environ.get("NOTION_TOKEN", "")
NOTION_DATABASE_ID = os.environ.get("NOTION_DATABASE_ID", "")
NOTION_API_URL = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def notion_headers():
    return {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }


def create_database_template(parent_page_id: str) -> dict:
    """Create a new database with the right schema."""
    
    payload = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "MUSE Test Results"}}],
        "properties": {
            "Test ID": {"title": {}},
            "Category": {
                "select": {
                    "options": [
                        {"name": "Precise Scale", "color": "blue"},
                        {"name": "Product Replication", "color": "purple"},
                        {"name": "Multi-Element", "color": "red"},
                        {"name": "Photorealistic Integration", "color": "orange"},
                        {"name": "Consistency", "color": "yellow"},
                        {"name": "Material Transfer", "color": "green"},
                        {"name": "Style Transfer", "color": "pink"},
                        {"name": "Edge Cases", "color": "gray"},
                    ]
                }
            },
            "Name": {"rich_text": {}},
            "Difficulty": {
                "select": {
                    "options": [
                        {"name": "medium", "color": "green"},
                        {"name": "hard", "color": "yellow"},
                        {"name": "very_hard", "color": "red"},
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "passed", "color": "green"},
                        {"name": "failed", "color": "red"},
                        {"name": "pending_review", "color": "yellow"},
                    ]
                }
            },
            "Score": {"number": {"format": "number"}},
            "Prompt": {"rich_text": {}},
            "Duration (s)": {"number": {"format": "number"}},
            "Result Image": {"url": {}},
            "Notes": {"rich_text": {}},
            "Date": {"date": {}},
            "Success Criteria": {"rich_text": {}},
            "Failure Indicators": {"rich_text": {}},
        }
    }
    
    resp = requests.post(
        f"{NOTION_API_URL}/databases",
        headers=notion_headers(),
        json=payload
    )
    
    if resp.status_code == 200:
        data = resp.json()
        print(f"✅ Created database: {data['id']}")
        print(f"   Set NOTION_DATABASE_ID={data['id']}")
        return data
    else:
        print(f"❌ Failed to create database: {resp.text}")
        return None


def push_test_result(result: dict, test_case: dict = None) -> bool:
    """Push a single test result to Notion."""
    
    # Build properties
    properties = {
        "Test ID": {
            "title": [{"text": {"content": result.get("test_id", "unknown")}}]
        },
        "Category": {
            "select": {"name": result.get("category", "Unknown")}
        },
        "Name": {
            "rich_text": [{"text": {"content": result.get("name", "")[:2000]}}]
        },
        "Difficulty": {
            "select": {"name": result.get("difficulty", "medium")}
        },
        "Status": {
            "select": {"name": "passed" if result.get("success") else "failed"}
        },
        "Prompt": {
            "rich_text": [{"text": {"content": result.get("prompt", "")[:2000]}}]
        },
        "Duration (s)": {
            "number": result.get("duration_seconds", 0)
        },
        "Date": {
            "date": {"start": result.get("timestamp", datetime.now().isoformat())[:10]}
        },
    }
    
    # Add image URL if available
    if result.get("output_url"):
        properties["Result Image"] = {"url": result["output_url"]}
    
    # Add criteria from test case if provided
    if test_case:
        criteria = ", ".join(test_case.get("success_criteria", []))
        failures = ", ".join(test_case.get("failure_indicators", []))
        
        if criteria:
            properties["Success Criteria"] = {
                "rich_text": [{"text": {"content": criteria[:2000]}}]
            }
        if failures:
            properties["Failure Indicators"] = {
                "rich_text": [{"text": {"content": failures[:2000]}}]
            }
    
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties
    }
    
    resp = requests.post(
        f"{NOTION_API_URL}/pages",
        headers=notion_headers(),
        json=payload
    )
    
    if resp.status_code == 200:
        print(f"  ✅ {result.get('test_id')}: pushed to Notion")
        return True
    else:
        print(f"  ❌ {result.get('test_id')}: {resp.status_code} - {resp.text[:200]}")
        return False


def push_results_file(filepath: str):
    """Push all results from a JSON file."""
    
    path = Path(filepath)
    if not path.exists():
        print(f"❌ File not found: {filepath}")
        return
    
    with open(path) as f:
        data = json.load(f)
    
    results = data.get("results", [])
    print(f"\n📤 Pushing {len(results)} results to Notion...")
    
    success = 0
    for result in results:
        if push_test_result(result):
            success += 1
    
    print(f"\n✅ Done: {success}/{len(results)} pushed successfully")


def push_single_result(
    test_id: str,
    category: str,
    name: str,
    prompt: str,
    success: bool,
    output_url: str = None,
    duration: float = 0,
    difficulty: str = "medium",
    success_criteria: list = None,
    failure_indicators: list = None
):
    """Convenience function to push a single result programmatically."""
    
    result = {
        "test_id": test_id,
        "category": category,
        "name": name,
        "prompt": prompt,
        "success": success,
        "output_url": output_url,
        "duration_seconds": duration,
        "difficulty": difficulty,
        "timestamp": datetime.now().isoformat()
    }
    
    test_case = {}
    if success_criteria:
        test_case["success_criteria"] = success_criteria
    if failure_indicators:
        test_case["failure_indicators"] = failure_indicators
    
    return push_test_result(result, test_case if test_case else None)


def update_score(page_id: str, score: int, notes: str = ""):
    """Update the score for an existing result."""
    
    properties = {
        "Score": {"number": score},
        "Status": {"select": {"name": "passed" if score >= 3 else "failed"}}
    }
    
    if notes:
        properties["Notes"] = {
            "rich_text": [{"text": {"content": notes[:2000]}}]
        }
    
    resp = requests.patch(
        f"{NOTION_API_URL}/pages/{page_id}",
        headers=notion_headers(),
        json={"properties": properties}
    )
    
    return resp.status_code == 200


def main():
    if not NOTION_TOKEN:
        print("❌ NOTION_TOKEN not set")
        print("   Get one at https://www.notion.so/my-integrations")
        return
    
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        
        if arg == "--setup":
            if len(sys.argv) < 3:
                print("Usage: python notion_integration.py --setup <parent_page_id>")
                print("       The parent_page_id is the Notion page where you want the database")
                return
            create_database_template(sys.argv[2])
            return
        
        elif arg.endswith(".json"):
            if not NOTION_DATABASE_ID:
                print("❌ NOTION_DATABASE_ID not set")
                return
            push_results_file(arg)
            return
    
    # Default: look for latest results
    if not NOTION_DATABASE_ID:
        print("❌ NOTION_DATABASE_ID not set")
        print("   Create a database with --setup first, or set the ID manually")
        return
    
    results_file = Path("test_results/test_results.json")
    if results_file.exists():
        push_results_file(str(results_file))
    else:
        print("No test_results.json found. Run tests first or specify a file.")


if __name__ == "__main__":
    main()
