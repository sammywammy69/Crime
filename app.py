import os
import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

# --- LOAD DATA ---
df = pd.read_csv("01_District_wise_crimes_committed_IPC_2001_2012.csv")
df.columns = df.columns.str.strip()

# FIX: Remove aggregated TOTAL rows to avoid double-counting
df = df[df["DISTRICT"].str.upper() != "TOTAL"]

# Crime columns to rank for Top 3
CRIME_COLS = [
    'MURDER', 'ATTEMPT TO MURDER', 'RAPE', 'KIDNAPPING & ABDUCTION',
    'DACOITY', 'ROBBERY', 'BURGLARY', 'THEFT', 'AUTO THEFT',
    'RIOTS', 'CRIMINAL BREACH OF TRUST', 'CHEATING',
    'ARSON', 'HURT/GREVIOUS HURT', 'CAUSING DEATH BY NEGLIGENCE'
]

WOMEN_HELPLINES = [
    "Women Helpline — 1091",
    "Domestic Abuse Helpline — 181",
    "NCW Helpline — 7827170170",
    "iCall (Mental Health) — 9152987821",
    "Vandrevala Foundation — 1860-2662-345",
    "Police Emergency — 100 / 112"
]

# --- GET STATE DATA ---
def get_state_data(state):
    state_df = df[df["STATE/UT"] == state]

    if state_df.empty:
        return {"crimes": ["No data available"], "women_stats": [], "helplines": WOMEN_HELPLINES}

    def s(col):
        return int(state_df[col].sum()) if col in state_df.columns else 0

    # Compute top 3 crimes
    crime_totals = {col: s(col) for col in CRIME_COLS if col in state_df.columns}
    top3 = sorted(crime_totals.items(), key=lambda x: x[1], reverse=True)[:3]
    crimes = [f"{name.title()}: {count:,}" for name, count in top3]

    # Women-specific stats
    women_stats = []
    for col in ['ASSAULT ON WOMEN WITH INTENT TO OUTRAGE HER MODESTY',
                'CRUELTY BY HUSBAND OR HIS RELATIVES',
                'DOWRY DEATHS', 'RAPE',
                'KIDNAPPING AND ABDUCTION OF WOMEN AND GIRLS']:
        val = s(col)
        if val > 0:
            women_stats.append(f"{col.title()}: {val:,}")

    return {
        "crimes": crimes,
        "women_stats": women_stats,
        "helplines": WOMEN_HELPLINES
    }

# --- HOME ROUTE ---
@app.route("/")
def home():
    state = "ANDHRA PRADESH"
    state_data = get_state_data(state)
    data = {
        "helplines": [
            "Police — 100",
            "Emergency — 112",
            "Cyber Crime — 1930",
            "Child Helpline — 1098"
        ],
        "crimes": state_data["crimes"],
        "women_stats": state_data["women_stats"],
        "women_helplines": state_data["helplines"]
    }
    return render_template("index.html", state=state, data=data)

@app.route("/map")
def map_page():
    return render_template("india_crime_map.html")

# --- STATE ROUTE ---
@app.route("/state/<state>")
def state_dashboard(state):
    state_data = get_state_data(state.upper())
    data = {
        "helplines": [
            "Police — 100",
            "Emergency — 112",
            "Cyber Crime — 1930",
            "Child Helpline — 1098"
        ],
        "crimes": state_data["crimes"],
        "women_stats": state_data["women_stats"],
        "women_helplines": state_data["helplines"]
    }
    return render_template("index.html", state=state.upper(), data=data)

# --- RUN ---
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
