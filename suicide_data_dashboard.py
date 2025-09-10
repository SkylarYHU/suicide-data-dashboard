# Import necessary libraries
import streamlit.components.v1 as components
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# Set the configuration for the page
st.set_page_config(
    layout="wide",
    page_title="Global Suicide Trends Dashboard",
)

# Load data from a cleaned CSV and cache it for performance optimization
@st.cache_data
def load_data():
    df = pd.read_csv('cleaned_suicide_data.csv')
    return df


# Load the dataset
df = load_data()

# Set CSS styles for the dashboard
st.markdown(
    """
    <style>
    .dashboard-title {
        text-align: center;
        padding: 10px 0;
        color: 'black'; 
        font-size: 2.5rem; 
        font-weight: 700; 
        margin-top: -2rem;
    }

    .metric-container {
        background-color: white;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
        border: 1px solid white;
        margin-bottom: 2rem;
        height: 150px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }

    .metric-container:hover {
        transform: translateY(-5px);
    }

    .metric-title {
        font-size: 1rem;
        color: 'black';
        text-align: center;
        font-weight: 500;
    }

    .metric-value {
        font-size: 1.9rem;
        font-weight: 700;
        color: 'black';
        text-align: center;
    }

    .trend-indicator {
        vertical-align: middle;
        font-size: 0.9rem;
        font-weight: 600;
        margin: 0.5rem 0;
    }

    .highest-rate{
        color: #ff6ba1;
        background-color: rgba(255, 165,190 , 0.1);
        padding:2px 8px;
        border-radius:4px;
        margin: 0.7rem 0;
    }

    .chart-title {
        color: 'black';
        font-size: 1.3rem;
        text-align: center;
        margin: 1rem 0;
        font-weight: 600;
        padding: 0.5rem;
        line-height: 1;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Define color sequences for charts
COLOR_SEQUENCE = [
    "#ff6ba1",
    "#fc6c6c",
    "#FE9563",
    "#CC96E6",
    "#6FB8FF",
    "#5A87E7",
]

# Reversed palette
COLOR_SEQUENCE_LIGHT_TO_DARK = COLOR_SEQUENCE[::-1]

# Set the main title of the dashboard
st.markdown(
    """
    <div class='dashboard-title'>
        Global Suicide Trends Dashboard
    </div>
    """, unsafe_allow_html=True)

# ========================
# Sidebar Filters Section
# ========================

# Set the sidebar title
st.sidebar.header("Filters")

# Get minimum and maximum year in the dataset
min_year, max_year = df['year'].min(), df['year'].max()

# Create a year range slider
selected_year_range = st.sidebar.slider(
    "Select Year Range", min_year, max_year, (min_year, max_year))

# Create options for sex selection
sex_options = ['All'] + sorted(df['sex'].unique())

# Create a dropdown menu for sex selection
selected_sex = st.sidebar.selectbox(
    "Select Sex", sex_options, index=0)

# Rename and define fixed age group options
age_options = ['All', '5-14', '15-24', '25-34', '35-54', '55-74', '75+']

# Create a dropdown menu for age group selection
selected_age = st.sidebar.selectbox(
    "Select Age Group", age_options, index=0)

# Define the preferred order for generation display
gen_order = ['G.I. Generation', 'Silent', 'Boomers',
             'Generation X', 'Millennials', 'Generation Z']

# Filter available generations
gen_options = ['All'] + \
    [gen for gen in gen_order if gen in df['generation'].unique()]

# Create a dropdown menu for generation selection
selected_gen = st.sidebar.selectbox(
    "Select Generation", gen_options, index=0)

# Create a checkbox to select all countries
select_all_countries = st.sidebar.checkbox("Select All Countries", value=False)

# Get a list of all countries
all_countries = sorted(df['country'].unique())

# Define default countries
default_countries = ['South Africa', 'Ireland', 'Greece', 'Norway', 'Brazil', 'Nicaragua', 'Austria',
                     'Uruguay', 'Australia', 'United States', 'Ukraine', 'Republic of Korea', 'Russian Federation']

# Create a multiselect for country selection
if select_all_countries:
    selected_countries = all_countries
    st.sidebar.multiselect(
        "Select Countries (disabled when 'All' is selected)",
        options=all_countries,
        default=[],
        disabled=True
    )

# If not selecting all, allow user to choose from the list
else:
    selected_countries = st.sidebar.multiselect(
        "Select Countries",
        options=all_countries,
        default=[country for country in default_countries if country in all_countries]
    )

# Handle errors if no country is selected
if not selected_countries:
    st.sidebar.warning("Please select at least one country.")
    st.stop()

# Filter the DataFrame based on selected filters
df_filtered = df[
    (df['country'].isin(selected_countries)) &
    (df['year'] >= selected_year_range[0]) &
    (df['year'] <= selected_year_range[1]) &
    df['population'].notna() &
    df['suicides_no'].notna() &
    (df['population'] > 0)
]

# Apply additional filters for sex based on user selections
if selected_sex != 'All':
    df_filtered = df_filtered[df_filtered['sex'] == selected_sex]

# Apply additional filters for age based on user selections
if selected_age != 'All':
    df_filtered = df_filtered[df_filtered['age'] == selected_age]

# Apply additional filters for generation based on user selections
if selected_gen != 'All':
    df_filtered = df_filtered[df_filtered['generation'] == selected_gen]

if df_filtered.empty:
    st.warning(
        "No data available for analysis. Please adjust filters and try again.")
    st.stop()


# ====================
# Key Metrics Section
# ====================

# Total number of suicides in the filtered dataset
total_suicides = df_filtered['suicides_no'].sum()
total_suicides_millions = total_suicides / 1000000

# Total population for the filtered data
total_population = df_filtered['population'].sum()

# Average suicide rate per 100k population
average_suicide_rate = (total_suicides / total_population) * 100000

# Separate data by sex
male_data = df_filtered[df_filtered['sex'] == 'male']
female_data = df_filtered[df_filtered['sex'] == 'female']

# Total suicide number for each sex
total_male_suicide = male_data['suicides_no'].sum()
total_female_suicide = female_data['suicides_no'].sum()

# Suicide rates per 100k population for males and females
male_suicide_rate = (total_male_suicide /
                     male_data['population'].sum()) * 100000
female_suicide_rate = (total_female_suicide /
                       female_data['population'].sum()) * 100000

# Calculate the suicide rate ratio
suicide_rate_ratio = male_suicide_rate / \
    female_suicide_rate if female_suicide_rate > 0 else float('inf')

# Identify the country with the highest average suicide rate
# If the filtered dataframe has zero rows, it simply sets the result to "N/A"
highest_suicide_country = df_filtered.groupby(
    'country')['suicides/100k pop'].mean().idxmax() if not df_filtered.empty else "N/A"

# Set the title for the metrics section
st.subheader("Metrics")

# Create four columns for displaying metrics
col1, col2, col3, col4 = st.columns(4)

# Function to display trend arrows and numbers for metrics
def trend_arrow_display(df, year_col, value_col, year_min, year_max):
    try:
        # Get data for the starting year and ending year
        start_data = df[df[year_col] == year_min]
        end_data = df[df[year_col] == year_max]

        # If either starting or ending data is empty, return an empty strin
        if start_data.empty or end_data.empty:
            return ""

        # Calculate the change in suicide rates
        if value_col == 'suicides_no':
            # If the column is 'suicides_no', sum suicides in both years
            start_value = start_data['suicides_no'].sum()
            end_value = end_data['suicides_no'].sum()
        elif value_col == 'suicides/100k pop':
            # If the column is 'suicides/100k pop', calculate the suicide rate per 100k
            start_value = (start_data['suicides_no'].sum(
            ) / start_data['population'].sum()) * 100000
            end_value = (end_data['suicides_no'].sum() /
                         end_data['population'].sum()) * 100000
        elif value_col == 'ratio':
            # If the column is 'ratio', calculate the gender ratio change
            start_male = start_data[start_data['sex']
                                    == 'male']['suicides_no'].sum()
            start_female = start_data[start_data['sex']
                                      == 'female']['suicides_no'].sum()
            end_male = end_data[end_data['sex'] == 'male']['suicides_no'].sum()
            end_female = end_data[end_data['sex']
                                  == 'female']['suicides_no'].sum()

            start_value = start_male / start_female if start_female > 0 else 0
            end_value = end_male / end_female if end_female > 0 else 0

        # If the start value is zero, return an empty string
        if start_value == 0:
            return ""

        # Calculate the percentage change in the value
        change = ((end_value - start_value) / start_value) * 100

        # Determine the arrow, color and background color based on the change
        arrow = "↑" if change > 0 else "↓"
        color = "#ff6ba1" if change > 0 else "#5A87E7"
        bg_color = "rgba(255, 165,190 , 0.1)" if change > 0 else "rgba(160, 200, 255, 0.1)"
        return f"<span style='font-size:0.9rem; color:{color}; background-color:{bg_color}; padding:4px 8px; border-radius:4px;'>{arrow} {abs(change):.2f}%</span>"
    except:
        # In case of any error, return an empty string
        return ""


# Get the selected year range
year_min, year_max = selected_year_range

# Display for the first metric : Total suicides
with col1:
    trend_arrow = trend_arrow_display(
        df_filtered, 'year', 'suicides_no', year_min, year_max)

    display_value = f"{total_suicides_millions:.2f}M" if total_suicides >= 1000000 else f"{
        total_suicides:,.0f}"

    # Render total suicides in millions with a trend arrow
    st.markdown(
        f'''
        <div class="metric-container">
            <div class="metric-value">{display_value}</div>
            <div class='trend-indicator'>{trend_arrow}</div>
            <div class="metric-title">Total Suicides</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

# Display for the second metric : Average suicide rate
with col2:
    trend_arrow = trend_arrow_display(
        df_filtered, 'year', 'suicides/100k pop', year_min, year_max)

    # Render average suicide rate with a trend arrow
    st.markdown(
        f'''
        <div class="metric-container">
            <div class="metric-value">{average_suicide_rate:.2f}</div>
            <div class="trend-indicator">{trend_arrow}</div>
            <div class="metric-title">Avg Suicide Rate (per 100k)</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

# Display for the third metric : Gender ratio
with col3:
    trend_arrow = trend_arrow_display(
        df_filtered, 'year', 'ratio', year_min, year_max)

    # Display ratio as "N/A" if either male or female suicides is 0
    if total_male_suicide == 0 or total_female_suicide == 0:
        ratio_text = "N/A"
    else:
        ratio_text = f"{suicide_rate_ratio:.2f}:1"

    # Render ratio with trend arrow
    st.markdown(
        f'''
        <div class="metric-container">
            <div class="metric-value">{ratio_text}</div>
            <div class="trend-indicator">{trend_arrow}</div>
            <div class="metric-title">Male : Female</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

# Calculate highest average suicide rate by country
country_rates = df_filtered.groupby('country')['suicides/100k pop'].mean()

# If data is available, find the country with the highest rate
if not df_filtered.empty:
    highest_suicide_country = country_rates.idxmax()
    highest_rate = country_rates.max()
else:
    highest_suicide_country = "N/A"
    highest_rate = 0

# Display for the fourth metric : Highest suicide rate country
with col4:
    # Adjust font size based on country name length
    font_size = "2rem" if len(highest_suicide_country) <= 10 else "1.6rem"

    # Display highest rate only if country is not "N/A"
    if highest_suicide_country != "N/A":
        rate_display = f'<div class="trend-indicator highest-rate">{
            highest_rate:.2f}/100k</div>'
    else:
        rate_display = '<div class="trend-indicator highest-rate">N/A</div>'

    # Render highest suicide rate country with value
    st.markdown(
        f'''
            <div class="metric-container">
            <div class="metric-value" style="font-size: {font_size};">{highest_suicide_country}</div>
            {rate_display}
            <div class="metric-title">Highest Suicide Rate Country</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

# ====================
# Overview Section
# ====================

# Set the title for the overview section
st.subheader("Overview")

# Create two columns
col1, col2 = st.columns(2)

# Aggregate data by country: total suicides and total population
map_data = df_filtered.groupby('country').agg(
    total_suicides=('suicides_no', 'sum'),
    total_population=('population', 'sum')
).reset_index()

# Calculate average suicide rate per 100k people
map_data['avg_rate'] = (map_data['total_suicides'] /
                        map_data['total_population']) * 100000

# --- Geographic Distribution Map ---
with col1:
    st.markdown(
        """
            <div class='chart-title'>Geographic Distribution</div>
        """, unsafe_allow_html=True)

    # Create a choropleth map showing average suicide rate by country
    fig_map = px.choropleth(
        map_data,
        locations="country",
        locationmode="country names",
        color="avg_rate",
        hover_name="country",
        hover_data={
            'avg_rate': ':.2f',
            'total_suicides': ':,',
            'country': False
        },
        color_continuous_scale=COLOR_SEQUENCE_LIGHT_TO_DARK,
        scope="world",
        labels={'avg_rate': 'Suicide Rate<br>(per 100k)',
                'total_suicides': 'Total Suicides'},
    )

    # Update layout of the map
    fig_map.update_layout(
        height=450,
        geo=dict(
            coastlinecolor="#7f8c8d",
            projection_type='miller'
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        coloraxis_colorbar=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='center',
            x=0.5,
            len=0.9,
        )
    )

    # Display the map chart
    st.plotly_chart(fig_map)

# --- High-Risk Groups Bar Chart ---
with col2:
    # Set title for high-risk group chart
    st.markdown(
        """
            <div class='chart-title'>High-Risk Groups (Top 10)</div>
        """, unsafe_allow_html=True)

    # Aggregate suicide data by country, gender, and age group
    high_risk_groups = df_filtered.groupby(['country', 'sex', 'age']).agg({
        'suicides_no': 'sum',
        'population': 'sum',
        'suicides/100k pop': 'mean'
    }).reset_index()

    # Calculate suicide rate per 100k for each group
    high_risk_groups['calculated_rate'] = (
        high_risk_groups['suicides_no'] / high_risk_groups['population']) * 100000

    # Get the top 10 groups with the highest suicide rate
    top_10_groups = high_risk_groups.nlargest(10, 'calculated_rate')

    # Sort the groups by suicide rate in ascending order
    top_10_groups = top_10_groups.sort_values(
        'calculated_rate', ascending=True)

    # Create label for each group:
    # The label format combines country, capitalized gender, and age group
    top_10_groups['group_label'] = top_10_groups.apply(
        lambda row: f"{row['country']}<br>{row['sex'].title()} ({row['age']})",
        axis=1,
        result_type='reduce'
    )

    # Create a horizontal bar chart for top 10 high-risk groups
    fig_high_risk = px.bar(
        top_10_groups,
        y='group_label',
        x='calculated_rate',
        text='calculated_rate',
        color='calculated_rate',
        labels={
            'group_label': '',
            'calculated_rate': 'Suicide Rate<br>(per 100k)',
        },
        color_continuous_scale=COLOR_SEQUENCE_LIGHT_TO_DARK,
        orientation='h'
    )

    # Set text position: all outside except the longest bar
    text_positions = ['outside'] * (len(top_10_groups) - 1) + ['inside']

    # Customize hover info and trace display
    fig_high_risk.update_traces(
        texttemplate='%{text:.2f}',
        textposition=text_positions,
        hovertemplate="<b>%{y}</b><br>" +
        "Suicide Rate: %{x:.2f}/100k<br>" +
        "Total Suicides: %{customdata[0]:,.0f}<br>" +
        "Population: %{customdata[1]:,.0f}<extra></extra>",
        customdata=top_10_groups[['suicides_no', 'population']],
    )

    # Update layout of the chart
    fig_high_risk.update_layout(
        xaxis_title="",
        yaxis_title="",
        showlegend=False,
        height=450,
        margin=dict(l=10, r=10, t=0, b=0),
        coloraxis_colorbar=dict(
            orientation='h',
            yanchor='top',
            y=-0.15,
            xanchor='center',
            x=0.4,
            len=1.2,
        )
    )

    # Display the chart
    st.plotly_chart(fig_high_risk)


# =============================
# Gender-based analysis section
# =============================

# Set the title for the gender-based analysis section
st.subheader("Gender-Based Suicide Analysis (Connected Visualizations)")

# Create two columns
col1, col2 = st.columns([3, 2])

# Multi-select widget for users to choose which chart types to display
with col1:
    chart_types = st.multiselect(
        'Select chart types to view gender-based suicide data:',
        ['Bar Chart', 'Area Chart', 'Violin Plot', 'Pie Chart'],
        default=['Bar Chart', 'Area Chart']
    )

# Radio buttons for users to choose data type
with col2:
    data_type = st.radio(
        "Select Data Type",
        ["Total Numbers", "Rate per 100k"],
        horizontal=True,
        key="gender_data_type"
    )

# Prepare base data by grouping by year and sex
base_data = df_filtered.groupby(['year', 'sex']).agg({
    'suicides_no': 'sum',
    'population': 'sum'
}).reset_index()

# Calculate suicide rate per 100,000 population
base_data['suicide_rate'] = (
    base_data['suicides_no'] / base_data['population']) * 100000

# If any chart type is selected
if chart_types:
    # Decide layout based on number of selected charts
    if len(chart_types) <= 2:
        # For 1–2 charts, show all in one row
        cols = st.columns(len(chart_types))
        chart_rows = [cols]
    else:
        # For 3–4 charts, use two rows with two columns each
        row1 = st.columns(2)
        row2 = st.columns(2)
        chart_rows = [row1, row2]

    # Loop through selected chart types
    for i, chart_type in enumerate(chart_types):
        # Determine row and column index for layout
        row_index = i // 2
        col_index = i % 2

        # Display the chart in the appropriate position
        with chart_rows[row_index][col_index]:

            # ------- Bar Chart -------
            if chart_type == 'Bar Chart':
                st.markdown(
                    "<div class='chart-title'>Gender Distribution (Bar)</div>", unsafe_allow_html=True)

                # Create grouped bar chart
                fig = px.bar(
                    base_data,
                    x='year',
                    y='suicides_no' if data_type == "Total Numbers" else 'suicide_rate',
                    color='sex',
                    barmode='group',
                    color_discrete_map={
                        'male': COLOR_SEQUENCE[-1],
                        'female': COLOR_SEQUENCE[0]
                    }
                )

                # Customize hover info
                fig.update_traces(
                    hovertemplate="<b>%{x}</b><br>" +
                    "Sex: %{data.name}<br>" +
                    ("Suicide Rate: %{y:.2f}/100k<br>" if data_type == "Rate per 100k" else "Suicides: %{y:,.0f}<br>") +
                    "<extra></extra>"
                )

                # Update y-axis label
                fig.update_layout(
                    yaxis_title="Number of Suicides" if data_type == "Total Numbers" else "Suicide Rate per 100k"
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True,
                                key=f"gender_bar_{i}")

            # ------- Area Chart -------
            elif chart_type == 'Area Chart':
                st.markdown(
                    "<div class='chart-title'>Gender Distribution (Area)</div>", unsafe_allow_html=True)

                # Create area chart
                fig = px.area(
                    base_data,
                    x='year',
                    y='suicides_no' if data_type == "Total Numbers" else 'suicide_rate',
                    color='sex',
                    color_discrete_map={
                        'male': COLOR_SEQUENCE[-1],
                        'female': COLOR_SEQUENCE[0]
                    }
                )

                # Calculate yearly total suicides for hover information
                yearly_total = df_filtered.groupby(
                    'year')['suicides_no'].sum().to_dict()

                # Customize hover info
                fig.update_traces(
                    hovertemplate="<b>%{x}</b><br>" +
                    "Sex: %{data.name}<br>" +
                    ("Suicide Rate: %{y:.2f}/100k<br>" if data_type == "Rate per 100k" else "Suicides: %{y:,.0f}<br>") +
                    "Total Suicides: %{customdata:,.0f}<br>" +
                    "<extra></extra>",
                    customdata=[yearly_total[year]
                                for year in base_data['year'].unique()]
                )

                # Update y-axis label
                fig.update_layout(
                    yaxis_title="Number of Suicides" if data_type == "Total Numbers" else "Suicide Rate per 100k"
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True,
                                key=f"gender_area_{i}")

            # ------- Violin Plot -------
            elif chart_type == 'Violin Plot':
                st.markdown(
                    "<div class='chart-title'>Gender Distribution (Violin)</div>", unsafe_allow_html=True)

                # Initialize a new plotly figure
                fig = go.Figure()

                # Create violin plot for each gender
                for sex in ['male', 'female']:
                    sex_data = base_data[base_data['sex'] == sex]
                    value_col = 'suicides_no' if data_type == "Total Numbers" else 'suicide_rate'

                    # Calculate statistical measures for hover info
                    mean_val = sex_data[value_col].mean()
                    median_val = sex_data[value_col].median()

                    # Add violin trace
                    fig.add_trace(go.Violin(
                        x=[sex.title()] * len(sex_data),
                        y=sex_data[value_col],
                        name=sex.title(),
                        box_visible=True,
                        meanline_visible=True,
                        line_color=COLOR_SEQUENCE[-1] if sex == 'male' else COLOR_SEQUENCE[0],
                        hovertemplate=(
                            "<b>%{x}</b><br>" +
                            ("Suicides: %{y:,.0f}<br>" if data_type == "Total Numbers"
                                else "Rate per 100k: %{y:.2f}<br>") +
                            f"Mean: {mean_val:,.2f}<br>" +
                            f"Median: {median_val:,.2f}<br>" +
                            "<extra></extra>"
                        )
                    ))

                # Update layout
                fig.update_layout(
                    height=380,
                    margin=dict(l=0, r=0, t=20, b=0),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    showlegend=False,
                    xaxis_title="Gender",
                    yaxis_title="Number of Suicides" if data_type == "Total Numbers" else "Suicide Rate per 100k"
                )

                # Display the violin plot
                st.plotly_chart(fig, use_container_width=True,
                                key=f"gender_violin_{i}")

            # ------- Pie Chart -------
            elif chart_type == 'Pie Chart':
                st.markdown(
                    "<div class='chart-title'>Gender Proportion (Pie)</div>", unsafe_allow_html=True)

                # Aggregate total suicides by sex
                total_by_gender = base_data.groupby(
                    'sex')['suicides_no'].sum().reset_index()

                # Create a donut-style pie chart
                fig = px.pie(
                    total_by_gender,
                    values='suicides_no',
                    names='sex',
                    color='sex',
                    color_discrete_map={
                        'male': COLOR_SEQUENCE[-1],
                        'female': COLOR_SEQUENCE[0]
                    },
                    hole=0.6,
                )

                # Customize text and hover info
                fig.update_traces(
                    textposition='inside',
                    textinfo='label+percent',
                    textfont=dict(size=14, color='white'),
                    texttemplate="%{label}<br>%{percent:.2%}",
                    hovertemplate="<b>%{label}</b><br>" +
                    "Suicides: %{value:,.0f}<br>" +
                    "Percentage: %{percent:.2%}<extra></extra>"
                )

                # Update layout
                fig.update_layout(
                    height=380,
                    margin=dict(l=0, r=0, t=20, b=0),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.1,
                        xanchor="center",
                        x=0.5
                    ),
                    annotations=[
                        dict(
                            text=f'Total<br>{
                                total_by_gender["suicides_no"].sum():,.0f}',
                            font_size=16,
                            showarrow=False
                        )
                    ]
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True,
                                key=f"gender_pie_{i}")

else:
    # Display warning if no chart types are selected
    st.warning("Please select at least one chart type.")

# ====================================================
# Suicide Trends by Age, Country & Generation section
# ====================================================

# Set the title
st.subheader(
    "Suicide Trends by Age, Country & Generation (Connected Visualizations)")

# Create two columns
col1, col2 = st.columns([3, 2])


with col1:
    # Add a multiselect widget to allow users to choose different chart types
    chart_types = st.multiselect(
        "Select visualization perspectives (at least one):",
        options=[
            "Country Comparison (Line)",
            "Generation Analysis (Bar)",
            "Age Group Distribution (Area)"
        ],
        default=["Country Comparison (Line)"],
        key="temporal_charts"
    )

# Define the order for age groups
age_order = ['5-14', '15-24', '25-34', '35-54', '55-74', '75+']

# Create a dictionary to map age groups to their labels
age_labels = {
    '5-14': '5-14 years old',
    '15-24': '15-24 years old',
    '25-34': '25-34 years old',
    '35-54': '35-54 years old',
    '55-74': '55-74 years old',
    '75+': '75+ years old'
}

with col2:
    # Add a radio button selector for data type
    data_type = st.radio(
        "Select Data Type",
        ["Total Numbers", "Rate per 100k"],
        horizontal=True
    )

# If no chart is selected, show a warning
if not chart_types:
    st.warning("Please select at least one visualization type.")
else:
    # Create dynamic layout columns based on number of selected charts
    cols = st.columns([1] * len(chart_types))

    # Iterate through each selected chart type
    for i, chart_type in enumerate(chart_types):
        with cols[i]:
            # ------- Country Comparison (Line) -------
            if chart_type == "Country Comparison (Line)":
                st.markdown(
                    "<div class='chart-title'>Country Comparison (Line)</div>", unsafe_allow_html=True)

                # Group data by year and country
                country_data = df_filtered.groupby(['year', 'country']).agg({
                    'suicides_no': 'sum',
                    'population': 'sum'
                }).reset_index()

                # Calculate suicide rate or total numbers based on user selection
                if data_type == "Rate per 100k":
                    country_data['value'] = (
                        country_data['suicides_no'] / country_data['population']) * 100000
                    y_title = "Suicide Rate per 100k"
                else:
                    country_data['value'] = country_data['suicides_no']
                    y_title = "Number of Suicides"

                # Create line chart
                fig = px.line(
                    country_data,
                    x='year',
                    y='value',
                    color='country',
                    markers=True
                )

                # Create an optional checkbox to show or hide legend
                show_legend = st.checkbox(
                    "Show Legend", value=False, key=f"legend_{i}")

                fig.update_traces(
                    hovertemplate="<b>%{data.name}</b><br>" +
                    "Year: %{x}<br>" +
                    ("Suicide Rate: %{y:.2f}/100k<br>" if data_type == "Rate per 100k"
                     else "Suicides: %{y:,}<br>") +
                    "<extra></extra>"
                )

                # Update layout
                fig.update_layout(
                    height=380,
                    margin=dict(t=0, b=0, l=0, r=0),
                    xaxis_title="Year",
                    yaxis_title=y_title,
                    legend_title="Country",
                    showlegend=show_legend
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)

            # ------- Generation Analysis (Bar) -------
            elif chart_type == "Generation Analysis (Bar)":
                st.markdown(
                    "<div class='chart-title'>Suicide Trends by Generation (Bar)</div>", unsafe_allow_html=True)

                # Group data by year and generation
                gen_data = df_filtered.groupby(['year', 'generation']).agg({
                    'suicides_no': 'sum',
                    'population': 'sum'
                }).reset_index()

                # Calculate suicide rate or total numbers based on user selection
                if data_type == "Rate per 100k":
                    gen_data['value'] = (
                        gen_data['suicides_no'] / gen_data['population']) * 100000
                    y_title = "Suicide Rate per 100k"
                else:
                    gen_data['value'] = gen_data['suicides_no']
                    y_title = "Number of Suicides"

                # Create a bar chart
                fig = px.bar(
                    gen_data,
                    x='year',
                    y='value',
                    color='generation',
                    barmode='stack',
                    color_discrete_sequence=COLOR_SEQUENCE,
                    category_orders={'generation': gen_order}
                )

                # Create an optional checkbox to show or hide legend
                show_legend = st.checkbox(
                    "Show Legend", value=False, key=f"legend_{i}")

                fig.update_traces(
                    hovertemplate="<b>%{data.name}</b><br>" +
                    "Year: %{x}<br>" +
                    ("Suicide Rate: %{y:.2f}/100k<br>" if data_type == "Rate per 100k"
                     else "Suicides: %{y:,}<br>") +
                    "<extra></extra>"
                )

                # Update layout
                fig.update_layout(
                    height=370,
                    margin=dict(t=0, b=0, l=0, r=0),
                    xaxis_title="Year",
                    yaxis_title=y_title,
                    legend_title="Generation",
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.3,
                        xanchor="center",
                        x=0.5,
                    ),
                    showlegend=show_legend
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)

            # ------- Age Group Distribution (Area) -------
            elif chart_type == "Age Group Distribution (Area)":
                st.markdown(
                    "<div class='chart-title'>Age Trends Over Time (Area)</div>", unsafe_allow_html=True)

                # Group data by year and age
                age_time_data = df_filtered.groupby(['year', 'age']).agg({
                    'suicides_no': 'sum',
                    'population': 'sum'
                }).reset_index()

                # Calculate suicide rate if selected
                if data_type == "Rate per 100k":
                    age_time_data['value'] = (
                        age_time_data['suicides_no'] / age_time_data['population']) * 100000
                    y_title = "Suicide Rate per 100k"
                else:
                    age_time_data['value'] = age_time_data['suicides_no']
                    y_title = "Number of Suicides"

                # Create area chart
                fig = px.area(
                    age_time_data,
                    x='year',
                    y='value',
                    color='age',
                    category_orders={'age': age_order},
                    color_discrete_sequence=COLOR_SEQUENCE,
                )

                # Customize hover info
                fig.update_traces(
                    hovertemplate="%{data.name}</br>" +
                    ("Suicide Rate: %{y:.2f}/100k<br>" if data_type ==
                     "Rate per 100k" else "Suicides: %{y:,}<br>") + "<extra></extra>"
                )

                # Create an optional checkbox to show or hide legend
                show_legend = st.checkbox(
                    "Show Legend", value=False, key=f"legend_{i}")

                # Update layout
                fig.update_layout(
                    height=370,
                    margin=dict(t=0, b=0, l=0, r=0),
                    xaxis_title="Year",
                    yaxis_title=y_title,
                    legend_title="Age Group",
                    hovermode='x unified',
                    hoverlabel=dict(bgcolor="white"),
                    legend=dict(
                        orientation="h",
                        yanchor="top",
                        y=-0.3,
                        xanchor="center",
                        x=0.5
                    ),
                    showlegend=show_legend
                )

                # Display the chart
                st.plotly_chart(fig, use_container_width=True)

# ====================
# Economic and Demographic Factors Behind Suicide Rates section
# ====================

# Set the title
st.subheader(
    "Economic and Demographic Factors Behind Suicide Rates")

# Create two columns
col1, col2 = st.columns([4, 5])

with col1:
    st.markdown(
        """
        <div class='chart-title'>Suicide Flow by GDP Level and Age</div>
        """,
        unsafe_allow_html=True
    )

    # Prepare the dataset for the Sankey diagram
    gdp_age_sankey = df_filtered.copy()

    # Categorize GDP per capita into 4 quartiles with labels
    gdp_age_sankey['gdp_level'] = pd.qcut(
        gdp_age_sankey['gdp_per_capita ($)'],
        q=4,
        labels=['Low GDP', 'Medium-Low GDP', 'Medium-High GDP', 'High GDP']
    )

    # Categorize suicide rates into 3 levels
    gdp_age_sankey['suicide_level'] = pd.qcut(
        gdp_age_sankey['suicides/100k pop'],
        q=3,
        labels=['Low Rate', 'Medium Rate', 'High Rate']
    )

    # Aggregate data by GDP level, age group, and suicide rate
    flow_data = gdp_age_sankey.groupby(['gdp_level', 'age', 'suicide_level'])[
        'suicides_no'].sum().reset_index()

    # Prepare data for the two flows: GDP → Age and Age → Suicide Rate
    gdp_age_flow = flow_data.groupby(['gdp_level', 'age'])[
        'suicides_no'].sum().reset_index()
    age_suicide_flow = flow_data.groupby(['age', 'suicide_level'])[
        'suicides_no'].sum().reset_index()

    # Generate unique node names and mapping IDs for Sankey diagram
    gdp_levels = sorted(flow_data['gdp_level'].unique())
    age_groups = [age for age in age_order if age in flow_data['age'].unique()]
    suicide_levels = sorted(flow_data['suicide_level'].unique())

    all_nodes = gdp_levels + age_groups + suicide_levels
    node_to_id = {node: idx for idx, node in enumerate(all_nodes)}

    # Initialize source, target, and value lists for Sankey links
    source = []
    target = []
    value = []

    # Build the flow from GDP levels to Age groups
    for _, row in gdp_age_flow.iterrows():
        source.append(node_to_id[row['gdp_level']])
        target.append(node_to_id[row['age']])
        value.append(row['suicides_no'])

    # Build the flow from Age groups to Suicide Rate levels
    for _, row in age_suicide_flow.iterrows():
        source.append(node_to_id[row['age']])
        target.append(node_to_id[row['suicide_level']])
        value.append(row['suicides_no'])

    # Set color for nodes
    gdp_colors = [COLOR_SEQUENCE[0]] * len(gdp_levels)
    age_colors = [COLOR_SEQUENCE[-2]] * len(age_groups)
    suicide_colors = [COLOR_SEQUENCE[-1]] * len(suicide_levels)
    node_colors = gdp_colors + age_colors + suicide_colors

    # Adjust link opacity based on suicide counts
    max_value = max(value)
    min_value = min(value)

    link_colors = []
    for v, s in zip(value, source):
        opacity = 0.3 + 0.5 * \
            ((v - min_value) / (max_value - min_value))
        if s < len(gdp_levels):
            color = f'rgba(255, 107, 161, {opacity:.2f})'
        elif s < len(gdp_levels) + len(age_groups):
            color = f'rgba(111, 184, 255, {opacity:.2f})'
        else:
            color = f'rgba(90, 135, 231, {opacity:.2f})'
        link_colors.append(color)

    # Create Sankey diagram
    fig_gdp_sankey = go.Figure(
        data=[go.Sankey(
            arrangement="snap",
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color="white", width=0.5),
                label=all_nodes,
                color=node_colors,
            ),
            textfont=dict(
                color="black",
                size=15,
            ),
            link=dict(
                source=source,
                target=target,
                value=value,
                color=link_colors,
                hovertemplate='%{source.label} → %{target.label}<br>Suicides: %{value:,.0f}<extra></extra>')
        )])

    # Update layout
    fig_gdp_sankey.update_layout(
        height=550,
        margin=dict(l=10, r=10, t=30, b=20)
    )

    # Display the diagram
    st.plotly_chart(fig_gdp_sankey, use_container_width=True)

# ------- GDP per Capita vs Suicide Rate -------
with col2:
    st.markdown("""
    <div class ='chart-title'>GDP per Capita vs Suicide Rate</div>
    """, unsafe_allow_html=True)

    # Aggregate data by country and year
    gdp_suicide_data = df_filtered.groupby(['country', 'year']).agg({
        'suicides_no': 'sum',
        'gdp_per_capita ($)': 'mean',
        'population': 'sum'
    }).reset_index()

    # Further aggregate by country
    bubble_data = gdp_suicide_data.groupby('country').agg({
        'gdp_per_capita ($)': 'mean',
        'suicides_no': 'sum',
        'population': 'sum'
    }).reset_index()

    # Calculate suicide rate per 100k / pop
    bubble_data['suicides/100k pop'] = (
        bubble_data['suicides_no'] / bubble_data['population']) * 100000

    # Filter countries from the sidebar
    bubble_data = bubble_data[bubble_data['country'].isin(selected_countries)]

    # Set a checkbox for displaying country names
    show_country_names = st.checkbox('Display country name', value=True)

    # Create a bubble scatter plot
    fig_bubble = px.scatter(
        bubble_data,
        x='gdp_per_capita ($)',
        y='suicides/100k pop',
        size='population',
        color='suicides/100k pop',
        text='country' if show_country_names else None,
        color_continuous_scale=COLOR_SEQUENCE_LIGHT_TO_DARK,
        size_max=70,
    )

    # Update layout
    fig_bubble.update_layout(
        height=520,
        xaxis_title='GDP per Capita',
        yaxis_title='Suicide Rate per 100k',
        coloraxis_colorbar=dict(
            title='Suicide Rate per 100k',
            tickformat='.0f',
            orientation='h',
            yanchor='top',
            y=-0.2,
            x=0.5,
            len=0.9
        ),
        showlegend=False
    )

    # Update hover template
    fig_bubble.update_traces(
        marker=dict(
            sizemode='area',
            opacity=0.7
        ),
        customdata=np.column_stack((
            bubble_data['country'],
            bubble_data['population'],
            bubble_data['gdp_per_capita ($)'],
            bubble_data['suicides/100k pop']
        )),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>" +
            "GDP per Capita: $%{customdata[2]:,.0f}<br>" +
            "Suicide Rate: %{customdata[3]:.2f}/100k<br>" +
            "Population: %{customdata[1]:,.0f}<extra></extra>"
        )
    )


    # If country names are shown, set the text position
    if show_country_names:
        fig_bubble.update_traces(
            textposition='top center'
        )

    # Display the chart
    st.plotly_chart(fig_bubble, use_container_width=True)

# ====================================
# Country Comparison Analysis section
# ====================================

# Set the title
st.subheader("Country Comparison Analysis (Conditional Content)")

# Filter data to include only selected countries from the sidebar
df_comparison = df_filtered[df_filtered['country'].isin(selected_countries)]

# Calculate total suicides and average GDP for each country
total_suicides = df_comparison.groupby('country').agg({
    'suicides_no': 'sum',
    'gdp_per_capita ($)': 'mean',
    'gdp_for_year ($)': 'mean'
}).reset_index()

# Get the latest year for each country in the filtered dataset
max_year_by_country = df_comparison.groupby('country')['year'].max()

# Get population data for each country's latest year
population_data = df_comparison[
    df_comparison.apply(lambda x: x['year'] == max_year_by_country[x['country']], axis=1)
].groupby('country')['population'].sum().reset_index()

# Merge suicide and population data
country_summary = pd.merge(total_suicides, population_data, on='country', how='outer')

# Fill any missing values with 0
country_summary = country_summary.fillna(0)

# Calculate suicide rate per 100k population
country_summary['suicide_rate'] = np.where(
    country_summary['population'] > 0,
    (country_summary['suicides_no'] / country_summary['population']) * 100000,
    0
)

# Set a selectbox for the first country
country1 = st.selectbox(
    "Select the first country:",
    options=sorted(country_summary['country'].unique()),
    key='country1'
)

# Get the selected country's summary data
country1_data = country_summary[country_summary['country'] == country1].iloc[0]

# Display key metrics for the first country
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Population", f"{country1_data['population']:,}")
with col2:
    st.metric("Suicide Rate (per 100k)",
              f"{country1_data['suicide_rate']:.2f}")

# Set a selectbox for the second country
country2 = st.selectbox(
    "Select the second country:",
    options=sorted(country_summary['country'].unique()),
    key='country2'
)

# Get the selected country's summary data
country2_data = country_summary[country_summary['country'] == country2].iloc[0]

# Display key metrics for the second country
col1, col2 = st.columns(2)
with col1:
    st.metric("Total Population", f"{country2_data['population']:,}")
with col2:
    st.metric("Suicide Rate (per 100k)",
              f"{country2_data['suicide_rate']:.2f}")

# Create a checkbox to display or hide detailed comparison metrics
show_details = st.checkbox("Show detailed comparison metrics", value=False)

if show_details:
    # Calculate total female and male suicides for each country
    female_suicides1 = df_filtered[
        (df_filtered['country'] == country1) &
        (df_filtered['sex'] == 'female')]['suicides_no'].sum()

    male_suicides1 = df_filtered[
        (df_filtered['country'] == country1) &
        (df_filtered['sex'] == 'male')]['suicides_no'].sum()

    female_suicides2 = df_filtered[
        (df_filtered['country'] == country2) &
        (df_filtered['sex'] == 'female')]['suicides_no'].sum()

    male_suicides2 = df_filtered[
        (df_filtered['country'] == country2) &
        (df_filtered['sex'] == 'male')]['suicides_no'].sum()

    # Calculate male-to-female suicide ratio
    gender_ratio1 = "N/A" if female_suicides1 == 0 else f"{
        (male_suicides1 / female_suicides1):.2f}:1"
    gender_ratio2 = "N/A" if female_suicides2 == 0 else f"{
        (male_suicides2 / female_suicides2):.2f}:1"

    # Create a metrics dictionary for structured display
    metrics = {
        'Suicide Rate': [
            f"{country1_data['suicide_rate']:.2f}/100k",
            f"{country2_data['suicide_rate']:.2f}/100k"
        ],
        'Total Suicides': [
            f"{country1_data['suicides_no']:,}",
            f"{country2_data['suicides_no']:,}"
        ],
        'GDP per Capita': [
            f"${country1_data['gdp_per_capita ($)']:,.0f}",
            f"${country2_data['gdp_per_capita ($)']:,.0f}"
        ],
        'Total GDP': [
            f"${country1_data['gdp_for_year ($)']:,.0f}",
            f"${country2_data['gdp_for_year ($)']:,.0f}"
        ],
        'Male : Female': [
            gender_ratio1,
            gender_ratio2
        ]
    }

    # Set the title
    st.markdown(
        f''' <div class="chart-title">Detailed Comparison</div>''',
        unsafe_allow_html=True
    )

    # Display the metrics
    for metric, values in metrics.items():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(
                f'''
                <div class="metric-container" style="height: 120px;">
                    <div class="metric-title">{country1}</div>
                    <div class="metric-value">{values[0]}</div>
                    <div class="metric-title">{metric}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )
        with col2:
            st.markdown(
                f'''
                <div class="metric-container" style="height: 120px;">
                    <div class="metric-title">{country2}</div>
                    <div class="metric-value">{values[1]}</div>
                    <div class="metric-title">{metric}</div>
                </div>
                ''',
                unsafe_allow_html=True
            )

# =============================
# Suicide Dataset View section
# =============================

# Set the title
st.subheader("Suicide Dataset View")

# Display the filtered dataset as an interactive table
st.dataframe(
    df_filtered,
    column_config={
        "suicides_no": st.column_config.NumberColumn(
            "Suicides",
            format="%d",
        ),
        "suicides/100k pop": st.column_config.NumberColumn(
            "Suicide Rate / 100k",
            format="%.2f",
        ),
        "gdp_for_year ($)": st.column_config.NumberColumn(
            "Total GDP",
            format="$%d",
        ),
        "gdp_per_capita ($)": st.column_config.NumberColumn(
            "GDP per Capita",
            format="$%.0f",
        ),
    },
    hide_index=True,
    use_container_width=True
)
