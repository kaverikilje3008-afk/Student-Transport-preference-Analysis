
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

st.set_page_config(
    page_title="Student Transport Dashboard",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Student Transportation Preference Analysis")
st.write("Data Science Field Project")
st.caption(
    "Analysis of student transport preferences, travel distance, "
    "time, cost, safety and delays."
)

csv_path = Path(__file__).with_name("student_transport.csv")

try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    st.error(
        "CSV file not found! Keep student_transport.csv "
        "in the same folder as dashboard.py."
    )
    st.stop()
except Exception as e:
    st.error(f"Could not read the CSV file: {e}")
    st.stop()

# Clean column names and text
df.columns = df.columns.str.strip()

for col in df.select_dtypes(include="str").columns:
    df[col] = df[col].str.strip()

# Column names from your dataset
transport_col = "mode of transport"
distance_col = "one way travel distance"
time_col = "How long does your one way journey takes?"
cost_col = "What is your approximate one way  travel cost?"
safety_col = "How safe do you feel during your commute?"
factor_col = "biggest factor influencing your transport choice"
delay_col = "How often do you experience travel delays?"

required_cols = [
    transport_col, distance_col, time_col, cost_col,
    safety_col, factor_col, delay_col
]

missing_cols = [c for c in required_cols if c not in df.columns]

if missing_cols:
    st.error(f"Missing columns in CSV: {missing_cols}")
    st.write("Columns found:", df.columns.tolist())
    st.stop()

# ---------------- SIDEBAR FILTER ----------------
st.sidebar.title("Dashboard Filters")

transport_modes = sorted(
    df[transport_col].dropna().unique().tolist()
)

selected_modes = st.sidebar.multiselect(
    "Select Transport Mode",
    transport_modes,
    default=transport_modes
)

filtered = df[df[transport_col].isin(selected_modes)].copy()

if filtered.empty:
    st.warning("Please select at least one transport mode.")
    st.stop()

st.sidebar.success(f"{len(filtered)} responses selected")

st.subheader("Project Overview")

total_students = len(filtered)
most_used = filtered[transport_col].mode().iloc[0]
missing_values = int(filtered.isnull().sum().sum())

c1, c2, c3 = st.columns(3)
c1.metric("Total Responses", total_students)
c2.metric("Most Preferred Transport", most_used)
c3.metric("Missing Values", missing_values)

st.subheader("1. Transport Preferences - Bar Chart")

transport_counts = filtered[transport_col].value_counts()

fig, ax = plt.subplots(figsize=(8, 4))
transport_counts.plot(kind="bar", ax=ax)
ax.set_xlabel("Transport Mode")
ax.set_ylabel("Number of Students")
ax.set_title("Number of Students by Transport Mode")
plt.xticks(rotation=35, ha="right")
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

st.subheader("2. Transport Preferences - Pie Chart")

fig, ax = plt.subplots(figsize=(7, 5))
ax.pie(
    transport_counts.values,
    labels=transport_counts.index,
    autopct="%1.1f%%",
    startangle=90
)
ax.set_title("Percentage of Students by Transport Mode")
ax.axis("equal")
st.pyplot(fig)
plt.close(fig)

def show_category_chart(data, column, title, chart_type="bar"):
    values = data[column].fillna("Not answered").astype(str)
    counts = values.value_counts()

    if counts.empty:
        st.info("No data available for " + title)
        return

    fig, ax = plt.subplots(figsize=(7, 4))

    if chart_type == "pie":
        ax.pie(
            counts.values,
            labels=counts.index,
            autopct="%1.1f%%",
            startangle=90
        )
        ax.axis("equal")
    else:
        counts.plot(kind="bar", ax=ax)
        ax.set_xlabel("")
        ax.set_ylabel("Number of Students")
        plt.xticks(rotation=35, ha="right")

    ax.set_title(title)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

st.subheader("3. Travel Analysis")

left, right = st.columns(2)

with left:
    show_category_chart(
        filtered, distance_col, "One-way Travel Distance"
    )

with right:
    show_category_chart(
        filtered, time_col, "One-way Travel Time"
    )

left, right = st.columns(2)

with left:
    show_category_chart(
        filtered, cost_col, "One-way Travel Cost"
    )

with right:
    show_category_chart(
        filtered, safety_col, "Commute Safety Ratings"
    )

left, right = st.columns(2)

with left:
    show_category_chart(
        filtered, factor_col, "Main Transport Choice Factor"
    )

with right:
    show_category_chart(
        filtered, delay_col, "Travel Delay Frequency"
    )

st.subheader("4. Box Plot Analysis")

st.write(
    "Box plots show the distribution of numeric travel values. "
    "If survey answers are ranges or categories, results may be approximate."
)

def extract_number(series):
    # Extract the first number from answers such as
    # "20 km", "₹50", or "20-30".
    return pd.to_numeric(
        series.astype(str).str.extract(r"(-?\d+\.?\d*)")[0],
        errors="coerce"
    )

distance_numbers = extract_number(filtered[distance_col]).dropna()
cost_numbers = extract_number(filtered[cost_col]).dropna()

left, right = st.columns(2)

with left:
    st.write("**One-way Travel Distance**")
    if not distance_numbers.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(distance_numbers, tick_labels=["Distance"])
        ax.set_ylabel("Distance (dataset units)")
        ax.set_title("Travel Distance Distribution")
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No numeric distance values found.")

with right:
    st.write("**One-way Travel Cost**")
    if not cost_numbers.empty:
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.boxplot(cost_numbers, tick_labels=["Cost"])
        ax.set_ylabel("Cost (dataset units)")
        ax.set_title("Travel Cost Distribution")
        ax.grid(axis="y", alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
    else:
        st.info("No numeric cost values found.")

st.subheader("5. Student Survey Data")

st.write("Student names are hidden to protect privacy.")

display_df = filtered.drop(
    columns=["Name of student"],
    errors="ignore"
)

st.dataframe(display_df, use_container_width=True)

csv_data = display_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data as CSV",
    data=csv_data,
    file_name="filtered_transport_data.csv",
    mime="text/csv"
)

st.divider()
st.caption("Student Transportation Preference Analysis | Data Science Project")
