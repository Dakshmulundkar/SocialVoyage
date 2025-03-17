document.getElementById("search").addEventListener("input", function () {
    let query = this.value.toLowerCase();
    let plans = document.querySelectorAll(".plan-card p");
    
    plans.forEach(plan => {
        let text = plan.textContent.toLowerCase();
        if (text.includes(query)) {
            plan.parentElement.style.display = "block";
        } else {
            plan.parentElement.style.display = "none";
        }
    });
});

function openCreatePlan() {
    alert("Create Plan feature coming soon!");
}
