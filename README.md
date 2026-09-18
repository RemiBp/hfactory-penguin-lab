# Penguin Lab

An offline-ready Streamlit application exploring Palmer penguin measurements
and evaluating a reproducible body-mass regression. Prepared as a **new personal
course project draft**, not presented as a project previously completed in class.
Review and adapt it before submitting.

## Run locally

Requirements: Python 3.12 and uv 0.11.24.

```sh
uv sync --locked
uv run streamlit run app.py --server.address=127.0.0.1
```

Open http://localhost:8501. No credentials or external data service is needed.
Use the species/island/year filters, download the selected rows, and open the
Model evaluation tab to inspect the held-out predictions.

## Run with Docker

```sh
docker compose up --build
```

Or:

```sh
docker build -t penguin-lab:local .
docker run --rm -p 127.0.0.1:8501:8501 penguin-lab:local
```

The container runs as a non-root user. Its health check tests
`/_stcore/health`. Data are included in the image. The image is not automatically
published to any registry. Python packages are locked by `uv.lock`; base-image
tags are versioned but mutable, so identical image digests are not guaranteed.

## Validate

```sh
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=penguin_lab --cov-branch --cov-report=term-missing --cov-fail-under=90
shasum -a 256 -c data/SHA256SUMS
```

The GitHub Actions workflow runs lint, formatting, import/filter/model tests and
Streamlit interaction tests, builds the Docker image, executes AppTest inside it,
then checks the running container's HTTP endpoint. The data checksum is checked
independently. It does not deploy or submit the project.

## Scientific question and approach

How well do morphology, species, sex and island predict body mass in this sample?
The baseline always predicts the mean training mass. The candidate is a ridge
regression (alpha 1.0 fixed before evaluation). A fixed, species-stratified 75/25
train/test split uses seed 42. Rows with missing targets are excluded; missing
predictors are imputed using training-set statistics only. Scaling and one-hot
encoding are also fitted only on the training set. No target information is
included in predictors, and no hyperparameters are selected on the holdout.

The explorer's filters never change the model experiment. The app reports MAE in
grams, R², train/test sizes, the mean baseline, and measured vs predicted values.
MAE provides a direct unit-based error; R² is relative to variability in the test
set. A single split does not measure uncertainty over all possible splits.

## Limitations

- Only 344 observations from three species, three islands and 2007–2009.
- Sites and collection conditions are clustered; a random split does not measure
  generalization to new islands or years.
- Missing sex is imputed with the training mode, potentially weakening subgroup
  estimates; no causal or population-wide conclusion is justified.
- The simplified dataset lacks individual IDs; independence cannot be verified.
- No deployment or decision-making use is intended.

## Structure

- `app.py`: Streamlit interface and visualizations.
- `penguin_lab/data.py`: validated import and deterministic filtering.
- `penguin_lab/model.py`: preprocessing, holdout experiment and baseline.
- `tests/`: malformed inputs, empty filters, train/test separation and UI checks.
- `data/`: pinned dataset snapshot, provenance and checksum.
- `Dockerfile`, `compose.yaml`, `.github/workflows/ci.yml`: reproducible execution.

## Review before submission

1. Run the app and explain the data filters, missing-value policy and model split.
2. Check the CI results and reproduce the tests.
3. Adapt the text and scope to the work you are comfortable presenting.
4. Ensure the instructor can read the chosen repository. The assignment accepts
   HFactory internal GitLab or a public GitHub repo. A private GitHub draft must
   be made accessible before submitting its URL.
5. Submit the Git repository URL on HFactory yourself. Registry URL is optional.

**No final submission has been made.**

Dataset attribution and CC0 license: see [data/README.md](data/README.md).
App-testing and container setup follow the official Streamlit documentation:
https://docs.streamlit.io/develop/api-reference/app-testing
and https://docs.streamlit.io/deploy/tutorials/docker.
