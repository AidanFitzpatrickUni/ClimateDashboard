# Climate Change Data & Prediction Dashboard

> **An interactive, AI-powered climate data visualization platform** that tracks historical climate trends, predicts future conditions, and visualizes them through clean, dynamic charts powered by Chart.js.

---

## Overview

This project visualizes and forecasts key climate indicators using real data.
It combines machine learning (**Python**) with interactive data visualization (**Chart.js**) to provide insight into both **historical** and **projected** climate trends.

---

### Machine Learning

* Derived analytics for decadal rates and change over time
* All predictions stored in an SQLite database for persistence

### Interactive Dashboard

* Real-time visualizations with **Chart.js**
* Clear distinction between **observed data** and **AI predictions**

---

## Data Sources

All datasets are retrieved directly from **ClimateChangeTracker.org** via their Data API.

---

## Tech Stack

| Layer             | Tools                             |
| ----------------- | --------------------------------- |
| **Frontend**      | HTML5, CSS3, JavaScript, Chart.js |
| **Backend**       | Python, Flask                     |
| **Database**      | SQLite3                           |
| **Visualization** | Chart.js                          |

---

## How it Works

* **Data Upload:** CSVs are imported into SQLite tables.
* **Model Training:** ML models learn patterns from historical data.
* **Prediction Generation:** Future values (e.g., 2026–2050) are computed.
* **Frontend:** Chart.js visualizes both as continuous interactive lines.

---

## Running the Application

To start the dashboard locally:

1. Navigate into the **backend** folder:

   ```bash
   cd backend
   ```

2. Run the Flask app:

   ```bash
   py app.py
   ```

3. Open your browser and visit:
   **[http://127.0.0.1:5000](http://127.0.0.1:5000)**
