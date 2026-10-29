/**
 * NutriScore AI Vision · Interactive Engine v6.0
 * Deep Solid Pastel Aesthetic · 3D Scroll-Driven Exploded Showcase
 * Real-Time Dual-Engine AI + ICMR-NIN & USDA Clinical Recalculation
 */

document.addEventListener("DOMContentLoaded", () => {

    // =========================================================================
    // 1. GLOBAL STATE & DISH ARCHIVE
    // =========================================================================
    const state = {
        activeEngine: "gemini", // "gemini" | "local"
        selectedDishId: 0,
        selectedImageSrc: "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80",
        isUserUpload: false,
        userFile: null,
        portion: 1.0,
        cookingFat: "desi_ghee",
        fatTablespoons: 1.0,
        prepStyle: "homestyle", // homestyle (1.0), restaurant (1.25), diet (0.80)
        activeIngredients: [],
        isAnalyzing: false
    };

    // Clinical Nutrient Database (per 100g): [kcal, protein, fat, carbs, sat_fat, sugar, sodium_mg, fiber, fvln_flag]
    const CLINICAL_INGREDIENTS = {
        rice: { name: "Basmati Rice (cooked)", data: [130, 2.7, 0.3, 28.0, 0.1, 0.0, 1.0, 0.4, 0], source: "ICMR-NIN #A001" },
        chicken: { name: "Chicken Thigh (roasted)", data: [209, 26.0, 11.0, 0.0, 3.0, 0.0, 95.0, 0.0, 0], source: "USDA FDC #172389" },
        birista: { name: "Biryani Fried Onion", data: [240, 1.5, 16.0, 20.0, 2.0, 8.0, 10.0, 2.0, 1], source: "ICMR-NIN 2017" },
        ghee: { name: "Desi Ghee (Cooking Fat)", data: [900, 0.0, 100.0, 0.0, 62.0, 0.0, 2.0, 0.0, 0], source: "ICMR-NIN #K008" },
        herbs: { name: "Fresh Mint & Coriander", data: [40, 3.0, 0.5, 6.0, 0.1, 0.5, 20.0, 4.0, 1], source: "ICMR-NIN #E008" },
        pasta: { name: "Durum Wheat Pasta", data: [158, 5.8, 0.9, 31.0, 0.2, 0.6, 1.0, 1.8, 0], source: "USDA FDC #168927" },
        ragu: { name: "Lean Beef Ragù", data: [150, 12.0, 9.0, 5.0, 3.5, 3.0, 320.0, 1.0, 0], source: "USDA FDC #174032" },
        bechamel: { name: "Béchamel White Sauce", data: [130, 4.0, 8.0, 10.0, 5.0, 4.0, 250.0, 0.2, 0], source: "USDA FDC #173299" },
        mozzarella: { name: "Mozzarella Cheese", data: [280, 28.0, 17.0, 3.0, 10.9, 1.0, 627.0, 0.0, 0], source: "USDA FDC #170845" },
        tomato: { name: "San Marzano Puree", data: [18, 0.9, 0.2, 3.9, 0.0, 2.6, 5.0, 1.2, 1], source: "USDA FDC #170457" },
        pizza_crust: { name: "Neapolitan Crust", data: [270, 9.0, 3.0, 52.0, 0.6, 3.0, 500.0, 2.5, 0], source: "USDA FDC #173295" },
        dosa_crepe: { name: "Fermented Dosa Crepe", data: [200, 4.0, 6.0, 32.0, 1.5, 1.0, 300.0, 1.5, 0], source: "ICMR-NIN 2017" },
        potato_masala: { name: "Spiced Potato Masala", data: [100, 2.0, 4.0, 15.0, 0.7, 1.5, 200.0, 2.0, 0], source: "ICMR-NIN #D001" },
        idli_cake: { name: "Steamed Idli Cakes", data: [130, 4.0, 0.4, 28.0, 0.1, 0.5, 200.0, 1.2, 0], source: "ICMR-NIN 2017" },
        sambar: { name: "Toor Dal Sambar", data: [55, 3.0, 1.5, 8.0, 0.3, 2.0, 350.0, 3.0, 1], source: "ICMR-NIN #B001" },
        samosa_crust: { name: "Crisp Pastry Crust", data: [310, 6.0, 16.0, 36.0, 4.0, 1.0, 300.0, 2.0, 0], source: "ICMR-NIN 2017" },
        paneer: { name: "Fresh Malai Paneer", data: [296, 18.0, 22.0, 3.0, 14.0, 3.0, 20.0, 0.0, 0], source: "ICMR-NIN #K006" },
        peppers: { name: "Tandoori Bell Peppers", data: [30, 1.0, 0.3, 6.0, 0.0, 3.0, 5.0, 1.8, 1], source: "ICMR-NIN #E005" },
        curd_marinade: { name: "Dahi Yogurt Marinade", data: [61, 3.5, 3.3, 4.7, 2.1, 4.7, 46.0, 0.0, 0], source: "ICMR-NIN #K004" }
    };

    // Cooking Fats configuration
    const COOKING_FATS = [
        { id: "none", name: "None / Steamed", sat_fat: 0, density: 0, desc: "Zero added lipid medium" },
        { id: "olive_oil", name: "Olive Oil", sat_fat: 14, density: 100, desc: "Heart-healthy monounsaturated oleic acid" },
        { id: "desi_ghee", name: "Desi Ghee", sat_fat: 62, density: 100, desc: "Clarified butter, high saturated lipids, traditional aroma" },
        { id: "mustard_oil", name: "Mustard Oil", sat_fat: 12, density: 100, desc: "Pungent North Indian cold-pressed oil" },
        { id: "coconut_oil", name: "Coconut Oil", sat_fat: 82, density: 100, desc: "Medium-chain triglycerides (MCTs)" },
        { id: "vegetable_oil", name: "Refined Oil", sat_fat: 14, density: 100, desc: "Standard neutral cooking fat" }
    ];

    // Preparation styles
    const PREP_STYLES = [
        { id: "homestyle", name: "Homestyle", multiplier: 1.0, badge: "Standard", desc: "Measured salt and moderate oil" },
        { id: "restaurant", name: "Restaurant", multiplier: 1.25, badge: "+25% Kcal", desc: "Heavy butter, cream finish, extra sodium" },
        { id: "diet", name: "Diet / Lean", multiplier: 0.80, badge: "-20% Kcal", desc: "Steamed or air-fried with minimal oil" }
    ];

    // Culinary Vault Dishes
    const VAULT_DISHES = [
        {
            id: 0,
            name: "Chicken Biryani",
            origin: "Indian · Hyderabadi",
            desc: "Aromatic basmati rice layered with tender spiced chicken, golden birista onions, and pure desi ghee.",
            img: "https://images.unsplash.com/photo-1563379091339-03b21ab4a4f8?w=800&auto=format&fit=crop&q=80",
            ingredients: [
                { key: "rice", grams: 180 },
                { key: "chicken", grams: 120 },
                { key: "birista", grams: 25 },
                { key: "ghee", grams: 15 },
                { key: "herbs", grams: 10 }
            ],
            recommendation: "Rich in high-biological-value protein. Keep portions moderate to regulate saturated lipid density.",
            pairing: "Pair with cucumber mint raita to lower meal glycemic velocity."
        },
        {
            id: 1,
            name: "Baked Lasagna",
            origin: "Italian Cuisine",
            desc: "Durum wheat pasta layered with lean beef ragù bolognese, béchamel sauce, and bubbling mozzarella.",
            img: "https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=800&auto=format&fit=crop&q=80",
            ingredients: [
                { key: "pasta", grams: 110 },
                { key: "ragu", grams: 120 },
                { key: "bechamel", grams: 60 },
                { key: "mozzarella", grams: 40 },
                { key: "tomato", grams: 40 }
            ],
            recommendation: "Satisfying carbohydrate and protein balance. Regulate serving size to control dairy saturated fats.",
            pairing: "Serve with a crisp arugula salad dressed in lemon juice to assist lipid metabolism."
        },
        {
            id: 2,
            name: "Neapolitan Pizza",
            origin: "Italian · 1 slice",
            desc: "Naturally fermented sourdough crust topped with San Marzano tomatoes, fresh mozzarella, and olive drizzle.",
            img: "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=800&auto=format&fit=crop&q=80",
            ingredients: [
                { key: "pizza_crust", grams: 70 },
                { key: "mozzarella", grams: 35 },
                { key: "tomato", grams: 30 }
            ],
            recommendation: "Moderate single slice serving. High glycemic starch; balance with leafy vegetables.",
            pairing: "Pair with sparkling water and a side of steamed greens."
        },
        {
            id: 3,
            name: "Masala Dosa",
            origin: "South Indian",
            desc: "Crispy fermented rice and urad dal crepe rolled around mustard-tempered potato masala.",
            img: "https://images.unsplash.com/photo-1668236543090-82eba5ee5976?w=800&auto=format&fit=crop&q=80",
            ingredients: [
                { key: "dosa_crepe", grams: 90 },
                { key: "potato_masala", grams: 90 },
                { key: "ghee", grams: 6 }
            ],
            recommendation: "Fermented batter aids gut microbiome health. Watch the potato filling carbohydrate load.",
            pairing: "Dip generously in vegetable sambar to boost dietary fiber intake."
        },
        {
            id: 4,
            name: "Steamed Idli Sambar",
            origin: "South Indian (Zero-Oil)",
            desc: "Light steamed rice-lentil cakes served in a rich toor dal and vegetable broth with drumsticks.",
            img: "https://images.unsplash.com/photo-1589301760014-d929f3979dbc?w=800&auto=format&fit=crop&q=80",
            ingredients: [
                { key: "idli_cake", grams: 110 },
                { key: "sambar", grams: 120 }
            ],
            recommendation: "Virtually zero oil, easily digestible, and balanced in amino acids. Excellent everyday staple.",
            pairing: "Ideal breakfast plate on its own; keep coconut chutney portions controlled."
        },
        {
            id: 5,
            name: "Vegetable Samosa",
            origin: "Indian Street Food",
            desc: "Golden pyramid pastry stuffed with cumin-spiced potatoes, green peas, and whole coriander seeds.",
            img: "https://images.unsplash.com/photo-1601050690597-df0568f70950?w=800&auto=format&fit=crop&q=80",
            ingredients: [
                { key: "samosa_crust", grams: 65 },
                { key: "potato_masala", grams: 75 }
            ],
            recommendation: "High lipid absorption from deep frying. Best enjoyed occasionally as a mindful snack.",
            pairing: "Pair with raw mint coriander chutney rather than sweet tamarind syrup."
        },
        {
            id: 6,
            name: "Tandoori Paneer Tikka",
            origin: "North Indian Tandoori",
            desc: "Char-grilled cottage cheese cubes marinated in hung curd, Kashmiri chili, bell peppers, and carom seeds.",
            img: "https://images.unsplash.com/photo-1567188040759-fb8a883dc6d8?w=800&auto=format&fit=crop&q=80",
            ingredients: [
                { key: "paneer", grams: 85 },
                { key: "peppers", grams: 60 },
                { key: "curd_marinade", grams: 25 },
                { key: "ghee", grams: 5 }
            ],
            recommendation: "Excellent vegetarian protein and calcium source. Moderate saturated fat density.",
            pairing: "Serve with onion salad and lemon wedges for ascorbic acid enhancement."
        }
    ];

    // =========================================================================
    // 2. DOM REFERENCES
    // =========================================================================
    const el = {
        glCanvas: document.getElementById("glCanvas"),
        heroStage: document.getElementById("hero"),
        projectedLabels: document.getElementById("projectedLabels"),
        heroTotalPill: document.getElementById("heroTotalPill"),
        heroCalorieNum: document.getElementById("heroCalorieNum"),
        heroGradeBadge: document.getElementById("heroGradeBadge"),
        scrollCaptions: document.querySelectorAll(".caption-item"),
        
        btnEngineGemini: document.getElementById("btnEngineGemini"),
        btnEngineLocal: document.getElementById("btnEngineLocal"),
        
        vaultGrid: document.getElementById("vaultGrid"),
        hiddenFileInput: document.getElementById("hiddenFileInput"),
        
        platePhotoImg: document.getElementById("platePhotoImg"),
        plateCuisineTag: document.getElementById("plateCuisineTag"),
        plateDishTitle: document.getElementById("plateDishTitle"),
        plateDishDesc: document.getElementById("plateDishDesc"),
        laserScannerHud: document.getElementById("laserScannerHud"),
        
        nsPillsRow: document.getElementById("nsPillsRow"),
        nsVerdictTitle: document.getElementById("nsVerdictTitle"),
        nsScoreVal: document.getElementById("nsScoreVal"),
        nsPointsStack: document.getElementById("nsPointsStack"),
        
        calorieNumber: document.getElementById("calorieNumber"),
        activePortionTag: document.getElementById("activePortionTag"),
        macrosStream: document.getElementById("macrosStream"),
        
        portionRange: document.getElementById("portionRange"),
        portionValBadge: document.getElementById("portionValBadge"),
        fatChipsGrid: document.getElementById("fatChipsGrid"),
        fatRange: document.getElementById("fatRange"),
        fatTablespoonBadge: document.getElementById("fatTablespoonBadge"),
        fatLipidHint: document.getElementById("fatLipidHint"),
        prepChipsRow: document.getElementById("prepChipsRow"),
        prepStyleHint: document.getElementById("prepStyleHint"),
        btnRunInference: document.getElementById("btnRunInference"),
        
        matchedCountPill: document.getElementById("matchedCountPill"),
        ingredientsStream: document.getElementById("ingredientsStream"),
        guidanceRecommendation: document.getElementById("guidanceRecommendation"),
        guidancePairing: document.getElementById("guidancePairing")
    };

    // =========================================================================
    // 3. EUROPEAN NUTRI-SCORE COMPUTATION ENGINE (FSAm-NPS Standard)
    // =========================================================================
    const NUTRISCORE_META = {
        "A": { label: "Grade A · Optimal Nutritional Balance", color: "#028040" },
        "B": { label: "Grade B · High Nutritional Quality", color: "#84BA2F" },
        "C": { label: "Grade C · Balanced Profile", color: "#FDC901" },
        "D": { label: "Grade D · High Calorie / Mindful Intake", color: "#EE8000" },
        "E": { label: "Grade E · High Lipid / Occasional Treat", color: "#E53B10" }
    };

    function calculateNutriScore(activeIngredients, portion, fatId, fatTbsp, prepStyleId) {
        let totalWeight = 0;
        let sumKcal = 0;
        let sumProt = 0;
        let sumFat = 0;
        let sumCarbs = 0;
        let sumSatFat = 0;
        let sumSugar = 0;
        let sumSodium = 0;
        let sumFiber = 0;
        let sumFvlnWeight = 0;

        const prep = PREP_STYLES.find(p => p.id === prepStyleId) || PREP_STYLES[0];
        const mult = prep.multiplier;

        // Sum active ingredients
        activeIngredients.forEach(ing => {
            if (!ing.active) return;
            const w = ing.grams * portion;
            const d = ing.data; // [kcal, protein, fat, carbs, sat_fat, sugar, sodium_mg, fiber, fvln_flag]
            totalWeight += w;
            sumKcal += (d[0] * w / 100) * mult;
            sumProt += (d[1] * w / 100) * mult;
            sumFat += (d[2] * w / 100) * mult;
            sumCarbs += (d[3] * w / 100) * mult;
            sumSatFat += (d[4] * w / 100) * mult;
            sumSugar += (d[5] * w / 100) * mult;
            sumSodium += (d[6] * w / 100) * mult;
            sumFiber += (d[7] * w / 100) * mult;
            if (d[8] === 1) sumFvlnWeight += w;
        });

        // Add extra cooking fat
        const fat = COOKING_FATS.find(f => f.id === fatId) || COOKING_FATS[0];
        if (fatId !== "none" && fatTbsp > 0) {
            const fatGrams = fatTbsp * 14.0 * portion;
            totalWeight += fatGrams;
            sumKcal += (884.0 * fatGrams / 100);
            sumFat += fatGrams;
            sumSatFat += (fat.sat_fat * fatGrams / 100);
        }

        if (totalWeight < 1) {
            return {
                grade: "C", score: 0, kcal: 0, prot: 0, fat: 0, carbs: 0, satFat: 0, sugar: 0, sodium: 0, fiber: 0,
                negativePts: { energy: 0, satFat: 0, sugars: 0, sodium: 0 },
                positivePts: { fiber: 0, protein: 0, fvln: 0 }
            };
        }

        // Standardize to 100g basis for European FSAm-NPS scoring
        const factor = 100.0 / totalWeight;
        const qKcal = sumKcal * factor;
        const qKj = qKcal * 4.184;
        const qSatFat = sumSatFat * factor;
        const qSugar = sumSugar * factor;
        const qSodium = sumSodium * factor;
        const qFiber = sumFiber * factor;
        const qProtein = sumProt * factor;
        const qFvlnPct = (sumFvlnWeight / totalWeight) * 100.0;

        // Points threshold evaluation
        const countThresholds = (val, thArr) => thArr.filter(t => val > t).length;

        const ptsEnergy = Math.min(10, countThresholds(qKj, [335, 670, 1005, 1340, 1675, 2010, 2345, 2680, 3015, 3350]));
        const ptsSatFat = Math.min(10, countThresholds(qSatFat, [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]));
        const ptsSugars = Math.min(10, countThresholds(qSugar, [4.5, 9, 13.5, 18, 22.5, 27, 31, 36, 40, 45]));
        const ptsSodium = Math.min(10, countThresholds(qSodium, [90, 180, 270, 360, 450, 540, 630, 720, 810, 900]));

        const ptsFiber = Math.min(5, countThresholds(qFiber, [0.9, 1.9, 2.8, 3.7, 4.7]));
        let ptsProtein = Math.min(5, countThresholds(qProtein, [1.6, 3.2, 4.8, 6.4, 8.0]));
        const ptsFvln = qFvlnPct > 80 ? 5 : (qFvlnPct > 60 ? 2 : (qFvlnPct > 40 ? 1 : 0));

        const totalN = ptsEnergy + ptsSatFat + ptsSugars + ptsSodium;
        // Protein cap rule: If N >= 11 and FVLN < 5, protein points are zeroed out
        if (totalN >= 11 && ptsFvln < 5) {
            ptsProtein = 0;
        }

        const totalP = ptsFiber + ptsProtein + ptsFvln;
        const score = totalN - totalP;

        let grade = "C";
        if (score <= -1) grade = "A";
        else if (score <= 2) grade = "B";
        else if (score <= 10) grade = "C";
        else if (score <= 18) grade = "D";
        else grade = "E";

        return {
            grade,
            score,
            kcal: Math.round(sumKcal),
            prot: parseFloat(sumProt.toFixed(1)),
            fat: parseFloat(sumFat.toFixed(1)),
            carbs: parseFloat(sumCarbs.toFixed(1)),
            satFat: parseFloat(sumSatFat.toFixed(1)),
            sugar: parseFloat(sumSugar.toFixed(1)),
            sodium: Math.round(sumSodium),
            fiber: parseFloat(sumFiber.toFixed(1)),
            negativePts: { energy: ptsEnergy, satFat: ptsSatFat, sugars: ptsSugars, sodium: ptsSodium },
            positivePts: { fiber: ptsFiber, protein: ptsProtein, fvln: ptsFvln }
        };
    }

    // =========================================================================
    // 4. RENDER STUDIO & DASHBOARD
    // =========================================================================
    function renderStudio() {
        const dish = VAULT_DISHES[state.selectedDishId];
        const res = calculateNutriScore(
            state.activeIngredients,
            state.portion,
            state.cookingFat,
            state.fatTablespoons,
            state.prepStyle
        );

        // Update Dish Metadata
        el.plateDishTitle.textContent = dish.name;
        el.plateDishDesc.textContent = dish.desc;
        el.plateCuisineTag.textContent = dish.origin;
        if (!state.isUserUpload) {
            el.platePhotoImg.src = dish.img;
        }

        // Nutri-Score Pills
        const pills = el.nsPillsRow.querySelectorAll(".ns-pill-badge");
        pills.forEach(p => {
            if (p.dataset.grade === res.grade) {
                p.classList.add("active");
            } else {
                p.classList.remove("active");
            }
        });

        const meta = NUTRISCORE_META[res.grade] || NUTRISCORE_META["C"];
        el.nsVerdictTitle.textContent = meta.label;
        el.nsScoreVal.textContent = `Score: ${res.score >= 0 ? '+' : ''}${res.score}`;

        // Breakdown Points Stack
        el.nsPointsStack.innerHTML = `
            <div class="ns-point-row">
                <span class="ns-point-label">Energy (kJ)</span>
                <div class="ns-point-track"><div class="ns-point-fill" style="width: ${(res.negativePts.energy / 10) * 100}%; background: var(--pastel-coral);"></div></div>
                <span class="ns-point-val" style="color: var(--pastel-coral);">−${res.negativePts.energy}</span>
            </div>
            <div class="ns-point-row">
                <span class="ns-point-label">Saturated Fat</span>
                <div class="ns-point-track"><div class="ns-point-fill" style="width: ${(res.negativePts.satFat / 10) * 100}%; background: var(--pastel-coral);"></div></div>
                <span class="ns-point-val" style="color: var(--pastel-coral);">−${res.negativePts.satFat}</span>
            </div>
            <div class="ns-point-row">
                <span class="ns-point-label">Sugars</span>
                <div class="ns-point-track"><div class="ns-point-fill" style="width: ${(res.negativePts.sugars / 10) * 100}%; background: var(--pastel-coral);"></div></div>
                <span class="ns-point-val" style="color: var(--pastel-coral);">−${res.negativePts.sugars}</span>
            </div>
            <div class="ns-point-row">
                <span class="ns-point-label">Sodium Salt</span>
                <div class="ns-point-track"><div class="ns-point-fill" style="width: ${(res.negativePts.sodium / 10) * 100}%; background: var(--pastel-coral);"></div></div>
                <span class="ns-point-val" style="color: var(--pastel-coral);">−${res.negativePts.sodium}</span>
            </div>
            <div class="ns-point-row">
                <span class="ns-point-label">Dietary Fiber</span>
                <div class="ns-point-track"><div class="ns-point-fill" style="width: ${(res.positivePts.fiber / 5) * 100}%; background: var(--pastel-emerald);"></div></div>
                <span class="ns-point-val" style="color: var(--pastel-emerald);">+${res.positivePts.fiber}</span>
            </div>
            <div class="ns-point-row">
                <span class="ns-point-label">Protein</span>
                <div class="ns-point-track"><div class="ns-point-fill" style="width: ${(res.positivePts.protein / 5) * 100}%; background: var(--pastel-emerald);"></div></div>
                <span class="ns-point-val" style="color: var(--pastel-emerald);">+${res.positivePts.protein}</span>
            </div>
        `;

        // Energy & Animated Counter
        tweenNumber(el.calorieNumber, res.kcal);
        el.activePortionTag.textContent = `${state.portion}× (${state.portion <= 0.6 ? 'Light' : state.portion <= 1.25 ? 'Standard' : 'Hearty'})`;

        // Macros Trio Stream
        const totalMacroCal = (res.prot * 4) + (res.carbs * 4) + (res.fat * 9) || 1;
        el.macrosStream.innerHTML = `
            <div class="macro-bar-row">
                <span class="macro-bar-label">Protein</span>
                <div class="macro-bar-track"><div class="macro-bar-fill" style="width: ${Math.min(100, (res.prot * 4 / totalMacroCal) * 100)}%; background: var(--pastel-slate);"></div></div>
                <span class="macro-bar-val">${res.prot}g</span>
            </div>
            <div class="macro-bar-row">
                <span class="macro-bar-label">Carbs</span>
                <div class="macro-bar-track"><div class="macro-bar-fill" style="width: ${Math.min(100, (res.carbs * 4 / totalMacroCal) * 100)}%; background: var(--pastel-amber);"></div></div>
                <span class="macro-bar-val">${res.carbs}g</span>
            </div>
            <div class="macro-bar-row">
                <span class="macro-bar-label">Total Fat</span>
                <div class="macro-bar-track"><div class="macro-bar-fill" style="width: ${Math.min(100, (res.fat * 9 / totalMacroCal) * 100)}%; background: var(--pastel-coral);"></div></div>
                <span class="macro-bar-val">${res.fat}g</span>
            </div>
        `;

        // Customizer UI Badges
        el.portionValBadge.textContent = `${state.portion}×`;
        el.fatTablespoonBadge.textContent = state.cookingFat === "none" ? "0 tbsp (None)" : `${state.fatTablespoons} tbsp (~${Math.round(state.fatTablespoons * 120 * state.portion)} kcal)`;
        
        const activeFatObj = COOKING_FATS.find(f => f.id === state.cookingFat) || COOKING_FATS[0];
        el.fatLipidHint.textContent = activeFatObj.desc;
        
        const activePrepObj = PREP_STYLES.find(p => p.id === state.prepStyle) || PREP_STYLES[0];
        el.prepStyleHint.textContent = `${activePrepObj.desc} (${activePrepObj.badge})`;

        // Render Ingredients Checklist
        renderIngredientChecklist(state.activeIngredients, state.portion, activePrepObj.multiplier);

        // Update Guidance
        el.guidanceRecommendation.textContent = dish.recommendation || "Balanced profile. Keep portions moderate.";
        el.guidancePairing.textContent = dish.pairing || "Pair with fresh greens and plenty of water.";

        // Also update Hero Total Badge if biryani is selected
        if (state.selectedDishId === 0) {
            tweenNumber(el.heroCalorieNum, res.kcal);
            el.heroGradeBadge.textContent = res.grade;
            el.heroGradeBadge.style.backgroundColor = meta.color;
        }
    }

    function renderIngredientChecklist(ingredients, portion, multiplier) {
        const activeCount = ingredients.filter(i => i.active).length;
        el.matchedCountPill.textContent = `${activeCount}/${ingredients.length} Clinical Matches`;

        const maxKcal = Math.max(...ingredients.map(i => (i.data[0] * (i.grams * portion) / 100) * multiplier), 1);

        el.ingredientsStream.innerHTML = ingredients.map((ing, idx) => {
            const scaledGrams = Math.round(ing.grams * portion);
            const ingKcal = Math.round((ing.data[0] * (ing.grams * portion) / 100) * multiplier);
            const barWidth = Math.min(100, (ingKcal / maxKcal) * 100);

            return `
                <label class="ing-row-item ${ing.active ? '' : 'disabled'}">
                    <input type="checkbox" data-index="${idx}" ${ing.active ? 'checked' : ''}>
                    <div class="ing-name-group">
                        <span class="ing-title">${ing.name}</span>
                        <span class="ing-source-citation">${ing.source}</span>
                    </div>
                    <span class="ing-grams-tag">${scaledGrams}g</span>
                    <span class="ing-cal-tag">${ingKcal} kcal</span>
                    <div class="ing-row-bar"><i style="width: ${barWidth}%;"></i></div>
                </label>
            `;
        }).join('');
    }

    function tweenNumber(element, target) {
        if (!element) return;
        const current = parseInt(element.textContent) || 0;
        const diff = target - current;
        if (Math.abs(diff) < 1) {
            element.textContent = target;
            return;
        }
        const startTime = performance.now();
        const duration = 400;

        function animate(now) {
            const p = Math.min((now - startTime) / duration, 1);
            const val = Math.round(current + diff * (p * (2 - p)));
            element.textContent = val;
            if (p < 1) requestAnimationFrame(animate);
        }
        requestAnimationFrame(animate);
    }

    // =========================================================================
    // 5. CULINARY VAULT SETUP
    // =========================================================================
    function initVault() {
        const tilesHtml = VAULT_DISHES.map(dish => {
            const defaultRes = calculateNutriScore(
                dish.ingredients.map(i => ({ ...CLINICAL_INGREDIENTS[i.key], grams: i.grams, active: true })),
                1.0, "desi_ghee", 1.0, "homestyle"
            );
            const meta = NUTRISCORE_META[defaultRes.grade] || NUTRISCORE_META["C"];

            return `
                <div class="vault-dish-tile ${dish.id === state.selectedDishId ? 'active' : ''}" data-id="${dish.id}">
                    <div class="tile-image-box">
                        <img src="${dish.img}" alt="${dish.name}" loading="lazy">
                        <div class="tile-corner-grade" style="background-color: ${meta.color};">${defaultRes.grade}</div>
                    </div>
                    <div class="tile-meta-box">
                        <h4 class="tile-dish-name">${dish.name}</h4>
                        <p class="tile-dish-sub">${dish.origin} · ~${defaultRes.kcal} kcal</p>
                    </div>
                </div>
            `;
        }).join('');

        const uploadTileHtml = `
            <div class="vault-upload-tile" id="btnUploadTile">
                <div class="upload-icon-circle">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
                        <polyline points="17 8 12 3 7 8"></polyline>
                        <line x1="12" y1="3" x2="12" y2="15"></line>
                    </svg>
                </div>
                <h4>Upload Meal Photo</h4>
                <p>Drop any JPG or PNG image</p>
            </div>
        `;

        el.vaultGrid.innerHTML = tilesHtml + uploadTileHtml;

        // Tile Click Listeners
        el.vaultGrid.querySelectorAll(".vault-dish-tile").forEach(tile => {
            tile.addEventListener("click", () => {
                const id = parseInt(tile.dataset.id);
                loadVaultDish(id);
                document.getElementById("studio").scrollIntoView({ behavior: "smooth" });
            });
        });

        // Upload Tile Trigger
        const uploadBtn = document.getElementById("btnUploadTile");
        if (uploadBtn) {
            uploadBtn.addEventListener("click", () => el.hiddenFileInput.click());
        }

        el.hiddenFileInput.addEventListener("change", handleFileUpload);
    }

    function loadVaultDish(dishId) {
        state.selectedDishId = dishId;
        state.isUserUpload = false;
        state.portion = 1.0;
        state.fatTablespoons = 1.0;
        state.cookingFat = "desi_ghee";
        state.prepStyle = "homestyle";

        el.portionRange.value = 1.0;
        el.fatRange.value = 1.0;

        // Highlight vault tile
        el.vaultGrid.querySelectorAll(".vault-dish-tile").forEach(t => {
            t.classList.toggle("active", parseInt(t.dataset.id) === dishId);
        });

        // Load constituent ingredients
        const dish = VAULT_DISHES[dishId];
        state.activeIngredients = dish.ingredients.map(i => ({
            ...CLINICAL_INGREDIENTS[i.key],
            grams: i.grams,
            active: true
        }));

        renderStudio();
    }

    // =========================================================================
    // 6. CUSTOMIZER CONTROLS SETUP
    // =========================================================================
    function initCustomizerControls() {
        // Render Cooking Fat Chips
        el.fatChipsGrid.innerHTML = COOKING_FATS.map(f => `
            <button type="button" class="fat-chip-btn ${f.id === state.cookingFat ? 'active' : ''}" data-fat="${f.id}">
                ${f.name}
            </button>
        `).join('');

        el.fatChipsGrid.querySelectorAll(".fat-chip-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                state.cookingFat = btn.dataset.fat;
                el.fatChipsGrid.querySelectorAll(".fat-chip-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                if (state.cookingFat === "none") {
                    state.fatTablespoons = 0;
                    el.fatRange.value = 0;
                } else if (state.fatTablespoons === 0) {
                    state.fatTablespoons = 1.0;
                    el.fatRange.value = 1.0;
                }
                renderStudio();
            });
        });

        // Render Prep Style Chips
        el.prepChipsRow.innerHTML = PREP_STYLES.map(p => `
            <button type="button" class="prep-chip-btn ${p.id === state.prepStyle ? 'active' : ''}" data-prep="${p.id}">
                <strong>${p.name}</strong>
                <span>${p.badge}</span>
            </button>
        `).join('');

        el.prepChipsRow.querySelectorAll(".prep-chip-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                state.prepStyle = btn.dataset.prep;
                el.prepChipsRow.querySelectorAll(".prep-chip-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                renderStudio();
            });
        });

        // Portion Slider
        el.portionRange.addEventListener("input", (e) => {
            state.portion = parseFloat(e.target.value);
            renderStudio();
        });

        // Fat Volume Slider
        el.fatRange.addEventListener("input", (e) => {
            state.fatTablespoons = parseFloat(e.target.value);
            if (state.fatTablespoons > 0 && state.cookingFat === "none") {
                state.cookingFat = "desi_ghee";
                el.fatChipsGrid.querySelectorAll(".fat-chip-btn").forEach(b => {
                    b.classList.toggle("active", b.dataset.fat === "desi_ghee");
                });
            }
            renderStudio();
        });

        // Ingredient Checklist Delegated Toggle
        el.ingredientsStream.addEventListener("change", (e) => {
            if (e.target.matches("input[type='checkbox']")) {
                const idx = parseInt(e.target.dataset.index);
                if (state.activeIngredients[idx]) {
                    state.activeIngredients[idx].active = e.target.checked;
                    renderStudio();
                }
            }
        });

        // Engine Toggle
        el.btnEngineGemini.addEventListener("click", () => {
            state.activeEngine = "gemini";
            el.btnEngineGemini.classList.add("active");
            el.btnEngineLocal.classList.remove("active");
        });

        el.btnEngineLocal.addEventListener("click", () => {
            state.activeEngine = "local";
            el.btnEngineLocal.classList.add("active");
            el.btnEngineGemini.classList.remove("active");
        });

        // Re-analyze trigger
        el.btnRunInference.addEventListener("click", () => {
            triggerAIVisionInference();
        });
    }

    // =========================================================================
    // 7. REAL BACKEND INTEGRATION (Inference & Upload)
    // =========================================================================
    async function handleFileUpload(e) {
        const file = e.target.files[0];
        if (!file) return;

        state.isUserUpload = true;
        state.userFile = file;
        const objectUrl = URL.createObjectURL(file);
        el.platePhotoImg.src = objectUrl;

        document.getElementById("studio").scrollIntoView({ behavior: "smooth" });
        await triggerAIVisionInference(file);
    }

    async function triggerAIVisionInference(fileOverride = null) {
        if (state.isAnalyzing) return;
        state.isAnalyzing = true;

        el.laserScannerHud.classList.remove("hidden");
        el.btnRunInference.disabled = true;
        el.btnRunInference.querySelector("span").textContent = "Analyzing Image Tensor...";

        try {
            const formData = new FormData();
            if (fileOverride) {
                formData.append("file", fileOverride);
            } else if (state.userFile) {
                formData.append("file", state.userFile);
            } else {
                // Fetch blob from active Unsplash image
                const dish = VAULT_DISHES[state.selectedDishId];
                const resp = await fetch(dish.img);
                const blob = await resp.blob();
                formData.append("file", blob, "dish.jpg");
            }

            formData.append("cooking_fat", state.cookingFat);
            formData.append("prep_style", state.prepStyle);
            formData.append("fat_tablespoons", state.fatTablespoons);
            formData.append("portion", state.portion);

            const endpoint = state.activeEngine === "gemini" ? "/api/analyze" : "/api/predict";
            const res = await fetch(endpoint, { method: "POST", body: formData });
            const data = await res.json();

            if (data.success && data.data) {
                const d = data.data;
                el.plateDishTitle.textContent = d.dish_name || d.display_name || "Recognized Plate";
                el.plateCuisineTag.textContent = d.cuisine || "Global Cuisine";
                if (d.dish_description) el.plateDishDesc.textContent = d.dish_description;

                if (d.ingredient_breakdown && d.ingredient_breakdown.length > 0) {
                    state.activeIngredients = d.ingredient_breakdown.map(ing => ({
                        name: ing.name,
                        grams: ing.grams || ing.estimated_grams || 100,
                        data: [
                            (ing.calories || 150) * 100 / (ing.grams || 100),
                            (ing.protein || 5) * 100 / (ing.grams || 100),
                            (ing.fat || 4) * 100 / (ing.grams || 100),
                            (ing.carbs || 20) * 100 / (ing.grams || 100),
                            2.0, 1.0, 150.0, 1.5, 0
                        ],
                        source: ing.source || "Clinical ICMR-NIN Lookup",
                        active: true
                    }));
                }
            }
        } catch (err) {
            console.warn("Backend inference notice:", err);
            // Graceful fallback to client clinical database
        } finally {
            state.isAnalyzing = false;
            el.laserScannerHud.classList.add("hidden");
            el.btnRunInference.disabled = false;
            el.btnRunInference.querySelector("span").textContent = "Re-Analyze with Vision AI";
            renderStudio();
        }
    }

    // =========================================================================
    // 8. THREE.JS 3D EXPLODED FOOD BOWL SHOWCASE
    // =========================================================================
    function init3DExplodedBowl() {
        if (!window.THREE || !el.glCanvas) return;

        const canvas = el.glCanvas;
        const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(40, window.innerWidth / window.innerHeight, 0.1, 50);
        camera.position.set(0, 0.8, 9.2);
        camera.lookAt(0, 0.3, 0);

        const group = new THREE.Group();
        scene.add(group);

        // Studio Lights
        scene.add(new THREE.AmbientLight(0xffffff, 0.7));
        const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
        dirLight.position.set(3, 7, 5);
        scene.add(dirLight);

        const lightAmber = new THREE.PointLight(0xD99C2E, 1.4, 16);
        lightAmber.position.set(-4, 3, 3);
        scene.add(lightAmber);

        const lightGreen = new THREE.PointLight(0x358B68, 1.1, 14);
        lightGreen.position.set(4, 2, -2);
        scene.add(lightGreen);

        // Ceramic Gourmet Bowl
        const bowlPoints = [
            [0, 0], [0.75, 0.02], [1.25, 0.25], [1.7, 0.75],
            [1.85, 1.05], [1.78, 1.08], [1.55, 0.8], [1.1, 0.36],
            [0.6, 0.2], [0, 0.18]
        ].map(p => new THREE.Vector2(p[0], p[1]));

        const bowlGeo = new THREE.LatheGeometry(bowlPoints, 64);
        const bowlMat = new THREE.MeshStandardMaterial({
            color: 0x161E2C,
            roughness: 0.35,
            metalness: 0.25,
            side: THREE.DoubleSide
        });
        const bowl = new THREE.Mesh(bowlGeo, bowlMat);
        bowl.position.y = -1.35;
        group.add(bowl);

        // Golden Ceramic Rim
        const rimGeo = new THREE.TorusGeometry(1.82, 0.035, 12, 80);
        const rimMat = new THREE.MeshBasicMaterial({ color: 0xD99C2E });
        const rim = new THREE.Mesh(rimGeo, rimMat);
        rim.rotation.x = Math.PI / 2;
        rim.position.y = -0.28;
        group.add(rim);

        // Realistic 3D Ingredients Configuration
        // Clusters: Rice, Roasted Chicken, Fried Onions, Ghee Droplets, Green Herb Leaves
        const CLUSTERS = [
            {
                name: "Basmati Rice", labelText: "Basmati Rice · 180g · 234 kcal",
                count: 38,
                geo: new THREE.SphereGeometry(1, 8, 6),
                scale: [0.09, 0.045, 0.045],
                color: 0xF5EFE6, roughness: 0.6,
                targetAnchor: [-2.9, 0.7, 0],
                spread: 0.65, baseY: -0.9, radius: 1.0
            },
            {
                name: "Roasted Chicken", labelText: "Chicken Thigh · 120g · 250 kcal",
                count: 5,
                geo: new THREE.DodecahedronGeometry(0.32, 1),
                scale: [1.0, 0.8, 0.9],
                color: 0xB84D28, roughness: 0.75,
                targetAnchor: [2.9, 1.0, 0],
                spread: 0.5, baseY: -0.65, radius: 0.85
            },
            {
                name: "Fried Onions", labelText: "Fried Onions · 25g · 60 kcal",
                count: 4,
                geo: new THREE.TorusGeometry(0.18, 0.045, 8, 20),
                scale: [1, 1, 1],
                color: 0xD98A28, roughness: 0.45,
                targetAnchor: [-2.1, 2.4, 0],
                spread: 0.4, baseY: -0.55, radius: 0.65
            },
            {
                name: "Fresh Herbs", labelText: "Fresh Herbs · 10g · 5 kcal",
                count: 6,
                geo: new THREE.PlaneGeometry(0.24, 0.14, 2, 2),
                scale: [1, 1, 1],
                color: 0x2E8B57, roughness: 0.5, doubleSided: true,
                targetAnchor: [2.2, 2.5, 0],
                spread: 0.45, baseY: -0.5, radius: 0.8
            },
            {
                name: "Desi Ghee", labelText: "Desi Ghee · 15g · 135 kcal",
                count: 3,
                geo: new THREE.SphereGeometry(0.16, 14, 12),
                scale: [1, 1, 1],
                color: 0xE5A93C, roughness: 0.15, metalness: 0.1,
                targetAnchor: [0.0, 2.9, 0],
                spread: 0.3, baseY: -0.6, radius: 0.5
            }
        ];

        // Generate Projected DOM Labels
        el.projectedLabels.innerHTML = CLUSTERS.map(c => `
            <div class="projected-tag" data-cluster="${c.name}">
                <b>${c.name}</b>
                <span>${c.labelText.split('·')[1] || ''} · ${c.labelText.split('·')[2] || ''}</span>
            </div>
        `).join('');

        const labelElements = [...el.projectedLabels.querySelectorAll(".projected-tag")];

        // Instantiate 3D Meshes
        const items = [];
        const rand = (min, max) => min + Math.random() * (max - min);

        CLUSTERS.forEach((cluster, cIdx) => {
            const mat = new THREE.MeshStandardMaterial({
                color: cluster.color,
                roughness: cluster.roughness,
                metalness: cluster.metalness || 0,
                side: cluster.doubleSided ? THREE.DoubleSide : THREE.FrontSide
            });

            for (let i = 0; i < cluster.count; i++) {
                const mesh = new THREE.Mesh(cluster.geo, mat);
                mesh.scale.set(...cluster.scale);

                const angle = rand(0, Math.PI * 2);
                const dist = Math.sqrt(Math.random()) * cluster.radius;

                // 3 Key Positions:
                // 1. basePos: resting in bowl
                // 2. hoverPos: floating slightly
                // 3. spreadPos: exploded out to designated cluster anchor
                const basePos = new THREE.Vector3(
                    Math.cos(angle) * dist,
                    cluster.baseY + rand(0, 0.15),
                    Math.sin(angle) * dist
                );

                const hoverPos = new THREE.Vector3(
                    rand(-1.1, 1.1),
                    rand(0.2, 1.3),
                    rand(-0.7, 0.7)
                );

                const spreadPos = new THREE.Vector3(
                    cluster.targetAnchor[0] + rand(-cluster.spread, cluster.spread),
                    cluster.targetAnchor[1] + rand(-cluster.spread, cluster.spread),
                    cluster.targetAnchor[2] + rand(-0.4, 0.4)
                );

                items.push({
                    mesh,
                    basePos,
                    hoverPos,
                    spreadPos,
                    clusterIndex: cIdx,
                    rotSpeedX: rand(-1, 1) * 0.015,
                    rotSpeedY: rand(-1, 1) * 0.015,
                    phase: rand(0, Math.PI * 2)
                });

                group.add(mesh);
            }
        });

        // Resize Handling
        function onResize() {
            const w = window.innerWidth;
            const h = window.innerHeight;
            renderer.setSize(w, h, false);
            camera.aspect = w / h;
            camera.updateProjectionMatrix();
            const scaleFactor = Math.min(1.0, Math.max(0.55, camera.aspect / 1.6));
            group.scale.setScalar(scaleFactor);
        }
        window.addEventListener("resize", onResize);
        onResize();

        // Scroll Progress Interpolation
        let scrollProgress = 0;
        function updateScroll() {
            const heroHeight = el.heroStage.offsetHeight - window.innerHeight;
            scrollProgress = Math.min(1, Math.max(0, window.scrollY / Math.max(1, heroHeight)));

            // Hero Canvas Fadeout as we leave Hero
            const fadeStart = el.heroStage.offsetHeight - window.innerHeight * 1.2;
            const fadeProgress = Math.min(1, Math.max(0.12, 1 - (window.scrollY - fadeStart) / (window.innerHeight * 0.6)));
            canvas.style.opacity = fadeProgress;

            // Headline Fadeout
            const titleWrap = document.querySelector(".hero-title-wrap");
            if (titleWrap) {
                titleWrap.style.opacity = Math.max(0, 1 - scrollProgress / 0.15);
                titleWrap.style.transform = `translateY(${-scrollProgress * 50}px)`;
            }

            // Captions Crossfade
            el.scrollCaptions.forEach((cap, idx) => {
                const isActive = (idx === 0 && scrollProgress < 0.28) ||
                                 (idx === 1 && scrollProgress >= 0.28 && scrollProgress < 0.62) ||
                                 (idx === 2 && scrollProgress >= 0.62);
                cap.classList.toggle("on", isActive);
            });

            // Calorie Total Pill Trigger
            const showTotal = scrollProgress > 0.65;
            el.heroTotalPill.classList.toggle("visible", showTotal);
        }
        window.addEventListener("scroll", updateScroll, { passive: true });
        updateScroll();

        // Render Loop
        const startTime = performance.now();
        const projVector = new THREE.Vector3();

        function renderLoop(now) {
            const elapsed = (now - startTime) / 1000;
            const hoverLerp = Math.min(1, Math.max(0, (elapsed - 0.8) / 2.0));
            // Exploded view eases smoothly with scroll progress
            const explodeLerp = Math.min(1, Math.max(0, (scrollProgress - 0.08) / 0.5));

            // Animate 3D Items
            items.forEach(item => {
                item.mesh.position.lerpVectors(item.basePos, item.hoverPos, hoverLerp).lerp(item.spreadPos, explodeLerp);
                item.mesh.position.y += Math.sin(elapsed * 1.5 + item.phase) * 0.04 * hoverLerp;
                item.mesh.rotation.x += item.rotSpeedX;
                item.mesh.rotation.y += item.rotSpeedY;
            });

            // Gentle Group & Bowl Sway
            group.rotation.y = Math.sin(elapsed * 0.3) * 0.15;
            bowl.rotation.y = elapsed * 0.08;

            renderer.render(scene, camera);

            // Project 3D Anchors to 2D Screen Labels
            for (let cIdx = 0; cIdx < CLUSTERS.length; cIdx++) {
                const anchor = CLUSTERS[cIdx].targetAnchor;
                projVector.set(anchor[0], anchor[1] - 0.45, 0).applyMatrix4(group.matrixWorld).project(camera);

                const label = labelElements[cIdx];
                if (label) {
                    const screenX = (projVector.x * 0.5 + 0.5) * window.innerWidth;
                    const screenY = (-projVector.y * 0.5 + 0.5) * window.innerHeight;
                    const opacity = Math.min(1, Math.max(0, (explodeLerp - 0.55) * 3.5));

                    label.style.opacity = opacity;
                    label.style.transform = `translate(${screenX}px, ${screenY}px) translate(-50%, 0)`;
                }
            }

            requestAnimationFrame(renderLoop);
        }

        requestAnimationFrame(renderLoop);
    }

    // =========================================================================
    // 9. INITIALIZATION
    // =========================================================================
    init3DExplodedBowl();
    initVault();
    initCustomizerControls();
    loadVaultDish(0); // Load Chicken Biryani by default

    console.log("NutriScore AI Vision v6.0 Active (Deep Solid Pastel & 3D Deconstruction Showcase).");
});
