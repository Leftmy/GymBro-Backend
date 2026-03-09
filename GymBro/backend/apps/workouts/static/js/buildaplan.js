document.addEventListener('DOMContentLoaded', () => {
    const stepContainer = document.querySelector(".steps-container");
    const steps = document.querySelectorAll('.steps');
    
    const progress = document.querySelector(".progress");
    const StepIndicators = document.querySelectorAll('.progress-container li');

    const chooseRadio = document.getElementById("choose");
    const createRadio = document.getElementById("create");

    const workoutsBlock = document.getElementById("workouts-block");
    const exercisesBlock = document.getElementById("exercises-block");

    const prevButton = document.querySelector(".prev-btn");
    const nextButton = document.querySelector(".next-btn");
    const submitButton = document.querySelector(".submit-btn");
    document.documentElement.style.setProperty('--steps', StepIndicators.length);

    const muscleSelect = document.getElementById("muscle-select");
    const exerciseList = document.getElementById("exercise-list");

    muscleSelect.addEventListener("change", async () => {

        const muscle = muscleSelect.value;

        const response = await fetch(`/api/exercises/?muscle=${muscle}`);
        const data = await response.json();

        exerciseList.innerHTML = "";

        data.exercises.forEach(ex => {
            const label = document.createElement("label");

            label.innerHTML = `
                <input type="checkbox" name="exercises" value="${ex.id}">
                ${ex.name}
            `;

            exerciseList.appendChild(label);
        });
    });

    let currentStep = 0;

    const togglePlanType = () => {

    if (chooseRadio.checked) {

        workoutsBlock.style.display = "block";
        exercisesBlock.style.display = "none";

        document.querySelectorAll('input[name="exercises"]:checked')
            .forEach(el => el.checked = false);

    } else {

        workoutsBlock.style.display = "none";
        exercisesBlock.style.display = "block";

        const workout = document.querySelector('input[name="workoutPlan"]:checked');
        if (workout) workout.checked = false;
    }
};

    chooseRadio.addEventListener("change", togglePlanType);
    createRadio.addEventListener("change", togglePlanType);

    togglePlanType();

    const validateStep = () => {

    if (currentStep === 1) {

        const planType = document.querySelector('input[name="planType"]:checked')?.value;

        // якщо choose → треба workout
        if (planType === "choose") {
            const workout = document.querySelector('input[name="workoutPlan"]:checked');
            if (!workout) {
                alert("Please select a workout.");
                return false;
            }
        }

        // якщо create → треба хоча б один exercise
        if (planType === "create") {
            const exercises = document.querySelectorAll('input[name="exercises"]:checked');
            if (exercises.length === 0) {
                alert("Please select at least one exercise.");
                return false;
            }
        }
    }

    return true;
};

    const updateButtons = () => {
        prevButton.hidden = currentStep === 0;
        nextButton.hidden = currentStep >= StepIndicators.length - 1;
        submitButton.hidden = !nextButton.hidden;
    };

    const updateProgress = () => {
        let width = currentStep / (StepIndicators.length - 1);

        progress.style.transform = `scaleX(${width})`;

        stepContainer.style.height = `${steps[currentStep].offsetHeight}px`;

        StepIndicators.forEach((indicator, index) => {
            indicator.classList.toggle('current', currentStep === index);
            indicator.classList.toggle('done', currentStep > index)
        })

        steps.forEach((step, index) => {
            step.style.transform = `translateX(-${currentStep * 100}%)`;
            step.classList.toggle('current', currentStep === index);
        })
        updateButtons();
    }

    

    prevButton.addEventListener('click', (e) => {
        e.preventDefault();
        if (currentStep > 0) {
            currentStep--;
            updateProgress();
        }
    });
    nextButton.addEventListener('click', (e) => {
        e.preventDefault();
        if (!validateStep()) return;
        if (currentStep < StepIndicators.length - 1) {
            currentStep++;
            if (currentStep === 2) {
                generatePreview();
            }
            updateProgress();
        }
    });
    updateProgress();
    });

function generatePreview() {

    const preview = document.getElementById("plan-preview");
    preview.innerHTML = "";

    const planType = document.querySelector('input[name="planType"]:checked').value;

    if (planType === "choose") {

        const workout = document.querySelector('input[name="workoutPlan"]:checked');

        if (workout) {

            const name = workout.closest("label").textContent.trim();

            preview.innerHTML = `
                <p><strong>Selected plan:</strong> ${name}</p>
            `;
        }

    } else {

        const exercises = document.querySelectorAll('input[name="exercises"]:checked');

        if (exercises.length === 0) {
            preview.innerHTML = "<p>No exercises selected.</p>";
            return;
        }

        const list = document.createElement("ul");

        exercises.forEach(ex => {

            const label = ex.closest("label").textContent.trim();

            const li = document.createElement("li");
            li.textContent = label;

            list.appendChild(li);

        });

        preview.appendChild(list);
    }
}