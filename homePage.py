import streamlit as st
import pandas as pd
import math
from pathlib import Path
from st_pages import add_page_title, get_nav_from_toml

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            div.stHeading {display: none;}
            .css-18e3th9 {padding-top: 0rem;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Draw the actual page


# Set the title that appears at the top of the page.
st.markdown(
    '''
    # :boom: Terror Attacks Visualization Project
    <div style="text-align: right; direction: rtl;">

    בחרנו לעבד, לנתח ולהציג נתונים אודות אירועי טרור בישראל לאורך השנים, מתוך מאגר הנתונים Global Terrorism Database (GTD).
    </div>
    ''',
    unsafe_allow_html=True
)

# Add some spacing
''
''

