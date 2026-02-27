document.addEventListener('DOMContentLoaded', () => {
    const stepContainer = document.querySelector(".steps-container");
    const steps = document.querySelectorAll('.steps');
    
    const progress = document.querySelector(".progress");
    const StepIndicators = document.querySelectorAll('.progress-container li');

    const prevButton = document.querySelector(".prev-btn");
    const nextButton = document.querySelector(".next-btn");
    const submitButton = document.querySelector(".submit-btn");
    document.documentElement.style.setProperty('--steps', StepIndicators.length);

    let currentStep = 0;

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
        if (currentStep < StepIndicators.length - 1) {
            currentStep++;
            updateProgress();
        }
    });
    updateProgress();
});