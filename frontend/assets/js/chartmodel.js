const API_BASE = 'http://127.0.0.1:5000/api';

// Helper to create a chart with shared styling defaults
function createChart(canvasId, chartType, chartData, label, options = {}) {
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  
  return new Chart(ctx, {
    type: chartType,
    data: {
      labels: chartData.labels,
      datasets: chartData.datasets || [{
        label: label,
        data: chartData.values,
        backgroundColor: 'rgba(75, 192, 192, 0.5)',
        borderColor: 'rgba(75, 192, 192, 1)',
        borderWidth: 2,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { display: true },
        title: {
          display: true,
          text: label,
          color: '#f0f0f0'
        }
      },
      scales: { 
        y: { 
          beginAtZero: options.beginAtZero !== false,
          ticks: { color: '#f0f0f0' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        },
        x: {
          ticks: { color: '#f0f0f0' },
          grid: { color: 'rgba(255, 255, 255, 0.1)' }
        }
      }
    }
  });
}

// Fetch and display all charts
async function loadCharts() {
  try {
    // Fetch all data in parallel
    const [tempData, seaLevelData, tempPredData, seaLevelPredData] = await Promise.all([
      fetch(`${API_BASE}/temperature`).then(r => r.json()),
      fetch(`${API_BASE}/sea-level`).then(r => r.json()),
      fetch(`${API_BASE}/temperature-predictions`).then(r => r.json()),
      fetch(`${API_BASE}/sea-level-predictions`).then(r => r.json())
    ]);

    // Chart 1: Historical Observed Temperature
    if (tempData.years && tempData.observed_c) {
      createChart('chart1', 'line', {
        labels: tempData.years,
        values: tempData.observed_c
      }, 'Historical Observed Temperature (°C)');
    }

    // Chart 2: Historical Anthropogenic Temperature
    if (tempData.years && tempData.anthropogenic_c) {
      createChart('chart2', 'line', {
        labels: tempData.years,
        values: tempData.anthropogenic_c
      }, 'Historical Anthropogenic Temperature (°C)');
    }

    // Chart 3: Combined Temperature Comparison
    if (tempData.years) {
      createChart('chart3', 'line', {
        labels: tempData.years,
        datasets: [
          {
            label: 'Observed',
            data: tempData.observed_c,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 2
          },
          {
            label: 'Anthropogenic',
            data: tempData.anthropogenic_c,
            borderColor: 'rgba(255, 99, 132, 1)',
            backgroundColor: 'rgba(255, 99, 132, 0.1)',
            borderWidth: 2
          }
        ]
      }, 'Temperature Comparison');
    }

    // Chart 4: Historical Sea Level
    if (seaLevelData.years && seaLevelData.gmsl) {
      createChart('chart4', 'line', {
        labels: seaLevelData.years,
        values: seaLevelData.gmsl
      }, 'Historical Sea Level (mm)', { beginAtZero: false });
    }

    // Chart 5: Temperature Predictions
    if (tempPredData.years && tempPredData.predictions) {
      createChart('chart5', 'line', {
        labels: tempPredData.years,
        values: tempPredData.predictions
      }, 'Temperature Predictions 2025-2050 (°C)', { beginAtZero: false });
    }

    // Chart 6: Sea Level Predictions
    if (seaLevelPredData.years && seaLevelPredData.predictions) {
      createChart('chart6', 'line', {
        labels: seaLevelPredData.years,
        values: seaLevelPredData.predictions
      }, 'Sea Level Predictions 2025-2050 (mm)', { beginAtZero: false });
    }

    // Chart 7: Combined Historical + Predictions Temperature
    if (tempData.years && tempPredData.years) {
      const allYears = [...tempData.years, ...tempPredData.years];
      const allObserved = [...tempData.observed_c, ...new Array(tempPredData.years.length).fill(null)];
      const allPredictions = [...new Array(tempData.years.length).fill(null), ...tempPredData.predictions];
      
      createChart('chart7', 'line', {
        labels: allYears,
        datasets: [
          {
            label: 'Historical',
            data: allObserved,
            borderColor: 'rgba(75, 192, 192, 1)',
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 2
          },
          {
            label: 'Predictions',
            data: allPredictions,
            borderColor: 'rgba(255, 206, 86, 1)',
            backgroundColor: 'rgba(255, 206, 86, 0.1)',
            borderWidth: 2,
            borderDash: [5, 5]
          }
        ]
      }, 'Temperature: Historical + Predictions');
    }

    // Chart 8: Combined Historical + Predictions Sea Level
    if (seaLevelData.years && seaLevelPredData.years) {
      const allYears = [...seaLevelData.years, ...seaLevelPredData.years];
      const allHistorical = [...seaLevelData.gmsl, ...new Array(seaLevelPredData.years.length).fill(null)];
      const allPredictions = [...new Array(seaLevelData.years.length).fill(null), ...seaLevelPredData.predictions];
      
      createChart('chart8', 'line', {
        labels: allYears,
        datasets: [
          {
            label: 'Historical',
            data: allHistorical,
            borderColor: 'rgba(54, 162, 235, 1)',
            backgroundColor: 'rgba(54, 162, 235, 0.1)',
            borderWidth: 2
          },
          {
            label: 'Predictions',
            data: allPredictions,
            borderColor: 'rgba(255, 159, 64, 1)',
            backgroundColor: 'rgba(255, 159, 64, 0.1)',
            borderWidth: 2,
            borderDash: [5, 5]
          }
        ]
      }, 'Sea Level: Historical + Predictions', { beginAtZero: false });
    }

    // Chart 9: Temperature Trend (all data combined)
    if (tempData.years && tempPredData.years) {
      const allYears = [...tempData.years, ...tempPredData.years];
      const allObserved = [...tempData.observed_c];
      const lastObserved = tempData.observed_c[tempData.observed_c.length - 1];
      const firstPred = tempPredData.predictions[0];
      const allPredictions = [lastObserved, ...tempPredData.predictions];
      const allData = [...allObserved, ...tempPredData.predictions];
      
      createChart('chart9', 'line', {
        labels: allYears,
        values: allData
      }, 'Complete Temperature Trend (°C)', { beginAtZero: false });
    }

  } catch (error) {
    console.error('Error loading charts:', error);
    // Display error message
    document.querySelector('.chart-grid').innerHTML = 
      '<div style="color: white; text-align: center; padding: 20px;">Error loading data. Make sure the Flask server is running on port 5000.</div>';
  }
}

// Load charts when page loads
loadCharts();