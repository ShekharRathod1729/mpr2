function checkAnswer(button) {
    const correctOption = parseInt(button.getAttribute("data-correct"));
    const selectedOption = parseInt(button.value);

    if (selectedOption === correctOption) {
        button.classList.add("correct"); // Apply 'correct' style
    } else {
        button.classList.add("incorrect"); // Apply 'incorrect' style
    }

    // Disable all buttons after selection
    const allButtons = document.querySelectorAll(".option");
    allButtons.forEach(btn => btn.disabled = true);
}
