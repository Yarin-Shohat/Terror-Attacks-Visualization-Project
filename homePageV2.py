import streamlit as st
import pandas as pd
from pathlib import Path
from st_pages import add_page_title, get_nav_from_toml
from ydata_profiling import ProfileReport
from streamlit_ydata_profiling import st_profile_report


hide_streamlit_style = """
            <style>
            div.stHeading {display: none;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
@st.cache_data
def get_data():
    """
    Read the Terror Attacks data from the CSV file.
    """
    DATA_FILENAME = Path(__file__).parent/'data/IL_data.csv'
    df = pd.read_csv(DATA_FILENAME, encoding='ISO-8859-1')
    columns_names = ["eventid","iyear","imonth","iday","country","city","latitude","longitude","nperps","nkill","nwound",
        "location","success","attacktype1","suicide","targtype1","weaptype1_txt","gname","extended"]

    df = df[columns_names]

    return df


# Set the title that appears at the top of the page.
st.markdown(
    '''
    # :boom: Terror Attacks Visualization Project
    <div style="text-align: right; direction: rtl;">
    פרויקט בקורס ויזואליזציה במטרה לעבד, לנתח ולהציג נתונים אודות אירועי טרור בישראל לאורך השנים, מתוך מאגר הנתונים Global Terrorism Database (GTD).
    <br>
    בפרויקט התמקדנו בפיגועים שהתרחשו בשטח ישראל בלבד, במטרה להבין את דפוסי הפעולה והמאפיינים הייחודיים למרחב המקומי.
    <br><br>
    השאלה המרכזית עליה נרצה לענות בעזרת הנתונים שבחרנו היא:
    <br>
    <span><b>כיצד השתנה דפוס הטרור בישראל לאורך השנים מבחינת תדירות האירועים, הפיזור הגיאוגרפי ושיטות הפעולה?</b></span>
    <br>
    מטרתנו בפרויקט היא להבין את מגמות הטרור בישראל לאורך זמן, תוך התמקדות בזיהוי מוקדי הפעולה המרכזיים, קשרים בין מאפייני האירועים והתפתחותם ההיסטורית.
    <br><br>
    יתר על כן, נרצה לענות על מספר שאלות משנה נוספות:
    </div>
    ''',
    unsafe_allow_html=True
)
st.markdown(
        '''
        <ol style="text-align: right; direction: rtl;">
            <li>תדירות התקיפות לפי אזורים: מהם האזורים בהם התרחשו המספר הגבוה ביותר של תקיפות טרור?</li>
            <li>קורלציה בין מספר המחבלים למספר הנפגעים: האם קיים קשר בין כמות המחבלים באירוע לכמות הנפגעים?</li>
            <li>כמות פיגועי הטרור לאורך השנים: כיצד השתנתה תדירות הפיגועים לאורך השנים?</li>
        </ol>
        ''',
        unsafe_allow_html=True
)
# Add some spacing
''
''

@st.cache_data
def generate_profile_report(df):
    return ProfileReport(df, title="Terror Attacks Dataset Analysis")

df = get_data()

# Generate and display profile report
with st.expander("Data Profile Report", expanded=True):
    profile_report = generate_profile_report(df)
    st_profile_report(profile_report)


st.write(df)
