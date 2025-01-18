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

st.markdown("<br>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        '''
        <div style="text-align: right; direction: rtl;">
        כל משבצת במטריצה מציגה את הקשר בין שני משתנים, כאשר:
        
        <ul><br>
            <li>באלכסון - התפלגות המשתנה</li>
            <li>מעל/מתחת לאלכסון - פיזור הנקודות בין שני המשתנים</li>
        </ul>
        </p>
        </div>
        ''',
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        '''
        <div style="text-align: right; direction: rtl;">
        <p>
        מטריצת הגרפים מציגה את כל הקשרים האפשריים בין המשתנים הבאים:
        <ul>
            <li>מספר המחבלים (Terorists Involved)</li>
            <li>מספר ההרוגים (Live Loss)</li>
            <li>מספר הפצועים (Injuries)</li>
        </ul>
        </p>
        </div>
        ''',
        unsafe_allow_html=True
    )

@st.cache_data
def get_data():
    """
    Read the Terror Attacks data from the CSV file.
    """
    DATA_FILENAME = Path(__file__).parent.parent / 'data/IL_data.csv'
    df = pd.read_csv(DATA_FILENAME, encoding='ISO-8859-1')
    columns_names = ["eventid","iyear","imonth","iday","country","city","latitude","longitude","nperps","nkill","nwound",
        "location","success","attacktype1","suicide","targtype1","weaptype1_txt","gname","extended"]
    features = ['nperps', 'nkill', 'nwound']
    df = df[columns_names]
    df = df[df[features].gt(0).all(axis=1)]

    return df

df = get_data()

# Add date range filter
min_year = int(df['iyear'].min())
max_year = int(df['iyear'].max())
selected_years = st.slider(
    'Select Year Range',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter dataframe based on selected years
df_filtered = df[(df['iyear'] >= selected_years[0]) & (df['iyear'] <= selected_years[1])]

features = ['nperps', 'nkill', 'nwound']
labels = {
    'nperps': 'Terorists Involved',
    'nkill': 'Live Loss',
    'nwound': 'Injuries'
}

try:
    # Check if we have valid data
    if df_filtered.empty or df_filtered[features].sum().sum() == 0:
        raise ValueError("No valid data in selected range")
        
    # Create subplot figure with filtered data
    fig = make_subplots(
        rows=3, 
        cols=3,
        subplot_titles=[f"{labels[feat1]} vs {labels[feat2]} ({selected_years[0]}-{selected_years[1]})" 
                       if i != j else f"{labels[feat1]} Distribution ({selected_years[0]}-{selected_years[1]})"
                       for i, feat1 in enumerate(features)
                       for j, feat2 in enumerate(features)]
    )

    # Add traces for each combination
    for i, feat1 in enumerate(features):
        for j, feat2 in enumerate(features):
            # If on diagonal, create distribution plot
            if i == j:
                # Create distribution plot
                hist_data = [df_filtered[feat1].dropna()]
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
                        x=df_filtered[feat1],
                        y=df_filtered[feat2],
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
                        customdata=df_filtered[['iyear', 'city', 'location']].values
                    ),
                    row=j+1, col=i+1
                )

    corr_matrix = df_filtered[features].corr()

except ValueError as e:
    # Create empty subplot figure
    fig = make_subplots(
        rows=3, 
        cols=3,
        subplot_titles=[f"No data available for {labels[feat1]} vs {labels[feat2]}" 
                       for i, feat1 in enumerate(features)
                       for j, feat2 in enumerate(features)]
    )
    
    # Add empty plots with "No data" message
    for i, feat1 in enumerate(features):
        for j, feat2 in enumerate(features):
            fig.add_trace(
                go.Scatter(
                    x=[],
                    y=[],
                    name="No data",
                    showlegend=False,
                ),
                row=j+1, col=i+1
            )
    
    # Create empty correlation matrix
    corr_matrix = pd.DataFrame(0, index=features, columns=features)
    
    # Show warning message
    st.warning(f"No valid data found for the selected year range ({selected_years[0]}-{selected_years[1]})")



# Update layout
fig.update_layout(
    height=900,
    width=900,
    showlegend=False,
    title_text='Correlation Matrix with Distributions',
    title_x=0.39,
)

# Update axes labels
for i, feat1 in enumerate(features):
    for j, feat2 in enumerate(features):
        fig.update_xaxes(title_text=labels[feat1], row=j+1, col=i+1)
        fig.update_yaxes(title_text=labels[feat2], row=j+1, col=i+1)

# Display plot
st.plotly_chart(fig, use_container_width=True)

st.write("### Correlation Matrix")
st.markdown(
    '''
    <div>
    <ul>
        <li>1: Perfect positive correlation</li>
        <li>0: No correlation</li>
        <li>-1: Perfect negative correlation</li>
    </ul>
    </div>
''',
unsafe_allow_html=True
)

st.dataframe(corr_matrix.style.format("{:.3f}"))
