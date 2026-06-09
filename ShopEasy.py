import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Custom CSS
st.markdown("""
<style>

/* Page Background */
[data-testid="stAppViewContainer"] {
    background-color: #EFE4B1;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #C19A6B;
}

[data-testid="stSidebar"] * {
    color: #000000;
    border-radius: 8px;
}

/* Login Inputs */
.stTextInput input {
    background-color: white !important;
    color: black !important;
    border: 1px solid #B0BEC5 !important;
    border-radius: 8px !important;
}

/* Date Input */
.stDateInput input {
    background-color: white !important;
    color: black !important;
}

/* Select Box */
.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
}

/* Buttons */
.stButton > button {
    background-color: #1976D2;
    color: white;
    border-radius: 8px;
}

/* Metric Cards */
[data-testid="stMetric"] {
    background-color:#E1F5FE;
    border-radius: 10px;
    border: 1px solid #000000;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    background-color: black;
    border-radius: 12px;
}

/* Headings */
h1 {
    color: #000000;
    text-align: center;
}

h2, h3 {
    color: #374151;
}
</style>
""", unsafe_allow_html=True)

# Page Settings
st.set_page_config(
    page_title="ShopEasy Sales Dashboard",
    layout="wide"
)

# Login Credentials
ADMIN_ID = "Admin"
PASSWORD = "1234"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login Page
if not st.session_state.logged_in:

    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        st.image("Logo.png", width=500)

    st.title("ShopEasy Login")

    admin_id = st.text_input("Admin ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if admin_id == ADMIN_ID and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login Successful!")
            st.rerun()

        else:
            st.error("Invalid Admin ID or Password")

    st.stop()
# Sidebar Logo
st.sidebar.image(
    "Logo.png",
    use_container_width=True
)

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Sales Dashboard", "Inventory Management"]
)

# Sales Dashboard
if page == "Sales Dashboard":

    st.title("Sales Dashboard")

    # Load Dataset
    df = pd.read_csv("sales_data.csv")
    df.columns = df.columns.str.strip()
    df["Date of Sale"] = pd.to_datetime(df["Date of Sale"])

    # Sales Filters
    st.sidebar.subheader("Sales Filters")

    category = st.sidebar.selectbox(
        "Select Category",
        ["All"] + list(df["Category"].unique()),
        key="sales_category"
    )

    start_date = st.sidebar.date_input(
        "Start Date",
        df["Date of Sale"].min(),
        key="sales_start_date"
    )

    end_date = st.sidebar.date_input(
        "End Date",
        df["Date of Sale"].max(),
        key="sales_end_date"
    )

    # Filter Data
    filtered_df = df.copy()

    if category != "All":
        filtered_df = filtered_df[
            filtered_df["Category"] == category
        ]

    filtered_df = filtered_df[
        (filtered_df["Date of Sale"] >= pd.Timestamp(start_date))
        &
        (filtered_df["Date of Sale"] <= pd.Timestamp(end_date))
    ]

    # Business Metrics
    filtered_df["Revenue"] = (
        filtered_df["Quantity Sold"] *
        filtered_df["Unit Price"]
    )

    total_revenue = filtered_df["Revenue"].sum()
    total_units = filtered_df["Quantity Sold"].sum()
    avg_price = filtered_df["Unit Price"].mean()

    st.subheader("Business Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Revenue", f"RM {total_revenue:,.2f}")

    with col2:
        st.metric("Total Units Sold", total_units)

    with col3:
        st.metric("Average Selling Price", f"RM {avg_price:.2f}")

    # Sales Data
    st.subheader("Sales Data")

    display_df = filtered_df.copy()

    display_df["Date of Sale"] = (
        display_df["Date of Sale"]
        .dt.strftime("%Y-%m-%d")
    )

    st.dataframe(display_df)

    # Prepare Data for Charts
    category_revenue = (
        filtered_df.groupby("Category")["Revenue"]
        .sum()
        .reset_index()
    )

    monthly_sales = filtered_df.copy()

    monthly_sales["Month_Num"] = (
        monthly_sales["Date of Sale"].dt.month
    )

    monthly_sales["Month"] = (
        monthly_sales["Date of Sale"].dt.strftime("%b")
    )

    monthly_sales = (
        monthly_sales.groupby(["Month_Num", "Month"])["Revenue"]
        .sum()
        .reset_index()
        .sort_values("Month_Num")
    )

    # Sales Graphics
    st.subheader("Sales Graphics")

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("#### Revenue by Product Category")

        fig1, ax1 = plt.subplots(figsize=(6, 4))

        ax1.bar(
            category_revenue["Category"],
            category_revenue["Revenue"]
        )

        ax1.set_xlabel("Category")
        ax1.set_ylabel("Revenue (RM)")
        ax1.set_title("Revenue by Category")

        st.pyplot(fig1)

    with col2:

        st.markdown("#### Monthly Sales Trend")

        fig2, ax2 = plt.subplots(figsize=(6, 4))

        sns.lineplot(
            data=monthly_sales,
            x="Month",
            y="Revenue",
            marker="o",
            ax=ax2
        )

        ax2.set_xlabel("Month")
        ax2.set_ylabel("Revenue (RM)")
        ax2.set_title("Monthly Sales Trend")

        st.pyplot(fig2)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:

        st.markdown("#### Revenue Earned by Category")

        fig3, ax3 = plt.subplots(figsize=(5, 4))

        ax3.pie(
            category_revenue["Revenue"],
            labels=category_revenue["Category"],
            autopct="%1.1f%%"
        )

        ax3.set_title("Revenue Earned by Category")

        st.pyplot(fig3)

