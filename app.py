"""Explore Palmer penguin measurements and evaluate body-mass predictions."""

import altair as alt
import streamlit as st

from penguin_lab.data import complete_measurements, filter_penguins, load_penguins
from penguin_lab.model import evaluate_model

st.set_page_config(page_title="Penguin Lab", page_icon="🐧", layout="wide")
st.markdown(
    """<style>
.stApp {background:#f6f8f7} h1,h2,h3 {color:#153f3b}
[data-testid="stMetric"] {background:white;border:1px solid #dde6e2;
padding:18px;border-radius:12px}
.block-container {padding-top:2.5rem}
</style>""",
    unsafe_allow_html=True,
)
st.caption("Palmer Archipelago, 2007 to 2009")
st.title("Penguin Lab")
st.write("Measurements of 344 penguins from three species, with a model to estimate body mass.")


@st.cache_data
def data():
    return load_penguins()


@st.cache_resource
def experiment():
    return evaluate_model(load_penguins())


try:
    frame = data()
except (OSError, ValueError) as error:
    st.error(f"Cannot load the bundled dataset: {error}")
    st.stop()

with st.sidebar:
    st.header("Filter observations")
    species = st.multiselect(
        "Species",
        sorted(frame.species.unique()),
        default=sorted(frame.species.unique()),
        key="species",
    )
    islands = st.multiselect(
        "Islands",
        sorted(frame.island.unique()),
        default=sorted(frame.island.unique()),
        key="islands",
    )
    years = st.multiselect(
        "Years", sorted(frame.year.unique()), default=sorted(frame.year.unique()), key="years"
    )
    st.caption("Filters affect the Explorer only. The model uses a fixed train/test split.")

explorer, modelling, methods = st.tabs(["Explore", "Model evaluation", "Data & methods"])
with explorer:
    selected = filter_penguins(frame, species, islands, years)
    measured = complete_measurements(selected)
    first, second, third = st.columns(3)
    first.metric("Selected observations", len(selected))
    second.metric("Species represented", selected.species.nunique())
    mean_mass = selected.body_mass_g.mean()
    third.metric(
        "Mean measured mass", "N/A" if selected.body_mass_g.count() == 0 else f"{mean_mass:,.0f} g"
    )
    if selected.empty:
        st.info(
            "No observations match these filters. Select at least one species, island and year."
        )
    else:
        st.subheader("Flipper length and body mass")
        st.caption(
            f"{len(measured)} complete pairs shown; {len(selected) - len(measured)} rows missing a plotted measurement omitted."
        )
        if measured.empty:
            st.info("No complete flipper-length / body-mass pair in this selection.")
        else:
            chart = (
                alt.Chart(measured)
                .mark_circle(size=65, opacity=0.75)
                .encode(
                    x=alt.X(
                        "flipper_length_mm:Q",
                        title="Flipper length (mm)",
                        scale=alt.Scale(zero=False),
                    ),
                    y=alt.Y("body_mass_g:Q", title="Body mass (g)", scale=alt.Scale(zero=False)),
                    color=alt.Color(
                        "species:N",
                        title="Species",
                        scale=alt.Scale(
                            domain=["Adelie", "Chinstrap", "Gentoo"],
                            range=["#168277", "#dc925a", "#647bb1"],
                        ),
                    ),
                    tooltip=[
                        "species",
                        "island",
                        "sex",
                        "year",
                        "flipper_length_mm",
                        "body_mass_g",
                    ],
                )
                .properties(height=390)
                .interactive()
            )
            st.altair_chart(chart, width="stretch")
        st.caption(
            "Association is not causation. Species and sex contribute to the visible groups."
        )
        with st.expander("Inspect the selected rows"):
            st.dataframe(selected, hide_index=True, width="stretch")
        st.download_button(
            "Download selected CSV",
            selected.to_csv(index=False),
            "penguins_selected.csv",
            "text/csv",
        )

with modelling:
    st.subheader("Predict body mass from observed characteristics")
    st.write(
        "A ridge regression uses bill dimensions, flipper length, species, sex and island. "
        "We compare it with a baseline that always predicts the training-set mean mass."
    )
    result = experiment()
    a, b, c = st.columns(3)
    a.metric("Model MAE · holdout", f"{result['mae']:.0f} g")
    b.metric("Baseline MAE · holdout", f"{result['baseline_mae']:.0f} g")
    c.metric("Holdout R²", f"{result['r2']:.3f}")
    st.caption(
        f"Training: {result['n_train']} rows · Test: {result['n_test']} rows · "
        f"Missing targets excluded: {result['n_excluded']} · Fixed seed: 42"
    )
    predictions = result["predictions"]
    low = float(predictions.iloc[:, :2].min().min())
    high = float(predictions.iloc[:, :2].max().max())
    points = (
        alt.Chart(predictions)
        .mark_circle(size=55, opacity=0.7)
        .encode(
            x=alt.X("Measured mass (g):Q", scale=alt.Scale(domain=[low, high], zero=False)),
            y=alt.Y("Predicted mass (g):Q", scale=alt.Scale(domain=[low, high], zero=False)),
            color=alt.Color(
                "Species:N",
                scale=alt.Scale(
                    domain=["Adelie", "Chinstrap", "Gentoo"],
                    range=["#168277", "#dc925a", "#647bb1"],
                ),
            ),
            tooltip=list(predictions.columns),
        )
    )
    diagonal = (
        alt.Chart(alt.Data(values=[{"x": low, "y": low}, {"x": high, "y": high}]))
        .mark_line(color="#999999", strokeDash=[4, 4])
        .encode(x="x:Q", y="y:Q")
    )
    st.altair_chart((points + diagonal).properties(height=370), width="stretch")
    st.info(
        "The dashed line indicates a perfect prediction. MAE is the average absolute error in grams; lower is better."
    )
    st.write(
        "This is one held-out split of a small observational dataset. It estimates performance "
        "within this sample, not on other regions, years or penguin populations. No causal claim is made."
    )

with methods:
    st.subheader("Data and methods")
    st.markdown("""
- **Source:** Palmer penguins, collected by Dr. Kristen Gorman and the Palmer Station LTER program.
- **Snapshot:** the CSV is included in the repository; normal runs require no data download.
- **Missing values:** retained in exploration; incomplete plotted pairs are counted and omitted.
- **Model:** 75/25 split stratified by species; fixed seed 42; ridge alpha 1.0 set in advance.
- **Preprocessing:** numeric median imputation and scaling; categorical mode imputation and
  one-hot encoding. All learned preprocessing is fitted on the training set only.
- **Reproducibility:** locked dependencies, data checksum, unit tests, CI and Docker.
- **Limits:** small sample, clustered collection sites, only three species, no causal interpretation.
""")
    st.dataframe(frame.isna().sum().rename("Missing values"), width="stretch")
    st.link_button(
        "Dataset documentation & attribution", "https://allisonhorst.github.io/palmerpenguins/"
    )
st.caption("Tooling for the Data Scientist | Individual project")
