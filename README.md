# Climate Change Data & Prediction Dashboard

> **An interactive, AI-powered climate data visualization platform** that tracks historical climate trends, predicts future conditions, and visualizes them through clean, dynamic charts powered by Chart.js.

---

## Overview

This project visualizes and forecasts key climate indicators using real data. It combines machine learning (**Python**) with interactive data visualization (**Chart.js**) to provide insight into both **historical** and **projected** climate trends.

### Machine Learning

* Derived analytics for decadal rates and change over time
* All predictions stored in an SQLite database for persistence
* Hybrid polynomial + XGBoost models for temperature and sea level predictions

### Interactive Dashboard

* Real-time visualizations with **Chart.js**
* Clear distinction between **observed data** and **AI predictions**

---

## Tech Stack

| Layer             | Tools                             |
| ----------------- | --------------------------------- |
| **Frontend**      | HTML5, CSS3, JavaScript, Chart.js |
| **Backend**       | Python, Flask                     |
| **Database**      | SQLite3                           |
| **ML Models**     | scikit-learn, XGBoost             |
| **Visualization** | Chart.js                          |

---

## Setup

### Install Dependencies

First, install all required packages:

```bash
pip install -r requirements.txt
```

### Initialize Database

Create the SQLite database from CSV files:

```bash
python backend/utils/create_db.py
```

This will create `backend/data/climate.db` with all the necessary tables.

---

## Running the Application

### Generate Predictions

To train the models and generate future predictions:

```bash
python backend/main.py
```

This will:
- Load historical data from the database
- Train temperature and sea level prediction models
- Generate forecasts for 2025-2050
- Save predictions to the database
- Print results to the console

### Start the Web Dashboard

To launch the Flask web server:

```bash
cd backend
python app.py
```

Or from the project root:

```bash
python backend/app.py
```

Then open your browser and visit: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

The dashboard provides:
- Interactive charts showing historical data and predictions
- News feed with climate-related articles
- Admin panel for database management

---

## How it Works

1. **Data Storage:** CSV files are imported into SQLite tables for efficient querying
2. **Model Training:** ML models learn patterns from historical data
   - Polynomial regression captures long-term trends
   - XGBoost handles residual patterns and complex interactions
3. **Prediction Generation:** Future values (2025–2050) are computed and anchored to recent observations
4. **Frontend:** Chart.js visualizes both historical and predicted data as continuous interactive lines

---

## Testing

The project includes a comprehensive test suite covering all components.

### Test Structure

The test suite is organized into:

- `tests/test_data_loader.py` - Data loading and database utilities
- `tests/test_temperature_model.py` - Temperature prediction model
- `tests/test_sea_level_model.py` - Sea level prediction model
- `tests/test_api.py` - Flask API endpoints
- `tests/test_integration.py` - End-to-end integration tests
- `tests/test_database.py` - Database operations
- `tests/conftest.py` - Shared fixtures and test configuration

### Running Tests

**Run all tests:**
```bash
pytest
# or
python run_tests.py
```

**Run specific test categories:**
```bash
# Unit tests only
python run_tests.py --unit
pytest -m unit

# Integration tests only
python run_tests.py --integration
pytest -m integration

# API tests only
python run_tests.py --api
pytest -m api

# Model tests only
python run_tests.py --model
pytest -m model

# Database tests only
python run_tests.py --database
pytest -m database
```

**Run specific test files:**
```bash
pytest tests/test_data_loader.py
pytest tests/test_temperature_model.py
pytest tests/test_api.py
```

### Troubleshooting Tests

**Import Errors:**
If you encounter import errors, ensure the project root is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

**Database Errors:**
Tests use temporary databases that are cleaned up automatically. If you see database errors, check that SQLite is properly installed and accessible.

**Missing Dependencies:**
Ensure all dependencies from `requirements.txt` are installed:

```bash
pip install -r requirements.txt
```

---

## Data Sources

All datasets are retrieved directly from **ClimateChangeTracker.org** via their Data API.

The database stores:
- Historical temperature anomalies and anthropogenic forcing
- CO₂ concentration measurements
- Global mean sea level (GMSL) data
- Model predictions for future years

---

## Project Structure

```
ClimateDashboard/
├── backend/
│   ├── data/              # CSV files and SQLite database
│   ├── model/             # ML model implementations
│   │   ├── temprature_model.py
│   │   └── sea_level_model.py
│   ├── utils/             # Data loading and database utilities
│   ├── app.py             # Flask web server
│   └── main.py            # Main script to generate predictions
├── frontend/              # HTML, CSS, and JavaScript files
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

---
