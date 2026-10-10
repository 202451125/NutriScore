# NutriScore: AI-Based Food Recognition & Nutritional Analysis System

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TensorFlow 2.15+](https://img.shields.io/badge/TensorFlow-2.15%2B-orange.svg)](https://tensorflow.org/)
[![Deep Learning](https://img.shields.io/badge/Architecture-MobileNetV2%20%7C%20Transfer%20Learning-green.svg)]()
[![Status](https://img.shields.io/badge/Project%20Status-Midsem%20Milestone-brightgreen.svg)]()

> An end-to-end Computer Vision and Deep Learning system designed to classify consumer food images in real-time, instantly map them to estimated nutritional profiles (Calories, Protein, Carbohydrates, Fats), and generate rule-based dietary recommendations.

---

## 📌 Problem Statement

Diet tracking and mindful nutrition are essential for long-term health, yet existing mobile solutions require tedious manual keyword searches or barcode scanning—both of which fail for home-cooked meals, restaurant plates, or unpackaged foods. 

**NutriScore** addresses this bottleneck by replacing manual logging with computer vision:
1. **User uploads an image** of a meal.
2. **Deep Learning classifier** identifies the food category with high confidence.
3. **Automated Nutrition Engine** looks up macronutrients (Calories, Protein, Carbs, Fat, Fiber).
4. **Health Advisory Module** outputs dietary guidance (portion alerts, glycemic impact, healthier alternatives).

---

## 🏗️ System Architecture & Pipeline

```text
  [ Food Image ]
        │
        ▼
  [ Image Preprocessing & Data Augmentation ]
  (Resize to 224x224, Random Flip, Zoom, Contrast, Normalization)
        │
        ▼
  [ Transfer Learning Backbone: MobileNetV2 ]
  (Pre-trained ImageNet Feature Extractor + GlobalAveragePooling2D)
        │
        ▼
  [ Dense Classifier Head & Softmax ]
  (Dropout Regularization + Multi-Class Probabilities)
        │
        ▼
  [ Predicted Class & Confidence Score ]
        │
        ▼
  [ Nutrition Database Lookup Engine ]
  (Matches class to Calories, Protein, Carbs, Fats, Fiber)
        │
        ▼
  [ NutriScore Health & Dietary Advisory Engine ]
        │
        ▼
  [ User Interface / Full-Stack Dashboard ]
```

---

## 📊 Dataset Strategy

The project utilizes the **Food-101 Benchmark Dataset**:
- **Total Images:** 101,000 real-world food photographs.
- **Classes:** 101 fine-grained culinary categories (750 training images + 250 validation images per category).
- **Phased Implementation:**
  - **Phase 1 (Midsem Milestone):** Model training, metric verification, and hyperparameter tuning on representative core categories (`pizza`, `hamburger`, `french_fries`, `sushi`, `ice_cream`, `spaghetti_bolognese`, `fried_rice`, `caesar_salad`, `steak`, `hot_dog`, `pancakes`, `donuts`, `ramen`, `samosa`, `biryani`).
  - **Phase 2 (Post-Midsem Scaling):** Full 101-category weights scaling and fine-tuning with low learning rate ($10^{-5}$).

---

## 🔬 Machine Learning Methodology

- **Backbone Architecture:** MobileNetV2 (chosen for optimal accuracy-to-latency trade-off and lightweight deployment).
- **Overfitting Countermeasures:**
  - Data Augmentation layers integrated directly into the model graph.
  - Dropout layer ($p = 0.3$) before final projection.
  - `EarlyStopping` callback monitoring `val_loss` with patience of 3 epochs.
  - `ModelCheckpoint` to persist only the optimal validation weight state.
- **Evaluation Metrics:**
  - Categorical Accuracy & Cross-Entropy Loss
  - Precision, Recall, and Macro F1-Score
  - Multi-class Confusion Matrix

---

## 🗂️ Project Directory Structure

```text
NutriScore/
│
├── README.md               # Comprehensive project documentation & architecture
├── requirements.txt        # Python package dependencies
├── .gitignore              # Standard git rules for ML models & large files
│
├── data/
│   └── nutrition_db.csv    # Macronutrient and dietary recommendation dataset
│
├── notebooks/
│   └── NutriScore_Model_Training.ipynb  # End-to-end Google Colab training notebook
│
├── src/
│   ├── __init__.py
│   ├── nutrition.py        # Nutrition database lookup & recommendation logic
│   └── predict.py          # Standalone inference & prediction script
│
└── docs/
    └── timeline_roadmap.md # Detailed project timeline & milestone schedule
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/NutriScore.git
cd NutriScore
```

### 2. Set Up Virtual Environment & Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Model Training
Open `notebooks/NutriScore_Model_Training.ipynb` in **Google Colab** (recommended: GPU runtime `T4`) and execute the sequential cells to train and evaluate the model.

---

## 👥 Team & Responsibilities

- **Lead ML / AI Engineer:** Model architecture design, data preprocessing & augmentation pipeline, transfer learning model training, hyperparameter optimization, and evaluation metrics.
- **Full-Stack & UI/UX Engineer:** REST API endpoints, interactive web dashboard, animated macronutrient sliders, and end-to-end integration.

---

## 📄 License
This project is developed for academic evaluation under the MIT License.
