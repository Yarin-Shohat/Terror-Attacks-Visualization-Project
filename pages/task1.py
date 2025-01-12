import streamlit as st
import pandas as pd
from folium.plugins import MarkerCluster
import folium
from pathlib import Path


# -----------------------------------------------------------------------------

st.markdown(
    '''
    <div style="text-align: right; direction: rtl;font-size: large;">
    בעמוד זה נענה על המטלה הבאה:
    <br>
    <b>התפלגות תקיפות הטרור לפי אזורים: כמות אירועי הטרור לפי מיקומים שונים בישראל</b>
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

    df = df[df["latitude"].notna() & df["longitude"].notna()]

    df = df[columns_names]

    return df


data = get_data()

# Define a list of specific cities with their latitudes, longitudes, and labels
city_labels = [{'name': 'Jerusalem', 'lat': 31.772180600401597, 'lon': 35.20426017469879},
 {'name': 'Tel Aviv', 'lat': 32.082969999999996, 'lon': 34.81188600000001},
 {'name': 'Ashkelon', 'lat': 31.665745571428566, 'lon': 34.57345348214286},
 {'name': 'Sderot', 'lat': 31.528199999999995, 'lon': 34.596382000000006},
 {'name': 'Eshkol regional council',
  'lat': 31.213881746268658,
  'lon': 34.460347388059695},
 {'name': 'Ashdod', 'lat': 31.819970431372543, 'lon': 34.66481956862746},
 {'name': 'Beersheba', 'lat': 31.258944624999998, 'lon': 34.786781},
 {'name': 'Haifa', 'lat': 32.79357451219513, 'lon': 34.990603195121956},
 {'name': 'Shaar HaNegev regional council',
  'lat': 31.51099376923077,
  'lon': 34.62375746153846},
 {'name': 'Petah Tiqwa', 'lat': 32.089161, 'lon': 34.88382},
 {'name': 'Netanya', 'lat': 32.32518116, 'lon': 34.85378992},
 {'name': 'Sdot Negev regional council',
  'lat': 31.41276371428572,
  'lon': 34.580247190476186},
 {'name': 'Kissufim', 'lat': 31.373840000000005, 'lon': 34.39836371428571}]
# Create a base map centered on Israel
label_map = folium.Map(
    location=[31.5, 34.8],  # Center of Israel
    zoom_start=8,           # Appropriate zoom level for full coverage
    tiles="CartoDB positron",
    control_scale=True
)

# Add a Marker Cluster for ALL points
marker_cluster = MarkerCluster(
    options={
        'spiderfyOnMaxZoom': True,
        'disableClusteringAtZoom': 11,
        'maxClusterRadius': 40,
        'showCoverageOnHover': True
    }
).add_to(label_map)

# Add ALL points to the cluster
for idx, row in data.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=6,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.7,
        popup=(
            f"<b>City:</b> {row['city']}<br>"
            f"<b>Casualties:</b> {row['nkill'] + row['nwound']}<br>"
            f"<b>Location:</b> {row['location']}"
        )
    ).add_to(marker_cluster)

# Add labels for specific cities
for city in city_labels:
    folium.Marker(
        location=[city["lat"], city["lon"]],
        icon=None,  # No icon, just text
        popup=city["name"],
        tooltip=city["name"]
    ).add_to(label_map)

# Save the map with city labels
label_map.save("labeled_israel_map.html")
st.components.v1.html(label_map._repr_html_(), height=700)
