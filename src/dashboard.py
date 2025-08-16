import streamlit as st
import pandas as pd
import glob
import os

st.set_page_config(page_title="BART Delay Explorer", layout="wide")
st.title("BART Transit Delay Explorer")
st.markdown("### Latest fetched ETD data")

files = sorted(glob.glob("data/raw/*.csv"), reverse=True)
if not files:
    st.warning("No data found. Run `python src/ingest.py` to fetch BART data.")
else:
    latest = files[0]
    df = pd.read_csv(latest)
    st.write(f"Showing data from: **{os.path.basename(latest)}**")
    st.dataframe(df)

    st.markdown("#### Upcoming trains by destination")
    dest_counts = df["destination"].value_counts().reset_index()
    dest_counts.columns = ["destination", "count"]
    st.bar_chart(dest_counts.set_index("destination"))
