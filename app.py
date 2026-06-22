import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "plotly"])
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# Page configuration
st.set_page_config(page_title="Local Food Wastage Management System", layout="wide", page_icon="🍏")

# Database Connection Helper
def get_db_connection():
    conn = sqlite3.connect('food_wastage.db')
    conn.row_factory = sqlite3.Row
    return conn

# Database Initialization
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS food_listings (
        Food_ID INTEGER PRIMARY KEY AUTOINCREMENT,
        Food_Name TEXT,
        Quantity INTEGER,
        Location TEXT,
        Food_Type TEXT,
        Meal_Type TEXT,
        Provider_Name TEXT,
        Provider_Type TEXT,
        Status TEXT DEFAULT 'Available'
    )''')
    cursor.execute("SELECT COUNT(*) FROM food_listings")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            (1, 'Pasta Trays', 25, 'New York', 'Vegetarian', 'Dinner', 'Delish Bistro', 'Restaurant', 'Available'),
            (2, 'Assorted Sandwiches', 40, 'Los Angeles', 'Non-Vegetarian', 'Snacks', 'SuperMart Foods', 'Supermarket', 'Available'),
            (3, 'Organic Apples', 15, 'New York', 'Vegan', 'Breakfast', 'Green Grocers', 'Grocery Store', 'Available'),
            (4, 'Buffet Trays', 30, 'Chicago', 'Non-Vegetarian', 'Lunch', 'Hotel Regal', 'Hotel', 'Available'),
            (5, 'Baked Goods', 10, 'New York', 'Vegetarian', 'Lunch', 'Delish Bistro', 'Restaurant', 'Available'),
            (6, 'Rice & Curry', 50, 'Chicago', 'Vegan', 'Dinner', 'Metro Eats', 'Restaurant', 'Available')
        ]
        cursor.executemany('''INSERT INTO food_listings 
            (Food_ID, Food_Name, Quantity, Location, Food_Type, Meal_Type, Provider_Name, Provider_Type, Status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', sample_data)
        conn.commit()
    conn.close()

init_db()

st.title("🍏 Local Food Wastage Management System")

# Fetch data
conn = get_db_connection()
df_all = pd.read_sql_query("SELECT * FROM food_listings", conn)
conn.close()

# SIDEBAR
st.sidebar.header("🔍 System-Wide Filtering")
cities = ["All"] + sorted(list(df_all['Location'].unique())) if not df_all.empty else ["All"]
filter_city = st.sidebar.selectbox("Filter Location (City)", cities)

df_filtered = df_all.copy()
if filter_city != "All":
    df_filtered = df_filtered[df_filtered['Location'] == filter_city]

# TABS
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Strategic Analytics Dashboard", 
    "🛠️ Operational CRUD Control Panel", 
    "📈 Advanced EDA Insights", 
    "🗄️ SQL Core Query Engine"
])

with tab1:
    st.header("📋 Platform Strategic Overview")
    m1, m2, m3 = st.columns(3)
    m1.metric("Filtered Active Listings", len(df_filtered))
    m2.metric("Total Food Volume Units", f"{df_filtered['Quantity'].sum()} units")
    m3.metric("Active Providers Listed", df_filtered['Provider_Name'].nunique() if not df_filtered.empty else 0)
    st.write("---")
    st.dataframe(df_filtered, use_container_width=True)

