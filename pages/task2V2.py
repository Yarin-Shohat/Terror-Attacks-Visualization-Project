import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path


# -----------------------------------------------------------------------------

st.markdown(
    '''
    <div style="text-align: right; direction: rtl;font-size: large;">
    בעמוד זה נענה על המטלה הבאה:
    <br>
    <b>קורלציה בין מספר המחבלים למספר הנפגעים: האם קיים קשר בין כמות המחבלים באירוע לכמות הנפגעים?</b>
    </div>
    ''',
    unsafe_allow_html=True
)

@st.cache_data
def get_data():
    """
    Read the Terror Attacks data from the CSV file.
    """
    # Instead of a CSV on disk, you could read from an HTTP endpoint here too.
    DATA_FILENAME = Path(__file__).parent.parent / 'data/IL_data.csv'
    df = pd.read_csv(DATA_FILENAME, encoding='ISO-8859-1')
    columns_names = ["eventid","iyear","imonth","iday","country","city","latitude","longitude","nperps","nkill","nwound",
        "location","success","attacktype1","suicide","targtype1","weaptype1_txt","gname","extended"]

    df = df[columns_names]

    return df

df = get_data()

# Create column selection
col1, col2 = st.columns(2)
with col1:
    x_column = st.selectbox('Select X-axis', ['nperps', 'nkill', 'nwound'], index=0)
with col2:
    y_column = st.selectbox('Select Y-axis', ['nperps', 'nkill', 'nwound'], index=1)

# Create scatter plot
fig = px.scatter(
    df,
    x=x_column,
    y=y_column,
    title=f'Correlation between {x_column} and {y_column}',
    labels={
        'nperps': 'Number of Perpetrators',
        'nkill': 'Number of Kills',
        'nwound': 'Number of Wounded'
    },
    hover_data=['iyear', 'city', 'location']  # Show these additional columns on hover
)

# Update layout
fig.update_layout(
    title_x=0.5,  # Center the title
    height=600,    # Set height
    width=800     # Set width
)

# Add correlation coefficient
correlation = df[x_column].corr(df[y_column])
st.metric('Correlation Coefficient', f'{correlation:.3f}')

# Display plot
st.plotly_chart(fig, use_container_width=True)

# Add explanation in Hebrew
st.markdown(
    '''
    <div style="text-align: right; direction: rtl;">
    <h3>ניתוח הקשר:</h3>
    <p>
    הגרף מציג את הקשר בין מספר המחבלים לבין מספר הנפגעים בכל פיגוע.
    ניתן לבחור את המשתנים להצגה בצירי X ו-Y כדי לבחון קשרים שונים.
    מקדם המתאם (Correlation Coefficient) מציג את עוצמת הקשר בין המשתנים, כאשר:
    <ul>
        <li>1 מייצג קשר חיובי מושלם</li>
        <li>0 מייצג העדר קשר</li>
        <li>-1 מייצג קשר שלילי מושלם</li>
    </ul>
    </p>
    </div>
    ''',
    unsafe_allow_html=True
)

