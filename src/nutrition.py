"""
Nutrition Engine for NutriScore
Handles database lookups, macronutrient breakdowns, and health recommendations.
"""

import os
import pandas as pd


class NutritionEngine:
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Default to data/nutrition_db.csv relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, "data", "nutrition_db.csv")
        
        self.db_path = db_path
        self.df = self._load_database()

    def _load_database(self) -> pd.DataFrame:
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Nutrition database not found at {self.db_path}")
        return pd.read_csv(self.db_path)

    def get_nutrition_info(self, food_class: str) -> dict:
        """
        Lookup nutritional profile and recommendations for a predicted food class.
        """
        food_class_clean = food_class.strip().lower().replace(" ", "_")
        match = self.df[self.df["food_class"] == food_class_clean]

        if match.empty:
            return {
                "found": False,
                "food_class": food_class,
                "display_name": food_class.replace("_", " ").title(),
                "message": "Nutritional information not found for this food category."
            }

        row = match.iloc[0]
        return {
            "found": True,
            "food_class": row["food_class"],
            "display_name": row["display_name"],
            "serving_size": row["serving_size"],
            "calories_kcal": int(row["calories_kcal"]),
            "protein_g": float(row["protein_g"]),
            "carbs_g": float(row["carbs_g"]),
            "fat_g": float(row["fat_g"]),
            "fiber_g": float(row["fiber_g"]),
            "health_category": row["health_category"],
            "recommendation": row["recommendation"],
        }


if __name__ == "__main__":
    engine = NutritionEngine()
    sample = engine.get_nutrition_info("pizza")
    print("Sample Lookup Result:")
    for k, v in sample.items():
        print(f"  {k}: {v}")
