# Climate Change Data & Prediction Dashboard

> **An interactive, AI-powered climate data visualization platform** that tracks historical climate trends, predicts future conditions, and visualizes them through clean, dynamic charts powered by Chart.js.

---

## Overview

This project visualizes and forecasts key climate indicators using real data from [ClimateChangeTracker.org](https://climatechangetracker.org).  
It combines machine learning (via **Python**) with interactive data visualization (**Chart.js**) to provide insight into both **historical** and **projected** climate trends.

---

### Machine Learning  
- Derived analytics for decadal rates and change over time  
- All predictions stored in an SQLite database for persistence  

### Interactive Dashboard
- Real-time visualizations with **Chart.js**
- Clear distinction between **observed data** and **AI predictions**
- Seamless integration between Flask API and frontend charts

---

## Data Sources

All datasets are retrieved directly from **[ClimateChangeTracker.org](https://climatechangetracker.org/data-api)**.

---

## Tech Stack

| Layer | Tools |
|-------|--------|
| **Frontend** | HTML5, CSS3, JavaScript, Chart.js |
| **Backend** | Python, Flask, Flask-CORS |
| **Database** | SQLite3 |
| **Visualization** | Chart.js |

---

## How to works
- Data Upload: CSVs are imported into SQLite tables.
- Model Training: ML models learn patterns from historical data.
- Prediction Generation: Future values (e.g., 2025–2050) are computed.
- Frontend: Chart.js visualizes both as continuous interactive lines.