"""
Ingredient-Level Nutrition Engine for NutriScore
=================================================
Step 2: ICMR/USDA Clinical Nutrition Database

This module provides per-100g nutritional values for individual ingredients.
When Gemini Vision detects "Basmati Rice: 180g" and "Chicken Thigh: 120g",
this engine calculates the EXACT calories and macros for those specific weights.

Data Sources:
  - ICMR-NIN (Indian Council of Medical Research - National Institute of Nutrition)
    "Indian Food Composition Tables 2017"
  - USDA FoodData Central (fdc.nal.usda.gov)
  - IFCT 2024 updates for regional Indian ingredients

Why per-100g?
  Nutrition science universally measures nutrients per 100g. When Gemini tells
  us an ingredient weighs X grams, we compute: actual_cal = (cal_per_100g * X) / 100
"""

import logging
import os
import sqlite3

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════
#  INGREDIENT NUTRITION DATABASE (per 100g)
#  Source: ICMR-NIN Indian Food Composition Tables + USDA FoodData Central
# ═══════════════════════════════════════════════════════════════════════════
#
#  Format: "ingredient_key": {
#      "display": "Human Name",
#      "cal": calories_per_100g,
#      "protein": grams_per_100g,
#      "carbs": grams_per_100g,
#      "fat": grams_per_100g,
#      "fiber": grams_per_100g,
#      "source": "ICMR/USDA reference"
#  }

