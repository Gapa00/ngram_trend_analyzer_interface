# N-Gram Trend Analysis Dashboard

A dashboard for analyzing temporal patterns in term frequencies to identify emerging "hot" n-grams.

## How to Run

### Using Docker

1. Install Docker: [https://www.docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)

2. Run the app:
   ```bash
   docker-compose up -d
   ```

3. Access at [http://localhost:8501](http://localhost:8501)

### Manual Installation

1. Install Python 3.9+
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## How to Use

1. **Search for an n-gram** in the search box
2. **Configure criteria functions parameters** to adjust sensitivity for each criteria seperately
3. **View results** in two main sections:

### Criteria Functions Results

This section shows statistical analyses for your selected n-gram:

- **Percent Change Analysis**: Shows significant changes in frequency over time, with z-score thresholds highlighting statistically significant changes
- **MACD Analysis**: Shows trend momentum and reversals, with the histogram highlighting significant signals
- **Exponential Smoothing**: Breaks down time series into components with statistical thresholds on residuals
- **Seasonal Decomposition**: Separates data into trend, seasonal, and residual components

### Trend Detection

This section combines results from all enabled criteria functions:

- **Signal Heatmap**: Displays quarters that exceed statistical thresholds (green cells) for each criteria function. By default, values above 2 standard deviations (σ=2) are flagged. A quarter must be identified by a majority of enabled criteria functions to become a consensus point.
- **Trend Zones**: Highlights periods of significant upward momentum (green shaded areas). These zones are identified through a two-step process: first by finding consensus points where multiple methods agree, then by analyzing the smoothed derivative pattern to expand these zones using z-score thresholding.
- **Quarters List**: Shows the specific quarters within identified trend zones, representing time periods where the term demonstrates statistically significant growth patterns.

___

### Future Improvements

- Global Leaderboard of ngrams that show significant trend
- Implementation of dynamic preprocessing instead of direct reading of the dataset from a file
- Addition of larger ngrams (n>1)
