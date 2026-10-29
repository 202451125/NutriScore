import os
os.environ['MPLCONFIGDIR'] = os.path.join(os.getcwd(), '.matplotlib_cache')
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np

os.makedirs('docs', exist_ok=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1: BIRD'S EYE MACRO PIPELINE (High-Level End-to-End Conceptual Workflow)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_figure_1():
    fig = plt.figure(figsize=(19, 10.5), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 190)
    ax.set_ylim(0, 105)
    ax.axis('off')

    # Color Palette - Professional IEEE Journal Aesthetic
    c_bg = "#F8FAFC"
    c_card = "#FFFFFF"
    c_border = "#94A3B8"
    c_blue = "#1E40AF"      # Deep Navy
    c_teal = "#0F766E"      # Deep Teal
    c_coral = "#BE123C"     # Deep Crimson
    c_amber = "#B45309"     # Deep Amber
    c_purple = "#6D28D9"    # Deep Violet
    c_green = "#15803D"     # Forest Green
    c_text_dark = "#0F172A"
    c_text_muted = "#475569"

    fig.patch.set_facecolor(c_bg)

    # Main Title Header
    ax.text(95, 101.5, "NUTRISCORE AI: END-TO-END MULTIMODAL DIETARY RECOGNITION & CLINICAL ASSESSMENT", 
            ha='center', va='center', fontsize=15, fontweight='bold', color=c_blue, family='sans-serif')
    ax.text(95, 98.8, "Macro-Pipeline: From Unconstrained Dining Environment to Ingredient Decompilation and FSAm-NPS Grade Derivation", 
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color=c_text_muted, family='sans-serif')

    def draw_box(x, y, w, h, title, subtitle, color, alpha=0.95):
        p_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6,rounding_size=1.2",
                               fc=c_card, ec=color, lw=1.8, zorder=2)
        ax.add_patch(p_box)
        p_hdr = FancyBboxPatch((x, y + h - 5.5), w, 5.5, boxstyle="round,pad=0.2,rounding_size=1.0",
                               fc=color, ec=color, lw=1.0, zorder=3)
        ax.add_patch(p_hdr)
        ax.text(x + w/2, y + h - 2.8, title, ha='center', va='center', 
                color='#FFFFFF', fontsize=9.5, fontweight='bold', zorder=4)
        if subtitle:
            ax.text(x + w/2, y + h - 8.2, subtitle, ha='center', va='center', 
                    color=color, fontsize=8.0, fontweight='bold', zorder=4)

    def draw_arrow(x1, y1, x2, y2, color="#475569", text=""):
        arrow = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", 
                                mutation_scale=16, lw=1.8, color=color, zorder=5)
        ax.add_patch(arrow)
        if text:
            ax.text((x1+x2)/2, (y1+y2)/2 + 1.8, text, ha='center', va='bottom', 
                    fontsize=7.5, fontweight='bold', color=color, zorder=6)

    # ---------------- STAGE 1: PHYSICAL INGESTION ----------------
    draw_box(4, 52, 32, 42, "STAGE 1: IMAGE INGESTION", "Real-World Capture", c_blue)
    ax.text(20, 80, "RGB Food Capture", ha='center', fontsize=9, fontweight='bold', color=c_text_dark)
    ax.text(20, 76.5, "Smartphones, Nutrition5k, Dining", ha='center', fontsize=7.5, color=c_text_muted)
    
    # Draw miniature plate
    circle_outer = Circle((20, 67), 6.5, fc="#E2E8F0", ec="#CBD5E1", lw=1.5, zorder=4)
    circle_food1 = Circle((18, 68), 3.2, fc="#F59E0B", ec="#D97706", lw=1, zorder=5) # Rice
    circle_food2 = Circle((22, 65.5), 2.8, fc="#EF4444", ec="#B91C1C", lw=1, zorder=5) # Curry
    circle_food3 = Circle((20, 69.5), 1.8, fc="#10B981", ec="#047857", lw=1, zorder=5) # Veg
    ax.add_patch(circle_outer)
    ax.add_patch(circle_food1)
    ax.add_patch(circle_food2)
    ax.add_patch(circle_food3)
    ax.text(20, 56.5, "Input: X in R^{224 x 224 x 3}\nResolution & Color Normalized", ha='center', fontsize=7.5, color=c_blue, fontweight='bold')

    draw_arrow(37, 73, 44, 73, c_blue, "Tensor Ingestion")

    # ---------------- STAGE 2: VISUAL VECTORIZATION ----------------
    draw_box(45, 52, 33, 42, "STAGE 2: VECTORIZATION", "Multi-Scale Tokenization", c_purple)
    ax.text(61.5, 80, "Spatial Feature Extraction", ha='center', fontsize=9, fontweight='bold', color=c_text_dark)
    
    # Diagram of Patches & Feature Maps
    for i in range(3):
        for j in range(3):
            p = patches.Rectangle((53 + i*5.5, 63 + j*4.2), 4.8, 3.6, fc="#EDE9FE", ec="#8B5CF6", lw=1, zorder=4)
            ax.add_patch(p)
            ax.text(53 + i*5.5 + 2.4, 63 + j*4.2 + 1.8, f"P_{j*3+i+1}", ha='center', va='center', fontsize=6.5, color=c_purple)

    ax.text(61.5, 57, "Vision Patch Embedding:\nZ_v = [P_1, P_2, ..., P_N] + E_pos\nFeature Maps: 112x112 -> 56x56", ha='center', fontsize=7.5, color=c_purple, fontweight='bold')

    # Fork Arrow to Stage 3
    draw_arrow(79, 78, 87, 85, c_teal, "Edge Triage")
    draw_arrow(79, 68, 87, 60, c_coral, "LMM Decompilation")

    # ---------------- STAGE 3A: EDGE MOBILENETV2 ----------------
    draw_box(88, 70, 42, 24, "ENGINE 1: LOCAL EDGE CNN", "MobileNetV2 (101 Classes)", c_teal)
    ax.text(109, 83.5, "Inverted Residuals + Linear Bottlenecks", ha='center', fontsize=8, color=c_text_dark)
    ax.text(109, 79.5, "Inference: 14 ms | Offline Capable\nTop-1 Acc: 82.1% | Top-5 Acc: 94.8%", ha='center', fontsize=7.5, color=c_teal, fontweight='bold')
    ax.text(109, 73.5, "Coarse Output: 'Chicken Biryani' (0.96)", ha='center', fontsize=7.5, color=c_text_muted)

    # ---------------- STAGE 3B: MULTIMODAL DECOMPILER ----------------
    draw_box(88, 38, 42, 28, "ENGINE 2: MULTIMODAL LMM", "Gemini 3.5 Flash Vision", c_coral)
    ax.text(109, 57.5, "Cross-Attention Ingredient Parser", ha='center', fontsize=8, color=c_text_dark)
    ax.text(109, 53.5, "Attention(Q, K, V) over Visual Tokens\nZero-Shot Semantic Decompilation", ha='center', fontsize=7.5, color=c_coral, fontweight='bold')
    ax.text(109, 47, "Deconstructed Entities Isolated:\n- Basmati Rice: 180g (rho=1.3 g/cm^3)\n- Chicken Meat: 120g | Ghee: 15g", ha='center', fontsize=7.2, color=c_text_muted)

    # Convergence Arrows to Stage 4
    draw_arrow(131, 82, 137, 72, c_teal)
    draw_arrow(131, 52, 137, 62, c_coral)

    # ---------------- STAGE 4: CLINICAL DATABASE FUSION ----------------
    draw_box(138, 45, 48, 49, "STAGE 4: CLINICAL FUSION", "Laboratory Assay Database", c_amber)
    ax.text(162, 83, "ICMR-NIN IFCT 2017 + USDA FDC", ha='center', fontsize=9, fontweight='bold', color=c_text_dark)
    
    # SQLite Table visual
    table_x, table_y = 141, 57
    ax.plot([table_x, table_x + 42], [table_y + 19, table_y + 19], color=c_amber, lw=1.2, zorder=4)
    ax.plot([table_x, table_x + 42], [table_y + 15, table_y + 15], color=c_amber, lw=1.0, zorder=4)
    headers = ["Ingredient", "Grams", "Kcal", "Protein", "Fat"]
    hx = [142, 151, 158, 166, 175]
    for h_name, h_pos in zip(headers, hx):
        ax.text(h_pos, table_y + 16.5, h_name, fontsize=6.8, fontweight='bold', color=c_text_dark, zorder=4)
    
    rows = [
        ["Basmati Rice", "180g", "234", "4.9g", "0.5g"],
        ["Chicken Thigh", "120g", "250", "31.2g", "13.1g"],
        ["Fried Onion", "25g", "60", "0.6g", "4.0g"],
        ["Desi Ghee", "15g", "135", "0.0g", "14.9g"]
    ]
    for r_idx, r in enumerate(rows):
        ry = table_y + 11.5 - r_idx*3.2
        for val, x_pos in zip(r, hx):
            ax.text(x_pos, ry, val, fontsize=6.5, color=c_text_muted, zorder=4)

    ax.text(162, 48.5, "Indexed SQLite Engine | 528 Analytical Entries\nZero Nutritional Hallucination Guarantee", ha='center', fontsize=7.2, color=c_amber, fontweight='bold')

    # Arrow to Lower Pipeline (HITL)
    draw_arrow(162, 44, 162, 38, c_amber, "Raw Matrix")

    # ---------------- STAGE 5: HUMAN-IN-THE-LOOP CUSTOMIZER ----------------
    draw_box(92, 5, 94, 31, "STAGE 5: HUMAN-IN-THE-LOOP (HITL) CULINARY CUSTOMIZER", "Live Formulation Rebalancing", c_green)
    
    # HITL Interactive Controls (Cooking Fat, Prep Style, Toggles)
    ax.text(108, 26, "Cooking Fat Modulation", fontsize=8, fontweight='bold', color=c_green)
    ax.text(108, 22.5, "V_fat in [0.0, 4.0] tbsp\nDesi Ghee / Olive / Air-Fried\nDelta E = V_fat * rho_fat * eps", fontsize=7.0, color=c_text_dark)

    ax.text(142, 26, "Preparation Multiplier (alpha)", fontsize=8, fontweight='bold', color=c_green)
    ax.text(142, 22.5, "Homestyle: alpha = 1.00\nRestaurant: alpha = 1.25 (+25%)\nDiet Lean: alpha = 0.80 (-20%)", fontsize=7.0, color=c_text_dark)

    ax.text(172, 26, "Active Ingredient Mask", fontsize=8, fontweight='bold', color=c_green)
    ax.text(172, 22.5, "u in {0, 1}^K (Live Checkbox)\nSkip Fried Onions -> -60 kcal\nSub-50 ms Live Recalculation", fontsize=7.0, color=c_text_dark)

    ax.text(139, 9, "Energy Equation: E_total = alpha_prep * [ Sum( (m_i / 100) * E_i ) ] + V_fat * rho_fat * eps_lipid", 
            ha='center', fontsize=8.2, fontweight='bold', color=c_green)

    # Arrow from Stage 5 to Stage 6
    draw_arrow(91, 20, 83, 20, c_green, "Final Nutrients")

    # ---------------- STAGE 6: EUROPEAN NUTRI-SCORE ENGINE ----------------
    draw_box(4, 5, 78, 31, "STAGE 6: EUROPEAN NUTRI-SCORE PROFILING", "FSAm-NPS Standardized Classification", c_blue)
    
    # NutriScore Pills
    grades = [("A", "#038141"), ("B", "#85BB2F"), ("C", "#FECB02"), ("D", "#EE8100"), ("E", "#E63E11")]
    for g_idx, (g_char, g_color) in enumerate(grades):
        px = 10 + g_idx * 9.5
        is_active = (g_char == "C")
        pw = 8.5
        ph = 11 if is_active else 9
        py = 17 if is_active else 18
        p_pill = FancyBboxPatch((px, py), pw, ph, boxstyle="round,pad=0.2,rounding_size=1.5",
                                fc=g_color, ec='#0F172A' if is_active else 'none', lw=2.0 if is_active else 0, zorder=5)
        ax.add_patch(p_pill)
        ax.text(px + pw/2, py + ph/2, g_char, ha='center', va='center', 
                color='#FFFFFF', fontsize=12 if is_active else 10, fontweight='bold', zorder=6)
        if is_active:
            ax.text(px + pw/2, py + ph + 2.2, "ACTIVE", ha='center', fontsize=7, fontweight='bold', color="#0F172A")

    ax.text(61, 23, "FSAm-NPS = Negative (0-40) - Positive (0-15)", fontsize=7.5, fontweight='bold', color=c_blue)
    ax.text(61, 19, "Negative: Energy, Sat Fat, Sugar, Sodium\nPositive: Dietary Fiber, Protein, FVLN %", fontsize=7.0, color=c_text_muted)
    ax.text(43, 9.5, "Clinical Decision: Chicken Biryani Assigned Grade C (Score: 6) -> High Protein Balanced Energy", 
            ha='center', fontsize=7.5, color=c_text_dark, fontweight='bold')

    plt.tight_layout()
    plt.savefig('docs/fig1_macro_pipeline.png', dpi=300, facecolor=c_bg, edgecolor='none')
    plt.close()
    print("Figure 1 generated successfully at docs/fig1_macro_pipeline.png")

# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2: PINPOINT MICRO-ARCHITECTURE & MATHEMATICAL TENSOR PIPELINE
# ═══════════════════════════════════════════════════════════════════════════════
def generate_figure_2():
    fig = plt.figure(figsize=(19, 11), dpi=300)
    ax = fig.add_subplot(111)
    ax.set_xlim(0, 190)
    ax.set_ylim(0, 110)
    ax.axis('off')

    c_bg = "#FFFFFF"
    c_card = "#F8FAFC"
    c_blue = "#1D4ED8"
    c_cyan = "#0E7490"
    c_purple = "#7E22CE"
    c_emerald = "#047857"
    c_rose = "#BE123C"
    c_text_dark = "#0F172A"
    c_text_muted = "#475569"

    fig.patch.set_facecolor(c_bg)

    # Title
    ax.text(95, 106.5, "PINPOINT NEURAL MICRO-ARCHITECTURE & TENSOR DATAFLOW", 
            ha='center', va='center', fontsize=15, fontweight='bold', color=c_blue)
    ax.text(95, 103.5, "Layer-by-Layer Inverted Residual Bottlenecks, Cross-Attention Decompiler, and Exact Matrix Formulation", 
            ha='center', va='center', fontsize=10.5, fontstyle='italic', color=c_text_muted)

    def draw_node(x, y, w, h, header, body, color):
        p = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=0.8",
                           fc=c_card, ec=color, lw=1.6, zorder=2)
        ax.add_patch(p)
        hdr = FancyBboxPatch((x, y + h - 4.5), w, 4.5, boxstyle="round,pad=0.1,rounding_size=0.6",
                             fc=color, ec=color, lw=1, zorder=3)
        ax.add_patch(hdr)
        ax.text(x + w/2, y + h - 2.3, header, ha='center', va='center', color='#FFFFFF', fontsize=8.5, fontweight='bold', zorder=4)
        ax.text(x + w/2, y + (h - 4.5)/2, body, ha='center', va='center', color=c_text_dark, fontsize=7.2, zorder=4)

    def draw_tensor(x, y, w, h, name, shape, color):
        p = FancyBboxPatch((x, y), w, h, boxstyle="square,pad=0.2",
                           fc="#EEF2F6", ec=color, lw=1.2, ls="--", zorder=2)
        ax.add_patch(p)
        ax.text(x + w/2, y + h*0.65, name, ha='center', va='center', color=color, fontsize=7.5, fontweight='bold', zorder=3)
        ax.text(x + w/2, y + h*0.3, shape, ha='center', va='center', color=c_text_muted, fontsize=6.8, zorder=3)

    def arrow(x1, y1, x2, y2, color="#475569"):
        a = FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=14, lw=1.5, color=color, zorder=5)
        ax.add_patch(a)

    # ---------------- SECTION 1: MOBILENETV2 EDGE MICRO-ARCHITECTURE (Top Row) ----------------
    ax.text(6, 98, "MODULE A: MOBILENETV2 EDGE INVERTED RESIDUAL PIPELINE", fontsize=11, fontweight='bold', color=c_blue)
    
    # Input Tensor
    draw_tensor(5, 78, 18, 16, "Input Tensor X_0", "224 x 224 x 3", c_blue)
    arrow(24, 86, 29, 86, c_blue)

    # Stem Conv
    draw_node(30, 76, 22, 20, "Stem Conv2D", "Conv 3x3, Stride 2\nBatchNorm + ReLU6\nOut: 112 x 112 x 32", c_blue)
    arrow(53, 86, 58, 86, c_blue)

    # Inverted Residual Block Detail
    p_irb = FancyBboxPatch((59, 72), 65, 27, boxstyle="round,pad=0.8,rounding_size=1.2",
                           fc="#F0F9FF", ec=c_cyan, lw=1.5, ls="-.", zorder=1)
    ax.add_patch(p_irb)
    ax.text(91.5, 96, "Inverted Residual Block (IRB) with Linear Bottleneck", ha='center', fontsize=8.5, fontweight='bold', color=c_cyan)

    draw_node(62, 75, 17, 18, "1x1 Expansion", "Pointwise Conv\nFactor t=6\n112x112x192", c_cyan)
    arrow(80, 84, 84, 84, c_cyan)
    draw_node(85, 75, 17, 18, "3x3 Depthwise", "Depthwise Conv\nStride s=1 or 2\n56x56x192", c_cyan)
    arrow(103, 84, 107, 84, c_cyan)
    draw_node(108, 75, 14, 18, "1x1 Linear", "Pointwise Bottleneck\nNo Non-Linearity\n56x56x64", c_cyan)

    # Skip Connection
    ax.annotate("", xy=(115, 74), xytext=(68, 74),
                arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-0.4", lw=1.5, color=c_cyan, ls=":"))
    ax.text(91.5, 68.5, "Residual Add (X_in + F(X_in)) when s=1, c_in=c_out", ha='center', fontsize=7.2, color=c_cyan)

    arrow(125, 86, 131, 86, c_blue)

    # GAP & Softmax Head
    draw_node(132, 76, 24, 20, "Global Avg Pool", "Pool 7x7 -> 1x1x1280\nDropout (p=0.2)\nDense FC(1280 -> 101)", c_blue)
    arrow(157, 86, 163, 86, c_blue)

    # Class Output
    draw_tensor(164, 78, 22, 16, "Softmax Prob y_hat", "101 Categorical Classes\nTop-1 Match: 0.96", c_blue)

    # ---------------- SECTION 2: MULTIMODAL CROSS-ATTENTION DECOMPILER (Middle Row) ----------------
    ax.text(6, 62, "MODULE B: MULTIMODAL LMM ZERO-SHOT INGREDIENT DECOMPILER", fontsize=11, fontweight='bold', color=c_purple)

    draw_node(5, 42, 28, 17, "Vision Tokenizer", "Image -> Patches 16x16\nZ_v in R^{196 x 768}\nLinear Projection", c_purple)
    arrow(34, 50.5, 40, 50.5, c_purple)

    # Cross Attention Block
    p_attn = FancyBboxPatch((41, 38), 64, 23, boxstyle="round,pad=0.6,rounding_size=1.0",
                            fc="#FAF5FF", ec=c_purple, lw=1.5, ls="-.", zorder=1)
    ax.add_patch(p_attn)
    ax.text(73, 58.5, "Cross-Attention Multimodal Core (Gemini 3.5 Flash)", ha='center', fontsize=8.5, fontweight='bold', color=c_purple)

    draw_node(44, 41, 16, 15, "Queries (Q)", "W_q * E_prompt\nTask Semantics", c_purple)
    draw_node(64, 41, 16, 15, "Keys (K)", "W_k * Z_v\nVisual Features", c_purple)
    draw_node(84, 41, 16, 15, "Values (V)", "W_v * Z_v\nSpatial Context", c_purple)

    arrow(106, 50.5, 114, 50.5, c_purple)

    # Autoregressive Output
    draw_node(115, 39, 36, 21, "Ingredient Generator", "Softmax(Q K^T / sqrt(d_k)) * V\nStructured Output JSON:\n{ name: str, mass_g: float, rho: float }", c_purple)
    arrow(152, 50.5, 160, 50.5, c_purple)

    draw_tensor(161, 41, 25, 17, "Component Matrix W", "K x 3 (Constituents)\nMass & Density Vector", c_purple)

    # ---------------- SECTION 3: MATHEMATICAL CLINICAL MATRIX & FSAm-NPS (Bottom Row) ----------------
    ax.text(6, 32, "MODULE C: CLINICAL KNOWLEDGE MATRIX & DYNAMIC ENERGY REBALANCING", fontsize=11, fontweight='bold', color=c_emerald)

    # Matrix Equation Visual
    draw_node(5, 5, 40, 24, "Clinical Database Matrix C", 
              "Relational Table C in R^{K x 5}:\nC = [ Cal_100g,  Prot_100g,\n      Carb_100g, Fat_100g,\n      Sod_100g ]\nSource: ICMR-NIN IFCT 2017", c_emerald)
    
    ax.text(49, 17, "+", fontsize=18, fontweight='bold', color=c_emerald)

    draw_node(53, 5, 40, 24, "User HITL Modulation Vector", 
              "Active Mask: u in {0, 1}^K\nPortion Scale: S_p in [0.5, 3.0]\nEffective Mass:\nm_eff = S_p * (u (dot) m_est)\nFat Volume: V_fat in [0, 4] tbsp", c_emerald)

    ax.text(97, 17, "===>", fontsize=16, fontweight='bold', color=c_emerald)

    draw_node(104, 5, 42, 24, "Dynamic Nutrient Vector N_final", 
              "N_final = alpha_prep * ( (1/100) * m_eff^T * C )\n         + V_fat * rho_fat * [ eps, 0, 0, 14, 0 ]\n\nalpha: Homestyle=1.0 | Restaurant=1.25", c_emerald)

    arrow(147, 17, 154, 17, c_rose)

    draw_node(155, 5, 31, 24, "FSAm-NPS Decision Engine", 
              "Score = Sum(N_pts) - Sum(P_pts)\n\nScore <= -1  -> Grade A\n 0 to 2     -> Grade B\n 3 to 10    -> Grade C\n11 to 18    -> Grade D\nScore >= 19 -> Grade E", c_rose)

    plt.tight_layout()
    plt.savefig('docs/fig2_micro_architecture.png', dpi=300, facecolor=c_bg, edgecolor='none')
    plt.close()
    print("Figure 2 generated successfully at docs/fig2_micro_architecture.png")

if __name__ == '__main__':
    generate_figure_1()
    generate_figure_2()