INGREDIENT_DB = {
    # ── GRAINS & RICE ──────────────────────────────────────────────────
    "basmati rice": {
        "display": "Basmati Rice (cooked)",
        "cal": 130, "protein": 2.7, "carbs": 28.2, "fat": 0.3, "fiber": 0.4,
        "source": "ICMR-NIN 2017, Item #A001"
    },
    "rice": {
        "display": "White Rice (cooked)",
        "cal": 130, "protein": 2.7, "carbs": 28.2, "fat": 0.3, "fiber": 0.4,
        "source": "USDA FDC #169756"
    },
    "brown rice": {
        "display": "Brown Rice (cooked)",
        "cal": 112, "protein": 2.3, "carbs": 23.5, "fat": 0.8, "fiber": 1.8,
        "source": "USDA FDC #169714"
    },
    "wheat flour": {
        "display": "Whole Wheat Flour (atta)",
        "cal": 340, "protein": 12.1, "carbs": 64.7, "fat": 1.7, "fiber": 11.2,
        "source": "ICMR-NIN 2017"
    },
    "roti": {
        "display": "Whole Wheat Roti/Chapati",
        "cal": 264, "protein": 8.7, "carbs": 50.0, "fat": 3.7, "fiber": 4.0,
        "source": "ICMR-NIN 2017"
    },
    "naan": {
        "display": "Naan Bread",
        "cal": 262, "protein": 8.7, "carbs": 45.5, "fat": 5.1, "fiber": 2.0,
        "source": "USDA FDC #174842"
    },
    "puri": {
        "display": "Puri (fried flatbread)",
        "cal": 350, "protein": 7.0, "carbs": 42.0, "fat": 17.0, "fiber": 2.5,
        "source": "ICMR-NIN 2017"
    },
    "dosa batter": {
        "display": "Dosa Batter (rice+urad dal)",
        "cal": 150, "protein": 4.0, "carbs": 28.0, "fat": 2.0, "fiber": 1.5,
        "source": "ICMR-NIN 2017"
    },
    "idli batter": {
        "display": "Idli Batter (steamed)",
        "cal": 130, "protein": 3.9, "carbs": 26.0, "fat": 0.4, "fiber": 1.2,
        "source": "ICMR-NIN 2017"
    },
    "semolina": {
        "display": "Semolina (Suji/Rava)",
        "cal": 360, "protein": 12.7, "carbs": 72.8, "fat": 1.1, "fiber": 3.9,
        "source": "ICMR-NIN 2017"
    },
    "pasta": {
        "display": "Pasta (cooked)",
        "cal": 131, "protein": 5.0, "carbs": 25.4, "fat": 1.1, "fiber": 1.8,
        "source": "USDA FDC #168927"
    },
    "lasagna": {
        "display": "Lasagna Pasta Sheets (cooked)",
        "cal": 135, "protein": 5.2, "carbs": 26.0, "fat": 1.2, "fiber": 1.5,
        "source": "USDA FDC #168927"
    },
    "bolognese": {
        "display": "Bolognese Meat Sauce",
        "cal": 142, "protein": 11.5, "carbs": 4.8, "fat": 8.8, "fiber": 1.2,
        "source": "USDA FDC #172101"
    },
    "beef": {
        "display": "Minced Beef / Ground Beef",
        "cal": 250, "protein": 26.0, "carbs": 0.0, "fat": 15.0, "fiber": 0.0,
        "source": "USDA FDC #174036"
    },
    "pancetta": {
        "display": "Crispy Pancetta / Bacon",
        "cal": 350, "protein": 22.0, "carbs": 0.5, "fat": 29.0, "fiber": 0.0,
        "source": "USDA FDC #168012"
    },
    "bechamel": {
        "display": "Béchamel White Sauce",
        "cal": 160, "protein": 4.5, "carbs": 12.0, "fat": 10.5, "fiber": 0.2,
        "source": "USDA FDC #173420"
    },
    "ricotta": {
        "display": "Ricotta Cheese",
        "cal": 174, "protein": 11.3, "carbs": 3.0, "fat": 13.0, "fiber": 0.0,
        "source": "USDA FDC #173425"
    },
    "noodles": {
        "display": "Noodles (cooked)",
        "cal": 138, "protein": 4.5, "carbs": 25.6, "fat": 2.1, "fiber": 1.2,
        "source": "USDA FDC #168919"
    },
    "bread": {
        "display": "White Bread",
        "cal": 265, "protein": 9.4, "carbs": 49.2, "fat": 3.2, "fiber": 2.7,
        "source": "USDA FDC #174944"
    },

    # ── PROTEINS (MEAT & FISH) ─────────────────────────────────────────
    "chicken": {
        "display": "Chicken (cooked)",
        "cal": 239, "protein": 27.3, "carbs": 0.0, "fat": 13.6, "fiber": 0.0,
        "source": "USDA FDC #171116"
    },
    "chicken breast": {
        "display": "Chicken Breast (grilled)",
        "cal": 165, "protein": 31.0, "carbs": 0.0, "fat": 3.6, "fiber": 0.0,
        "source": "USDA FDC #171077"
    },
    "chicken thigh": {
        "display": "Chicken Thigh (bone-in)",
        "cal": 209, "protein": 26.0, "carbs": 0.0, "fat": 10.9, "fiber": 0.0,
        "source": "USDA FDC #171082"
    },
    "mutton": {
        "display": "Goat Meat (cooked)",
        "cal": 143, "protein": 27.1, "carbs": 0.0, "fat": 3.0, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "fish": {
        "display": "Fish (white, cooked)",
        "cal": 105, "protein": 22.0, "carbs": 0.0, "fat": 1.7, "fiber": 0.0,
        "source": "USDA FDC #171955"
    },
    "salmon": {
        "display": "Salmon (grilled)",
        "cal": 208, "protein": 20.4, "carbs": 0.0, "fat": 13.4, "fiber": 0.0,
        "source": "USDA FDC #175168"
    },
    "shrimp": {
        "display": "Shrimp (cooked)",
        "cal": 99, "protein": 20.9, "carbs": 0.2, "fat": 1.1, "fiber": 0.0,
        "source": "USDA FDC #175180"
    },
    "egg": {
        "display": "Whole Egg (boiled)",
        "cal": 155, "protein": 12.6, "carbs": 1.1, "fat": 10.6, "fiber": 0.0,
        "source": "USDA FDC #173424"
    },
    "beef": {
        "display": "Beef (cooked, lean)",
        "cal": 250, "protein": 26.1, "carbs": 0.0, "fat": 15.4, "fiber": 0.0,
        "source": "USDA FDC #174032"
    },
    "pork": {
        "display": "Pork (cooked)",
        "cal": 242, "protein": 27.3, "carbs": 0.0, "fat": 14.0, "fiber": 0.0,
        "source": "USDA FDC #167820"
    },

    # ── VEGETARIAN PROTEINS ───────────────────────────────────────────
    "paneer": {
        "display": "Paneer (Indian cottage cheese)",
        "cal": 265, "protein": 18.3, "carbs": 1.2, "fat": 20.8, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "tofu": {
        "display": "Tofu (firm)",
        "cal": 76, "protein": 8.1, "carbs": 1.9, "fat": 4.8, "fiber": 0.3,
        "source": "USDA FDC #174272"
    },
    "dal": {
        "display": "Cooked Dal (lentils)",
        "cal": 116, "protein": 9.0, "carbs": 20.1, "fat": 0.4, "fiber": 7.9,
        "source": "ICMR-NIN 2017"
    },
    "toor dal": {
        "display": "Toor Dal (cooked)",
        "cal": 116, "protein": 9.0, "carbs": 20.0, "fat": 0.4, "fiber": 7.9,
        "source": "ICMR-NIN 2017"
    },
    "chana dal": {
        "display": "Chana Dal (cooked)",
        "cal": 119, "protein": 8.9, "carbs": 20.0, "fat": 1.0, "fiber": 8.2,
        "source": "ICMR-NIN 2017"
    },
    "moong dal": {
        "display": "Moong Dal (cooked)",
        "cal": 105, "protein": 7.0, "carbs": 19.0, "fat": 0.4, "fiber": 7.6,
        "source": "ICMR-NIN 2017"
    },
    "urad dal": {
        "display": "Urad Dal (cooked)",
        "cal": 105, "protein": 8.0, "carbs": 18.0, "fat": 0.6, "fiber": 7.0,
        "source": "ICMR-NIN 2017"
    },
    "chickpeas": {
        "display": "Chickpeas / Chole (cooked)",
        "cal": 164, "protein": 8.9, "carbs": 27.4, "fat": 2.6, "fiber": 7.6,
        "source": "USDA FDC #173757"
    },
    "rajma": {
        "display": "Kidney Beans / Rajma (cooked)",
        "cal": 127, "protein": 8.7, "carbs": 22.8, "fat": 0.5, "fiber": 6.4,
        "source": "ICMR-NIN 2017"
    },
    "soybean": {
        "display": "Soybean (cooked)",
        "cal": 173, "protein": 16.6, "carbs": 9.9, "fat": 9.0, "fiber": 6.0,
        "source": "USDA FDC #174270"
    },

    # ── DAIRY ──────────────────────────────────────────────────────────
    "curd": {
        "display": "Curd / Yogurt",
        "cal": 60, "protein": 3.5, "carbs": 4.7, "fat": 3.3, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "yogurt": {
        "display": "Plain Yogurt",
        "cal": 61, "protein": 3.5, "carbs": 4.7, "fat": 3.3, "fiber": 0.0,
        "source": "USDA FDC #171284"
    },
    "milk": {
        "display": "Whole Milk",
        "cal": 61, "protein": 3.2, "carbs": 4.8, "fat": 3.3, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "cream": {
        "display": "Heavy Cream",
        "cal": 340, "protein": 2.1, "carbs": 2.8, "fat": 36.1, "fiber": 0.0,
        "source": "USDA FDC #170857"
    },
    "cheese": {
        "display": "Cheddar Cheese",
        "cal": 403, "protein": 24.9, "carbs": 1.3, "fat": 33.1, "fiber": 0.0,
        "source": "USDA FDC #173414"
    },
    "mozzarella": {
        "display": "Mozzarella Cheese",
        "cal": 280, "protein": 27.5, "carbs": 3.1, "fat": 17.1, "fiber": 0.0,
        "source": "USDA FDC #173416"
    },
    "butter": {
        "display": "Butter",
        "cal": 717, "protein": 0.9, "carbs": 0.1, "fat": 81.1, "fiber": 0.0,
        "source": "USDA FDC #173430"
    },
    "ghee": {
        "display": "Desi Ghee (clarified butter)",
        "cal": 900, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "raita": {
        "display": "Raita (yogurt + cucumber)",
        "cal": 45, "protein": 2.5, "carbs": 4.0, "fat": 2.0, "fiber": 0.3,
        "source": "ICMR-NIN 2017"
    },

    # ── VEGETABLES ─────────────────────────────────────────────────────
    "potato": {
        "display": "Potato (boiled)",
        "cal": 87, "protein": 1.9, "carbs": 20.1, "fat": 0.1, "fiber": 1.8,
        "source": "USDA FDC #170032"
    },
    "onion": {
        "display": "Onion",
        "cal": 40, "protein": 1.1, "carbs": 9.3, "fat": 0.1, "fiber": 1.7,
        "source": "USDA FDC #170000"
    },
    "tomato": {
        "display": "Tomato",
        "cal": 18, "protein": 0.9, "carbs": 3.9, "fat": 0.2, "fiber": 1.2,
        "source": "USDA FDC #170457"
    },
    "capsicum": {
        "display": "Bell Pepper / Capsicum",
        "cal": 26, "protein": 1.0, "carbs": 6.0, "fat": 0.3, "fiber": 2.1,
        "source": "USDA FDC #170108"
    },
    "spinach": {
        "display": "Spinach (palak)",
        "cal": 23, "protein": 2.9, "carbs": 3.6, "fat": 0.4, "fiber": 2.2,
        "source": "ICMR-NIN 2017"
    },
    "cauliflower": {
        "display": "Cauliflower (gobi)",
        "cal": 25, "protein": 1.9, "carbs": 5.0, "fat": 0.3, "fiber": 2.0,
        "source": "USDA FDC #169986"
    },
    "peas": {
        "display": "Green Peas (matar)",
        "cal": 81, "protein": 5.4, "carbs": 14.5, "fat": 0.4, "fiber": 5.1,
        "source": "USDA FDC #170419"
    },
    "brinjal": {
        "display": "Brinjal / Eggplant (baingan)",
        "cal": 25, "protein": 1.0, "carbs": 5.9, "fat": 0.2, "fiber": 3.0,
        "source": "ICMR-NIN 2017"
    },
    "okra": {
        "display": "Okra / Lady Finger (bhindi)",
        "cal": 33, "protein": 1.9, "carbs": 7.5, "fat": 0.2, "fiber": 3.2,
        "source": "ICMR-NIN 2017"
    },
    "cucumber": {
        "display": "Cucumber",
        "cal": 15, "protein": 0.7, "carbs": 3.6, "fat": 0.1, "fiber": 0.5,
        "source": "USDA FDC #170105"
    },
    "carrot": {
        "display": "Carrot",
        "cal": 41, "protein": 0.9, "carbs": 9.6, "fat": 0.2, "fiber": 2.8,
        "source": "USDA FDC #170393"
    },
    "lettuce": {
        "display": "Lettuce (romaine)",
        "cal": 17, "protein": 1.2, "carbs": 3.3, "fat": 0.3, "fiber": 2.1,
        "source": "USDA FDC #169247"
    },
    "mushroom": {
        "display": "Mushroom",
        "cal": 22, "protein": 3.1, "carbs": 3.3, "fat": 0.3, "fiber": 1.0,
        "source": "USDA FDC #169251"
    },
    "corn": {
        "display": "Sweet Corn",
        "cal": 86, "protein": 3.3, "carbs": 19.0, "fat": 1.4, "fiber": 2.7,
        "source": "USDA FDC #170288"
    },
    "cabbage": {
        "display": "Cabbage",
        "cal": 25, "protein": 1.3, "carbs": 5.8, "fat": 0.1, "fiber": 2.5,
        "source": "USDA FDC #169975"
    },

    # ── COOKING FATS & OILS ───────────────────────────────────────────
    "vegetable oil": {
        "display": "Vegetable / Soybean Oil",
        "cal": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "fiber": 0.0,
        "source": "USDA FDC #172336"
    },
    "mustard oil": {
        "display": "Mustard Oil (sarson ka tel)",
        "cal": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "olive oil": {
        "display": "Olive Oil (Extra Virgin)",
        "cal": 884, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "fiber": 0.0,
        "source": "USDA FDC #171413"
    },
    "coconut oil": {
        "display": "Coconut Oil",
        "cal": 862, "protein": 0.0, "carbs": 0.0, "fat": 100.0, "fiber": 0.0,
        "source": "USDA FDC #171412"
    },

    # ── SPICES & CONDIMENTS ───────────────────────────────────────────
    "ginger": {
        "display": "Fresh Ginger",
        "cal": 80, "protein": 1.8, "carbs": 17.8, "fat": 0.8, "fiber": 2.0,
        "source": "USDA FDC #169231"
    },
    "garlic": {
        "display": "Garlic",
        "cal": 149, "protein": 6.4, "carbs": 33.1, "fat": 0.5, "fiber": 2.1,
        "source": "USDA FDC #169230"
    },
    "turmeric": {
        "display": "Turmeric (haldi)",
        "cal": 312, "protein": 9.7, "carbs": 67.1, "fat": 3.3, "fiber": 22.7,
        "source": "ICMR-NIN 2017"
    },
    "cumin": {
        "display": "Cumin Seeds (jeera)",
        "cal": 375, "protein": 17.8, "carbs": 44.2, "fat": 22.3, "fiber": 10.5,
        "source": "ICMR-NIN 2017"
    },
    "coriander leaves": {
        "display": "Fresh Coriander / Cilantro",
        "cal": 23, "protein": 2.1, "carbs": 3.7, "fat": 0.5, "fiber": 2.8,
        "source": "ICMR-NIN 2017"
    },
    "mint": {
        "display": "Fresh Mint Leaves",
        "cal": 44, "protein": 3.3, "carbs": 8.4, "fat": 0.7, "fiber": 6.8,
        "source": "USDA FDC #173475"
    },
    "chili": {
        "display": "Green Chili",
        "cal": 40, "protein": 1.9, "carbs": 8.8, "fat": 0.4, "fiber": 1.5,
        "source": "ICMR-NIN 2017"
    },
    "lemon": {
        "display": "Lemon Juice",
        "cal": 29, "protein": 1.1, "carbs": 9.3, "fat": 0.3, "fiber": 2.8,
        "source": "USDA FDC #167747"
    },
    "tamarind": {
        "display": "Tamarind (imli)",
        "cal": 239, "protein": 2.8, "carbs": 62.5, "fat": 0.6, "fiber": 5.1,
        "source": "ICMR-NIN 2017"
    },
    "coconut": {
        "display": "Fresh Coconut (grated)",
        "cal": 354, "protein": 3.3, "carbs": 15.2, "fat": 33.5, "fiber": 9.0,
        "source": "ICMR-NIN 2017"
    },
    "jaggery": {
        "display": "Jaggery (gur)",
        "cal": 383, "protein": 0.4, "carbs": 95.0, "fat": 0.1, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "sugar": {
        "display": "White Sugar",
        "cal": 387, "protein": 0.0, "carbs": 100.0, "fat": 0.0, "fiber": 0.0,
        "source": "USDA FDC #169655"
    },
    "salt": {
        "display": "Salt",
        "cal": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0, "fiber": 0.0,
        "source": "N/A"
    },
    "saffron": {
        "display": "Saffron (kesar)",
        "cal": 310, "protein": 11.4, "carbs": 65.4, "fat": 5.9, "fiber": 3.9,
        "source": "USDA FDC #171330"
    },

    # ── SAUCES, CHUTNEYS & DRESSINGS ──────────────────────────────────
    "tomato sauce": {
        "display": "Tomato Sauce/Ketchup",
        "cal": 97, "protein": 1.0, "carbs": 24.0, "fat": 0.1, "fiber": 0.3,
        "source": "USDA FDC #174831"
    },
    "chutney": {
        "display": "Mint-Coriander Chutney",
        "cal": 30, "protein": 1.5, "carbs": 5.0, "fat": 0.5, "fiber": 1.5,
        "source": "ICMR-NIN 2017 (est.)"
    },
    "sambar": {
        "display": "Sambar (lentil stew)",
        "cal": 55, "protein": 3.0, "carbs": 8.5, "fat": 1.0, "fiber": 2.5,
        "source": "ICMR-NIN 2017"
    },
    "gravy": {
        "display": "Curry Gravy (onion-tomato)",
        "cal": 65, "protein": 1.5, "carbs": 7.0, "fat": 3.5, "fiber": 1.2,
        "source": "ICMR-NIN 2017 (est.)"
    },
    "mayo": {
        "display": "Mayonnaise",
        "cal": 680, "protein": 1.0, "carbs": 0.6, "fat": 75.0, "fiber": 0.0,
        "source": "USDA FDC #174642"
    },
    "soy sauce": {
        "display": "Soy Sauce",
        "cal": 53, "protein": 8.1, "carbs": 4.9, "fat": 0.0, "fiber": 0.8,
        "source": "USDA FDC #174250"
    },

    # ── FRUITS & NUTS ─────────────────────────────────────────────────
    "banana": {
        "display": "Banana",
        "cal": 89, "protein": 1.1, "carbs": 22.8, "fat": 0.3, "fiber": 2.6,
        "source": "USDA FDC #173944"
    },
    "mango": {
        "display": "Mango",
        "cal": 60, "protein": 0.8, "carbs": 15.0, "fat": 0.4, "fiber": 1.6,
        "source": "ICMR-NIN 2017"
    },
    "cashew": {
        "display": "Cashew Nuts",
        "cal": 553, "protein": 18.2, "carbs": 30.2, "fat": 43.9, "fiber": 3.3,
        "source": "USDA FDC #170162"
    },
    "almond": {
        "display": "Almonds",
        "cal": 579, "protein": 21.2, "carbs": 21.6, "fat": 49.9, "fiber": 12.5,
        "source": "USDA FDC #170567"
    },
    "peanut": {
        "display": "Peanuts (roasted)",
        "cal": 567, "protein": 25.8, "carbs": 16.1, "fat": 49.2, "fiber": 8.5,
        "source": "USDA FDC #172430"
    },
    "raisin": {
        "display": "Raisins (kishmish)",
        "cal": 299, "protein": 3.1, "carbs": 79.2, "fat": 0.5, "fiber": 3.7,
        "source": "USDA FDC #174652"
    },

    # ── SWEETS & DESSERT COMPONENTS ──────────────────────────────────
    "khoya": {
        "display": "Khoya / Mawa (reduced milk)",
        "cal": 321, "protein": 12.0, "carbs": 20.5, "fat": 22.0, "fiber": 0.0,
        "source": "ICMR-NIN 2017"
    },
    "syrup": {
        "display": "Sugar Syrup",
        "cal": 260, "protein": 0.0, "carbs": 67.0, "fat": 0.0, "fiber": 0.0,
        "source": "USDA (est.)"
    },
    "ice cream base": {
        "display": "Ice Cream",
        "cal": 207, "protein": 3.5, "carbs": 24.0, "fat": 11.0, "fiber": 0.7,
        "source": "USDA FDC #167575"
    },
    "chocolate": {
        "display": "Dark Chocolate",
        "cal": 546, "protein": 5.5, "carbs": 60.5, "fat": 31.3, "fiber": 7.0,
        "source": "USDA FDC #170273"
    },

    # ── MISC & STREET FOOD COMPONENTS ────────────────────────────────
    "papad": {
        "display": "Papad (fried)",
        "cal": 371, "protein": 18.8, "carbs": 52.1, "fat": 9.8, "fiber": 3.5,
        "source": "ICMR-NIN 2017"
    },
    "pickle": {
        "display": "Indian Pickle (achar)",
        "cal": 150, "protein": 1.5, "carbs": 10.0, "fat": 12.0, "fiber": 2.0,
        "source": "ICMR-NIN 2017 (est.)"
    },
    "bhature dough": {
        "display": "Bhatura Dough (fried)",
        "cal": 330, "protein": 7.5, "carbs": 48.0, "fat": 12.0, "fiber": 1.8,
        "source": "ICMR-NIN 2017 (est.)"
    },
    "puri shell": {
        "display": "Puri/Golgappa Shell (fried)",
        "cal": 350, "protein": 5.0, "carbs": 55.0, "fat": 12.0, "fiber": 1.5,
        "source": "ICMR-NIN 2017 (est.)"
    },
    "mint water": {
        "display": "Pani Puri Mint Water",
        "cal": 10, "protein": 0.2, "carbs": 2.5, "fat": 0.0, "fiber": 0.3,
        "source": "ICMR-NIN 2017 (est.)"
    },
    "sprouted moong": {
        "display": "Sprouted Moong (filling)",
        "cal": 30, "protein": 3.0, "carbs": 4.0, "fat": 0.2, "fiber": 1.8,
        "source": "ICMR-NIN 2017"
    },
    "sev": {
        "display": "Sev (gram flour noodles)",
        "cal": 545, "protein": 18.5, "carbs": 45.0, "fat": 33.0, "fiber": 3.0,
        "source": "ICMR-NIN 2017 (est.)"
    },
}


# ═══════════════════════════════════════════════════════════════════════════
#  COOKING METHOD MODIFIERS
#  These adjust the total calorie count based on how the food was prepared.
#  Applied AFTER base ingredient calculation.
# ═══════════════════════════════════════════════════════════════════════════

COOKING_MODIFIERS = {
    "desi_ghee": {
        "label": "Desi Ghee (Clarified Butter)",
        "cal_delta_per_tbsp": 120,
        "fat_delta_per_tbsp": 14.0,
        "description": "Traditional Indian cooking fat. Rich flavor, high saturated fat."
    },
    "mustard_oil": {
        "label": "Mustard Oil (Sarson Ka Tel)",
        "cal_delta_per_tbsp": 124,
        "fat_delta_per_tbsp": 14.0,
        "description": "Pungent North Indian cooking oil. High in erucic acid."
    },
    "vegetable_oil": {
        "label": "Vegetable / Refined Oil",
        "cal_delta_per_tbsp": 120,
        "fat_delta_per_tbsp": 14.0,
        "description": "Standard cooking oil. Neutral flavor."
    },
    "olive_oil": {
        "label": "Extra Virgin Olive Oil",
        "cal_delta_per_tbsp": 119,
        "fat_delta_per_tbsp": 13.5,
        "description": "Heart-healthy monounsaturated fat. Best for low-heat cooking."
    },
    "coconut_oil": {
        "label": "Coconut Oil",
        "cal_delta_per_tbsp": 117,
        "fat_delta_per_tbsp": 13.6,
        "description": "Medium-chain triglycerides. Popular in South Indian cuisine."
    },
    "air_fried": {
        "label": "Air-Fried / Steamed / No Oil",
        "cal_delta_per_tbsp": -40,   # Negative = saves calories
        "fat_delta_per_tbsp": -5.0,
        "description": "Minimal oil cooking. Significantly reduces fat content."
    },
}

PREPARATION_STYLES = {
    "homestyle": {
        "label": "Homestyle (Ghar Ka Khana)",
        "calorie_multiplier": 1.0,
        "description": "Balanced home cooking with moderate oil and spices."
    },
    "restaurant": {
        "label": "Restaurant / Dhaba Style",
        "calorie_multiplier": 1.25,  # Restaurants use ~25% more fat/cream
        "description": "Rich restaurant preparation with extra butter, cream, and oil."
    },
    "diet": {
        "label": "Diet / Health-Conscious",
        "calorie_multiplier": 0.80,  # 20% less oil/sugar
        "description": "Reduced oil, less sugar, measured portions."
    },
}


class IngredientNutritionEngine:
    """
    Calculates per-ingredient and total nutrition from Gemini's detected ingredients.
    
    Flow:
    1. Gemini says: [{"name": "Basmati Rice", "estimated_grams": 180}, ...]
    2. We look up each ingredient in INGREDIENT_DB
    3. We compute: actual_cal = (cal_per_100g × grams) / 100
    4. We sum everything up for the total meal nutrition
    5. We apply cooking method modifiers (ghee, oil, air-fried)
    """

    def __init__(self):
        self.db = INGREDIENT_DB
        self.cooking_modifiers = COOKING_MODIFIERS
        self.preparation_styles = PREPARATION_STYLES
        self.clinical_rows = self._load_clinical_sqlite()

    def _load_clinical_sqlite(self) -> list:
        """Load clinical ingredients from data/clinical_nutrition.db if available."""
        db_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "clinical_nutrition.db"
        )
        if not os.path.exists(db_path):
            logger.warning(f"Clinical SQLite database not found at {db_path}, using in-memory fallback.")
            return []
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ingredients")
            rows = [dict(r) for r in cursor.fetchall()]
            conn.close()
            logger.info(f"Loaded {len(rows)} clinical ingredients from {db_path}.")
            return rows
        except Exception as e:
            logger.error(f"Failed to load clinical database: {e}")
            return []

    def _find_ingredient(self, name: str) -> dict | None:
        """
        Fuzzy-match an ingredient name from Gemini to our ICMR/USDA database.
        
        Uses multi-tier scoring:
          1. Exact match against search aliases or ingredient_id or display_name
          2. Substring containment with longest-match preference
          3. Token / word overlap scoring
          4. In-memory dictionary fallback
        """
        name_lower = name.lower().strip()
        
        # ── TIER 1: Search SQLite Clinical Database ──
        if self.clinical_rows:
            # 1. Exact match in aliases or display name
            for r in self.clinical_rows:
                aliases = [a.strip().lower() for a in r.get("search_aliases", "").split(",")]
                if name_lower in aliases or name_lower == r.get("ingredient_id") or name_lower == r.get("display_name", "").lower():
                    return {
                        "display": r["display_name"],
                        "cal": r["calories_per_100g"],
                        "protein": r["protein_g"],
                        "carbs": r["carbs_g"],
                        "fat": r["fat_g"],
                        "fiber": r["fiber_g"],
                        "water_g": r.get("water_g", 0.0),
                        "density": r.get("density_g_per_ml", 1.0),
                        "source": r["clinical_source"],
                        "category": r["category"]
                    }
            
            # 2. Substring & word overlap candidate ranking
            candidates = []
            name_words = set(name_lower.split())
            for r in self.clinical_rows:
                aliases = [a.strip().lower() for a in r.get("search_aliases", "").split(",")]
                for a in aliases:
                    if a and (a in name_lower or name_lower in a):
                        candidates.append((r, len(a) * 2, "substr"))
                    overlap = len(name_words & set(a.split()))
                    if overlap > 0:
                        candidates.append((r, overlap * 10, "overlap"))
            
            if candidates:
                candidates.sort(key=lambda x: x[1], reverse=True)
                top_match = candidates[0][0]
                return {
                    "display": top_match["display_name"],
                    "cal": top_match["calories_per_100g"],
                    "protein": top_match["protein_g"],
                    "carbs": top_match["carbs_g"],
                    "fat": top_match["fat_g"],
                    "fiber": top_match["fiber_g"],
                    "water_g": top_match.get("water_g", 0.0),
                    "density": top_match.get("density_g_per_ml", 1.0),
                    "source": top_match["clinical_source"],
                    "category": top_match["category"]
                }
        
        # ── TIER 2: Fallback to INGREDIENT_DB dictionary ──
        if name_lower in self.db:
            return self.db[name_lower]
        
        for key, data in self.db.items():
            if key in name_lower:
                return data
        
        for key, data in self.db.items():
            if name_lower in key:
                return data
        
        name_words = set(name_lower.split())
        best_match = None
        best_score = 0
        for key, data in self.db.items():
            key_words = set(key.split())
            overlap = len(name_words & key_words)
            if overlap > best_score:
                best_score = overlap
                best_match = data
        
        if best_score >= 1:
            return best_match
        
        return None

    def calculate_ingredient_nutrition(self, ingredients: list) -> dict:
        """
        Given a list of ingredients from Gemini, calculate per-ingredient
        and total nutrition values.
        
        Parameters
        ----------
        ingredients : list of dict
            Each dict has: {"name": str, "estimated_grams": int, "category": str}
            
        Returns
        -------
        dict with:
            "ingredient_breakdown": list of per-ingredient nutrition
            "totals": aggregated total nutrition for the full dish
        """
        breakdown = []
        totals = {
            "calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0
        }
        
        for ing in ingredients:
            name = ing.get("name", "Unknown")
            grams = ing.get("estimated_grams", 0)
            category = ing.get("category", "other")
            is_primary = ing.get("is_primary", False)
            
            # Look up in our ICMR/USDA database
            db_entry = self._find_ingredient(name)
            
            if db_entry and grams > 0:
                # The core formula: (nutrient_per_100g × actual_grams) / 100
                cal = round((db_entry["cal"] * grams) / 100, 1)
                pro = round((db_entry["protein"] * grams) / 100, 1)
                carb = round((db_entry["carbs"] * grams) / 100, 1)
                fat = round((db_entry["fat"] * grams) / 100, 1)
                fib = round((db_entry["fiber"] * grams) / 100, 1)
                
                breakdown.append({
                    "name": name,
                    "display_name": db_entry["display"],
                    "grams": grams,
                    "category": category,
                    "is_primary": is_primary,
                    "calories": cal,
                    "protein": pro,
                    "carbs": carb,
                    "fat": fat,
                    "fiber": fib,
                    "density": db_entry.get("density", 1.0),
                    "water_g": db_entry.get("water_g", 0.0),
                    "source": db_entry["source"],
                    "matched": True
                })
                
                # Accumulate totals
                totals["calories"] += cal
                totals["protein"] += pro
                totals["carbs"] += carb
                totals["fat"] += fat
                totals["fiber"] += fib
            else:
                # Ingredient not in our database — flag it but don't crash
                breakdown.append({
                    "name": name,
                    "display_name": name,
                    "grams": grams,
                    "category": category,
                    "is_primary": is_primary,
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "fiber": 0,
                    "source": "Not in database",
                    "matched": False
                })
        
        # Round totals
        for key in totals:
            totals[key] = round(totals[key], 1)
        
        return {
            "ingredient_breakdown": breakdown,
            "totals": totals,
            "matched_count": sum(1 for b in breakdown if b["matched"]),
            "total_ingredients": len(breakdown)
        }

    def apply_cooking_modifier(
        self, totals: dict, cooking_fat: str = "vegetable_oil",
        prep_style: str = "homestyle", fat_tablespoons: float = 1.0
    ) -> dict:
        """
        Adjust total nutrition based on cooking method and preparation style.
        
        This is the "Human-in-the-Loop" part — the user tells us:
          - What fat they cooked with (ghee, mustard oil, olive oil, air-fried)
          - How it was prepared (homestyle vs restaurant)
          - How much fat was used (tablespoons)
        
        We then recalculate the totals accordingly.
        """
        modified = dict(totals)
        
        # Apply cooking fat delta
        if cooking_fat in self.cooking_modifiers:
            mod = self.cooking_modifiers[cooking_fat]
            cal_change = mod["cal_delta_per_tbsp"] * fat_tablespoons
            fat_change = mod["fat_delta_per_tbsp"] * fat_tablespoons
            modified["calories"] = round(modified["calories"] + cal_change, 1)
            modified["fat"] = round(modified["fat"] + fat_change, 1)
            modified["cooking_fat_label"] = mod["label"]
            modified["cooking_fat_description"] = mod["description"]
        
        # Apply preparation style multiplier
        if prep_style in self.preparation_styles:
            style = self.preparation_styles[prep_style]
            multiplier = style["calorie_multiplier"]
            modified["calories"] = round(modified["calories"] * multiplier, 1)
            modified["protein"] = round(modified["protein"] * multiplier, 1)
            modified["carbs"] = round(modified["carbs"] * multiplier, 1)
            modified["fat"] = round(modified["fat"] * multiplier, 1)
            modified["fiber"] = round(modified["fiber"] * multiplier, 1)
            modified["prep_style_label"] = style["label"]
            modified["prep_style_description"] = style["description"]
        
        return modified

    def compute_nutriscore(self, totals: dict, total_weight_grams: float = 100) -> str:
        """
        Compute the official French Nutri-Score grade (A to E) based on the
        European Santé Publique France algorithm.
        
        The algorithm scores "negative" nutrients (energy, sugar, saturated fat, sodium)
        and "positive" nutrients (fiber, protein, fruits/vegetables) on a point scale.
        
        Simplified implementation based on per-100g values:
          - High calories + high fat → D or E
          - High protein + high fiber + low fat → A or B
        """
        if total_weight_grams <= 0:
            return "C"
        
        # Convert to per-100g for scoring
        cal_100 = (totals["calories"] / total_weight_grams) * 100
        fat_100 = (totals["fat"] / total_weight_grams) * 100
        pro_100 = (totals["protein"] / total_weight_grams) * 100
        fib_100 = (totals["fiber"] / total_weight_grams) * 100
        
        # Negative points (0-10 scale each)
        neg_energy = min(10, int(cal_100 / 35))
        neg_fat = min(10, int(fat_100 / 1.0))
        negative_total = neg_energy + neg_fat
        
        # Positive points (0-5 scale each)
        pos_protein = min(5, int(pro_100 / 1.6))
        pos_fiber = min(5, int(fib_100 / 0.9))
        positive_total = pos_protein + pos_fiber
        
        # Final score
        final_score = negative_total - positive_total
        
        if final_score <= 0:
            return "A"
        elif final_score <= 3:
            return "B"
        elif final_score <= 10:
            return "C"
        elif final_score <= 18:
            return "D"
        else:
            return "E"

    def get_cooking_options(self) -> dict:
        """Return all available cooking fat and preparation style options for the frontend."""
        return {
            "cooking_fats": {
                key: {"label": v["label"], "description": v["description"]}
                for key, v in self.cooking_modifiers.items()
            },
            "preparation_styles": {
                key: {"label": v["label"], "description": v["description"]}
                for key, v in self.preparation_styles.items()
            }
        }
