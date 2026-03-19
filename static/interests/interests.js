document.addEventListener("DOMContentLoaded", function () {
    const interestItems = document.querySelectorAll(".interest-item");
    const saveButton = document.getElementById("save-button");

    let selectedInterests = [];

    // Interest selection logic
    interestItems.forEach(item => {
        item.addEventListener("click", function () {
            this.classList.toggle("selected");
            const interest = this.textContent;
            
            if (this.classList.contains("selected")) {
                selectedInterests.push(interest);
            } else {
                selectedInterests = selectedInterests.filter(i => i !== interest);
            }
        });
    });

    // Save Interests & Redirect
    saveButton.addEventListener("click", function () {
        if (selectedInterests.length === 0) {
            alert("Please select at least one interest.");
            return;
        }

        fetch("/interests", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: userEmail,  // You'll need to set this from your session
                interests: selectedInterests
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                window.location.href = "/new";  // Redirect to next page
            } else {
                alert("Error saving interests. Please try again.");
            }
        })
        .catch(error => {
            console.error("Error:", error);
            alert("An error occurred. Please try again.");
        });
    });
});
