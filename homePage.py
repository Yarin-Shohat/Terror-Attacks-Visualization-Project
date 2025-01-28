import streamlit as st
import pandas as pd
from pathlib import Path
import plotly.express as px

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
    Read the Terror Attacks data from the CSV file and convert negative values to null
    """
    DATA_FILENAME = Path(__file__).parent/'data/IL_data.csv'
    data = pd.read_csv(DATA_FILENAME, encoding='ISO-8859-1')
    columns_names = ["iyear","imonth","iday","city","latitude","longitude","nperps","nkill","nwound","weaptype1_txt"]

    data = data[columns_names]

    # Convert negative values to null in numeric columns
    for column in columns_names:
        if pd.api.types.is_numeric_dtype(data[column]):
            data.loc[data[column] < 0, column] = pd.NA

    # Change weapon type colors for vehicle-related attacks
    data.loc[data['weaptype1_txt'] == 'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)', 'weaptype1_txt'] = 'Vehicle'
    return data

@st.cache_data
def get_columns_desc():
    """
    Read the Terror Attacks data from the CSV file.
    """
    DATA_FILENAME = Path(__file__).parent/'data/column_desc.csv'
    df = pd.read_csv(DATA_FILENAME, encoding='ISO-8859-1')
    return df

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
            <li>האם קיימת מגמה כללית של שימוש בסוגי הנשק שונים בפיגועי טרור בישראל? כיצד מגמות אלו השפיעו על תדירות הפיגועים ועל מספר הנפגעים וההרוגים?</li>
        </ol>
        ''',
        unsafe_allow_html=True
)
''
''

# Function to display column information
def display_column_info(data):
    """
    Creates an interactive dashboard-style display of dataset information
    """
    st.header("Dataset Explorer", divider="rainbow")
    
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", f"{len(data):,}")
    with col2:
        st.metric("Total Columns", f"{len(data.columns):,}")
    with col3:
        st.metric("Missing Values", f"{data.isna().sum().sum():,}")
    
    # Create tabs for different views
    tab1, tab2 = st.tabs(["📊 Column Overview", "🔍 Detailed Analysis"])
    columns_decs = get_columns_desc()
    with tab1:
        # Create a summary table with color coding
        summary_data = []
        for column in data.columns:
            col_type = data[column].dtype
            unique_count = data[column].nunique()
            missing_count = data[column].isna().sum()
            missing_percentage = (missing_count / len(data)) * 100
            
            try:
                numeric_col = pd.to_numeric(data[column], errors='coerce')
                if numeric_col.notna().any():
                    min_val = f"{numeric_col.min():,.2f}"
                    max_val = f"{numeric_col.max():,.2f}"
                    mean_val = f"{numeric_col.mean():,.2f}"
                else:
                    min_val = max_val = mean_val = "N/A"
            except:
                min_val = max_val = mean_val = "N/A"
            
            summary_data.append({
                "Column": columns_decs[columns_decs.iloc[:, 0] == column].iloc[:, 2].values[0],
                "Type": str(col_type),
                "Unique Values": unique_count,
                "Missing Values (%)": f"{missing_percentage:.1f}%",
                "Min": min_val,
                "Max": max_val,
                "Mean": mean_val,
                "Description": columns_decs[columns_decs.iloc[:, 0] == column].iloc[:, 1].values[0] 
                              if not columns_decs[columns_decs.iloc[:, 0] == column].empty 
                              else "N/A"
            })
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(
            summary_df.style.background_gradient(
                subset=['Unique Values'], 
                cmap='YlOrRd'
            ),
            use_container_width=True,
            height=400
        )
    
    with tab2:
        # Column selector
        # Get display names for all columns
        display_names = {col: columns_decs[columns_decs.iloc[:, 0] == col].iloc[:, 2].values[0] for col in data.columns}
        
        selected_column = st.selectbox(
            "Select Column for Detailed Analysis",
            options=data.columns,
            format_func=lambda x: display_names[x]
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Get display name for the selected column
            display_name = columns_decs[columns_decs.iloc[:, 0] == selected_column].iloc[:, 2].values[0]
            
            # Visualization based on data type
            if pd.api.types.is_numeric_dtype(data[selected_column]):
                fig = px.histogram(
                    data, 
                    x=selected_column,
                    title=f"Distribution of {display_name}",
                    template="plotly_white",
                    labels={"x": display_name}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                # For categorical data, show top 10 values
                value_counts = data[selected_column].value_counts().head(10)
                fig = px.bar(
                    x=value_counts.index,
                    y=value_counts.values,
                    title=f"Top 10 Values in {display_name}",
                    labels={"x": display_name, "y": "Count"},
                    template="plotly_white"
                )
                st.plotly_chart(fig, use_container_width=True)
        with col2:
            st.write("#### Column Statistics")
            
            # Calculate and display statistics
            stats_dict = {
                "Total Values": len(data),
                "Unique Values": data[selected_column].nunique(),
                "Missing Values": data[selected_column].isna().sum(),
                "Missing (%)": f"{(data[selected_column].isna().sum() / len(data)) * 100:.1f}%"
            }
            
            # Add numeric statistics if applicable
            if pd.api.types.is_numeric_dtype(data[selected_column]):
                stats_dict.update({
                    "Mean": f"{data[selected_column].mean():,.2f}",
                    "Median": f"{data[selected_column].median():,.2f}",
                    "Std Dev": f"{data[selected_column].std():,.2f}",
                    "Min": f"{data[selected_column].min():,.2f}",
                    "Max": f"{data[selected_column].max():,.2f}"
                })
            
            # Display statistics as metrics
            for stat, value in stats_dict.items():
                st.metric(stat, value)
            
            # Show sample values
            st.write("#### Sample Values")
            st.write(data[selected_column].sample(min(5, len(data))).to_list())

df = get_data()

# Display the enhanced column information
st.divider()
display_column_info(df)
