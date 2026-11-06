import streamlit as st
import pandas as pd
import ast


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="IMDb Movie Dashboard",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("ToP 250 movies on imdb in 2026 (1).csv")
    return df


df = load_data()


# ============================================================
# CONVERT LIST-LIKE COLUMNS
# ============================================================

def convert_list(value):

    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    try:
        result = ast.literal_eval(str(value))

        if isinstance(result, list):
            return result

        return [str(result)]

    except (ValueError, SyntaxError):
        # Also handle normal comma-separated values
        if "," in str(value):
            return [
                item.strip()
                for item in str(value).split(",")
                if item.strip()
            ]

        return [str(value).strip()]


# Check required columns
required_columns = [
    "genres",
    "countriesOfOrigin",
    "averageRating",
    "numVotes",
    "grossWorldwide",
    "primaryTitle"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        "The following required columns are missing from the CSV: "
        + ", ".join(missing_columns)
    )

    st.write("Columns available in your CSV:")
    st.write(df.columns.tolist())

    st.stop()


df["genres_list"] = df["genres"].apply(convert_list)

df["countries_list"] = df["countriesOfOrigin"].apply(convert_list)


# ============================================================
# CONVERT NUMERIC COLUMNS
# ============================================================

df["averageRating"] = pd.to_numeric(
    df["averageRating"],
    errors="coerce"
)

df["numVotes"] = pd.to_numeric(
    df["numVotes"],
    errors="coerce"
)

df["grossWorldwide"] = pd.to_numeric(
    df["grossWorldwide"],
    errors="coerce"
)


# ============================================================
# TITLE
# ============================================================

st.title("🎬 IMDb Top 250 Movies Dashboard")

st.success("IMDb Dataset Loaded Successfully!")


# ============================================================
# QUESTION 1
# DATASET LOADING AND INITIAL EXPLORATION
# ============================================================

st.header("1. Dataset Loading and Initial Exploration")


# First 10 records
st.subheader("First 10 Movie Records")

st.dataframe(
    df.head(10),
    use_container_width=True
)


# Dataset information
st.subheader("Dataset Information")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Total Rows",
        df.shape[0]
    )

with col2:
    st.metric(
        "Total Columns",
        df.shape[1]
    )


# Column names
st.write("### Column Names")

st.write(
    df.columns.tolist()
)


# Data types
st.write("### Data Types")

st.dataframe(
    df.dtypes.astype(str).reset_index().rename(
        columns={
            "index": "Column",
            0: "Data Type"
        }
    ),
    use_container_width=True
)


# Missing values
st.subheader("Missing Values")

missing_values = (
    df.isnull()
    .sum()
    .reset_index()
)

missing_values.columns = [
    "Column",
    "Missing Values"
]

st.dataframe(
    missing_values,
    use_container_width=True
)


# Additional information
with st.expander("📋 Additional Dataset Information"):

    st.write(
        "Total Records:",
        len(df)
    )

    st.write(
        "Total Columns:",
        len(df.columns)
    )

    st.write(
        "Movie Information:",
        df["primaryTitle"].count()
    )


st.divider()


# ============================================================
# QUESTION 2
# KPI DASHBOARD
# ============================================================

st.header("2. Movie Analytics Dashboard")


total_movies = len(df)

average_rating = df["averageRating"].mean()

highest_rating = df["averageRating"].max()

total_votes = df["numVotes"].sum()


col1, col2, col3, col4 = st.columns(4)


with col1:
    st.metric(
        "Total Movies",
        total_movies
    )


with col2:
    st.metric(
        "Average Rating",
        round(average_rating, 2)
    )


with col3:
    st.metric(
        "Highest Rating",
        highest_rating
    )


with col4:
    st.metric(
        "Total Votes",
        f"{int(total_votes):,}"
    )


st.divider()


# ============================================================
# QUESTION 3
# DATA VISUALIZATION
# ============================================================

st.header("3. Data Visualization")


tab1, tab2, tab3 = st.tabs(
    [
        "🎭 Genre Analysis",
        "⭐ Rating Analysis",
        "💰 Gross Collection"
    ]
)


# ------------------------------------------------------------
# GENRE BAR CHART
# ------------------------------------------------------------

with tab1:

    st.subheader(
        "Number of Movies by Genre"
    )

    genre_data = df.explode(
        "genres_list"
    )

    genre_counts = (
        genre_data["genres_list"]
        .dropna()
        .value_counts()
    )

    st.bar_chart(
        genre_counts
    )


# ------------------------------------------------------------
# RATING ANALYSIS
# ------------------------------------------------------------

with tab2:

    st.subheader(
        "IMDb Rating Distribution"
    )

    rating_data = df[
        "averageRating"
    ].dropna()

    rating_bins = pd.cut(
        rating_data,
        bins=10
    )

    rating_counts = (
        rating_bins
        .value_counts()
        .sort_index()
    )

    rating_chart = pd.DataFrame(
        {
            "Number of Movies":
                rating_counts.values
        },
        index=rating_counts.index.astype(str)
    )

    st.bar_chart(
        rating_chart
    )


    # Scatter plot
    st.subheader(
        "Rating vs Number of Votes"
    )

    scatter_data = df[
        ["averageRating", "numVotes"]
    ].dropna()

    st.scatter_chart(
        scatter_data,
        x="averageRating",
        y="numVotes"
    )


# ------------------------------------------------------------
# TOP 10 GROSSING MOVIES
# ------------------------------------------------------------

with tab3:

    st.subheader(
        "Top 10 Movies by Worldwide Gross"
    )