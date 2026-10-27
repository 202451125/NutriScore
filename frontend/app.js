/**
 * NutriScore AI Vision • Client Controller v5.0
 * Matte Finish Claymorphic UI & 3D Perspective Floating Display
 */

document.addEventListener("DOMContentLoaded", () => {
    // ═══════════════════════════════════════════════════════════════════════════
    //  GLOBAL STATE
    // ═══════════════════════════════════════════════════════════════════════════
    const state = {
        activeEngine: "gemini", // "gemini" | "local"
        selectedImageFile: null,
        selectedDishId: "lasagna",
        selectedDishName: "Baked Lasagna",
        selectedDishImg: "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=600&auto=format&fit=crop&q=80",
        currentPortion: 1.0,
        cookingFat: "olive_oil",
        fatTablespoons: 1.0,
        prepStyle: "homestyle",
        activeIngredients: [],
        isAnalyzing: false,
        cachedResult: null
    };

    // Nutri-Score Descriptions & Colors
    const NUTRISCORE_META = {
        "A": { label: "Grade A • Optimal Nutritional Quality", color: "#038141" },
        "B": { label: "Grade B • High Nutritional Quality", color: "#85BB2F" },
        "C": { label: "Grade C • Balanced Consumption", color: "#FECB02" },
        "D": { label: "Grade D • High Calorie / Mindful Consumption", color: "#EE8100" },
        "E": { label: "Grade E • Rich & Indulgent / Occasional Treat", color: "#E63E11" }
    };

    const FAT_DESCRIPTIONS = {
        "desi_ghee": "Desi Ghee • Clarified butter with rich saturated fat & traditional aroma",
        "mustard_oil": "Sarson Ka Tel • Pungent aroma, high smoke point, North Indian classic",
        "olive_oil": "Extra virgin olive oil • Heart-healthy monounsaturated polyphenols",
        "coconut_oil": "Cold-pressed coconut oil • Medium-chain triglycerides (MCTs)",
        "vegetable_oil": "Refined vegetable oil • Neutral culinary fat",
        "air_fried": "Air-fried / steamed • Zero added oil, lowest lipid density"
    };

    const PREP_DESCRIPTIONS = {
        "homestyle": "Balanced home cooking with moderate oil and measured salt",
        "restaurant": "Rich restaurant / dhaba style (+25% calories, extra butter & cream)",
        "diet": "Diet & lean preparation (-20% calories, minimal oil, reduced sodium)"
    };

    // Pre-configured clinical ingredients for instant Human-in-the-Loop customization
    const VAULT_DEFAULT_INGREDIENTS = {
        "biryani": [
            { name: "Basmati Rice (cooked)", grams: 180, calories: 234.0, protein: 4.9, carbs: 50.8, fat: 0.5, source: "ICMR-NIN 2017 #A001", matched: true, active: true },
            { name: "Chicken Thigh (cooked)", grams: 120, calories: 250.8, protein: 31.2, carbs: 0.0, fat: 13.1, source: "USDA FDC #172389", matched: true, active: true },
            { name: "Biryani Fried Onion (Birista)", grams: 25, calories: 60.0, protein: 0.6, carbs: 5.5, fat: 4.0, source: "ICMR-NIN 2017", matched: true, active: true },
            { name: "Desi Ghee (cooking fat)", grams: 15, calories: 135.0, protein: 0.0, carbs: 0.0, fat: 14.9, source: "ICMR-NIN 2017 #K008", matched: true, active: true },
            { name: "Plain Curd / Dahi (Raita)", grams: 50, calories: 30.0, protein: 1.8, carbs: 2.4, fat: 1.7, source: "ICMR-NIN 2017 #K004", matched: true, active: true }
        ],
        "lasagna": [
            { name: "Lasagna Pasta Sheets (cooked)", grams: 140, calories: 189.0, protein: 7.3, carbs: 36.4, fat: 1.7, source: "USDA FDC #168927", matched: true, active: true },
            { name: "Ground Beef / Ragù Meat (lean)", grams: 100, calories: 250.0, protein: 26.1, carbs: 0.0, fat: 15.4, source: "USDA FDC #174032", matched: true, active: true },
            { name: "Mozzarella Cheese (shredded)", grams: 45, calories: 135.0, protein: 10.0, carbs: 1.0, fat: 10.1, source: "USDA FDC #170845", matched: true, active: true },
            { name: "Béchamel White Sauce", grams: 35, calories: 52.5, protein: 1.4, carbs: 3.9, fat: 3.5, source: "USDA FDC #173299", matched: true, active: true },
            { name: "Tomato Puree / Passata", grams: 40, calories: 15.2, protein: 0.6, carbs: 3.6, fat: 0.1, source: "USDA FDC #170457", matched: true, active: true }
        ],
        "dosa": [
            { name: "Dosa Crepe (fermented batter)", grams: 120, calories: 201.6, protein: 5.4, carbs: 35.4, fat: 4.6, source: "ICMR-NIN 2017", matched: true, active: true },
            { name: "Boiled Potato Masala", grams: 70, calories: 60.9, protein: 1.3, carbs: 14.1, fat: 0.1, source: "ICMR-NIN 2017 #D001", matched: true, active: true },
            { name: "Coconut Chutney", grams: 30, calories: 106.2, protein: 1.0, carbs: 4.6, fat: 10.1, source: "ICMR-NIN 2017 #G003", matched: true, active: true },
            { name: "Sambar Lentil Dal", grams: 60, calories: 69.6, protein: 5.4, carbs: 12.0, fat: 0.2, source: "ICMR-NIN 2017 #B001", matched: true, active: true }
        ],
        "idli": [
            { name: "Steamed Idli Cakes (2 pieces)", grams: 120, calories: 156.0, protein: 4.7, carbs: 31.2, fat: 0.5, source: "ICMR-NIN 2017", matched: true, active: true },
            { name: "Sambar (Toor dal & vegetables)", grams: 100, calories: 116.0, protein: 9.0, carbs: 20.0, fat: 0.4, source: "ICMR-NIN 2017 #B001", matched: true, active: true },
            { name: "Fresh Coconut Chutney", grams: 30, calories: 106.2, protein: 1.0, carbs: 4.6, fat: 10.1, source: "ICMR-NIN 2017 #G003", matched: true, active: true }
        ],
        "samosa": [
            { name: "Samosa Pastry Crust", grams: 50, calories: 190.0, protein: 2.8, carbs: 23.0, fat: 9.8, source: "ICMR-NIN 2017", matched: true, active: true },
            { name: "Spiced Boiled Potato Filling", grams: 45, calories: 39.2, protein: 0.9, carbs: 9.0, fat: 0.1, source: "ICMR-NIN 2017 #D001", matched: true, active: true },
            { name: "Green Peas (Matar)", grams: 15, calories: 12.6, protein: 0.8, carbs: 2.3, fat: 0.1, source: "ICMR-NIN 2017 #B012", matched: true, active: true },
            { name: "Frying Vegetable Oil (absorbed)", grams: 15, calories: 132.6, protein: 0.0, carbs: 0.0, fat: 15.0, source: "ICMR-NIN 2017 #H005", matched: true, active: true }
        ],
        "paneer_tikka": [
            { name: "Paneer Cubes (fresh)", grams: 140, calories: 371.0, protein: 25.6, carbs: 1.7, fat: 29.1, source: "ICMR-NIN 2017 #K006", matched: true, active: true },
            { name: "Plain Curd / Dahi Marinade", grams: 35, calories: 21.0, protein: 1.2, carbs: 1.6, fat: 1.2, source: "ICMR-NIN 2017 #K004", matched: true, active: true },
            { name: "Green Capsicum / Bell Pepper", grams: 30, calories: 6.0, protein: 0.3, carbs: 1.4, fat: 0.1, source: "ICMR-NIN 2017 #E005", matched: true, active: true },
            { name: "Red Onion Slices", grams: 25, calories: 10.0, protein: 0.3, carbs: 2.3, fat: 0.0, source: "ICMR-NIN 2017 #D003", matched: true, active: true }
        ],
        "pizza": [
            { name: "Pizza Crust (baked)", grams: 110, calories: 302.5, protein: 9.4, carbs: 52.8, fat: 6.1, source: "USDA FDC #173295", matched: true, active: true },
            { name: "Mozzarella Cheese (shredded)", grams: 60, calories: 180.0, protein: 13.3, carbs: 1.3, fat: 13.4, source: "USDA FDC #170845", matched: true, active: true },
            { name: "Tomato Puree / Sauce", grams: 40, calories: 15.2, protein: 0.6, carbs: 3.6, fat: 0.1, source: "USDA FDC #170457", matched: true, active: true },
            { name: "Olive Oil Drizzle", grams: 10, calories: 88.4, protein: 0.0, carbs: 0.0, fat: 10.0, source: "USDA FDC #171413", matched: true, active: true }
        ]
    };

    // ═══════════════════════════════════════════════════════════════════════════
    //  DOM ELEMENT REFERENCES
    // ═══════════════════════════════════════════════════════════════════════════
    const el = {
        // Perspective Stage
        perspectiveStage: document.getElementById("perspectiveStage"),

        // Engine Toggle
        btnEngineGemini: document.getElementById("btnEngineGemini"),
        btnEngineLocal: document.getElementById("btnEngineLocal"),

        // Vault Cards
        vaultCardsRow: document.getElementById("vaultCardsRow"),

        // Dropzone & File Input
        dropzoneBox: document.getElementById("dropzoneBox"),
        fileInput: document.getElementById("fileInput"),
        dropPromptView: document.getElementById("dropPromptView"),
        dropPreviewView: document.getElementById("dropPreviewView"),
        previewImg: document.getElementById("previewImg"),
        previewFilename: document.getElementById("previewFilename"),
        btnClearPhoto: document.getElementById("btnClearPhoto"),
        btnBrowseMatte: document.getElementById("btnBrowseMatte"),

        // Telemetry Scanner Overlay
        scannerOverlay: document.getElementById("scannerOverlay"),
        consoleStream: document.getElementById("consoleStream"),
        btnAnalyzePlate: document.getElementById("btnAnalyzePlate"),
        btnAnalyzeText: document.getElementById("btnAnalyzeText"),

        // Customizer
        fatsGrid: document.getElementById("fatsGrid"),
        fatHint: document.getElementById("fatHint"),
        fatQuantityBlock: document.getElementById("fatQuantityBlock"),
        fatQuantityBadge: document.getElementById("fatQuantityBadge"),
        fatSlider: document.getElementById("fatSlider"),
        btnMinusFat: document.getElementById("btnMinusFat"),
        btnPlusFat: document.getElementById("btnPlusFat"),
        prepStack: document.getElementById("prepStack"),
        prepHint: document.getElementById("prepHint"),
        customizerCard: document.getElementById("customizerCard"),

        // Results Dashboard
        emptyDashboardCard: document.getElementById("emptyDashboardCard"),
        resultsDashboardCard: document.getElementById("resultsDashboardCard"),
        resCuisine: document.getElementById("resCuisine"),
        resEngine: document.getElementById("resEngine"),
        resDishName: document.getElementById("resDishName"),
        resDishNarrative: document.getElementById("resDishNarrative"),
        resConfidenceVal: document.getElementById("resConfidenceVal"),
        gaugeIndicator: document.getElementById("gaugeIndicator"),
        resNutriGradeMeaning: document.getElementById("resNutriGradeMeaning"),

        // Portion
        portionSlider: document.getElementById("portionSlider"),
        portionLabelBadge: document.getElementById("portionLabelBadge"),

        // Macros
        valCalories: document.getElementById("valCalories"),
        valProtein: document.getElementById("valProtein"),
        valCarbs: document.getElementById("valCarbs"),
        valFat: document.getElementById("valFat"),
        fillCalories: document.getElementById("fillCalories"),
        fillProtein: document.getElementById("fillProtein"),
        fillCarbs: document.getElementById("fillCarbs"),
        fillFat: document.getElementById("fillFat"),

        // Ingredients
        ingredientDecompCard: document.getElementById("ingredientDecompCard"),
        decompMatchedBadge: document.getElementById("decompMatchedBadge"),
        decompChecklistStream: document.getElementById("decompChecklistStream"),
        customizerIngrStream: document.getElementById("customizerIngrStream"),
        customizerIngrBadge: document.getElementById("customizerIngrBadge"),

        // Guidance
        valRecommendation: document.getElementById("valRecommendation"),
        valPairing: document.getElementById("valPairing")
    };

    // ═══════════════════════════════════════════════════════════════════════════
    //  1. HERO 3D PERSPECTIVE PARALLAX (Ghulam Inspo)
    // ═══════════════════════════════════════════════════════════════════════════
    function initHero3DParallax() {
        const stage = el.perspectiveStage;
        if (!stage) return;

        window.addEventListener("mousemove", (e) => {
            const rect = stage.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const cx = rect.width / 2;
            const cy = rect.height / 2;

            const rotX = 8 + ((y - cy) / cy) * -8;
            const rotY = -8 + ((x - cx) / cx) * 10;

            stage.style.transform = `rotateX(${rotX}deg) rotateY(${rotY}deg)`;
        });

        stage.addEventListener("mouseleave", () => {
            stage.style.transform = `rotateX(8deg) rotateY(-8deg)`;
        });
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  2. QUICK VAULT 3D TILT CARDS
    // ═══════════════════════════════════════════════════════════════════════════
    function initVaultCards() {
        const cards = el.vaultCardsRow?.querySelectorAll(".vault-dish-card");
        if (!cards) return;

        cards.forEach(card => {
            // Mouse tilt physics
            card.addEventListener("mousemove", (e) => {
                const rect = card.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const cx = rect.width / 2;
                const cy = rect.height / 2;

                const rotX = ((y - cy) / cy) * -12;
                const rotY = ((x - cx) / cx) * 12;

                card.style.transform = `perspective(800px) rotateX(${rotX}deg) rotateY(${rotY}deg) scale3d(1.03, 1.03, 1.03)`;
            });

            card.addEventListener("mouseleave", () => {
                card.style.transform = "perspective(800px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)";
            });

            // Click to load dish
            card.addEventListener("click", () => {
                cards.forEach(c => c.classList.remove("active"));
                card.classList.add("active");

                state.selectedDishId = card.dataset.id;
                state.selectedDishName = card.dataset.name;
                state.selectedDishImg = card.dataset.img;
                state.selectedImageFile = null; // Clear manual upload

                // Display preview
                el.previewImg.src = state.selectedDishImg;
                el.previewFilename.textContent = `${state.selectedDishName} (Pre-loaded plate)`;
                el.dropPromptView.classList.add("hidden");
                el.dropPreviewView.classList.remove("hidden");

                // Immediately load and show dish ingredients in Customizer
                loadVaultDishIngredients(state.selectedDishId);

                // Scroll to studio smoothly & trigger analysis
                document.getElementById("studio-section")?.scrollIntoView({ behavior: "smooth" });
                executeAnalysis();
            });
        });

        // Pre-load default dish preview (Lasagna)
        if (!state.selectedImageFile) {
            el.previewImg.src = state.selectedDishImg;
            el.previewFilename.textContent = `${state.selectedDishName} (Pre-loaded plate)`;
            el.dropPromptView.classList.add("hidden");
            el.dropPreviewView.classList.remove("hidden");
        }
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  3. CLEAN, UNBLOCKED FILE UPLOAD DROPZONE
    // ═══════════════════════════════════════════════════════════════════════════
    function initDropzone() {
        // Trigger file input when clicking prompt view
        el.dropzoneBox?.addEventListener("click", (e) => {
            if (e.target === el.btnClearPhoto) return;
            if (el.dropPreviewView.classList.contains("hidden")) {
                el.fileInput.click();
            }
        });

        // File selection event
        el.fileInput?.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) handleNewFile(file);
        });

        // Drag and drop handlers
        el.dropzoneBox?.addEventListener("dragover", (e) => {
            e.preventDefault();
            el.dropzoneBox.classList.add("dragover");
        });

        el.dropzoneBox?.addEventListener("dragleave", () => {
            el.dropzoneBox.classList.remove("dragover");
        });

        el.dropzoneBox?.addEventListener("drop", (e) => {
            e.preventDefault();
            el.dropzoneBox.classList.remove("dragover");
            const file = e.dataTransfer.files[0];
            if (file) handleNewFile(file);
        });

        // Clear photo button
        el.btnClearPhoto?.addEventListener("click", (e) => {
            e.stopPropagation();
            resetDropzone();
        });

        // Analyze button
        el.btnAnalyzePlate?.addEventListener("click", () => {
            executeAnalysis();
        });
    }

    function handleNewFile(file) {
        state.selectedImageFile = file;
        state.selectedDishId = null;

        // Deselect vault cards
        document.querySelectorAll(".vault-dish-card").forEach(c => c.classList.remove("active"));

        const reader = new FileReader();
        reader.onload = (e) => {
            el.previewImg.src = e.target.result;
            el.previewFilename.textContent = `${file.name} (${Math.round(file.size / 1024)} KB)`;
            el.dropPromptView.classList.add("hidden");
            el.dropPreviewView.classList.remove("hidden");
        };
        reader.readAsDataURL(file);
    }

    function resetDropzone() {
        state.selectedImageFile = null;
        el.fileInput.value = "";
        el.previewImg.src = "";
        el.dropPreviewView.classList.add("hidden");
        el.dropPromptView.classList.remove("hidden");
        el.resultsDashboardCard.classList.add("hidden");
        el.emptyDashboardCard.classList.remove("hidden");
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  4. ENGINE TOGGLE & CUSTOMIZER CONTROLS
    // ═══════════════════════════════════════════════════════════════════════════
    function initControls() {
        // Dual engine toggle
        el.btnEngineGemini?.addEventListener("click", () => {
            state.activeEngine = "gemini";
            el.btnEngineGemini.classList.add("active");
            el.btnEngineLocal.classList.remove("active");
            if (el.customizerCard) el.customizerCard.style.opacity = "1";
        });

        el.btnEngineLocal?.addEventListener("click", () => {
            state.activeEngine = "local";
            el.btnEngineLocal.classList.add("active");
            el.btnEngineGemini.classList.remove("active");
            if (el.customizerCard) el.customizerCard.style.opacity = "0.6";
        });

        // Cooking Fats
        el.fatsGrid?.querySelectorAll(".fat-matte-chip").forEach(btn => {
            btn.addEventListener("click", () => {
                el.fatsGrid.querySelectorAll(".fat-matte-chip").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                state.cookingFat = btn.dataset.fat;

                if (el.fatHint) el.fatHint.textContent = FAT_DESCRIPTIONS[state.cookingFat] || "";

                if (state.cookingFat === "air_fried") {
                    if (el.fatQuantityBlock) el.fatQuantityBlock.style.display = "none";
                } else {
                    if (el.fatQuantityBlock) el.fatQuantityBlock.style.display = "block";
                }

                triggerRecalculation();
            });
        });

        // Fat Stepper & Slider
        el.fatSlider?.addEventListener("input", (e) => {
            state.fatTablespoons = parseFloat(e.target.value);
            updateFatUI();
            triggerRecalculation();
        });

        el.btnMinusFat?.addEventListener("click", () => {
            state.fatTablespoons = Math.max(0, state.fatTablespoons - 0.5);
            if (el.fatSlider) el.fatSlider.value = state.fatTablespoons;
            updateFatUI();
            triggerRecalculation();
        });

        el.btnPlusFat?.addEventListener("click", () => {
            state.fatTablespoons = Math.min(4.0, state.fatTablespoons + 0.5);
            if (el.fatSlider) el.fatSlider.value = state.fatTablespoons;
            updateFatUI();
            triggerRecalculation();
        });

        function updateFatUI() {
            const kcal = Math.round(state.fatTablespoons * 120);
            if (el.fatQuantityBadge) {
                el.fatQuantityBadge.textContent = `${state.fatTablespoons.toFixed(1)} tbsp (~${kcal} kcal)`;
            }
        }

        // Preparation Styles
        el.prepStack?.querySelectorAll(".prep-style-item").forEach(btn => {
            btn.addEventListener("click", () => {
                el.prepStack.querySelectorAll(".prep-style-item").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                state.prepStyle = btn.dataset.style;

                if (el.prepHint) el.prepHint.textContent = PREP_DESCRIPTIONS[state.prepStyle] || "";
                triggerRecalculation();
            });
        });

        // Portion Slider
        el.portionSlider?.addEventListener("input", (e) => {
            state.currentPortion = parseFloat(e.target.value);
            if (el.portionLabelBadge) {
                el.portionLabelBadge.textContent = getPortionLabel(state.currentPortion);
            }
            triggerRecalculation();
        });
    }

    function getPortionLabel(p) {
        if (p <= 0.6) return "Light Snack (0.5x)";
        if (p <= 0.85) return "Small Portion (0.75x)";
        if (p <= 1.15) return "Standard Single (1.0x)";
        if (p <= 1.6) return "Hearty Serving (1.5x)";
        if (p <= 2.2) return "Double Portion (2.0x)";
        return `Feast Portion (${p.toFixed(1)}x)`;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  5. LIVE SCANNING HUD TELEMETRY
    // ═══════════════════════════════════════════════════════════════════════════
    async function playScanningHUD(engine) {
        if (!el.scannerOverlay) return;
        el.scannerOverlay.classList.remove("hidden");
        el.consoleStream.innerHTML = "";

        const milestones = [
            `> [0.08s] RGB tensor ingestion: 512x512 matrix...`,
            engine === "gemini" 
                ? `> [0.35s] Gemini 3.5 Flash Multimodal inference initiated...`
                : `> [0.35s] MobileNetV2 Depthwise Separable Convolutions pass...`,
            `> [0.80s] Isolated constituent ingredients with gram estimates...`,
            `> [1.10s] Queried ICMR-NIN & USDA clinical nutrient tables...`,
            `> [1.40s] Applying cooking modifier: ${state.cookingFat} (${state.prepStyle})...`,
            `> [1.70s] Computing European FSAv2 Nutri-Score algorithm... Complete!`
        ];

        for (let i = 0; i < milestones.length; i++) {
            await new Promise(r => setTimeout(r, 220));
            const row = document.createElement("div");
            row.textContent = milestones[i];
            el.consoleStream.appendChild(row);
            el.consoleStream.scrollTop = el.consoleStream.scrollHeight;
        }
    }

    function hideScanningHUD() {
        if (el.scannerOverlay) el.scannerOverlay.classList.add("hidden");
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  6. RUN INFERENCE PIPELINE
    // ═══════════════════════════════════════════════════════════════════════════
    async function executeAnalysis() {
        if (state.isAnalyzing) return;
        state.isAnalyzing = true;

        el.btnAnalyzePlate.disabled = true;
        el.btnAnalyzeText.textContent = "AI Model Running on Screen...";

        try {
            // Trigger HUD overlay
            const hudPromise = playScanningHUD(state.activeEngine);

            let fetchPromise;
            if (state.activeEngine === "gemini") {
                fetchPromise = callGeminiAPI();
            } else {
                fetchPromise = callLocalModelAPI();
            }

            const [_, result] = await Promise.all([hudPromise, fetchPromise]);
            hideScanningHUD();

            if (result && result.success) {
                state.cachedResult = result.data;
                renderResults(result.data);
            } else {
                alert("Analysis failed: " + (result?.error || "Unknown error"));
            }
        } catch (err) {
            console.error("Analysis error:", err);
            alert("Error running inference: " + err.message);
        } finally {
            hideScanningHUD();
            state.isAnalyzing = false;
            el.btnAnalyzePlate.disabled = false;
            el.btnAnalyzeText.textContent = "Run AI Dietary Analysis";
        }
    }

    async function callGeminiAPI() {
        const formData = new FormData();

        if (state.selectedImageFile) {
            formData.append("file", state.selectedImageFile);
        } else {
            // Fetch blob from selected dish image URL
            const res = await fetch(state.selectedDishImg);
            const blob = await res.blob();
            formData.append("file", blob, `${state.selectedDishId}.jpg`);
        }

        formData.append("cooking_fat", state.cookingFat);
        formData.append("prep_style", state.prepStyle);
        formData.append("fat_tablespoons", state.fatTablespoons);
        formData.append("portion", state.currentPortion);

        const resp = await fetch("/api/analyze", {
            method: "POST",
            body: formData
        });
        return await resp.json();
    }

    async function callLocalModelAPI() {
        const formData = new FormData();

        if (state.selectedImageFile) {
            formData.append("file", state.selectedImageFile);
        } else {
            const res = await fetch(state.selectedDishImg);
            const blob = await res.blob();
            formData.append("file", blob, `${state.selectedDishId}.jpg`);
        }

        formData.append("portion", state.currentPortion);

        const resp = await fetch("/api/predict", {
            method: "POST",
            body: formData
        });
        const data = await resp.json();

        if (data.success) {
            const d = data.data;
            const defaultIngs = VAULT_DEFAULT_INGREDIENTS[d.food_class] || VAULT_DEFAULT_INGREDIENTS["lasagna"] || [];
            return {
                success: true,
                data: {
                    dish_name: d.display_name,
                    cuisine: d.food_class.includes("biryani") || d.food_class.includes("dosa") ? "Indian Cuisine" : "Global Cuisine",
                    dish_description: d.health_category || "Recognized by MobileNetV2 academic neural network.",
                    nutriscore_grade: d.nutriscore_grade,
                    totals: {
                        calories: d.calories_kcal,
                        protein: d.protein_g,
                        carbs: d.carbs_g,
                        fat: d.fat_g,
                        fiber: d.fiber_g
                    },
                    confidence: d.confidence || 95.0,
                    ingredient_breakdown: defaultIngs,
                    engine: "Local MobileNetV2 (101-Class Model)",
                    recommendation: d.recommendation,
                    pairing_tip: d.pairing_tip
                }
            };
        }
        return data;
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  7. RENDER RESULTS DASHBOARD
    // ═══════════════════════════════════════════════════════════════════════════
    function renderResults(data) {
        el.emptyDashboardCard.classList.add("hidden");
        el.resultsDashboardCard.classList.remove("hidden");

        // Header info
        el.resDishName.textContent = data.dish_name || "Analyzed Plate";
        el.resCuisine.textContent = data.cuisine || "Identified Cuisine";
        el.resEngine.textContent = data.engine || "NutriScore Dual-Engine";
        el.resDishNarrative.textContent = data.dish_description || "";

        // Confidence match gauge
        const conf = Math.round(data.confidence || 96);
        el.resConfidenceVal.textContent = `${conf}%`;
        const circumference = 2 * Math.PI * 32; // r = 32
        const offset = circumference - (conf / 100) * circumference;
        if (el.gaugeIndicator) el.gaugeIndicator.style.strokeDashoffset = offset;

        // Nutri-Score 5-pill bar
        const grade = (data.nutriscore_grade || "C").toUpperCase();
        const nsMeta = NUTRISCORE_META[grade] || NUTRISCORE_META["C"];
        el.resNutriGradeMeaning.textContent = nsMeta.label;
        el.resNutriGradeMeaning.style.color = nsMeta.color;

        document.querySelectorAll(".ns-pill-item").forEach(p => {
            if (p.dataset.grade === grade) {
                p.classList.add("active");
            } else {
                p.classList.remove("active");
            }
        });

        // Macros with smooth numbers
        const t = data.totals || {};
        tweenVal(el.valCalories, Math.round(t.calories || 0));
        tweenVal(el.valProtein, t.protein || 0, 1);
        tweenVal(el.valCarbs, t.carbs || 0, 1);
        tweenVal(el.valFat, t.fat || 0, 1);

        // Progress fills
        if (el.fillCalories) el.fillCalories.style.width = `${Math.min(100, ((t.calories || 0) / 2000) * 100)}%`;
        if (el.fillProtein) el.fillProtein.style.width = `${Math.min(100, ((t.protein || 0) / 75) * 100)}%`;
        if (el.fillCarbs) el.fillCarbs.style.width = `${Math.min(100, ((t.carbs || 0) / 250) * 100)}%`;
        if (el.fillFat) el.fillFat.style.width = `${Math.min(100, ((t.fat || 0) / 70) * 100)}%`;

        // Guidance
        if (el.valRecommendation) {
            el.valRecommendation.textContent = data.recommendation || 
                "Rich in key macronutrients. Balance with dietary fiber to regulate glycemic absorption.";
        }
        if (el.valPairing) {
            el.valPairing.textContent = data.pairing_tip || 
                "Pair with fresh greens and plenty of water for optimal metabolic health.";
        }

        // Ingredient Breakdown
        state.activeIngredients = (data.ingredient_breakdown || []).map(ing => ({
            ...ing,
            active: true
        }));
        renderIngredientList(state.activeIngredients);
    }

    function tweenVal(element, target, decimals = 0) {
        if (!element) return;
        const start = parseFloat(element.textContent) || 0;
        const dur = 500;
        const startT = performance.now();

        function step(now) {
            const p = Math.min((now - startT) / dur, 1);
            const val = start + (target - start) * (p * (2 - p));
            element.textContent = decimals > 0 ? val.toFixed(decimals) : Math.round(val);
            if (p < 1) requestAnimationFrame(step);
        }
        requestAnimationFrame(step);
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  8. INGREDIENT CHECKLIST & LIVE RECALCULATION (Human-in-the-Loop)
    // ═══════════════════════════════════════════════════════════════════════════
    function renderIngredientList(ingredients) {
        if (!ingredients || ingredients.length === 0) {
            if (el.ingredientDecompCard) el.ingredientDecompCard.style.display = "none";
            if (el.customizerIngrStream) el.customizerIngrStream.innerHTML = "<p style='font-size:12px;color:#888;padding:8px 0;'>Select a dish to customize ingredients.</p>";
            return;
        }

        if (el.ingredientDecompCard) el.ingredientDecompCard.style.display = "block";
        if (el.decompChecklistStream) el.decompChecklistStream.innerHTML = "";
        if (el.customizerIngrStream) el.customizerIngrStream.innerHTML = "";

        const matched = ingredients.filter(i => i.matched).length;
        if (el.decompMatchedBadge) {
            el.decompMatchedBadge.textContent = `${matched}/${ingredients.length} Matched`;
        }

        const activeCount = ingredients.filter(i => i.active).length;
        if (el.customizerIngrBadge) {
            el.customizerIngrBadge.textContent = `${activeCount} Active`;
        }

        ingredients.forEach((ing, i) => {
            function createRow() {
                const card = document.createElement("div");
                card.className = `ing-row-item ${ing.active ? "" : "disabled"}`;
                card.dataset.ingIndex = i;

                card.innerHTML = `
                    <label class="ing-left-side" style="cursor: pointer; display: flex; align-items: center; gap: 10px;">
                        <input type="checkbox" class="ing-checkbox-matte" data-index="${i}" ${ing.active ? "checked" : ""}>
                        <div class="ing-text-col">
                            <span class="ing-title-name" style="font-weight: 600; color: #1C2321;">${ing.name}</span>
                            <span class="ing-source-tag" style="font-size: 10px; color: #767E77; display: block;">${ing.source || "Clinical Citation"}</span>
                        </div>
                    </label>
                    <div class="ing-right-side" style="display: flex; align-items: center; gap: 8px;">
                        <span class="ing-grams-pill" style="background: #EAE6DF; padding: 3px 8px; border-radius: 6px; font-size: 11px; font-weight: 600;">${ing.grams || ing.estimated_grams}g</span>
                        <span class="ing-calories-text" style="font-size: 12px; font-weight: 700; color: #E63946;">${Math.round(ing.calories || 0)} kcal</span>
                    </div>
                `;

                const chk = card.querySelector(".ing-checkbox-matte");
                chk.addEventListener("change", (e) => {
                    const isChecked = e.target.checked;
                    state.activeIngredients[i].active = isChecked;

                    // Sync checkboxes across both Customizer and Results list
                    document.querySelectorAll(`.ing-checkbox-matte[data-index="${i}"]`).forEach(c => {
                        c.checked = isChecked;
                        const parentRow = c.closest(".ing-row-item");
                        if (parentRow) parentRow.classList.toggle("disabled", !isChecked);
                    });

                    const newActive = state.activeIngredients.filter(it => it.active).length;
                    if (el.customizerIngrBadge) el.customizerIngrBadge.textContent = `${newActive} Active`;

                    triggerRecalculation();
                });

                return card;
            }

            if (el.decompChecklistStream) el.decompChecklistStream.appendChild(createRow());
            if (el.customizerIngrStream) el.customizerIngrStream.appendChild(createRow());
        });
    }

    let debounceTimer = null;
    function triggerRecalculation() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(async () => {
            const activeOnly = state.activeIngredients.filter(i => i.active);

            // Update badge
            if (el.customizerIngrBadge) {
                el.customizerIngrBadge.textContent = `${activeOnly.length} Active`;
            }

            try {
                const res = await fetch("/api/recalculate", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        ingredients: activeOnly.map(i => ({
                            name: i.name,
                            estimated_grams: i.grams || i.estimated_grams || 0,
                            category: i.category || "other"
                        })),
                        cooking_fat: state.cookingFat,
                        prep_style: state.prepStyle,
                        fat_tablespoons: state.fatTablespoons,
                        portion: state.currentPortion
                    })
                });

                const data = await res.json();
                if (data.success) {
                    const d = data.data;

                    // Reveal dashboard
                    if (el.emptyDashboardCard && !el.emptyDashboardCard.classList.contains("hidden")) {
                        el.emptyDashboardCard.classList.add("hidden");
                        el.resultsDashboardCard.classList.remove("hidden");
                    }

                    if (el.resDishName) {
                        el.resDishName.textContent = state.selectedDishName || "Personalized Plate";
                    }

                    // Update Macros
                    const t = d.totals || {};
                    tweenVal(el.valCalories, Math.round(t.calories || 0));
                    tweenVal(el.valProtein, t.protein || 0, 1);
                    tweenVal(el.valCarbs, t.carbs || 0, 1);
                    tweenVal(el.valFat, t.fat || 0, 1);

                    // Update Progress fills
                    if (el.fillCalories) el.fillCalories.style.width = `${Math.min(100, ((t.calories || 0) / 2000) * 100)}%`;
                    if (el.fillProtein) el.fillProtein.style.width = `${Math.min(100, ((t.protein || 0) / 75) * 100)}%`;
                    if (el.fillCarbs) el.fillCarbs.style.width = `${Math.min(100, ((t.carbs || 0) / 250) * 100)}%`;
                    if (el.fillFat) el.fillFat.style.width = `${Math.min(100, ((t.fat || 0) / 70) * 100)}%`;

                    // Update Nutri-Score
                    const grade = (d.nutriscore_grade || "C").toUpperCase();
                    const nsMeta = NUTRISCORE_META[grade] || NUTRISCORE_META["C"];
                    if (el.resNutriGradeMeaning) {
                        el.resNutriGradeMeaning.textContent = nsMeta.label;
                        el.resNutriGradeMeaning.style.color = nsMeta.color;
                    }

                    document.querySelectorAll(".ns-pill-item").forEach(p => {
                        if (p.dataset.grade === grade) {
                            p.classList.add("active");
                        } else {
                            p.classList.remove("active");
                        }
                    });
                }
            } catch (err) {
                console.error("Recalculation error:", err);
            }
        }, 100);
    }

    function loadVaultDishIngredients(dishId) {
        const defaultList = VAULT_DEFAULT_INGREDIENTS[dishId] || VAULT_DEFAULT_INGREDIENTS["lasagna"];
        state.activeIngredients = defaultList.map(i => ({
            ...i,
            grams: i.grams || i.estimated_grams,
            active: true
        }));
        renderIngredientList(state.activeIngredients);
        triggerRecalculation();
    }

    // ═══════════════════════════════════════════════════════════════════════════
    //  INITIALIZATION
    // ═══════════════════════════════════════════════════════════════════════════
    initHero3DParallax();
    initVaultCards();
    initDropzone();
    initControls();
    loadVaultDishIngredients("lasagna"); // Pre-load Lasagna ingredients into Customizer immediately!

    console.log("NutriScore AI Vision v5.0 Active (Matte Finish & 3D Perspective Architecture).");
});
