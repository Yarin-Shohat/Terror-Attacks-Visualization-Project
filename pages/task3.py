import streamlit as st
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px

# -----------------------------------------------------------------------------

st.markdown(
    '''
    <div style="text-align: right; direction: rtl;font-size: large;">
    בעמוד זה נענה על המטלה הבאה:
    <br>
    <b>כמות פיגועי הטרור לאורך השנים: כיצד השתנתה תדירות הפיגועים לאורך השנים?</b>
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
    columns_names = ['eventid', 'iyear', 'imonth', 'iday', 'country_txt', 'provstate',
                                   'targtype1_txt', 'weaptype1_txt', 'nkill', 'nwound']

    df = df[columns_names]
    # Rename columns for consistency
    terror_data = df.rename(
        columns={
            'eventid': 'id',
            'iyear': 'year',
            'imonth': 'month',
            'iday': 'day',
            'country_txt': 'country',
            'provstate': 'state',
            'targtype1_txt': 'target',
            'weaptype1_txt': 'weapon',
            'nkill': 'fatalities',
            'nwound': 'injuries'
        }
    )
    # Fill missing values in 'fatalities' and 'injuries' with 0 and convert to integers
    terror_data['fatalities'] = terror_data['fatalities'].fillna(0).astype(int)
    terror_data['injuries'] = terror_data['injuries'].fillna(0).astype(int)

    # Fill missing values in 'fatalities' and 'injuries' with 0 and convert to integers
    terror_data['fatalities'] = terror_data['fatalities'].fillna(0).astype(int)
    terror_data['injuries'] = terror_data['injuries'].fillna(0).astype(int)

    # Add year-month column for animation
    terror_data['date'] = pd.to_datetime(terror_data[['year', 'month', 'day']].assign(day=1))
    # Add full date column for better time handling
    terror_data['full_date'] = pd.to_datetime(
        terror_data[['year', 'month', 'day']].assign(day=1)
    )
    # Simplify weapon types
    terror_data['weapon'] = terror_data['weapon'].replace(
        'Vehicle (not to include vehicle-borne explosives, i.e., car or truck bombs)', 'Vehicle'
    )

    return terror_data

terror_data = get_data()

# Create sidebar controls
st.sidebar.header("Visualization Controls")

# Time aggregation selector
time_group = st.sidebar.selectbox(
    "Time Grouping",
    ["Month", "Quarter", "Year"],
    index=2
)

# Minimum incidents threshold
min_incidents = st.sidebar.slider(
    "Minimum Incidents per Weapon Type",
    min_value=1,
    max_value=50,
    value=5
)

# Prepare time grouping and ensure proper sorting
if time_group == "Month":
    # Format as YYYY-MM for proper chronological sorting
    terror_data['time_period'] = terror_data['full_date'].dt.strftime('%Y-%m')
elif time_group == "Quarter":
    # Format as YYYY-Q# for proper chronological sorting
    terror_data['time_period'] = terror_data['full_date'].dt.strftime('%Y-Q%q')
else:
    # Ensure year is padded with zeros for proper sorting
    terror_data['time_period'] = terror_data['year'].astype(str).str.zfill(4)

# Create time-series aggregation with weapon types
time_weapon_data = (
    terror_data.groupby(['time_period', 'weapon'])
    .agg({
        'id': 'count',
        'fatalities': 'sum',
        'injuries': 'sum'
    })
    .reset_index()
)

# Filter weapons based on total incidents across all time periods
weapon_counts = time_weapon_data.groupby('weapon')['id'].sum()
weapons_to_include = weapon_counts[weapon_counts >= min_incidents].index
time_weapon_data = time_weapon_data[time_weapon_data['weapon'].isin(weapons_to_include)]

# Calculate cumulative totals for each weapon type
time_weapon_data['cumulative_incidents'] = time_weapon_data.groupby('weapon')['id'].cumsum()
time_weapon_data['cumulative_fatalities'] = time_weapon_data.groupby('weapon')['fatalities'].cumsum()
time_weapon_data['cumulative_injuries'] = time_weapon_data.groupby('weapon')['injuries'].cumsum()

# Ensure minimum values of 1 for log scale (do this AFTER calculating cumulative totals)
time_weapon_data['cumulative_fatalities'] = time_weapon_data['cumulative_fatalities'].clip(lower=1)
time_weapon_data['cumulative_injuries'] = time_weapon_data['cumulative_injuries'].clip(lower=1)

# Sort by time_period and weapon
time_weapon_data = time_weapon_data.sort_values(['time_period', 'weapon'])

# Debug print to verify data
st.sidebar.write("Weapon types in visualization:", time_weapon_data['weapon'].nunique())

# Before creating the plot, ensure we have complete data for each time period
time_periods = sorted(time_weapon_data['time_period'].unique())
weapons = sorted(time_weapon_data['weapon'].unique())

# Create a complete DataFrame with all combinations
index = pd.MultiIndex.from_product([time_periods, weapons], names=['time_period', 'weapon'])
complete_data = pd.DataFrame(index=index).reset_index()

# Merge with existing data
time_weapon_data = pd.merge(
    complete_data,
    time_weapon_data,
    on=['time_period', 'weapon'],
    how='left'
).fillna(0)

# Recalculate cumulative totals
for weapon in weapons:
    mask = time_weapon_data['weapon'] == weapon
    time_weapon_data.loc[mask, 'cumulative_incidents'] = time_weapon_data.loc[mask, 'id'].cumsum()
    time_weapon_data.loc[mask, 'cumulative_fatalities'] = time_weapon_data.loc[mask, 'fatalities'].cumsum()
    time_weapon_data.loc[mask, 'cumulative_injuries'] = time_weapon_data.loc[mask, 'injuries'].cumsum()

# Ensure minimum values for log scale
time_weapon_data['cumulative_fatalities'] = time_weapon_data['cumulative_fatalities'].clip(lower=1)
time_weapon_data['cumulative_injuries'] = time_weapon_data['cumulative_injuries'].clip(lower=1)

# Create scatter plot with explicit category orders
weapon_categories = sorted(time_weapon_data['weapon'].unique())
fig = px.scatter(
    time_weapon_data,
    x='cumulative_injuries',
    y='cumulative_fatalities',
    animation_frame='time_period',
    animation_group='weapon',
    size='cumulative_incidents',
    color='weapon',
    hover_name='weapon',
    category_orders={'weapon': weapon_categories},  # Add this line
    log_x=True,
    log_y=True,
    size_max=60,
    range_x=[0.1, time_weapon_data['cumulative_injuries'].max() * 3],
    range_y=[0.1, time_weapon_data['cumulative_fatalities'].max() * 3],
    labels={
        'cumulative_injuries': 'Cumulative Number of Injuries (log scale)',
        'cumulative_fatalities': 'Cumulative Number of Fatalities (log scale)',
        'cumulative_incidents': 'Cumulative Number of Incidents',
        'weapon': 'Weapon Type',
        'time_period': 'Time Period'
    },
    title=f'Evolution of Terror Attacks by Weapon Type ({time_group}ly)',
    hover_data={  # Add more hover information
        'weapon': True,
        'cumulative_incidents': True,
        'cumulative_fatalities': ':,.0f',
        'cumulative_injuries': ':,.0f',
        'time_period': True
    }
)

# Update layout with proper log scale formatting and vertical lines
fig.update_layout(
    height=700,
    showlegend=True,
    hovermode='closest',
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=1.02,
        title="Weapon Types",
        itemsizing='constant'
    ),
    # Add vertical lines
    shapes=[
        dict(
            type='line',
            x0=x,
            x1=x,
            y0=0.1,  # Same as your range_y[0]
            y1=time_weapon_data['cumulative_fatalities'].max() * 3,  # Same as your range_y[1]
            yref='y',
            xref='x',
            line=dict(
                color='gray',
                width=1
            )
        )
        for x in [1, 10, 100, 1000, 10000]
    ],
    xaxis=dict(
        type='log',
        tickmode='array',
        ticktext=[1, 10, 100, 1000, 10000],
        tickvals=[1, 10, 100, 1000, 10000],
        title_text='Cumulative Number of Injuries (log scale)'
    ),
    yaxis=dict(
        type='log',
        tickmode='array',
        ticktext=[1, 10, 100, 1000, 10000],
        tickvals=[1, 10, 100, 1000, 10000],
        title_text='Cumulative Number of Fatalities (log scale)'
    ),
    updatemenus=[{
        'type': 'buttons',
        'showactive': False,
        'x': 0.05,
        'y': 1.1,
        'buttons': [{
            'label': '▶️ Play',
            'method': 'animate',
            'args': [None, {
                'frame': {'duration': 800, 'redraw': True},  # Adjusted duration
                'fromcurrent': True,
                'transition': {'duration': 300},
                'mode': 'immediate'
            }]
        }, {
            'label': '⏸️ Pause',
            'method': 'animate',
            'args': [[None], {
                'frame': {'duration': 0, 'redraw': False},
                'mode': 'immediate'
            }]
        }]
    }],
    sliders=[{
        'currentvalue': {'prefix': 'Time Period: '},
        'pad': {'t': 50},
        'len': 0.9,  # Make slider wider
        'x': 0.1,    # Adjust position
        'xanchor': 'left',
        'y': 0,      
        'yanchor': 'top',
        'transition': {'duration': 300}
    }],
    margin=dict(r=150)  # Add right margin for legend
)

# Add annotations for each frame
for frame in fig.frames:
    time = frame.name
    frame_data = time_weapon_data[time_weapon_data['time_period'] == time]
    
    # Add trend line
    frame.update(layout=dict(
        annotations=[{
            'text': f'Time Period: {time}',
            'x': 0.05,
            'y': 0.95,
            'showarrow': False,
            'xref': 'paper',
            'yref': 'paper'
        }]
    ))

# Display plot
st.plotly_chart(fig, use_container_width=True)

# Add statistics sidebar
st.sidebar.markdown("### Current Statistics")
current_stats = time_weapon_data.groupby('weapon').agg({
    'id': 'sum',
    'fatalities': 'sum',
    'injuries': 'sum'
}).sort_values('id', ascending=False).rename(columns={'id': 'incidents'})

st.sidebar.dataframe(current_stats, use_container_width=True)

# Add Hebrew explanation
st.markdown(
    '''
    <div style="text-align: right; direction: rtl;">
    <h3>ניתוח התפתחות הטרור לאורך זמן:</h3>
    <p>
    הויזואליזציה מציגה את התפתחות אירועי הטרור לאורך זמן, כאשר:
    <ul>
        <li>כל בועה מייצגת סוג נשק</li>
        <li>גודל הבועה מייצג את מספר האירועים</li>
        <li>מיקום הבועה מראה את היחס בין מספר ההרוגים והפצועים</li>
        <li>הצבע מבדיל בין סוגי הנשק השונים</li>
        <li>האנימציה מראה את השינוי לאורך זמן</li>
    </ul>
    ניתן לשלוט בויזואליזציה באמצעות:
    <ul>
        <li>כפתורי הפעלה/עצירה</li>
        <li>בחירת רמת הקיבוץ בזמן (חודשי/רבעוני/שנתי)</li>
        <li>סף מינימלי למספר האירועים</li>
    </ul>
    </p>
    </div>
    ''',
    unsafe_allow_html=True
)