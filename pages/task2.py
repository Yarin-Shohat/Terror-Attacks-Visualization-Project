import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from plotly.subplots import make_subplots
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
    features = ['nperps', 'nkill', 'nwound']
    df = df[columns_names]
    df = df[df[features].gt(0).all(axis=1)]

    return df

df = get_data()

features = ['nperps', 'nkill', 'nwound']
labels = {
    'nperps': 'Terorists Involved',
    'nkill': 'Live Loss',
    'nwound': 'Injuries'
}

# Create a 3x3 subplot figure
fig = make_subplots(
    rows=3, 
    cols=3,
    subplot_titles=[f"{labels[feat1]} vs {labels[feat2]}" 
                   if i != j else f"{labels[feat1]} Distribution"
                   for i, feat1 in enumerate(features)
                   for j, feat2 in enumerate(features)]
)


# Add traces for each combination
for i, feat1 in enumerate(features):
    for j, feat2 in enumerate(features):
        # If on diagonal, create distribution plot
        if i == j:
            # Create distribution plot
            hist_data = [df[feat1].dropna()]
            group_labels = [labels[feat1]]
            dist_fig = ff.create_distplot(hist_data, group_labels, show_rug=False)
            
            # Add distribution trace
            fig.add_trace(
                go.Scatter(
                    x=dist_fig.data[0].y,
                    y=dist_fig.data[0].x,
                    name=f'{labels[feat1]} Distribution',
                    showlegend=False
                ),
                row=j+1, col=i+1
            )
        else:
            # Add scatter plot
            fig.add_trace(
                go.Scatter(
                    x=df[feat1],
                    y=df[feat2],
                    mode='markers',
                    name=f'{labels[feat1]} vs {labels[feat2]}',
                    showlegend=False,
                    hovertemplate=
                    '<br>'.join([
                        f'{labels[feat1]}: %{{x}}',
                        f'{labels[feat2]}: %{{y}}',
                        'Year: %{customdata[0]}',
                        'City: %{customdata[1]}',
                        'Location: %{customdata[2]}'
                    ]) + '<extra></extra>',
                    customdata=df[['iyear', 'city', 'location']].values
                ),
                row=j+1, col=i+1
            )

# Update layout
fig.update_layout(
    height=900,
    width=900,
    showlegend=False,
    title_text='Correlation Matrix with Distributions',
    title_x=0.5,
)

# Update axes labels
for i, feat1 in enumerate(features):
    for j, feat2 in enumerate(features):
        fig.update_xaxes(title_text=labels[feat1], row=j+1, col=i+1)
        fig.update_yaxes(title_text=labels[feat2], row=j+1, col=i+1)

# Display plot
st.plotly_chart(fig, use_container_width=True)

# Calculate correlation matrix
corr_matrix = df[['nperps', 'nkill', 'nwound']].corr()

# Display correlation matrix
st.write("### Correlation Matrix")
st.dataframe(corr_matrix.style.format("{:.3f}"))

# Add explanation in Hebrew
st.markdown(
    '''
    <div style="text-align: right; direction: rtl;">
    <h3>ניתוח הקשר:</h3>
    <p>
    מטריצת הגרפים מציגה את כל הקשרים האפשריים בין המשתנים הבאים:
    <ul>
        <li>מספר המחבלים (Number of Perpetrators)</li>
        <li>מספר ההרוגים (Number of Kills)</li>
        <li>מספר הפצועים (Number of Wounded)</li>
    </ul>
    כל משבצת במטריצה מציגה את הקשר בין שני משתנים, כאשר:
    <ul>
        <li>באלכסון - התפלגות המשתנה</li>
        <li>מעל/מתחת לאלכסון - פיזור הנקודות בין שני המשתנים</li>
    </ul>
    טבלת המתאמים מציגה את מקדמי המתאם בין כל זוג משתנים, כאשר:
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

