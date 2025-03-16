from flask import Flask, request, jsonify, render_template
import numpy as np
import pandas as pd
import pickle
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend-backend communication

# Load the matches dataset
matches = pd.read_csv(r'C:\Users\prasa\OneDrive\Desktop\IPL PRED\Backend\matches.csv')

# Team name mapping (old names to 2019 names)
team_name_mapping = {
    'Deccan Chargers': 'Sunrisers Hyderabad',
    'Delhi Daredevils': 'Delhi Capitals',
    'Gujarat Lions': 'Gujarat Titans',
    'Kings XI Punjab': 'Punjab Kings',
    'Pune Warriors': 'None',
    'Rising Pune Supergiant': 'None'
}

# Replace old team names with 2019 names
for old_name, new_name in team_name_mapping.items():
    if new_name != 'None':
        matches.replace(old_name, new_name, inplace=True)

# Remove unwanted teams
teams_to_remove = ['Kochi Tuskers Kerala', 'Rising Pune Supergiants', 'Pune Warriors', 'Rising Pune Supergiant']
matches = matches[~matches[['team1', 'team2', 'toss_winner', 'winner']].isin(teams_to_remove).any(axis=1)]

# Feature Engineering
matches['team1_home'] = (matches['team1'] == matches['venue']).astype(int)
matches['team2_home'] = (matches['team2'] == matches['venue']).astype(int)

# Feature Selection
X = matches[['team1', 'team2', 'toss_winner', 'toss_decision', 'venue', 'team1_home', 'team2_home']].copy()
y = matches['winner'].copy()

# Handle Missing Values
X.fillna(X.mode().iloc[0], inplace=True)
y.fillna(y.mode()[0], inplace=True)

# Load the trained model
MODEL_PATH = r"C:\Users\prasa\OneDrive\Desktop\IPL PRED\Backend\ipl_winner_model.pkl"
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)

# IPL Teams Short Names Mapping
TEAM_SHORTNAMES = {
    "CSK": "Chennai Super Kings",
    "DC": "Delhi Capitals",
    "GT": "Gujarat Titans",
    "KKR": "Kolkata Knight Riders",
    "LSG": "Lucknow Super Giants",
    "MI": "Mumbai Indians",
    "PBKS": "Punjab Kings",
    "RR": "Rajasthan Royals",
    "RCB": "Royal Challengers Bangalore",
    "SRH": "Sunrisers Hyderabad"
}

# Available Venues
IPL_VENUES = sorted(matches['venue'].unique().tolist())

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.form
        print("Received Data:", data)  # Debugging

        team1 = TEAM_SHORTNAMES.get(data['team1'].upper(), data['team1'].title())
        team2 = TEAM_SHORTNAMES.get(data['team2'].upper(), data['team2'].title())
        toss_winner = TEAM_SHORTNAMES.get(data['toss_winner'].upper(), data['toss_winner'].title())
        toss_decision = data['toss_decision'].lower()
        venue = data['venue'].title()

        print(f"Processed Input: {team1}, {team2}, {toss_winner}, {toss_decision}, {venue}")

        if team1 not in TEAM_SHORTNAMES.values() or team2 not in TEAM_SHORTNAMES.values() or toss_winner not in TEAM_SHORTNAMES.values():
            return jsonify({"error": "Invalid team name"}), 400
        if toss_decision not in ["bat", "field"]:
            return jsonify({"error": "Invalid toss decision"}), 400
        if venue not in IPL_VENUES:
            return jsonify({"error": "Invalid venue"}), 400

        input_data = pd.DataFrame([[team1, team2, toss_winner, toss_decision, venue,
                                     int(team1 == venue), int(team2 == venue)]],
                                  columns=['team1', 'team2', 'toss_winner', 'toss_decision', 'venue',
                                           'team1_home', 'team2_home'])

        print("Input Data for Model:", input_data)  # Debugging

        prediction = model.predict(input_data)[0]
        print("Prediction:", prediction)  # Debugging

        return jsonify({"predicted_winner": prediction})

    except Exception as e:
        print("Error Occurred:", str(e))  # Debugging
        return jsonify({"error": str(e)}), 500

@app.route("/teams", methods=["GET"])
def get_teams():
    return jsonify({"teams": TEAM_SHORTNAMES})

@app.route("/venues", methods=["GET"])
def get_venues():
    return jsonify({"venues": IPL_VENUES})

if __name__ == "__main__":
    app.run(debug=True)