# Inventory Management
elif page == "Inventory Management":

    st.title("Inventory Management")

    inventory_df = pd.read_csv("inventory_data.csv")

    st.sidebar.title("Inventory Filters")

    inventory_category = st.sidebar.selectbox(
        "Select Category",
        ["All"] + list(inventory_df["Category"].unique()),
        key="inventory_category"
    )

    threshold = st.sidebar.slider(
        "Low Stock Threshold",
        min_value=1,
        max_value=50,
        value=25,
        key="inventory_threshold"
    )

    inventory_filtered = inventory_df.copy()

    if inventory_category != "All":

        inventory_filtered = inventory_filtered[
            inventory_filtered["Category"] == inventory_category
        ]

    st.subheader("Inventory Metrics")

    total_products = len(inventory_filtered)

    low_stock_count = len(
        inventory_filtered[
            inventory_filtered["Stock Quantity"] < threshold
        ]
    )

    total_stock = inventory_filtered["Stock Quantity"].sum()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Products", total_products)

    with col2:
        st.metric("Low Stock Products", low_stock_count)

    with col3:
        st.metric("Total Stock Units", total_stock)

    low_stock_items = list(
        filter(
            lambda product:
            product["Stock Quantity"] < threshold,
            inventory_filtered.to_dict("records")
        )
    )

    if low_stock_items:
        st.markdown(
            f"""
            <div style="
                background-color:#FFCBD1;
                padding:15px;
                border-radius:10px;
                border-left:5px solid #FF2C2C;
                color:#850413;
                font-size:16px;
            ">
                {len(low_stock_items)} products are below the stock threshold of {threshold} units !
            </div>
            """,
            unsafe_allow_html=True)

        st.subheader("Low Stock Products")

        st.dataframe(
            pd.DataFrame(low_stock_items)
        )

    inventory_filtered["Stock Status"] = (
        inventory_filtered["Stock Quantity"]
        .apply(
            lambda stock:
            "Low Stock"
            if stock < threshold
            else "In Stock"
        )
    )

    def highlight_stock(row):

        if row["Stock Quantity"] < threshold:
            return ["background-color: #ffcccc"] * len(row)

        return [""] * len(row)

    st.subheader("Inventory Table")

    st.dataframe(
        inventory_filtered.style.apply(
            highlight_stock,
            axis=1
        )
    )
