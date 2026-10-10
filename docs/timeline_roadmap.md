# NutriScore: Project Schedule & Timeline Roadmap (2026)

## Overview
This document outlines the end-to-end development phases, work packages, and milestone dates for the **NutriScore** AI-based Food Recognition and Nutritional Analysis System.

---

## Team Responsibilities

- **Lead ML / AI Engineer:** Model research, dataset preprocessing, transfer learning pipeline, hyperparameter tuning, model validation, and metrics reporting.
- **Full-Stack & UI/UX Engineer:** REST API framework, web interface, animated macronutrient sliders, confidence visualization, and system integration.

---

## Detailed Sprint Schedule

### Phase 1: Research, Formulation & Dataset Sourcing (Week 1 - Vacation) [COMPLETED]
- Explored computer vision feasibility for dietary analysis.
- Pivoted from noisy OCR label extraction to robust visual food classification.
- Analyzed benchmark datasets (Food-101 vs Kaggle Food Image datasets).
- Designed the modular 4-tier pipeline: Input Image -> CNN/Transfer Learning -> Food Classification -> Nutrition Mapping -> Recommendation Engine.

### Phase 2: Core ML Baseline & Midsem Milestone (Week 2 - Oct 03 to Oct 11) [CURRENT]
- Setup repository structure and nutrition database schema (`nutrition_db.csv`).
- Designed data augmentation pipeline (rotation, zoom, flips, normalization).
- Implemented MobileNetV2 transfer learning baseline on representative food categories.
- Evaluated training/validation convergence and monitored overfitting prevention techniques.
- **Midsem Deliverable:** Baseline model checkpoint, pipeline demonstration, and project timeline review.

### Phase 3: Model Scaling & Health Logic Engine (Week 3 - Oct 12 to Oct 18) [PLANNED]
- Scale training dataset to the full 101 food categories.
- Fine-tune top layers with reduced learning rate ($10^{-5}$).
- Generate detailed classification reports: Precision, Recall, Macro F1, and multi-class confusion matrix.
- Expand rule-based nutrition advice engine based on dietary guideline benchmarks.

### Phase 4: Full-Stack & Interactive UI Development (Week 4 - Oct 19 to Oct 25) [PLANNED]
- Develop lightweight REST API endpoints (`/predict`, `/nutrition`) using FastAPI / Flask.
- Build interactive frontend with drag-and-drop image upload and preview cards.
- Implement animated macronutrient sliders (Calories, Protein, Carbs, Fats) and visual health cards.

### Phase 5 & 6: System Integration, Deployment & Defense (Week 5 & 6 - Oct 26 to Nov 08) [PLANNED]
- Integrate frontend client with model inference backend.
- Optimize inference latency (<500ms) and implement confidence thresholding for unknown images.
- Cloud deployment (Streamlit / Render / Hugging Face Spaces).
- Comprehensive project documentation, final viva presentation, and end-sem defense.
