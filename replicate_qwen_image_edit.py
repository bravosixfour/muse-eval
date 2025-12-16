"""
title: Qwen Image Edit (Replicate API)
description: Edit/transform images using Qwen-Image-Edit-2509 via Replicate API. Supports up to 3 images for multi-image editing, style transfer, and compositing.
author: Adapted for Replicate
version: 0.2.0
license: MIT
"""
import json
import base64
import logging
import aiohttp
import io
from typing import Any, Dict, Optional, Callable, Awaitable, List, Literal
from pydantic import BaseModel, Field
from fastapi import UploadFile
from fastapi.responses import HTMLResponse
from open_webui.routers.files import upload_file_handler
from open_webui.models.users import Users

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".webp", ".bmp")


def extract_images_from_messages(messages: List[Dict[str, Any]]) -> List[str]:
    """Extract base64 images from the last user message."""
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
                if url and isinstance(url, str) and url.startswith("data:image"):
                    base64_data = url.split(",", 1)[1] if "," in url else url
                    base64_images.append(base64_data)

    return base64_images


class Tools:
    class Valves(BaseModel):
        replicate_api_token: str = Field(
            default="",
            description="Your Replicate API token. Get one at https://replicate.com/account/api-tokens",
        )
        model_version: Literal[
            "qwen/qwen-image-edit-plus",
            "qwen/qwen-image-edit-plus-lora",
            "qwen/qwen-image-edit",
        ] = Field(
            default="qwen/qwen-image-edit-plus",
            description="Replicate model to use. 'plus' supports multi-image, 'plus-lora' adds custom LoRA support.",
        )
        go_fast: bool = Field(
            default=True,
            description="Use Lightning mode (8 steps) for faster inference. Set False for 40 steps.",
        )
        aspect_ratio: Literal[
            "match_input_image", "1:1", "16:9", "9:16", "4:3", "3:4"
        ] = Field(
            default="match_input_image",
            description="Output aspect ratio.",
        )
        output_format: Literal["webp", "jpg", "png"] = Field(
            default="png",
            description="Output image format.",
        )
        output_quality: int = Field(
            default=95,
            description="Output quality (1-100). Applies to webp/jpg.",
            ge=1,
            le=100,
        )
        disable_safety_checker: bool = Field(
            default=False,
            description="Disable NSFW safety checker.",
        )
        return_html_embed: bool = Field(
            default=True,
            description="Return an HTML image embed upon completion.",
        )
        polling_interval: float = Field(
            default=1.0,
            description="Seconds between status checks while waiting for result.",
        )
        max_wait_time: int = Field(
            default=300,
            description="Maximum seconds to wait for generation to complete.",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def edit_image(
        self,
        prompt: str,
        __event_emitter__: Optional[Callable[[Any], Awaitable[None]]] = None,
        __user__: Optional[Dict[str, Any]] = None,
        __request__: Optional[Any] = None,
        __messages__: Optional[List[Dict[str, Any]]] = None,
    ) -> str | HTMLResponse:
        """
        Edit or transform images using Qwen-Image-Edit-2509 via Replicate API.
        Images are automatically extracted from the user's message attachments.

        **CRITICAL: Enhance and expand the user's prompt before passing it to this tool.**

        **Prompt Enhancement Guidelines:**
        - For object placement: Specify position, scale, blending method, and lighting
        - For style changes: Include artistic period, technique, color palette, textures
        - For removals: Specify what to fill the space with
        - For multi-image edits: State which elements from which image to combine

        **Examples:**
        - User: "make it vintage" → "Transform into 1970s photograph with warm faded tones, subtle grain, vignetting, and nostalgic aged film look"
        - User: "combine these two" → "Seamlessly composite subject from first image into the scene from second image, matching lighting and perspective"

        :param prompt: Detailed instruction for the image transformation
        """
        try:
            if not self.valves.replicate_api_token:
                return "❌ Error: Replicate API token not configured. Set it in the tool's Valves settings."

            if not __messages__:
                return "❌ Error: No messages provided. Please attach an image to your message."

            base64_images = extract_images_from_messages(__messages__)
            if not base64_images:
                return "❌ Error: No images found. Please attach at least one image and try again."

            # Limit to 3 images
            if len(base64_images) > 3:
                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": f"⚠️ Found {len(base64_images)} images, using first 3.",
                                "done": False,
                            },
                        }
                    )
                base64_images = base64_images[:3]

            # Build Replicate input
            replicate_input = {
                "prompt": prompt,
                "go_fast": self.valves.go_fast,
                "aspect_ratio": self.valves.aspect_ratio,
                "output_format": self.valves.output_format,
                "output_quality": self.valves.output_quality,
                "disable_safety_checker": self.valves.disable_safety_checker,
            }

            # Add images as data URIs
            for i, img_b64 in enumerate(base64_images):
                key = "image" if i == 0 else f"image_{i + 1}"
                # Replicate expects data URI format
                replicate_input[key] = f"data:image/png;base64,{img_b64}"

            if __event_emitter__:
                mode = "Lightning (8 steps)" if self.valves.go_fast else "Standard (40 steps)"
                await __event_emitter__(
                    {
                        "type": "status",
                        "data": {
                            "description": f"🎨 Editing {len(base64_images)} image(s) with Qwen... [{mode}]",
                            "done": False,
                        },
                    }
                )

            # Submit to Replicate
            headers = {
                "Authorization": f"Bearer {self.valves.replicate_api_token}",
                "Content-Type": "application/json",
                "Prefer": "wait",  # Try to get result in single request
            }

            async with aiohttp.ClientSession() as session:
                # Create prediction
                create_url = f"https://api.replicate.com/v1/models/{self.valves.model_version}/predictions"
                
                async with session.post(
                    create_url,
                    headers=headers,
                    json={"input": replicate_input},
                    timeout=aiohttp.ClientTimeout(total=self.valves.max_wait_time),
                ) as resp:
                    if resp.status not in (200, 201):
                        error_text = await resp.text()
                        return f"❌ Replicate API error ({resp.status}): {error_text}"

                    result = await resp.json()

                # Poll for completion if not already done
                prediction_url = result.get("urls", {}).get("get") or f"https://api.replicate.com/v1/predictions/{result['id']}"
                status = result.get("status")
                
                import asyncio
                elapsed = 0
                
                while status not in ("succeeded", "failed", "canceled"):
                    if elapsed >= self.valves.max_wait_time:
                        return f"⏰ Timeout after {self.valves.max_wait_time}s. Prediction ID: {result.get('id')}"

                    await asyncio.sleep(self.valves.polling_interval)
                    elapsed += self.valves.polling_interval

                    async with session.get(prediction_url, headers=headers) as poll_resp:
                        if poll_resp.status == 200:
                            result = await poll_resp.json()
                            status = result.get("status")
                            
                            if __event_emitter__ and status == "processing":
                                await __event_emitter__(
                                    {
                                        "type": "status",
                                        "data": {
                                            "description": f"🎨 Processing... ({int(elapsed)}s)",
                                            "done": False,
                                        },
                                    }
                                )

                if status == "failed":
                    error = result.get("error", "Unknown error")
                    return f"❌ Generation failed: {error}"

                if status == "canceled":
                    return "❌ Generation was canceled."

                # Get output
                output = result.get("output")
                if not output:
                    return f"❌ No output received. Full response: {json.dumps(result, indent=2)}"

                # Output can be a URL or list of URLs
                image_url = output[0] if isinstance(output, list) else output

                # Try to download and upload to Open WebUI
                final_url = image_url
                try:
                    if __request__ and __user__:
                        async with session.get(image_url) as img_resp:
                            if img_resp.status == 200:
                                content = await img_resp.read()
                                filename = f"qwen_edit_{result.get('id', 'output')}.{self.valves.output_format}"
                                
                                user = None
                                user_id = __user__.get("id")
                                if user_id:
                                    user = Users.get_user_by_id(user_id)
                                
                                if user:
                                    file = UploadFile(file=io.BytesIO(content), filename=filename)
                                    file_item = upload_file_handler(
                                        request=__request__,
                                        file=file,
                                        metadata={},
                                        process=False,
                                        user=user,
                                    )
                                    file_id = getattr(file_item, "id", None)
                                    if file_id:
                                        final_url = f"/api/v1/files/{file_id}/content"
                except Exception as e:
                    logger.warning(f"Failed to upload to Open WebUI, using Replicate URL: {e}")

                if __event_emitter__:
                    await __event_emitter__(
                        {
                            "type": "status",
                            "data": {
                                "description": "✅ Image edited successfully!",
                                "done": True,
                            },
                        }
                    )

                if self.valves.return_html_embed:
                    html_content = f"""<!DOCTYPE html>
<html style="margin:0; padding:0; overflow:hidden;">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ margin: 0; padding: 0; overflow: hidden; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
        .container {{ margin: 0; padding: 0; border: none; line-height: 0; }}
        .image-wrapper {{ margin: 0 0 8px 0; padding: 0; border-radius: 12px; overflow: hidden; line-height: 0; }}
        .image-wrapper img {{ max-width: 100%; height: auto; display: block; border: none; margin: 0; padding: 0; }}
        .prompt-bubble {{ background: rgba(0, 0, 0, 0.05); border: 1px solid rgba(0, 0, 0, 0.1); border-radius: 12px; padding: 12px 16px; margin: 8px 0 0 0; font-size: 13px; line-height: 1.5; color: #333; word-wrap: break-word; }}
        .prompt-label {{ font-weight: 600; color: #666; margin-bottom: 4px; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .prompt-text {{ color: #444; }}
        .meta {{ font-size: 11px; color: #888; margin-top: 8px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="image-wrapper">
            <img src="{final_url}" alt="Edited Image" />
        </div>
        <div class="prompt-bubble">
            <div class="prompt-label">Prompt</div>
            <div class="prompt-text">{prompt}</div>
            <div class="meta">Model: {self.valves.model_version} | Mode: {"Lightning" if self.valves.go_fast else "Standard"}</div>
        </div>
    </div>
</body>
</html>"""
                    return HTMLResponse(
                        content=html_content, headers={"content-disposition": "inline"}
                    )
                else:
                    return f"✅ Image edited!\n\n**Download:** [Edited Image]({final_url})\n\n**Prompt:** {prompt}"

        except aiohttp.ClientError as e:
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": f"❌ Network error: {e}", "done": True}}
                )
            return f"❌ Network error: {e}"
        except Exception as e:
            if __event_emitter__:
                await __event_emitter__(
                    {"type": "status", "data": {"description": f"❌ Error: {e}", "done": True}}
                )
            return f"❌ Error: {e}"
