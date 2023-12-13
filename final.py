# Illustrates use of columns container
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import folium
from folium import plugins
from folium.plugins import MarkerCluster, HeatMap
from streamlit_folium import folium_static

# Prevents loading the file every time the user interacts with widgets
@st.cache_data
def load_data():
    filename = "https://raw.githubusercontent.com/noliprez/dsc205-final/main/Significant_Earthquakes.csv"
    df = pd.read_csv(filename,
                     parse_dates=True)
    return df

df = load_data()

st.title("Earthquakes from the 1900's to the Present")
st.markdown('---')
st.subheader('The Data')
df['time'] = pd.to_datetime(df['time']).dt.date
df

st.markdown('---')

st.subheader('Depth and Magnitude Over the Years')
st.write('What are the global earthquake frequency and magnitude trends since 1900?')

# Extract year and create a new column
df['year'] = pd.to_datetime(df['time']).dt.year

year_range = st.slider("Select a Year Range",
                       min_value=df['year'].min(),
                       max_value=df['year'].max(),
                       value=(df['year'].min(), df['year'].max()))

# Filter DataFrame based on the selected year range
df_filtered = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
if not df_filtered.empty:
    fig1 = plt.figure()
    ax1 = fig1.add_subplot()
    ax1.set_title('Earthquake Magnitude')
    ax1.set_xlabel('Magnitude')
    ax1.set_ylabel('Frequency')
    average_mag = df_filtered['mag'].mean()
    ax1.axvline(x=average_mag, color='red', linestyle='dashed', linewidth=2, label=f'Average ({average_mag:.2f})')
    ax1.legend()
    ax1.hist(df_filtered['mag'], bins=10, color='blue')

    fig2 = plt.figure()
    ax2 = fig2.add_subplot()
    ax2.set_title('Earthquake Depth')
    ax2.set_xlabel('Depth')
    ax2.set_ylabel('Frequency')
    average_depth = df_filtered['depth'].mean()
    ax2.axvline(x=average_depth, color='blue', linestyle='dashed', linewidth=2, label=f'Average ({average_depth:.2f})')
    ax2.legend()
    ax2.hist(df_filtered['depth'], bins=10, color='red')
    
    fig3 = plt.figure()
    ax3 = fig3.add_subplot()
    ax3.set_title('Earthquake Magnitude')
    ax3.set_xlabel('Year')
    ax3.set_ylabel('Magnitude')
    ax3.set_yscale('log')
    overall_average_mag = df_filtered['mag'].mean()
    ax3.axhline(y=overall_average_mag, color='red', linestyle='dashed', linewidth=2, label=f'Overall Average ({overall_average_mag:.2f})')
    ax3.legend()
    ax3.scatter(df_filtered['year'], df_filtered['mag'], color='blue', alpha=0.5)

    fig4 = plt.figure()
    ax4 = fig4.add_subplot()
    ax4.set_title('Earthquake Depth')
    ax4.set_xlabel('Year')
    ax4.set_ylabel('Depth')
    ax4.set_yscale('log')
    overall_average_depth = df_filtered['depth'].mean()
    ax4.axhline(y=overall_average_depth, color='blue', linestyle='dashed', linewidth=2, label=f'Overall Average ({overall_average_depth:.2f})')
    ax4.legend()
    ax4.scatter(df_filtered['year'], df_filtered['depth'], color='red', alpha=0.5)
    
    tab1, tab2 = st.tabs(['Magnitude', 'Depth'])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(fig1)
        with col2:
            st.pyplot(fig3)
    with tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.pyplot(fig2)
        with col2:
            st.pyplot(fig4)
else:
    st.warning("No data available for the selected year.")

st.markdown('---')

st.subheader('Earthquakes Throughout the World')
st.write('Can we identify the seismic hotspots or regions with the highest frequency of earthquakes based on this dataset since 1900?')
min_mag = st.number_input('Enter a minimum magnitude: ',
                          min_value=0.0,
                          max_value=10.0,
                          step=0.1,
                          value=5.0)
mag_filtered = df.loc[df['mag'] > min_mag]
mag_filtered = mag_filtered.rename(columns={'longitude': 'lon'})
mag_filtered = mag_filtered.rename(columns={'latitude': 'lat'})


# Create a base map
base_m = folium.Map(location=[0,0], zoom_start=2)
# Create a HeatMap layer
heat_data = [[row['lat'], row['lon']] for index, row in mag_filtered.iterrows()]
HeatMap(heat_data).add_to(base_m)

tab1, tab2 = st.tabs(['Basic Map', 'Heat Map'])
with tab1:
    # Display map
    st.map(mag_filtered)
with tab2:
    # Display map
    folium_static(base_m)

local_image_path = "plates.jpg"
st.image(local_image_path, use_column_width=True)

st.markdown('---')

st.subheader('Earthquake Prone States')
st.write('What are the most earthquake-prone states or regions in the United States, and can we assess their earthquake risk based on the dataset?')

# Create map
m = folium.Map(location=[40.77, -73.95], zoom_start=4)
for index, row in df.iterrows():
    legend_entries = []
    quake_loc = [row['latitude'], row['longitude']]
    if row['mag'] < 7:
        c = folium.Circle(radius=50, location=quake_loc, color='red', fill=True)
        c.add_to(m)
    else:
        c = folium.Circle(radius=50, location=quake_loc, color='blue', fill=True)
        c.add_to(m)

# Add legend
legend_entries.append('<li style="color:red">Magnitude &lt; 7</li>')
legend_entries.append('<li style="color:blue">Magnitude &ge; 7</li>')

# Display the map
folium_static(m)

# Display the legend using Streamlit Markdown
legend_markdown = f'<ul>{" ".join(legend_entries)}</ul>'
st.markdown(legend_markdown, unsafe_allow_html=True)

st.markdown('---')

st.subheader('Earthquakes Throughout Seasons')
st.write('Are there any temporal trends in earthquake occurrences, such as seasonality or long-term variations?')

### Setting up the df to work with seasons ###
# Set the date as the index column
df['time'] = pd.to_datetime(df['time'])
df.set_index('time', inplace=True)
# Function to get the season based on the month
def get_season(month):
    if 3 <= month <= 5:
        return 'Spring'
    elif 6 <= month <= 8:
        return 'Summer'
    elif 9 <= month <= 11:
        return 'Fall'
    else:
        return 'Winter'
# Add a 'month' column to the dataframe
df['month'] = df.index.month
# Add a 'season' column to the dataframe
df['season'] = df['month'].apply(get_season)

# Add radio buttons and a year silder
selected_season = st.radio('Select a season: ', ('Winter', 'Spring', 'Summer', 'Fall'))
dynamic_key = 'generate_unique_key_based_on_condition'
year_range = st.slider("Select a Year Range",
                       min_value=df['year'].min(),
                       max_value=df['year'].max(),
                       value=(df['year'].min(), df['year'].max()),
                       key=dynamic_key)
df_filtered = df[(df['season'] == selected_season) & (df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
fig = plt.figure()
ax = fig.add_subplot()
ax.set_title(f'Earthquake Magnitude ({selected_season})')
ax.set_xlabel('Magnitude')
ax.set_ylabel('Frequency')
ax.hist(df_filtered['mag'], bins=20, color='red')
st.pyplot(fig)