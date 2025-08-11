import streamlit as st
import pandas as pd
import plotly.express as px

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("Electric_Vehicle_Population_Data.csv")
    df.dropna(subset=["Model Year", "Make", "Electric Vehicle Type"], inplace=True)
    df["Model Year"] = pd.to_datetime(df["Model Year"], format="%Y")
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filters")

# Year Range Slider
min_year = int(df["Model Year"].dt.year.min())
max_year = int(df["Model Year"].dt.year.max())
start_year, end_year = st.sidebar.slider("Select Model Year Range", min_year, max_year, (min_year, max_year))

# Country Selection (If Available)
if "Country" in df.columns:
    selected_countries = st.sidebar.multiselect("Select Country", df["Country"].unique())
else:
    selected_countries = []

# City Selection (If Available)
if "City" in df.columns:
    selected_cities = st.sidebar.multiselect("Select City", df["City"].unique())
else:
    selected_cities = []

# Manufacturer Selection
selected_brands = st.sidebar.multiselect("Select Manufacturers", df["Make"].unique())

# Filter Dataset
df_filtered = df[(df["Model Year"].dt.year >= start_year) & (df["Model Year"].dt.year <= end_year)]
if selected_countries:
    df_filtered = df_filtered[df_filtered["Country"].isin(selected_countries)]
if selected_cities:
    df_filtered = df_filtered[df_filtered["City"].isin(selected_cities)]
if selected_brands:
    df_filtered = df_filtered[df_filtered["Make"].isin(selected_brands)]

# Dashboard Title
st.title("🚗 **EV Market Dashboard**")
st.write("📊 **Explore Electric Vehicle Trends with Interactive Visualizations!**")

# Check for missing columns before plotting
available_columns = df_filtered.columns

# No Data Warning
if df_filtered.empty:
    st.warning("⚠️ No data available for the selected filters.")
else:
    # 1️⃣ **EV Adoption Over the Years (Full-Width)**
    adoption_trend = df_filtered.groupby(df_filtered["Model Year"].dt.year).size().reset_index(name="Count")

    fig1 = px.bar(adoption_trend, y="Count", x="Model Year", orientation='v', text_auto=True, 
                  title="📈 EV Adoption Over the Years (Inverted)")

    st.plotly_chart(fig1, use_container_width=True)  # ✅ Full-width chart



    col3, col4 = st.columns(2)

   # 3️⃣ **EVs by Battery Type (Pie Chart - Fixed)**
    if "Electric Vehicle Type" in available_columns and not df_filtered["Electric Vehicle Type"].isna().all():
        with col3:
            fig3 = px.pie(df_filtered, names="Electric Vehicle Type", title="🔋 EVs by Battery Type")
            st.plotly_chart(fig3, use_container_width=True)
    else:
        with col3:
            st.warning("⚠️ No valid data for Electric Vehicle Type.")

    # 4️⃣ **Top 10 EV Manufacturers (Bar Chart - Inverted)**
    top_makes = df_filtered["Make"].value_counts().nlargest(10).reset_index()
    top_makes.columns = ["Manufacturer", "Count"]
    with col4:
        fig4 = px.bar(top_makes, x="Count", y="Manufacturer", orientation='h', text_auto=True, 
                      title="🏆 Top 10 EV Manufacturers (Inverted)")
        st.plotly_chart(fig4, use_container_width=True)

    col5, col6 = st.columns(2)

    # 5️⃣ **Top 10 Models by Manufacturer (Bar Chart w/ Legend)**
    top_models = df_filtered.groupby(["Make", "Model"]).size().reset_index(name="Count")
    top_models = top_models.nlargest(10, "Count")
    with col5:
        fig5 = px.bar(top_models, x="Count", y="Model", color="Make", orientation='h',
                      title="🚗 Top 10 Models by Manufacturer")
        st.plotly_chart(fig5, use_container_width=True)

    # 6️⃣ **Avg. Electric Range by Model Year (Line Chart)**
    range_col = next((col for col in available_columns if "range" in col.lower()), None)
    if range_col:
        avg_range = df_filtered.groupby(df_filtered["Model Year"].dt.year)[range_col].mean().reset_index()
        with col6:
            fig6 = px.line(avg_range, x="Model Year", y=range_col, markers=True, 
                           title="🔋 Avg. Electric Range by Year")
            st.plotly_chart(fig6, use_container_width=True)

    col7, col8 = st.columns(2)

    # 7️⃣ **Top 10 Models by Manufacturer Based on Range (Bar Chart w/ Legend - Inverted)**
    if range_col:
        top_range_models = df_filtered.groupby(["Make", "Model"])[range_col].max().reset_index()
        top_range_models = top_range_models.nlargest(10, range_col)
        with col7:
            fig7 = px.bar(top_range_models, x=range_col, y="Model", color="Make", orientation='h',
                          title="🔝 Top 10 Models by Manufacturer (Electric Range)")
            st.plotly_chart(fig7, use_container_width=True)

    # 8️⃣ **Current & Estimated EV Market Growth (Line Chart)**
    sales_trend = df_filtered.groupby(df_filtered["Model Year"].dt.year).size().reset_index(name="Count")
    sales_trend["Projected"] = sales_trend["Count"].rolling(2).mean()  # Simple Moving Avg for Projection
    with col8:
        fig8 = px.line(sales_trend, x="Model Year", y=["Count", "Projected"], markers=True,
                       title="📈 Current & Estimated EV Market Growth")
        st.plotly_chart(fig8, use_container_width=True)

    # 9️⃣ **EV Type Distribution Over Time (Stacked Area Chart)**
    if "Electric Vehicle Type" in available_columns:
        ev_type_trend = df_filtered.groupby(["Model Year", "Electric Vehicle Type"]).size().reset_index(name="Count")
        fig9 = px.area(ev_type_trend, x="Model Year", y="Count", color="Electric Vehicle Type",
                       title="⚡ EV Type Distribution Over Time")
        st.plotly_chart(fig9, use_container_width=True)

# 📥 **Download Filtered Data**
st.markdown("### 📩 Download Data")
st.download_button(label="Download Filtered Data as CSV", data=df_filtered.to_csv(index=False),
                   file_name="filtered_EV_data.csv", mime="text/csv")

# Footer
st.markdown("---")
st.markdown("🔹 **Built with Streamlit & Plotly** | 📅 **Data Source: EV Dataset**")
