const BASE_URL = "http://127.0.0.1:5000"; // Flask backend URL

// Function to fetch IPL teams and venues dynamically
async function fetchTeamsAndVenues() {
    try {
        // Fetch IPL Teams
        const teamsResponse = await fetch(`${BASE_URL}/teams`);
        const teamsData = await teamsResponse.json();

        // Fetch IPL Venues
        const venuesResponse = await fetch(`${BASE_URL}/venues`);
        const venuesData = await venuesResponse.json();

        // Populate team dropdowns
        const teamSelects = ["team1", "team2", "toss_winner"];
        teamSelects.forEach(id => {
            const select = document.getElementById(id);
            select.innerHTML = '<option value="">Select Team</option>'; // Reset dropdown
            Object.values(teamsData.teams).forEach(team => {
                let option = new Option(team, team);
                select.add(option);
            });
        });

        // Populate venues dropdown
        const venueSelect = document.getElementById("venue");
        venueSelect.innerHTML = '<option value="">Select Stadium</option>'; // Reset dropdown
        venuesData.venues.forEach(venue => {
            let option = new Option(venue, venue);
            venueSelect.add(option);
        });

    } catch (error) {
        console.error("Error fetching teams and venues:", error);
    }
}

// Fetch teams and venues when the page loads
document.addEventListener("DOMContentLoaded", fetchTeamsAndVenues);

// Handle form submission (send data to Flask for prediction)
document.getElementById("predictForm").addEventListener("submit", async function(event) {
    event.preventDefault(); // Prevent default form submission

    // Collect form data
    const formData = new FormData();
    formData.append("team1", document.getElementById("team1").value);
    formData.append("team2", document.getElementById("team2").value);
    formData.append("toss_winner", document.getElementById("toss_winner").value);
    formData.append("toss_decision", document.getElementById("toss_decision").value);
    formData.append("venue", document.getElementById("venue").value);

    // Ensure all fields are selected before sending the request
    if ([...formData.values()].includes("")) {
        document.getElementById("predictionResult").innerText = "⚠️ Please select all fields before predicting!";
        return;
    }

    try {
        // Send request to Flask backend
        const response = await fetch(`${BASE_URL}/predict`, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        // Display prediction result or error message
        if (response.ok) {
            document.getElementById("predictionResult").innerText = `🏆 Predicted Winner: ${data.predicted_winner}`;
        } else {
            document.getElementById("predictionResult").innerText = `❌ Error: ${data.error}`;
        }

    } catch (error) {
        console.error("Prediction error:", error);
        document.getElementById("predictionResult").innerText = "❌ Error making prediction!";
    }
});
