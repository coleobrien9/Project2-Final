import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NFL Offense Dashboard", layout="wide")

st.title("NFL Offensive Trends Dashboard")
st.write("This dashboard explores how NFL offense has changed over time.")

github_url = "https://raw.githubusercontent.com/coleobrien9/Project2/main/AlltimeOffense.csv"
df = pd.read_csv(github_url)

# Clean data
df = df.dropna(subset=["Year"])
df["Year"] = df["Year"].astype(int)

# Rename important columns
df = df.rename(columns={
    "PF": "Points Per Game",
    "Yds": "Total Yards Per Game",
    "Yds.1": "Passing Yards Per Game",
    "Yds.2": "Rushing Yards Per Game",
    "TO": "Turnovers Per Game",
    "Int": "Interceptions Per Game",
    "TD": "Passing TDs",
    "TD.1": "Rushing TDs",
    "Sc%": "Scoring Drive %",
    "TO%": "Turnover Drive %"
})

df = df.sort_values("Year")

st.sidebar.header("Dashboard Filters")

year_range = st.sidebar.slider(
    "Select Year Range",
    int(df["Year"].min()),
    int(df["Year"].max()),
    (2000, int(df["Year"].max()))
)

filtered_df = df[
    (df["Year"] >= year_range[0]) &
    (df["Year"] <= year_range[1])
]

metric = st.sidebar.selectbox(
    "Choose a Metric",
    [
        "Points Per Game",
        "Total Yards Per Game",
        "Passing Yards Per Game",
        "Rushing Yards Per Game",
        "Turnovers Per Game",
        "Interceptions Per Game",
        "Scoring Drive %",
        "Turnover Drive %"
    ]
)

latest_year = filtered_df["Year"].max()
latest = filtered_df[filtered_df["Year"] == latest_year].iloc[0]

col1, col2, col3, col4 = st.columns(4)

col1.metric("Latest Year", int(latest["Year"]))
col2.metric("Points/Game", round(latest["Points Per Game"], 1))
col3.metric("Total Yards/Game", round(latest["Total Yards Per Game"], 1))
col4.metric("Turnovers/Game", round(latest["Turnovers Per Game"], 1))

st.subheader(f"{metric} Over Time")

fig = px.line(
    filtered_df,
    x="Year",
    y=metric,
    markers=True,
    title=f"{metric} from {year_range[0]} to {year_range[1]}"
)

st.plotly_chart(fig, use_container_width=True)



st.subheader("Passing Yards vs. Rushing Yards")

compare_df = filtered_df[
    ["Year", "Passing Yards Per Game", "Rushing Yards Per Game"]
]

compare_long = compare_df.melt(
    id_vars="Year",
    var_name="Category",
    value_name="Yards Per Game"
)

fig2 = px.line(
    compare_long,
    x="Year",
    y="Yards Per Game",
    color="Category",
    markers=True,
    title="Passing vs. Rushing Yards Per Game"
)

st.plotly_chart(fig2, use_container_width=True)

st.subheader("Data Table")
st.dataframe(filtered_df)

##----------------------------------------------------


st.subheader("NFL Team Stats Choropleth Map")

team_stats = pd.read_csv("https://raw.githubusercontent.com/coleobrien9/Project2/refs/heads/main/sportsref_download.csv")


# Clean column names
team_stats.columns = team_stats.columns.astype(str).str.strip()

# Team-to-state mapping
team_to_state = {
    "Arizona Cardinals": "AZ",
    "Atlanta Falcons": "GA",
    "Baltimore Ravens": "MD",
    "Buffalo Bills": "NY",
    "Carolina Panthers": "NC",
    "Chicago Bears": "IL",
    "Cincinnati Bengals": "OH",
    "Cleveland Browns": "OH",
    "Dallas Cowboys": "TX",
    "Denver Broncos": "CO",
    "Detroit Lions": "MI",
    "Green Bay Packers": "WI",
    "Houston Texans": "TX",
    "Indianapolis Colts": "IN",
    "Jacksonville Jaguars": "FL",
    "Kansas City Chiefs": "MO",
    "Las Vegas Raiders": "NV",
    "Los Angeles Chargers": "CA",
    "Los Angeles Rams": "CA",
    "Miami Dolphins": "FL",
    "Minnesota Vikings": "MN",
    "New England Patriots": "MA",
    "New Orleans Saints": "LA",
    "New York Giants": "NJ",
    "New York Jets": "NJ",
    "Philadelphia Eagles": "PA",
    "Pittsburgh Steelers": "PA",
    "San Francisco 49ers": "CA",
    "Seattle Seahawks": "WA",
    "Tampa Bay Buccaneers": "FL",
    "Tennessee Titans": "TN",
    "Washington Commanders": "MD"
}


team_stats = team_stats[team_stats["Tm"].isin(team_to_state.keys())].copy()

# Add State column
team_stats["State"] = team_stats["Tm"].map(team_to_state)

# Available stat categories
map_options = ["Yds", "TD", "Y/G", "Rate", "Cmp%", "Int", "Sk", "ANY/A", "EXP"]


map_options = [col for col in map_options if col in team_stats.columns]

map_metric = st.sidebar.selectbox(
    "Choose Choropleth Stat",
    map_options
)

# Make selected metric numeric
team_stats[map_metric] = pd.to_numeric(team_stats[map_metric], errors="coerce")

# Average teams by state
state_df = team_stats.groupby("State", as_index=False)[map_metric].mean()

# Build choropleth
fig_choro = px.choropleth(
    state_df,
    locations="State",
    locationmode="USA-states",
    color=map_metric,
    scope="usa",
    color_continuous_scale="Blues",
    title=f"Average NFL Team {map_metric} by State"
)

st.plotly_chart(fig_choro, use_container_width=True)

st.write("Note: States with multiple NFL teams use the average value for the selected statistic.")
