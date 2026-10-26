"""
Gemini Vision Service for NutriScore
=====================================
Engine 2: Production Semantic Vision Engine

Uses the Gemini REST API directly via `requests` — no SDK dependency needed.
This is actually more lightweight and reliable than the SDK.

This module sends food images to Google's Gemini multimodal model and receives
structured ingredient-level decomposition. Unlike the MobileNetV2 model which
only classifies into 101 fixed categories, Gemini can:
  1. Recognize ANY cuisine (Indian, Japanese, Mexican, etc.)
  2. Decompose a dish into its individual ingredients with gram estimates
  3. Detect cooking style cues (fried, steamed, grilled, etc.)

Architecture:
  Image bytes → Gemini REST API → Structured JSON → Ingredient Nutrition Lookup
"""

import os
import json
import base64
import logging
import requests
from dotenv import load_dotenv

# Load .env file so GEMINI_API_KEY is available
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiVisionService:
    """
    Sends food images to Gemini via REST API and receives structured ingredient breakdown.
    
    Why REST instead of SDK?
    -------------------------
    The `google-generativeai` SDK is a large package with many transitive dependencies
    (protobuf, grpcio, etc.). Using the REST API directly with `requests` is:
      - Lighter (no extra install needed)
      - More debuggable (you can see the exact HTTP request/response)
      - Equally powerful (same API, just a different client)
    """

    # REST API endpoint for Gemini
    API_BASE = "https://generativelanguage.googleapis.com/v1beta/models"
    MODEL_NAME = "gemini-3.5-flash"  # Fast, free-tier friendly, excellent at vision

    # The structured prompt that tells Gemini exactly what we need back
    ANALYSIS_PROMPT = """You are an expert nutritionist and food recognition AI.
Analyze the food image and provide a detailed breakdown.

You MUST respond with ONLY valid JSON (no markdown, no code fences, no explanation).
Use this exact schema:

{
  "dish_name": "Human-readable dish name (e.g., Chicken Biryani, Masala Dosa)",
  "cuisine": "Cuisine type (e.g., Indian, South Indian, Italian, Japanese)",
  "dish_description": "One sentence describing the dish",
  "detected_cooking_method": "Primary cooking method (e.g., fried, steamed, grilled, baked, roasted, raw)",
  "ingredients": [
    {
      "name": "Ingredient name (e.g., Basmati Rice, Chicken Thigh, Paneer Cubes)",
      "estimated_grams": 150,
      "category": "grain|protein|vegetable|dairy|fat|spice|condiment|other",
      "is_primary": true
    }
  ],
  "estimated_total_weight_grams": 350,
  "confidence_notes": "Any caveats about the estimation"
}

Rules:
1. List ALL visible ingredients, even garnishes and chutneys
2. Estimate grams based on standard serving sizes visible in the image  
3. Mark 2-3 main ingredients as is_primary=true
4. For Indian dishes, include specific spice/oil components (ghee, mustard oil, etc.)
5. If unsure about exact dish, give your best identification
6. estimated_grams should be realistic for what's visible on the plate
"""

    def __init__(self):
        """Initialize the Gemini client with API key from environment."""
        self.api_key = os.environ.get("GEMINI_API_KEY", "")
        self.available = False

        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY not found in environment. "
                "Gemini Vision Engine will be unavailable. "
                "Set it in your .env file."
            )
            return

        # Test connection with a simple request
        try:
            # Quick validation: list models to check if key works
            test_url = f"{self.API_BASE}?key={self.api_key}"
            resp = requests.get(test_url, timeout=10)
            if resp.status_code == 200:
                self.available = True
                logger.info("✅ Gemini Vision Engine initialized (REST API, gemini-3.5-flash)")
            else:
                logger.error(f"Gemini API key validation failed: {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            logger.error(f"Failed to connect to Gemini API: {e}")

    def analyze_food_image(self, image_bytes: bytes) -> dict:
        """
        Send a food image to Gemini Vision and get structured ingredient breakdown.
        
        Parameters
        ----------
        image_bytes : bytes
            Raw bytes of the uploaded food image (JPG, PNG, WebP)
            
        Returns
        -------
        dict
            Structured result with dish_name, cuisine, ingredients[], etc.
            On failure, returns {"error": "...", "success": False}
            
        How it works internally
        -----------------------
        1. Base64-encode the image bytes
        2. Build the REST API request body with both text prompt and image
        3. POST to Gemini's generateContent endpoint
        4. Parse the JSON response and return it
        """
        if not self.available:
            return {
                "error": "Gemini Vision Engine not available. Check API key in .env file.",
                "available": False,
                "success": False
            }

        try:
            # Step 1: Base64-encode the image
            # REST API requires images as base64 strings (unlike SDK which accepts raw bytes)
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Step 2: Build the request body
            # This follows Google's REST API schema for multimodal content
            url = f"{self.API_BASE}/{self.MODEL_NAME}:generateContent?key={self.api_key}"
            
            payload = {
                "contents": [
                    {
                        "parts": [
                            {"text": self.ANALYSIS_PROMPT},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_b64
                                }
                            }
                        ]
                    }
                ],
                "generationConfig": {
                    "temperature": 0.2,       # Low = more deterministic/accurate
                    "maxOutputTokens": 4096,  # Enough for detailed ingredient lists
                    "responseMimeType": "application/json"  # Force JSON output
                }
            }
            
            # Step 3: Send to Gemini (with retry for 503/overload)
            max_retries = 3
            response = None
            for attempt in range(max_retries):
                response = requests.post(
                    url,
                    json=payload,
                    headers={"Content-Type": "application/json"},
                    timeout=45  # 45 second timeout for slower networks
                )
                if response.status_code == 503:
                    import time
                    wait_time = 2 * (attempt + 1)
                    logger.warning(f"Gemini 503 overloaded, retrying in {wait_time}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                break
            
            if response.status_code != 200:
                error_msg = response.text[:500]
                logger.error(f"Gemini API error {response.status_code}: {error_msg}")
                return {
                    "error": f"Gemini API returned status {response.status_code}",
                    "details": error_msg,
                    "success": False
                }
            
            # Step 4: Extract the text from Gemini's response
            resp_json = response.json()
            candidates = resp_json.get("candidates", [])
            if not candidates:
                return {"error": "No response from Gemini", "success": False}
            
            raw_text = candidates[0]["content"]["parts"][0]["text"].strip()
            
            # Clean up: sometimes Gemini wraps response in ```json ... ```
            if raw_text.startswith("```"):
                lines = raw_text.split("\n")
                # Remove first line (```json) and last line (```)
                lines = [l for l in lines if not l.strip().startswith("```")]
                raw_text = "\n".join(lines).strip()
            
            # Step 5: Parse the JSON
            result = json.loads(raw_text)
            result["engine"] = "gemini-vision"
            result["success"] = True
            
            logger.info(
                f"🍽️ Gemini identified: {result.get('dish_name', 'Unknown')} "
                f"({len(result.get('ingredients', []))} ingredients)"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Gemini returned invalid JSON: {e}")
            return {
                "error": f"Failed to parse Gemini response: {e}",
                "raw_response": raw_text[:500] if 'raw_text' in dir() else "N/A",
                "success": False
            }
        except requests.exceptions.Timeout:
            logger.error("Gemini API request timed out (45s)")
            return {
                "error": "Gemini API timed out. Please try again.",
                "success": False
            }
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "error": f"Gemini API error: {str(e)}",
                "success": False
            }

    def is_available(self) -> bool:
        """Check if Gemini service is properly configured and ready."""
        return self.available


# Quick self-test when running this file directly
if __name__ == "__main__":
    print("🔧 Testing Gemini Vision Service (REST API)...")
    service = GeminiVisionService()
    print(f"   Available: {service.available}")
    if service.available:
        print("   ✅ Gemini is ready to analyze food images!")
    else:
        print("   ❌ Set GEMINI_API_KEY in your .env file")
