import streamlit as st
import pandas as pd
import glob

st.set_page_config(page_title="BART Delay Explorer", layout="wide")
st.title("🚇 BART Transit Delay Explorer")

# Find all available data files
files = sorted(glob.glob("data/raw/*.csv"), reverse=True)

if not files:
    st.warning("No data found. Run `python src/ingest.py` to fetch BART data.")
else:
    # Load and concatenate all CSVs
    all_data = []
    for f in files:
        df = pd.read_csv(f)
        all_data.append(df)
    data = pd.concat(all_data, ignore_index=True)

    # Clean data
    data["min_till_arrival"] = data["min_till_arrival"].replace("Leaving", 0).astype(int)
    data["fetched_at"] = pd.to_datetime(data["fetched_at"])

    # Let the user select a station
    stations = sorted(data["station"].unique())
    selected_station = st.selectbox("Select a station", stations)

    # Filter the data for that station
    station_data = data[data["station"] == selected_station]

    st.markdown(f"### Data for **{selected_station}**")
    st.dataframe(station_data)

    # --- Average wait time over time ---
    st.markdown("#### Average wait time over time")
    avg_wait = station_data.groupby(pd.Grouper(key="fetched_at", freq="5T"))["min_till_arrival"].mean()
    st.line_chart(avg_wait)

    # --- Top destinations by average wait ---
    st.markdown("#### Top destinations by average wait time")
    dest_avg = station_data.groupby("destination")["min_till_arrival"].mean().sort_values(ascending=False)
    st.bar_chart(dest_avg)

    # --- Distribution of wait times ---
    st.markdown("#### Distribution of wait times")
    wait_counts = station_data["min_till_arrival"].value_counts().sort_index()
    st.bar_chart(wait_counts)

    # --- Upcoming trains by destination ---
    st.markdown("#### Upcoming trains by destination (count)")
    dest_counts = station_data["destination"].value_counts().reset_index()
    dest_counts.columns = ["destination", "count"]
    st.bar_chart(dest_counts.set_index("destination"))
