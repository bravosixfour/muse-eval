"""
title: Qwen Image Edit (Replicate API) - MUSE Edition
description: Image editing tool for MUSE interior design assistant. Executes Qwen-Image-Edit-2509 via Replicate. Supports up to 3 images for multi-image editing.
author: MUSE System
version: 0.3.0
license: MIT
"""
import json
import base64
import logging
import aiohttp
import asyncio
import io
from typing import Any, Dict, Optional, Callable, Awaitable, List, Literal
from pydantic import BaseModel, Field
from fastapi import UploadFile
from fastapi.responses import HTMLResponse

# Conditional imports for Open WebUI integration
try:
    from open_webui.routers.files import upload_file_handler
    from open_webui.models.users import Users
    OPENWEBUI_AVAILABLE = True
except ImportError:
    OPENWEBUI_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_images_from_messages(messages: List[Dict[str, Any]], max_images: int = 3) -> List[str]:
    """
    Extract base64 images from the last user message.
    Returns list of base64 strings (without data URI prefix).
    """
    last_user_message = None
    for message in reversed(messages):
        if message.get("role") == "user":
            last_user_message = message
            break

    if not last_user_message:
        return []

    base64_images: List[str] = []
    content = last_user_message.get("content")

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict) and item.get("type") == "image_url":
                image_url_obj = item.get("image_url", {})
                url = (
                    image_url_obj.get("url")
                    if isinstance(image_url_obj, dict)
                    else None
                )
                if url and isinstance(url, str):
                    if url.startswith("data:image"):
                        # Extract base64 from data URI
                        base64_data = url.split(",", 1)[1] if "," in url else url
                        base64_images.append(base64_data)
                    elif url.startswith("http"):
                        # Keep URL as-is for Replicate to fetch
                        base64_images.append(url)
                        
                if len(base64_images) >= max_images:
                    break

    return base64_images


def detect_image_mime(base64_data: str) -> str:
    """Detect image MIME type from base64 header bytes."""
    try:
        header = base64.b64decode(base64_data[:32])
        if header.startswith(b'\x89PNG'):
            return "image/png"
        elif header.startswith(b'\xff\xd8\xff'):
            return "image/jpeg"
        elif header.startswith(b'GIF'):
            return "image/gif"
        elif header.startswith(b'RIFF') and b'WEBP' in header:
            return "image/webp"
    except:
        pass
    return "image/png"  # Default fallback


