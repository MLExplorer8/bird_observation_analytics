import streamlit as st
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px

# Load data from SQLite DB
@st.cache_data
def load_data():
    
    conn = sqlite3.connect(r"D:\mini_project_sport_analytics\aiml_birds_analysis\bird_observations.db")
    df = pd.read_sql_query("SELECT * FROM observations", conn)
    conn.close()
    return df

df = load_data()

# Sidebar for navigation
st.sidebar.title("Bird Observation Analysis")
page = st.sidebar.radio("Select Analysis", [
    "Species Distribution",
    "Temporal Analysis",
    "Spatial Analysis",
    "Species Analysis",
    "Environmental Conditions",
    "Distance & Behavior",
    "Conservation Insights"
])

# === 1. Species Distribution ===
if page == "Species Distribution":
    st.title("Species Distribution by Admin Unit and Habitat Type")

    # Step 1: Count unique species for each Admin Unit and Location Type
    species_dist = (
        df.groupby(['Admin_Unit_Code', 'Location_Type'])['Scientific_Name']
        .nunique()
        .reset_index(name='Species_Count')
    )

    # Step 2: Plot stacked bar chart using Plotly
    fig = px.bar(
        species_dist,
        x='Admin_Unit_Code',
        y='Species_Count',
        color='Location_Type',
        barmode='stack',
        title="Species Distribution by Habitat Type Across All Admin Units"
    )
    fig.update_layout(xaxis_title='Admin Unit', yaxis_title='Unique Species Count')

    st.plotly_chart(fig, use_container_width=True)

# === 2. Temporal Analysis ===
elif page == "Temporal Analysis":
    st.title("Bird Observation Frequency Over Time")

    # Ensure Date column is datetime
    df['Date'] = pd.to_datetime(df['Date'])

    # Sidebar filters
    admin_options = df['Admin_Unit_Code'].dropna().unique().tolist()
    selected_admin = st.selectbox("Select Admin Unit", ["All"] + sorted(admin_options))

    species_options = df['Scientific_Name'].dropna().unique().tolist()
    selected_species = st.selectbox("Select Species", ["All"] + sorted(species_options))

    # Apply filters
    filtered_df = df.copy()
    if selected_admin != "All":
        filtered_df = filtered_df[filtered_df['Admin_Unit_Code'] == selected_admin]
    if selected_species != "All":
        filtered_df = filtered_df[filtered_df['Scientific_Name'] == selected_species]

    # Group by date
    daily_counts = filtered_df.groupby('Date').size().reset_index(name='Observation Count')

    # Plot
    fig = px.line(
        daily_counts,
        x='Date',
        y='Observation Count',
        title="Observation Frequency Over Time",
        labels={'Date': 'Date', 'Observation Count': 'Number of Observations'}
    )

    fig.update_layout(bargap= 1)  # Increase gap between bars (default is 0.1)
    st.plotly_chart(fig)



# === 3. Spatial Analysis ===
elif page == "Spatial Analysis":
    st.title("Biodiversity by Location Type and Plot")

    # Unique species by Location_Type
    location_group = df.groupby('Location_Type')['Scientific_Name'].nunique().reset_index()
    fig1 = px.bar(
        location_group,
        x='Location_Type',
        y='Scientific_Name',
        color='Location_Type',
        title="Unique Species by Location Type"
    )
    fig1.update_layout(bargap=0.6)  # Increase gap between bars to reduce width
    st.plotly_chart(fig1)

    # Top 10 plots by species diversity
    plot_group = (
        df.groupby('Plot_Name')['Scientific_Name']
        .nunique()
        .reset_index()
        .sort_values(by='Scientific_Name', ascending=False)
        .head(10)
    )
    fig2 = px.bar(
        plot_group,
        x='Plot_Name',
        y='Scientific_Name',
        title="Top 10 Plots by Species Diversity"
    )
    fig2.update_layout(xaxis_tickangle=45)
    st.plotly_chart(fig2)


