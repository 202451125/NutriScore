"""
NutriScore FastAPI Backend Application
=======================================
Dual-Engine Architecture:
  Engine 1 (Local ML):    MobileNetV2 trained model — academic deep learning showcase
  Engine 2 (Gemini AI):   Multimodal vision for zero-shot ingredient decomposition
  Tier 3 (Nutrition):     ICMR/USDA clinical nutrition tables + Nutri-Score algorithm

Serves REST API endpoints for food image recognition, ingredient decomposition,
cooking customization, dynamic portion scaling, and hosts the frontend.
"""

import os
import logging
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from backend.model_service import ModelService
from backend.gemini_service import GeminiVisionService
from backend.ingredient_nutrition import IngredientNutritionEngine
from src.nutrition import NutritionEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="NutriScore AI",
    description="Dual-Engine Food Recognition & Nutritional Intelligence System",
    version="3.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═══════════════════════════════════════════════════════════════════════════
#  Initialize ALL three engines
# ═══════════════════════════════════════════════════════════════════════════
model_service = ModelService()            # Engine 1: MobileNetV2 local model
gemini_service = GeminiVisionService()    # Engine 2: Gemini Vision API
ingredient_engine = IngredientNutritionEngine()  # Tier 3: ICMR/USDA nutrition
nutrition_engine = NutritionEngine()      # Original dish-level nutrition DB

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


# ═══════════════════════════════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_service.model_loaded,
        "model_file": os.path.basename(getattr(model_service, "model_path", "best_nutriscore_model.keras")),
        "model_size_mb": round(getattr(model_service, "model_size", 0) / (1024 * 1024), 2),
        "gemini_available": gemini_service.is_available(),
        "engine": "NutriScore Dual-Engine Architecture v3.0",
        "engines": {
            "local_ml": "MobileNetV2 (101-class Food-101 trained)",
            "gemini_vision": "Gemini 2.0 Flash (zero-shot ingredient decomposition)",
            "nutrition_db": "ICMR-NIN + USDA FoodData Central"
        }
    }


