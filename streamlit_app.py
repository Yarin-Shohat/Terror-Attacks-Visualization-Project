import streamlit as st
import pandas as pd
import math
from pathlib import Path
from st_pages import add_page_title, get_nav_from_toml


# Set the title and favicon that appear in the Browser's tab bar.
st.set_page_config(layout="wide")

nav = get_nav_from_toml("pages.toml")

pg = st.navigation(nav)

add_page_title(pg)

pg.run()
# -----------------------------------------------------------------------------

