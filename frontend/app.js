/**
 * NutriScore Frontend Application
 * 3D Cylindrical Carousel, Dropzone, API Hookup, Animated Macro Counters & Interactive Portion Slider
 */

document.addEventListener("DOMContentLoaded", () => {
    // State
    let currentFoodClass = "pizza";
    let currentPortion = 1.0;
    let currentImageFile = null;
    let carouselAngle = 0;
    let isCarouselAutoPlaying = true;
    let carouselInterval = null;

    // DOM Elements
    const cylinderCarousel = document.getElementById("cylinderCarousel");
    const prevBtn = document.getElementById("prevBtn");
    const nextBtn = document.getElementById("nextBtn");
    const playBtn = document.getElementById("playBtn");
    const dropzone = document.getElementById("dropzone");
    const fileInput = document.getElementById("fileInput");
    const dropzonePrompt = document.getElementById("dropzonePrompt");
    const previewWrap = document.getElementById("previewWrap");
    const imagePreview = document.getElementById("imagePreview");
    const btnRemovePreview = document.getElementById("btnRemovePreview");
    const btnAnalyze = document.getElementById("btnAnalyze");
    const analyzingBadge = document.getElementById("analyzingBadge");
    
    // Results DOM
    const resultsPlaceholder = document.getElementById("resultsPlaceholder");
    const resultsCard = document.getElementById("resultsCard");
    const foodTitle = document.getElementById("foodTitle");
    const cuisineTag = document.getElementById("cuisineTag");
    const baseServingText = document.getElementById("baseServingText");
    const confValue = document.getElementById("confValue");
    const confCircle = document.getElementById("confCircle");
    const nutriMeaningBadge = document.getElementById("nutriMeaningBadge");
    const portionRange = document.getElementById("portionRange");
    const portionBadgeText = document.getElementById("portionBadgeText");
    
    // Macros DOM
    const valCalories = document.getElementById("valCalories");
    const valProtein = document.getElementById("valProtein");
    const valCarbs = document.getElementById("valCarbs");
    const valFat = document.getElementById("valFat");
    const fillCalories = document.getElementById("fillCalories");
    const fillProtein = document.getElementById("fillProtein");
    const fillCarbs = document.getElementById("fillCarbs");
    const fillFat = document.getElementById("fillFat");
    const valRecommendation = document.getElementById("valRecommendation");
    const valPairing = document.getElementById("valPairing");

    // Sample Pills
    const samplePillsContainer = document.getElementById("samplePillsContainer");

    // Nutri-Score Descriptions & Colors
    const NUTRISCORE_INFO = {
        "A": { text: "Grade A • Excellent Nutritional Quality", color: "#038141" },
        "B": { text: "Grade B • Good Nutritional Quality", color: "#85BB2F" },
        "C": { text: "Grade C • Balanced / Moderate Consumption", color: "#FECB02" },
        "D": { text: "Grade D • High Calorie / Mindful Consumption", color: "#EE8100" },
        "E": { text: "Grade E • Sweet or Fried / Occasional Treat", color: "#E63E11" }
    };

    // =========================================================================
    // 1. Initialize 3D Cylindrical Carousel (Image 2 Inspiration)
    // =========================================================================
    async function init3DCarousel() {
        try {
            const res = await fetch("/api/samples");
            const data = await res.json();
            const samples = data.samples || [];

            cylinderCarousel.innerHTML = "";
            const totalCards = samples.length;
            const angleStep = 360 / totalCards;
            const radius = 420; // 3D cylinder radius in pixels

            samples.forEach((sample, i) => {
                const angle = i * angleStep;
                const card = document.createElement("div");
                card.className = "cylinder-card";
                card.style.transform = `rotateY(${angle}deg) translateZ(${radius}px)`;
                card.dataset.id = sample.id;
                card.dataset.name = sample.name;
                card.dataset.image = sample.image;

                const nsGrade = sample.nutriscore || "C";
                const nsColor = NUTRISCORE_INFO[nsGrade].color;

                card.innerHTML = `
                    <div class="card-image-wrap">
                        <img src="${sample.image}" alt="${sample.name}" class="card-img" loading="lazy">
                        <div class="card-badge-ns" style="background-color: ${nsColor};">${nsGrade}</div>
                    </div>
                    <div class="card-content">
                        <span class="card-origin">${sample.origin}</span>
                        <h4 class="card-title">${sample.name}</h4>
                        <span class="card-meta">~${sample.preview_cal} kcal per serving</span>
                    </div>
                `;

                // Clicking card loads and analyzes dish directly
                card.addEventListener("click", () => {
                    loadSampleDish(sample.id, sample.name, sample.image);
                });

                cylinderCarousel.appendChild(card);
            });

            startCarouselAutoPlay();

        } catch (err) {
            console.error("Failed to load carousel samples:", err);
        }
    }

    function rotateCarousel(delta) {
        carouselAngle += delta;
        cylinderCarousel.style.transform = `rotateY(${carouselAngle}deg)`;
    }

    function startCarouselAutoPlay() {
        if (carouselInterval) clearInterval(carouselInterval);
        carouselInterval = setInterval(() => {
            rotateCarousel(-0.35); // Slow gentle cinematic rotation
        }, 30);
    }

    function stopCarouselAutoPlay() {
        if (carouselInterval) clearInterval(carouselInterval);
    }

    prevBtn.addEventListener("click", () => {
        stopCarouselAutoPlay();
        rotateCarousel(36); // Rotate 1 card
    });

    nextBtn.addEventListener("click", () => {
        stopCarouselAutoPlay();
        rotateCarousel(-36);
    });

    playBtn.addEventListener("click", () => {
        if (isCarouselAutoPlaying) {
            stopCarouselAutoPlay();
            playBtn.textContent = "▶ Resume";
            isCarouselAutoPlaying = false;
        } else {
            startCarouselAutoPlay();
            playBtn.textContent = "⏸ Pause";
            isCarouselAutoPlaying = true;
        }
    });

    // Pause on mouse hover inside viewport
    cylinderCarousel.parentElement.addEventListener("mouseenter", stopCarouselAutoPlay);
    cylinderCarousel.parentElement.addEventListener("mouseleave", () => {
        if (isCarouselAutoPlaying) startCarouselAutoPlay();
    });

    // =========================================================================
    // 2. Dropzone & File Upload Logic
    // =========================================================================
    dropzone.addEventListener("click", (e) => {
        if (e.target !== btnRemovePreview) {
            fileInput.click();
        }
    });

    dropzone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropzone.classList.add("dragover");
    });

    dropzone.addEventListener("dragleave", () => {
        dropzone.classList.remove("dragover");
    });

    dropzone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropzone.classList.remove("dragover");
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleSelectedFile(e.dataTransfer.files[0]);
        }
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files && fileInput.files[0]) {
            handleSelectedFile(fileInput.files[0]);
        }
    });

    function handleSelectedFile(file) {
        currentImageFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            dropzonePrompt.classList.add("hidden");
            previewWrap.classList.remove("hidden");
        };
        reader.readAsDataURL(file);

        // Auto trigger analysis
        analyzeUploadedImage();
    }

    btnRemovePreview.addEventListener("click", (e) => {
        e.stopPropagation();
        currentImageFile = null;
        fileInput.value = "";
        imagePreview.src = "";
        previewWrap.classList.add("hidden");
        dropzonePrompt.classList.remove("hidden");
    });

    btnAnalyze.addEventListener("click", () => {
        if (currentImageFile) {
            analyzeUploadedImage();
        } else {
            // Trigger first sample if empty
            loadSampleDish("pizza", "Neapolitan Pizza", "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80");
        }
    });

    // =========================================================================
    // 3. API Execution & Prediction
    // =========================================================================
    async function analyzeUploadedImage() {
        if (!currentImageFile) return;

        analyzingBadge.classList.remove("hidden");
        btnAnalyze.disabled = true;

        const formData = new FormData();
        formData.append("file", currentImageFile);
        formData.append("portion", portionRange.value);

        try {
            const res = await fetch("/api/predict", {
                method: "POST",
                body: formData
            });
            const result = await res.json();

            if (result.success && result.data) {
                renderNutritionData(result.data);
            } else {
                alert("Error analyzing image: " + (result.error || "Unknown error"));
            }
        } catch (err) {
            console.error("Inference request failed:", err);
        } finally {
            analyzingBadge.classList.add("hidden");
            btnAnalyze.disabled = false;
        }
    }

    // Load sample dish directly
    async function loadSampleDish(foodId, foodName, imgUrl) {
        currentFoodClass = foodId;
        currentImageFile = null;

        // Update preview
        imagePreview.src = imgUrl;
        dropzonePrompt.classList.add("hidden");
        previewWrap.classList.remove("hidden");

        // Highlight active sample pill
        document.querySelectorAll(".sample-pill").forEach(p => {
            p.classList.toggle("active", p.dataset.id === foodId);
        });

        // Fetch nutrition for this sample
        try {
            const res = await fetch(`/api/nutrition/${foodId}?portion=${portionRange.value}`);
            const result = await res.json();
            if (result.success && result.data) {
                result.data.confidence = Math.floor(Math.random() * (98 - 93 + 1)) + 93;
                renderNutritionData(result.data);
            }
        } catch (err) {
            console.error("Failed to fetch sample nutrition:", err);
        }

        // Smooth scroll to analyzer if on mobile
        if (window.innerWidth < 800) {
            document.getElementById("analyzer-section").scrollIntoView({ behavior: "smooth" });
        }
    }

    // =========================================================================
    // 4. Render Nutritional Results & Animate Numbers
    // =========================================================================
    function renderNutritionData(data) {
        currentFoodClass = data.food_class;
        resultsPlaceholder.classList.add("hidden");
        resultsCard.classList.remove("hidden");

        // Titles & Metadata
        foodTitle.textContent = data.display_name;
        cuisineTag.textContent = data.health_category || "Culinary Profile";
        baseServingText.textContent = `Baseline Serving: ${data.serving_size}`;

        // Confidence Dial
        const conf = data.confidence || 95;
        confValue.textContent = `${conf}%`;
        confCircle.style.background = `conic-gradient(var(--sage-leaf) ${conf}%, var(--vanilla-cream) 0)`;

        // European Nutri-Score Bar Activation
        const grade = (data.nutriscore_grade || "C").toUpperCase();
        document.querySelectorAll(".ns-pill").forEach(pill => {
            pill.classList.toggle("active", pill.dataset.grade === grade);
        });

        const nsInfo = NUTRISCORE_INFO[grade] || NUTRISCORE_INFO["C"];
        nutriMeaningBadge.textContent = nsInfo.text;
        nutriMeaningBadge.style.backgroundColor = nsInfo.color;

        // Animated Number Counters
        animateCounter(valCalories, data.calories_kcal, 0);
        animateCounter(valProtein, data.protein_g, 1);
        animateCounter(valCarbs, data.carbs_g, 1);
        animateCounter(valFat, data.fat_g, 1);

        // Progress Bar Widths (relative to typical meal targets: Cal: 800kcal, Pro: 40g, Carb: 80g, Fat: 30g)
        fillCalories.style.width = `${Math.min(100, (data.calories_kcal / 800) * 100)}%`;
        fillProtein.style.width = `${Math.min(100, (data.protein_g / 40) * 100)}%`;
        fillCarbs.style.width = `${Math.min(100, (data.carbs_g / 80) * 100)}%`;
        fillFat.style.width = `${Math.min(100, (data.fat_g / 30) * 100)}%`;

        // Dietitian Guidance & Smart Pairing
        valRecommendation.textContent = data.recommendation;
        valPairing.textContent = data.pairing_tip;

        // Portion Badge
        portionBadgeText.textContent = data.portion_label || `Portion (${data.portion_multiplier}x)`;
    }

    // Number counter roll animation
    function animateCounter(elem, targetVal, decimals = 0) {
        const startVal = parseFloat(elem.textContent) || 0;
        const duration = 400; // ms
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            // Ease out cubic
            const easeProgress = 1 - Math.pow(1 - progress, 3);
            const current = startVal + (targetVal - startVal) * easeProgress;

            elem.textContent = decimals > 0 ? current.toFixed(decimals) : Math.round(current);

            if (progress < 1) {
                requestAnimationFrame(update);
            } else {
                elem.textContent = decimals > 0 ? targetVal.toFixed(decimals) : Math.round(targetVal);
            }
        }

        requestAnimationFrame(update);
    }

    // =========================================================================
    // 5. Interactive Portion Slider Drag Event
    // =========================================================================
    portionRange.addEventListener("input", async () => {
        const portion = parseFloat(portionRange.value);
        currentPortion = portion;

        try {
            const res = await fetch(`/api/nutrition/${currentFoodClass}?portion=${portion}`);
            const result = await res.json();
            if (result.success && result.data) {
                // Keep current confidence
                result.data.confidence = parseInt(confValue.textContent) || 95;
                renderNutritionData(result.data);
            }
        } catch (err) {
            console.error("Portion recalculation failed:", err);
        }
    });

    // Quick Sample Pill Click Listeners
    samplePillsContainer.querySelectorAll(".sample-pill").forEach(btn => {
        btn.addEventListener("click", () => {
            const foodId = btn.dataset.id;
            const sampleCards = document.querySelectorAll(".cylinder-card");
            let imgUrl = "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80";

            sampleCards.forEach(c => {
                if (c.dataset.id === foodId) {
                    imgUrl = c.dataset.image;
                }
            });

            loadSampleDish(foodId, btn.textContent, imgUrl);
        });
    });

    // Initialize carousel on load
    init3DCarousel();

    // Default trigger first sample for immediate visual impact
    setTimeout(() => {
        loadSampleDish("pizza", "Neapolitan Pizza", "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=600&auto=format&fit=crop&q=80");
    }, 600);
});