class Tools:
    class Valves(BaseModel):
        replicate_api_token: str = Field(
            default="",
            description="Replicate API token from https://replicate.com/account/api-tokens",
        )
        model_version: Literal[
            "qwen/qwen-image-edit-plus",
            "qwen/qwen-image-edit-plus-lora",
            "qwen/qwen-image-edit",
        ] = Field(
            default="qwen/qwen-image-edit-plus",
            description="Model variant. 'plus' for multi-image, 'plus-lora' for custom LoRA support.",
        )
        go_fast: bool = Field(
            default=True,
            description="Lightning mode (8 steps). Set False for 40-step high-fidelity.",
        )
        default_aspect_ratio: Literal[
            "match_input_image", "1:1", "16:9", "9:16", "4:3", "3:4"
        ] = Field(
            default="match_input_image",
            description="Default output aspect ratio.",
        )
        output_format: Literal["webp", "jpg", "png"] = Field(
            default="png",
            description="Output image format.",
        )
        output_quality: int = Field(
            default=95,
            description="Output quality (1-100) for webp/jpg.",
            ge=1,
            le=100,
        )
        disable_safety_checker: bool = Field(
            default=False,
            description="Disable NSFW safety checker.",
        )
        max_wait_time: int = Field(
            default=300,
            description="Maximum seconds to wait for generation.",
        )
        polling_interval: float = Field(
            default=1.5,
            description="Seconds between status checks.",
        )
        return_html_embed: bool = Field(
            default=True,
            description="Return styled HTML embed (vs plain markdown).",
        )
        show_prompt_in_result: bool = Field(
            default=False,
            description="Show the generation prompt in result display.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def edit_image(
        self,
        prompt: str,
        aspect_ratio: Optional[str] = None,
        high_fidelity: Optional[bool] = None,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
        __user__: Optional[Dict[str, Any]] = None,
        __request__: Optional[Any] = None,
        __messages__: Optional[List[Dict[str, Any]]] = None,
    ) -> str | HTMLResponse:
        """
        Execute image editing via Qwen-Image-Edit-2509.
        
        Images are automatically extracted from the user's message:
        - First image → primary image to edit (image)
        - Second image → reference material/style/product (image_2)
        - Third image → additional context (image_3)
        
        The MUSE system crafts detailed prompts. This tool executes them.
        
        :param prompt: Detailed editing instruction crafted by MUSE
        :param aspect_ratio: Override aspect ratio (optional)
        :param high_fidelity: Use 40-step mode for this edit (optional)
        :return: Edited image result
        """
        try:
            # Validation
            if not self.valves.replicate_api_token:
                return "❌ Replicate API token not configured. Add it in tool Valves settings."

            if not __messages__:
                return "❌ No messages in context. Attach image(s) to proceed."

            # Extract images
            images = extract_images_from_messages(__messages__, max_images=3)
            if not images:
                return "❌ No images found. Attach at least one image to edit."

            # Build request
            use_fast = self.valves.go_fast if high_fidelity is None else not high_fidelity
            
            replicate_input = {
                "prompt": prompt,
                "go_fast": use_fast,
                "aspect_ratio": aspect_ratio or self.valves.default_aspect_ratio,
                "output_format": self.valves.output_format,
                "output_quality": self.valves.output_quality,
                "disable_safety_checker": self.valves.disable_safety_checker,
            }

            # Map images to slots
            image_keys = ["image", "image_2", "image_3"]
            for i, img in enumerate(images):
                if img.startswith("http"):
                    # URL - pass directly
                    replicate_input[image_keys[i]] = img
                else:
                    # Base64 - wrap in data URI
                    mime = detect_image_mime(img)
                    replicate_input[image_keys[i]] = f"data:{mime};base64,{img}"

            # Status update
            if __event_emitter__:
                mode = "Lightning" if use_fast else "High-fidelity"
                img_count = len(images)
                await __event_emitter__({
                    "type": "status",
                    "data": {
                        "description": f"🎨 Generating... [{img_count} image{'s' if img_count > 1 else ''}, {mode}]",
                        "done": False,
                    },
                })

            # API call
            headers = {
                "Authorization": f"Bearer {self.valves.replicate_api_token}",
                "Content-Type": "application/json",
                "Prefer": "wait",
            }

            async with aiohttp.ClientSession() as session:
                # Submit prediction
                create_url = f"https://api.replicate.com/v1/models/{self.valves.model_version}/predictions"
                
                async with session.post(
                    create_url,
                    headers=headers,
                    json={"input": replicate_input},
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status not in (200, 201):
                        error_text = await resp.text()
                        logger.error(f"Replicate API error: {resp.status} - {error_text}")
                        return f"❌ API error ({resp.status}): {error_text[:200]}"

                    result = await resp.json()

                # Poll for completion
                prediction_id = result.get("id")
                prediction_url = result.get("urls", {}).get("get") or f"https://api.replicate.com/v1/predictions/{prediction_id}"
                status = result.get("status")
                
                elapsed = 0
                last_status_update = 0
                
                while status not in ("succeeded", "failed", "canceled"):
                    if elapsed >= self.valves.max_wait_time:
                        return f"⏰ Timeout after {self.valves.max_wait_time}s. ID: {prediction_id}"

                    await asyncio.sleep(self.valves.polling_interval)
                    elapsed += self.valves.polling_interval

                    async with session.get(prediction_url, headers=headers) as poll_resp:
                        if poll_resp.status == 200:
                            result = await poll_resp.json()
                            status = result.get("status")
                            
                            # Update status every 5 seconds
                            if __event_emitter__ and elapsed - last_status_update >= 5:
                                await __event_emitter__({
                                    "type": "status",
                                    "data": {
                                        "description": f"🎨 Processing... ({int(elapsed)}s)",
                                        "done": False,
                                    },
                                })
                                last_status_update = elapsed

                # Handle result
                if status == "failed":
                    error = result.get("error", "Unknown error")
                    logger.error(f"Generation failed: {error}")
                    return f"❌ Generation failed: {error}"

                if status == "canceled":
                    return "❌ Generation canceled."

                output = result.get("output")
                if not output:
                    return f"❌ No output. Response: {json.dumps(result, indent=2)[:500]}"

                image_url = output[0] if isinstance(output, list) else output

                # Try to save to Open WebUI
                final_url = image_url
                if OPENWEBUI_AVAILABLE and __request__ and __user__:
                    try:
                        async with session.get(image_url) as img_resp:
                            if img_resp.status == 200:
                                content = await img_resp.read()
                                filename = f"muse_{prediction_id}.{self.valves.output_format}"
                                
                                user_id = __user__.get("id")
                                user = Users.get_user_by_id(user_id) if user_id else None
                                
                                if user:
                                    file = UploadFile(file=io.BytesIO(content), filename=filename)
                                    file_item = upload_file_handler(
                                        request=__request__,
                                        file=file,
                                        metadata={"source": "muse", "model": self.valves.model_version},
                                        process=False,
                                        user=user,
                                    )
                                    if hasattr(file_item, "id"):
                                        final_url = f"/api/v1/files/{file_item.id}/content"
                    except Exception as e:
                        logger.warning(f"Failed to save to Open WebUI: {e}")

                # Success status
                if __event_emitter__:
                    await __event_emitter__({
                        "type": "status",
                        "data": {"description": "✅ Complete", "done": True},
                    })

                # Format response
                if self.valves.return_html_embed:
                    prompt_section = ""
                    if self.valves.show_prompt_in_result:
                        escaped_prompt = prompt.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
                        prompt_section = f'''
                        <div class="prompt-info">
                            <span class="label">Prompt</span>
                            <p>{escaped_prompt}</p>
                        </div>'''
                    
                    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
.container {{ max-width: 100%; }}
.image-frame {{ border-radius: 8px; overflow: hidden; line-height: 0; }}
.image-frame img {{ width: 100%; height: auto; display: block; }}
.prompt-info {{ background: #f5f5f5; border-radius: 8px; padding: 12px; margin-top: 8px; font-size: 13px; }}
.prompt-info .label {{ font-weight: 600; color: #666; font-size: 11px; text-transform: uppercase; }}
.prompt-info p {{ color: #333; margin-top: 4px; line-height: 1.4; }}
</style></head>
<body>
<div class="container">
    <div class="image-frame"><img src="{final_url}" alt="Generated"></div>
    {prompt_section}
</div>
</body></html>'''
                    return HTMLResponse(content=html, headers={"content-disposition": "inline"})
                else:
                    return f"![Generated Image]({final_url})"

        except aiohttp.ClientError as e:
            logger.error(f"Network error: {e}")
            if __event_emitter__:
                await __event_emitter__({"type": "status", "data": {"description": f"❌ Network error", "done": True}})
            return f"❌ Network error: {e}"
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            if __event_emitter__:
                await __event_emitter__({"type": "status", "data": {"description": f"❌ Error", "done": True}})
            return f"❌ Error: {e}"
