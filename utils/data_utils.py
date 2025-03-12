import pandas as pd
from utils.crime_data_fetch import FROM_PRETTY_CATEGORIES
import streamlit as st

def add_pills_filter_df(df=pd.DataFrame()):
    pretty_selection = st.pills("Crime Category", FROM_PRETTY_CATEGORIES.keys(), selection_mode="multi", default=FROM_PRETTY_CATEGORIES.keys())
    selection = [FROM_PRETTY_CATEGORIES[cat] for cat in pretty_selection]
    if df.shape[0] != 0:
        filtered_df = df[df['category'].isin(selection)].copy()
        return filtered_df
    else:
        return df.copy()