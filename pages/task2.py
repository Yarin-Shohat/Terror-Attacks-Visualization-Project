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
            <li>מספר ההרוגים (Deaths)</li>
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

# Add color mapping at the start of the script
PAIR_COLORS = {
    ('nperps', 'nperps'): '#1f77b4',     # Blue
    ('nkill', 'nkill'): '#1f77b4',       # Blue
    ('nwound', 'nwound'): '#1f77b4',     # Blue
    ('nperps', 'nkill'): '#d62728',      # Red
    ('nperps', 'nwound'): '#7851a9',     # Purple
    ('nkill', 'nwound'): '#ff7f0e',      # Orange
}

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
    'nkill': 'Deaths',
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
        subplot_titles=[f"{labels[feat1]} vs {labels[feat2]}" 
                       if i != j else f"{labels[feat1]} Distribution"
                       for i, feat1 in enumerate(features)
                       for j, feat2 in enumerate(features)]
    )
    fig.update_annotations(font_size=16)  # Set the font size for subplot titles

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
                    go.Histogram(
                        x=df_filtered[feat1],
                        name=f'{labels[feat1]} Distribution',
                        marker_color=PAIR_COLORS[(feat1, feat1)],
                        showlegend=False,
                        hovertemplate='<span style="font-size: 14px;">' +
                                    f'{labels[feat1]}: %{{x}}<br>Count: %{{y}}' +
                                    '</span><extra></extra>',
                        nbinsx=30
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
                        marker=dict(
                            color=PAIR_COLORS.get((feat1, feat2)) or PAIR_COLORS.get((feat2, feat1)),
                            size=5,
                            opacity=0.6
                        ),
                        name=f'{labels[feat1]} vs {labels[feat2]}',
                        showlegend=False,
                        hovertemplate=
                        '<span style="font-size: 14px;">' +
                        '<br>'.join([
                            f'{labels[feat1]}: %{{x}}',
                            f'{labels[feat2]}: %{{y}}',
                            'Year: %{customdata[0]}',
                            'City: %{customdata[1]}',
                        ]) + '</span><extra></extra>',
                        customdata=df_filtered[['iyear', 'city']].values
                    ),
                    row=j+1, col=i+1
                )

    corr_matrix = df_filtered[features].corr()
except ValueError as e:
    # Create empty subplot figure
    fig = make_subplots(
        rows=3, 
        cols=3,
        subplot_titles=[f"No data available" 
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
    title={
        'text': f'Correlation Matrix with Distributions {selected_years[0]}-{selected_years[1]}',
        'font': {'size': 30},
        'y': 0.95,
        'x': 0.5,
        'xanchor': 'center',
        'yanchor': 'top'
    }
)

# Update axes labels
for i, feat1 in enumerate(features):
    for j, feat2 in enumerate(features):
        if i == j:
            # Distribution plots
            fig.update_yaxes(title_text="Count", title_font=dict(size=16), row=j+1, col=i+1)
            fig.update_xaxes(title_text=labels[feat1], title_font=dict(size=16), row=j+1, col=i+1)
        else:
            fig.update_xaxes(title_text=labels[feat1], title_font=dict(size=16), row=j+1, col=i+1)
            fig.update_yaxes(title_text=labels[feat2], title_font=dict(size=16), row=j+1, col=i+1)

# Display plot
st.plotly_chart(fig, use_container_width=True)

custom_names = ['Terrorists', 'Deaths', 'Injuries']
corr_matrix.columns = custom_names
corr_matrix.index = custom_names

# Create sidebar controls
st.sidebar.header("Correlation Matrix")
st.sidebar.dataframe(corr_matrix.style.format("{:.3f}"))
st.sidebar.markdown(
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