# ═══════════════════════════════════════════════════════════════════════════
#  ENGINE 1: LOCAL ML MODEL PREDICTION (Original endpoint — preserved)
# ═══════════════════════════════════════════════════════════════════════════
@app.post("/api/predict")
async def predict_food_image(
    file: UploadFile = File(...),
    portion: float = Form(1.0)
):
    """
    Engine 1: Uses the trained MobileNetV2 model to classify food images.
    This is the ACADEMIC showcase — demonstrates deep learning training.
    """
    try:
        image_bytes = await file.read()
        pred_result = model_service.predict(image_bytes, filename_hint=file.filename or "")
        food_class = pred_result["predicted_class"]
        confidence = pred_result["confidence"]

        # Fetch nutrition baseline from dish-level DB
        nutri_raw = nutrition_engine.get_nutrition_info(food_class)

        # Scale macros according to the portion slider
        portion_clamped = max(0.25, min(portion, 5.0))
        scaled_data = scale_nutrition(nutri_raw, portion_clamped)
        scaled_data["confidence"] = confidence
        scaled_data["model_source"] = pred_result.get("model_source", "NutriScore Vision Engine")
        scaled_data["top_candidates"] = pred_result.get("top_candidates", [])

        return JSONResponse(content={"success": True, "data": scaled_data})
    except Exception as e:
        logger.error(f"Predict error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════
#  ENGINE 2: GEMINI VISION — INGREDIENT DECOMPOSITION (NEW!)
# ═══════════════════════════════════════════════════════════════════════════
@app.post("/api/analyze")
async def analyze_food_image(
    file: UploadFile = File(...),
    cooking_fat: str = Form("vegetable_oil"),
    prep_style: str = Form("homestyle"),
    fat_tablespoons: float = Form(1.0),
    portion: float = Form(1.0)
):
    """
    Engine 2: Uses Gemini Vision to decompose a food image into ingredients,
    then calculates per-ingredient nutrition using ICMR/USDA tables.
    
    This is the PRODUCTION engine — handles ANY cuisine, breaks dishes into
    components, and supports human-in-the-loop cooking customization.
    
    Flow:
      1. Image → Gemini Vision → dish name + ingredient list with gram weights
      2. Each ingredient → ICMR/USDA lookup → per-ingredient calories/macros
      3. User's cooking choices (ghee/oil/air-fried) → modifier applied
      4. Nutri-Score grade computed from final totals
    """
    try:
        image_bytes = await file.read()
        
        # Step 1: Send image to Gemini for ingredient decomposition
        gemini_result = gemini_service.analyze_food_image(image_bytes)
        
        if not gemini_result.get("success", False):
            return JSONResponse(
                status_code=502,
                content={
                    "success": False,
                    "error": gemini_result.get("error", "Gemini analysis failed"),
                    "engine": "gemini-vision"
                }
            )
        
        # Step 2: Calculate per-ingredient nutrition from ICMR/USDA DB
        ingredients = gemini_result.get("ingredients", [])
        nutrition_result = ingredient_engine.calculate_ingredient_nutrition(ingredients)
        
        # Step 3: Apply cooking method modifiers (human-in-the-loop)
        base_totals = nutrition_result["totals"]
        modified_totals = ingredient_engine.apply_cooking_modifier(
            base_totals,
            cooking_fat=cooking_fat,
            prep_style=prep_style,
            fat_tablespoons=fat_tablespoons
        )
        
        # Step 4: Apply portion scaling
        portion_clamped = max(0.25, min(portion, 5.0))
        if portion_clamped != 1.0:
            for key in ["calories", "protein", "carbs", "fat", "fiber"]:
                modified_totals[key] = round(modified_totals[key] * portion_clamped, 1)
        
        # Step 5: Compute Nutri-Score grade from final values
        total_weight = gemini_result.get("estimated_total_weight_grams", 100)
        nutriscore_grade = ingredient_engine.compute_nutriscore(
            modified_totals, total_weight * portion_clamped
        )
        
        # Build the full response
        response_data = {
            # Dish identification (from Gemini)
            "dish_name": gemini_result.get("dish_name", "Unknown Dish"),
            "cuisine": gemini_result.get("cuisine", "Unknown"),
            "dish_description": gemini_result.get("dish_description", ""),
            "detected_cooking_method": gemini_result.get("detected_cooking_method", "unknown"),
            
            # Ingredient breakdown (the key feature sir asked for!)
            "ingredient_breakdown": nutrition_result["ingredient_breakdown"],
            "matched_ingredients": nutrition_result["matched_count"],
            "total_ingredients": nutrition_result["total_ingredients"],
            
            # Aggregated nutrition (with cooking modifiers applied)
            "totals": modified_totals,
            "nutriscore_grade": nutriscore_grade,
            
            # User's cooking customization applied
            "cooking_customization": {
                "cooking_fat": cooking_fat,
                "cooking_fat_label": modified_totals.get("cooking_fat_label", ""),
                "prep_style": prep_style,
                "prep_style_label": modified_totals.get("prep_style_label", ""),
                "fat_tablespoons": fat_tablespoons,
                "portion_multiplier": portion_clamped
            },
            
            # Metadata
            "portion_label": get_portion_label(portion_clamped),
            "estimated_total_weight_grams": total_weight,
            "confidence_notes": gemini_result.get("confidence_notes", ""),
            "engine": "gemini-vision + ICMR/USDA",
        }
        
        return JSONResponse(content={"success": True, "data": response_data})
        
    except Exception as e:
        logger.error(f"Analyze error: {e}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )


# ═══════════════════════════════════════════════════════════════════════════
#  COOKING OPTIONS — For the "How I Cooked It" UI
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/cooking-options")
def get_cooking_options():
    """Returns available cooking fats and preparation styles for the customizer UI."""
    return ingredient_engine.get_cooking_options()


# ═══════════════════════════════════════════════════════════════════════════
#  RECALCULATE — When user toggles ingredients or changes cooking method
# ═══════════════════════════════════════════════════════════════════════════
@app.post("/api/recalculate")
async def recalculate_nutrition(data: dict):
    """
    Recalculate nutrition when user modifies ingredients or cooking method.
    Called from the frontend when user toggles ingredient checkboxes,
    changes cooking fat, or adjusts preparation style.
    """
    try:
        ingredients = data.get("ingredients", [])
        cooking_fat = data.get("cooking_fat", "vegetable_oil")
        prep_style = data.get("prep_style", "homestyle")
        fat_tablespoons = data.get("fat_tablespoons", 1.0)
        portion = max(0.25, min(data.get("portion", 1.0), 5.0))
        
        # Recalculate from the toggled ingredient list
        nutrition_result = ingredient_engine.calculate_ingredient_nutrition(ingredients)
        
        # Apply cooking modifiers
        modified_totals = ingredient_engine.apply_cooking_modifier(
            nutrition_result["totals"],
            cooking_fat=cooking_fat,
            prep_style=prep_style,
            fat_tablespoons=fat_tablespoons
        )
        
        # Apply portion scaling
        if portion != 1.0:
            for key in ["calories", "protein", "carbs", "fat", "fiber"]:
                modified_totals[key] = round(modified_totals[key] * portion, 1)
        
        # Recompute Nutri-Score
        total_weight = sum(i.get("estimated_grams", 0) for i in ingredients)
        nutriscore_grade = ingredient_engine.compute_nutriscore(
            modified_totals, total_weight * portion
        )
        
        return JSONResponse(content={
            "success": True,
            "data": {
                "totals": modified_totals,
                "nutriscore_grade": nutriscore_grade,
                "ingredient_breakdown": nutrition_result["ingredient_breakdown"],
                "portion_label": get_portion_label(portion)
            }
        })
    except Exception as e:
        logger.error(f"Recalculate error: {e}")
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════
#  EXISTING ENDPOINTS (Preserved from v2.0)
# ═══════════════════════════════════════════════════════════════════════════
@app.get("/api/samples")
def get_sample_dishes():
    """Returns curated carousel items & quick-select dishes with high-quality imagery"""
    samples = [
        {
            "id": "pizza",
            "name": "Neapolitan Pizza",
            "origin": "Italian",
            "image": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "D",
            "preview_cal": 266
        },
        {
            "id": "biryani",
            "name": "Chicken Biryani",
            "origin": "Indian (Hyderabadi)",
            "image": "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "C",
            "preview_cal": 520
        },
        {
            "id": "dosa",
            "name": "Crispy Masala Dosa",
            "origin": "South Indian",
            "image": "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "B",
            "preview_cal": 280
        },
        {
            "id": "idli",
            "name": "Steamed Idli Sambar",
            "origin": "South Indian",
            "image": "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "A",
            "preview_cal": 160
        },
        {
            "id": "samosa",
            "name": "Crispy Samosa",
            "origin": "Indian (Punjabi)",
            "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "D",
            "preview_cal": 260
        },
        {
            "id": "paneer_tikka",
            "name": "Tandoori Paneer Tikka",
            "origin": "North Indian",
            "image": "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "B",
            "preview_cal": 260
        },
        {
            "id": "pani_puri",
            "name": "Crispy Pani Puri",
            "origin": "Indian Street Food",
            "image": "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "C",
            "preview_cal": 180
        },
        {
            "id": "sushi",
            "name": "Fresh Sushi Rolls",
            "origin": "Japanese",
            "image": "https://images.unsplash.com/photo-1579871494447-9811cf80d66c?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "B",
            "preview_cal": 250
        },
        {
            "id": "hamburger",
            "name": "Gourmet Cheeseburger",
            "origin": "American",
            "image": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "D",
            "preview_cal": 540
        },
        {
            "id": "ice_cream",
            "name": "Artisanal Ice Cream",
            "origin": "Dessert",
            "image": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "E",
            "preview_cal": 273
        },
        {
            "id": "caesar_salad",
            "name": "Caesar Garden Salad",
            "origin": "Mediterranean",
            "image": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=600&auto=format&fit=crop&q=80",
            "nutriscore": "A",
            "preview_cal": 180
        }
    ]
    return {"samples": samples}


@app.get("/api/dishes")
def get_dishes_list():
    """Returns list of all supported culinary dishes for quick selection or manual override"""
    return {"dishes": model_service.get_all_supported_dishes()}


@app.get("/api/nutrition/{food_class}")
def get_nutrition_by_class(
    food_class: str,
    portion: float = Query(1.0, ge=0.25, le=5.0)
):
    """Dynamically recalculates macronutrients when the user drags the portion slider"""
    try:
        nutri_raw = nutrition_engine.get_nutrition_info(food_class)
        scaled_data = scale_nutrition(nutri_raw, portion)
        return JSONResponse(content={"success": True, "data": scaled_data})
    except Exception as e:
        return JSONResponse(status_code=404, content={"success": False, "error": str(e)})


# ═══════════════════════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════
def scale_nutrition(base: dict, portion: float) -> dict:
    """Scales calories, protein, carbs, fats, and fiber by the interactive portion multiplier"""
    if not base.get("found", False):
        return base

    nutriscore_grade = base.get("nutriscore_grade", "C")
    match_row = nutrition_engine.df[nutrition_engine.df["food_class"] == base["food_class"]]
    pairing_tip = ""
    if not match_row.empty:
        nutriscore_grade = match_row.iloc[0].get("nutriscore_grade", "C")
        pairing_tip = match_row.iloc[0].get("pairing_tip", "")

    return {
        "food_class": base["food_class"],
        "display_name": base["display_name"],
        "serving_size": base["serving_size"],
        "portion_multiplier": portion,
        "portion_label": get_portion_label(portion),
        "calories_kcal": round(base["calories_kcal"] * portion),
        "protein_g": round(base["protein_g"] * portion, 1),
        "carbs_g": round(base["carbs_g"] * portion, 1),
        "fat_g": round(base["fat_g"] * portion, 1),
        "fiber_g": round(base["fiber_g"] * portion, 1),
        "nutriscore_grade": nutriscore_grade,
        "health_category": base["health_category"],
        "recommendation": base["recommendation"],
        "pairing_tip": pairing_tip or "Pair with fresh greens and plenty of water for optimal metabolic health."
    }


def get_portion_label(p: float) -> str:
    if p <= 0.6:
        return "Light Snack / Taster (0.5x)"
    elif p <= 0.85:
        return "Small Portion (0.75x)"
    elif p <= 1.15:
        return "Standard Single Serving (1.0x)"
    elif p <= 1.6:
        return "Hearty Portion (1.5x)"
    elif p <= 2.2:
        return "Double Portion / Sharing (2.0x)"
    else:
        return f"Feast Portion ({p:.1f}x)"


# ═══════════════════════════════════════════════════════════════════════════
#  SERVE FRONTEND WEB APP (With No-Cache Headers to Prevent Stale Browser Cache)
# ═══════════════════════════════════════════════════════════════════════════
if os.path.exists(FRONTEND_DIR):
    # Mount at /static for backward compatibility
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        response = FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response

    # Also serve static files directly from root (style.css, app.js, assets)
    @app.get("/{file_path:path}")
    def serve_frontend_files(file_path: str):
        full_path = os.path.join(FRONTEND_DIR, file_path)
        if os.path.isfile(full_path):
            resp = FileResponse(full_path)
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return resp
        return JSONResponse(status_code=404, content={"error": "File not found"})
