const imageButtons = document.querySelectorAll('.image-button');
const progress = document.getElementById('progress');
const formSteps = document.querySelectorAll('.form-step');
const nextBtns = document.querySelectorAll('.next-btn');
const prevBtns = document.querySelectorAll('.prev-btn');
const submitBtn = document.querySelector('.submit');

let currentStep = 0;

showStep(currentStep);

nextBtns.forEach(button => {
    button.addEventListener('click', () => {
        if (validateStep(currentStep)) {
            if (currentStep < formSteps.length - 1) {
                currentStep++;
                showStep(currentStep);
            }
        } else {
            alert("Please fill out all required fields.");
        }
    });
});

prevBtns.forEach(button => {
    button.addEventListener('click', () => {
        if (currentStep > 0) {
            currentStep--;
            showStep(currentStep);
        }
    });
});

function showStep(step) {
    formSteps.forEach((formStep, index) => {
        formStep.style.display = index === step ? 'block' : 'none';
    });

    const progressPercent = ((step + 1) / formSteps.length) * 100;
    progress.style.width = `${progressPercent}%`;

    submitBtn.style.display = step === formSteps.length - 1 ? 'block' : 'none';
}

function validateStep(step) {
    if (step === 0) {
        const nameInput = document.getElementById('name');
        return nameInput.value.length >= 2;
    }
    if (step === 1) {
        const checkedColors = document.querySelectorAll('input[name="image[]"]:checked');
        return checkedColors.length > 0;
    }
    return true;
}

imageButtons.forEach(button => {
    button.addEventListener('click', () => {
        button.classList.toggle('clicked');
    });
});

// Modified the submit button event listener to ensure proper form submission
document.getElementById('starmateForm').addEventListener('submit', function(event) {
    event.preventDefault();

    if (!validateStep(currentStep)) {
        alert("Please complete all required fields before submitting.");
        return;
    }

    const name = document.getElementById('name').value;

    const red = document.getElementById('red').checked;
    const orange = document.getElementById('orange').checked;
    const yellow = document.getElementById('yellow').checked;
    const green = document.getElementById('green').checked;
    const blue = document.getElementById('blue').checked;
    const violet = document.getElementById('violet').checked;

    const vastness = document.getElementById('preference1').checked;
    const distance = document.getElementById('preference2').checked;
    const vibrance = document.getElementById('preference3').checked;


    const formData = {
        name,
        red,
        orange,
        yellow,
        green,
        blue,
        violet,
        vastness,
        distance,
        vibrance
    };

    // Send data to the server
    fetch('https://starmate.earth/get_image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data && typeof data === 'object' && data.image) {
            localStorage.setItem('selectedImage', JSON.stringify(data.image));
            window.location.href = 'results.html';
        } else {
            alert("No suitable images found.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('There was an error submitting the form. Please try again later.');
    });
});
