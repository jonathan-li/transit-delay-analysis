import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="BART Delay Explorer", layout="wide")
st.title("🚇 BART Transit Delay Explorer")

# Find all available data files
files = sorted(glob.glob("data/raw/*.csv"), reverse=True)

if not files:
    st.warning("No data found. Run `python src/ingest.py` to fetch BART data.")
else:
    # Collect all station names from all CSVs
    all_data = []
    for f in files:
        df = pd.read_csv(f)
        all_data.append(df)
    data = pd.concat(all_data, ignore_index=True)

    # Let the user select a station
    stations = sorted(data["station"].unique())
    selected_station = st.selectbox("Select a station", stations)

    # Filter the data for that station
    station_data = data[data["station"] == selected_station]

    st.markdown(f"### Data for **{selected_station}**")
    st.dataframe(station_data)

    # Visualization: upcoming trains by destination
    st.markdown("#### Upcoming trains by destination")
    dest_counts = station_data["destination"].value_counts().reset_index()
    dest_counts.columns = ["destination", "count"]
    st.bar_chart(dest_counts.set_index("destination"))

    # Visualization: minutes until departure distribution
    st.markdown("#### Distribution of departure times (minutes)")
    # Convert "minutes" column (some values might be "Leaving")
    station_data = station_data[station_data["minutes"].apply(lambda x: str(x).isdigit())]
    station_data["minutes"] = station_data["minutes"].astype(int)

    if not station_data.empty:
        st.line_chart(station_data.set_index("fetched_at")["minutes"])
    else:
        st.info("No numeric departure data available to plot.")
