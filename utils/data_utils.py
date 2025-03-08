import pandas as pd
from utils.crime_data_fetch import CATEGORIES
import streamlit as st

def add_pills_filter_df(df=pd.DataFrame()):
    selection = st.pills("Crime Category", CATEGORIES, selection_mode="multi", default=CATEGORIES)
    if df.shape[0] != 0:
        filtered_df = df[df['category'].isin(selection)].copy()
        return filtered_df
    else:
        return df.copy()