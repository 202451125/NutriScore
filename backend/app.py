"""
NutriScore FastAPI Backend Application
Serves REST API endpoints for food image recognition, dynamic portion scaling,
and hosts the aesthetic frontend.
"""

import os
from fastapi import FastAPI, UploadFile, File, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from backend.model_service import ModelService
from src.nutrition import NutritionEngine

app = FastAPI(
    title="NutriScore AI",
    description="Food Recognition & European Nutri-Score Nutritional Intelligence System",
    version="2.0.0"
)

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
model_service = ModelService()
nutrition_engine = NutritionEngine()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model_service.model_loaded,
        "engine": "NutriScore Vision Engine"
    }


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


@app.post("/api/predict")
async def predict_food_image(
    file: UploadFile = File(...),
    portion: float = Form(1.0)
):
    """
    Accepts food image upload, predicts category, and retrieves
    macronutrients dynamically scaled by the portion slider.
    """
    try:
        image_bytes = await file.read()
        pred_result = model_service.predict(image_bytes, filename_hint=file.filename or "")
        food_class = pred_result["predicted_class"]
        confidence = pred_result["confidence"]

        # Fetch nutrition baseline
        nutri_raw = nutrition_engine.get_nutrition_info(food_class)

        # Scale macros according to the portion slider
        portion_clamped = max(0.25, min(portion, 5.0))
        scaled_data = scale_nutrition(nutri_raw, portion_clamped)
        scaled_data["confidence"] = confidence
        scaled_data["model_source"] = pred_result.get("model_source", "NutriScore Vision Engine")

        return JSONResponse(content={"success": True, "data": scaled_data})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})


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


def scale_nutrition(base: dict, portion: float) -> dict:
    """Scales calories, protein, carbs, fats, and fiber by the interactive portion multiplier"""
    if not base.get("found", False):
        return base

    nutriscore_grade = base.get("nutriscore_grade", "C")
    # Grab from row if available
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


# Serve Frontend Web App
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_index():
        return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))
