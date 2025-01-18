# :boom: Terror Attacks Visualization Project

A comprehensive data visualization dashboard analyzing terror attacks in Israel using the Global Terrorism Database (GTD).

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://terror-attacks-visualization-dashboard.streamlit.app/)

## :dart: Project Overview

This project aims to analyze and visualize terror attack patterns in Israel, focusing on:
- Geographical distribution of attacks
- Weapon types and their impact
- Casualty analysis over time

## :notebook: Features

### 1. Home Page
- Dataset overview and statistics
- Interactive column analysis
- Data quality metrics
- Key research questions

### 2. Geographic Distribution Analysis
- Interactive map visualization
- Cluster analysis of attack locations
- Major cities highlight
- Color-coded attack intensity

### 3. Weapon Analysis Over Time
- Interactive bubble chart
- Cumulative analysis of injuries and fatalities
- Weapon type comparison
- Time-based animation
- Customizable time aggregation (Monthly/Quarterly/Yearly)

## :gear: Technical Stack

- **Python 3.11+**
- **Streamlit** - Web application framework
- **Pandas** - Data manipulation
- **Plotly** - Interactive visualizations
- **Folium** - Geographic visualizations

## :computer: Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/Terror-Attacks-Visualization-Project.git
cd Terror-Attacks-Visualization-Project
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Run the application
```bash
streamlit run streamlit_app.py
```

## :file_folder: Project Structure

```
Terror-Attacks-Visualization-Project/
├── data/
│   ├── IL_data.csv          # Main dataset
│   ├── column_desc.csv      # Column descriptions
│   └── icons/               # UI icons and images
├── pages/
│   ├── task1.py            # Geographic distribution
│   ├── task2.py            # Correlation analysis
│   └── task3.py            # Weapon analysis
├── streamlit_app.py         # Main application file
├── homePage.py             # Dashboard home page
├── requirements.txt        # Project dependencies
└── README.md              # Project documentation
```

## :bar_chart: Visualizations

1. **Geographic Distribution Map**
   - Interactive clustering
   - Custom markers for major cities
   - Detailed attack information on hover

2. **Weapon Analysis Dashboard**
   - Dynamic bubble chart
   - Logarithmic scales for better visualization
   - Time series animation
   - Customizable filters

## :bulb: Usage Tips

1. **Map Navigation**
   - Zoom in/out for detailed view
   - Click clusters to expand
   - Hover over points for details

2. **Weapon Analysis**
   - Use time aggregation controls
   - Adjust minimum incident threshold
   - Play/pause animation
   - Filter by weapon type

## :memo: Data Source

The data is sourced from the Global Terrorism Database (GTD), focusing on incidents in Israel. The dataset includes:
- Attack locations
- Casualty information
- Weapon types
- Temporal data

## :hammer_and_wrench: Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## :page_facing_up: License

This project is licensed under the MIT License - see the LICENSE file for details.

## :telephone_receiver: Contact

For any queries regarding this project, please open an issue in the GitHub repository.

---

Made with :heart: for data visualization