with tab2:
    st.header("🛠️ Database Entry Records Management (CRUD)")
    crud_action = st.radio("Select Database Action:", ["Create", "Read", "Update", "Delete"], horizontal=True)
    if crud_action == "Create":
        with st.form("add_form"):
            f_name = st.text_input("Food Item Name")
            f_qty = st.number_input("Quantity", min_value=1, value=10)
            f_loc = st.text_input("City Location", value="New York")
            f_prov = st.text_input("Provider Name", value="Delish Bistro")
            f_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            m_type = st.selectbox("Meal Category", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            f_p_type = st.selectbox("Provider Class", ["Restaurant", "Grocery Store", "Supermarket", "Hotel"])
            if st.form_submit_button("Commit Entry to Database"):
                if f_name:
                    conn = get_db_connection()
                    conn.execute('''INSERT INTO food_listings (Food_Name, Quantity, Location, Food_Type, Meal_Type, Provider_Name, Provider_Type)
                                    VALUES (?, ?, ?, ?, ?, ?, ?)''', (f_name, f_qty, f_loc, f_type, m_type, f_prov, f_p_type))
                    conn.commit()
                    conn.close()
                    st.success("🎉 Entry successfully added!")
                    st.rerun()
    elif crud_action == "Read":
        st.dataframe(df_all, use_container_width=True)
    elif crud_action == "Update":
        if not df_all.empty:
            target_id = st.selectbox("Select Food_ID to Modify:", df_all['Food_ID'].tolist())
            new_qty = st.number_input("Input Revised Quantity:", min_value=0, value=20)
            if st.button("Apply Adjustment"):
                conn = get_db_connection()
                conn.execute("UPDATE food_listings SET Quantity = ? WHERE Food_ID = ?", (new_qty, target_id))
                conn.commit()
                conn.close()
                st.success("Quantity updated successfully.")
                st.rerun()
    elif crud_action == "Delete":
        if not df_all.empty:
            target_id = st.selectbox("Select Food_ID to Remove Permanently:", df_all['Food_ID'].tolist())
            if st.button("Execute Purge Process", type="primary"):
                conn = get_db_connection()
                conn.execute("DELETE FROM food_listings WHERE Food_ID = ?", (target_id,))
                conn.commit()
                conn.close()
                st.warning("⚠️ Record dropped successfully.")
                st.rerun()

with tab3:
    st.header("📈 Deep Exploratory Data Analysis")
    if not df_filtered.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig1 = px.bar(df_filtered, x='Provider_Type', color='Provider_Type', title="Volume Vectors By Provider Class")
            st.plotly_chart(fig1, use_container_width=True)
        with c2:
            fig2 = px.pie(df_filtered, names='Food_Type', title="Fraction By Diet Type", hole=0.3)
            st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.header("🗄️ Analytical SQL Query Core Engine (15+ Queries)")
    queries = {
        "1. Providers by city": "SELECT Location as City, COUNT(DISTINCT Provider_Name) as Total_Providers FROM food_listings GROUP BY Location",
        "2. Receivers by city": "SELECT Location as City, COUNT(*) as Inferred_Receivers FROM food_listings WHERE Status='Claimed' GROUP BY Location",
        "3. Most contributing provider": "SELECT Provider_Type, SUM(Quantity) as Total_Vol FROM food_listings GROUP BY Provider_Type ORDER BY Total_Vol DESC LIMIT 1",
        "4. Most claimed food": "SELECT Food_Type, COUNT(*) as Claim_Count FROM food_listings GROUP BY Food_Type ORDER BY Claim_Count DESC LIMIT 1",
        "5. Total food quantity": "SELECT SUM(Quantity) as Global_Inventory_Sum FROM food_listings",
        "6. Top city by food listing": "SELECT Location as City, COUNT(*) as Listing_Count FROM food_listings GROUP BY Location ORDER BY Listing_Count DESC LIMIT 1",
        "7. Most common food type": "SELECT Food_Type, COUNT(*) as Total_Listings FROM food_listings GROUP BY Food_Type ORDER BY Total_Listings DESC LIMIT 1",
        "8. Claims per food item": "SELECT Food_Name, Quantity FROM food_listings WHERE Status='Available'",
        "9. Provider with most successful claims": "SELECT Provider_Name, COUNT(*) as Successful_Claims FROM food_listings GROUP BY Provider_Name ORDER BY Successful_Claims DESC LIMIT 1",
        "10. Claim status distribution": "SELECT Status, COUNT(*) as Total_Count FROM food_listings GROUP BY Status",
        "11. Average quantity claimed": "SELECT AVG(Quantity) as Avg_Quantity FROM food_listings",
        "12. Most claimed meal type": "SELECT Meal_Type, COUNT(*) as Total FROM food_listings GROUP BY Meal_Type ORDER BY Total DESC LIMIT 1",
        "13. Total donated quantity by provider": "SELECT Provider_Name, SUM(Quantity) as Total_Donated FROM food_listings GROUP BY Provider_Name",
        "14. High volume surplus asset check": "SELECT Food_Name, Quantity, Location FROM food_listings WHERE Quantity > 25",
        "15. Total food items grouped by status": "SELECT Status, COUNT(*) as Total_Items FROM food_listings GROUP BY Status"
    }
    selected_query_name = st.selectbox("Choose a Target Structured Query Definition to Execute:", list(queries.keys()))
    sql_string = queries[selected_query_name]
    st.code(sql_string, language="sql")
    if st.button("Execute Transaction Routine"):
        conn = get_db_connection()
        res_df = pd.read_sql_query(sql_string, conn)
        conn.close()
        st.subheader("🎯 Query Result Output")
        st.dataframe(res_df, use_container_width=True)