# === 4. Species Analysis ===
elif page == "Species Analysis":
    st.title("Species Diversity and Activity Patterns")

    # Sex Ratio for Top 10 Species (static with Seaborn)
    st.subheader("Sex Ratio by Species")
    import matplotlib.pyplot as plt
    import seaborn as sns

    top_species = df['Scientific_Name'].value_counts().head(10).index
    subset = df[df['Scientific_Name'].isin(top_species)]
    sex_counts = subset.groupby(['Scientific_Name', 'Sex']).size().reset_index(name='Count')

    plt.figure(figsize=(12, 5))
    sns.barplot(data=sex_counts, x='Scientific_Name', y='Count', hue='Sex')
    plt.xticks(rotation=45, ha='right')
    plt.title("Sex Ratio for Top 10 Species")
    st.pyplot(plt.gcf())  # Show the static plot

    # ID Method Distribution (now as Pie Chart)
    st.subheader("Activity Patterns by ID Method")

    # Prepare data
    id_df = df['ID_Method'].value_counts().reset_index()
    id_df.columns = ['ID_Method', 'Count']

    # Create pie chart
    fig_id = px.pie(
        id_df,
        names='ID_Method',
        values='Count',
        title="Observation Methods by ID",
        color_discrete_sequence=px.colors.sequential.RdBu
    )

    st.plotly_chart(fig_id)




# === 5. Environmental Conditions ===
elif page == "Environmental Conditions":
    st.title("Environmental Impact within Admin Unit")

    # Dropdown to select Admin Unit
    admin_unit_selected = st.selectbox("Select Admin Unit:", sorted(df['Admin_Unit_Code'].unique()))

    # Filter the DataFrame based on selected Admin Unit
    filtered_df = df[df['Admin_Unit_Code'] == admin_unit_selected]

    # Group by Date to compute Observation Count, Avg Temp, Avg Humidity
    env_summary = filtered_df.groupby('Date').agg(
        Observation_Count=('Scientific_Name', 'count'),
        Avg_Temperature=('Temperature', 'mean'),
        Avg_Humidity=('Humidity', 'mean')
    ).reset_index()

    # --- Scatter plot for Temperature
    st.subheader("Temperature vs Observation Count")
    fig_temp = px.scatter(
        env_summary,
        x='Avg_Temperature',
        y='Observation_Count',
        color='Observation_Count',
        color_continuous_scale='Viridis',
        title=f"Effect of Temperature on Bird Observations in {admin_unit_selected}",
        labels={'Avg_Temperature': 'Average Temperature (°C)', 'Observation_Count': 'Observation Count'}
    )
    st.plotly_chart(fig_temp)

    # --- Scatter plot for Humidity
    st.subheader("Humidity vs Observation Count")
    fig_hum = px.scatter(
        env_summary,
        x='Avg_Humidity',
        y='Observation_Count',
        color='Observation_Count',
        color_continuous_scale='Blues',
        title=f"Effect of Humidity on Bird Observations in {admin_unit_selected}",
        labels={'Avg_Humidity': 'Average Humidity (%)', 'Observation_Count': 'Observation Count'}
    )
    st.plotly_chart(fig_hum)
    st.subheader("Sky vs Wind Heatmap")
    fig, ax = plt.subplots(figsize=(10, 6))
    cross_tab = pd.crosstab(df['Sky'], df['Wind'])
    sns.heatmap(cross_tab, annot=True, fmt='d', cmap='YlGnBu', ax=ax)
    plt.title("Observation Count by Sky and Wind Conditions")
    plt.xlabel("Wind")
    plt.ylabel("Sky")
    plt.tight_layout()
    st.pyplot(fig)




# === 6. Distance and Behavior ===
elif page == "Distance & Behavior":
    st.subheader("Heatmap: ID Method × Distance")
    heatmap_df = df.groupby(['ID_Method', 'Distance']).size().unstack().fillna(0)
    if not heatmap_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(heatmap_df, annot=True, fmt='g', cmap='YlGnBu', ax=ax)
        st.pyplot(fig)
    else:
        st.warning("No data available for heatmap visualization.")



# === 7. Conservation Insights ===
elif page == "Conservation Insights":
    st.subheader("Least Observed Species (Top 10)")
    least_observed = df['Scientific_Name'].value_counts().sort_values().head(10).reset_index()
    least_observed.columns = ['Scientific_Name', 'Observation_Count']
    least_observed['Observation_Count'] = least_observed['Observation_Count'].astype(int)

    # Display as table instead of bar chart
    st.dataframe(least_observed.style.format({'Observation_Count': '{:,.0f}'}))
