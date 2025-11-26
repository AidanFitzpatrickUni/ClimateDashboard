from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from pathlib import Path
import sqlite3
import requests
from datetime import datetime, timedelta
import os

# Get absolute paths
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend"

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path='')
CORS(app)  # Enable CORS for frontend requests

# Database path
DB_PATH = Path(__file__).resolve().parent / "data" / "climate.db"

# News API configuration
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '7f876b4083d6424a8a229aa66e0d78d4')
NEWS_API_URL = 'https://newsapi.org/v2/everything'

@app.route('/')
def index():
    """Serve the main index page"""
    return send_from_directory(str(FRONTEND_DIR), 'index.html')

@app.route('/frontend/<path:path>')
def serve_frontend(path):
    """Serve frontend static files"""
    return send_from_directory(str(FRONTEND_DIR), path)

@app.route('/assets/<path:path>')
def serve_assets(path):
    """Serve assets (CSS, JS, images)"""
    return send_from_directory(str(FRONTEND_DIR / 'assets'), path)

@app.route('/api/temperature')
def get_temperature():
    """Get historical temperature data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT year, observed_c, anthropogenic_c FROM temperature ORDER BY year")
        rows = cursor.fetchall()
        
        data = {
            'years': [row['year'] for row in rows],
            'observed_c': [row['observed_c'] for row in rows],
            'anthropogenic_c': [row['anthropogenic_c'] for row in rows]
        }
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sea-level')
def get_sea_level():
    """Get historical sea level data"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT year, gmsl FROM sea_level ORDER BY year")
        rows = cursor.fetchall()
        
        data = {
            'years': [row['year'] for row in rows],
            'gmsl': [row['gmsl'] for row in rows]
        }
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/temperature-predictions')
def get_temperature_predictions():
    """Get temperature predictions up to 2050"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT year, prediction FROM future_predictions ORDER BY year")
        rows = cursor.fetchall()
        
        data = {
            'years': [row['year'] for row in rows],
            'predictions': [row['prediction'] for row in rows]
        }
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sea-level-predictions')
def get_sea_level_predictions():
    """Get sea level predictions up to 2050"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT year, prediction FROM sea_level_predictions ORDER BY year")
        rows = cursor.fetchall()
        
        data = {
            'years': [row['year'] for row in rows],
            'predictions': [row['prediction'] for row in rows]
        }
        
        conn.close()
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news')
def get_news():
    """Get recent climate change and sea level news articles"""
    try:
        # Calculate date from 30 days ago for recent articles
        from_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Query parameters for NewsAPI
        params = {
            'q': 'global warming OR climate change OR sea level rise',
            'language': 'en',
            'sortBy': 'publishedAt',
            'from': from_date,
            'pageSize': 10,
            'apiKey': NEWS_API_KEY
        }
        
        response = requests.get(NEWS_API_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            news_data = response.json()
            articles = news_data.get('articles', [])
            
            # Format articles for frontend
            formatted_articles = []
            for article in articles[:10]:  # Limit to 10 articles
                formatted_articles.append({
                    'title': article.get('title', 'No title'),
                    'description': article.get('description', 'No description'),
                    'url': article.get('url', '#'),
                    'publishedAt': article.get('publishedAt', ''),
                    'source': article.get('source', {}).get('name', 'Unknown')
                })
            
            return jsonify({'articles': formatted_articles})
        else:
            # Fallback to mock data if API fails
            return jsonify({
                'articles': [
                    {
                        'title': 'Climate Change: Latest Research Findings',
                        'description': 'Recent studies show accelerating global temperature trends.',
                        'url': '#',
                        'publishedAt': datetime.now().isoformat(),
                        'source': 'Climate News'
                    }
                ]
            })
    except Exception as e:
        # Return mock data on error
        return jsonify({
            'articles': [
                {
                    'title': 'Error loading news',
                    'description': f'Could not fetch news: {str(e)}',
                    'url': '#',
                    'publishedAt': datetime.now().isoformat(),
                    'source': 'System'
                }
            ]
        })

@app.route('/api/admin/database-status')
def database_status():
    """Check database connection and return status"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if database exists and is accessible
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # Get row counts for each table
        table_info = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_info[table] = count
        
        # Get database file info
        db_size = DB_PATH.stat().st_size if DB_PATH.exists() else 0
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'connected': True,
            'database_path': str(DB_PATH),
            'database_exists': DB_PATH.exists(),
            'database_size_bytes': db_size,
            'database_size_mb': round(db_size / (1024 * 1024), 2),
            'tables': tables,
            'table_counts': table_info,
            'message': f'Database connected successfully. Found {len(tables)} tables.'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'connected': False,
            'database_path': str(DB_PATH),
            'database_exists': DB_PATH.exists(),
            'error': str(e),
            'message': f'Database connection failed: {str(e)}'
        }), 500

@app.route('/api/admin/read-database')
def read_database():
    """Read and return database contents from all tables"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        database_contents = {}
        
        for table in tables:
            # Get table schema
            cursor.execute(f"PRAGMA table_info({table})")
            columns = [{'name': row[1], 'type': row[2]} for row in cursor.fetchall()]
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            row_count = cursor.fetchone()[0]
            
            # Get sample data (limit to 100 rows per table to avoid overwhelming the response)
            cursor.execute(f"SELECT * FROM {table} ORDER BY year LIMIT 100")
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries
            data = []
            for row in rows:
                row_dict = {}
                for col in row.keys():
                    row_dict[col] = row[col]
                data.append(row_dict)
            
            database_contents[table] = {
                'columns': columns,
                'row_count': row_count,
                'sample_data': data,
                'showing_rows': len(data),
                'total_rows': row_count
            }
        
        conn.close()
        
        return jsonify({
            'status': 'success',
            'tables': list(database_contents.keys()),
            'data': database_contents,
            'message': f'Successfully read {len(tables)} tables'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': f'Failed to read database: {str(e)}'
        }), 500

@app.route('/api/admin/api-details')
def api_details():
    """Get API endpoint details and configuration"""
    try:
        # Test news API connection
        news_api_status = 'unknown'
        news_api_message = ''
        try:
            test_params = {
                'q': 'climate',
                'language': 'en',
                'pageSize': 1,
                'apiKey': NEWS_API_KEY
            }
            test_response = requests.get(NEWS_API_URL, params=test_params, timeout=5)
            if test_response.status_code == 200:
                news_api_status = 'connected'
                news_api_message = 'News API is working correctly'
            elif test_response.status_code == 401:
                news_api_status = 'unauthorized'
                news_api_message = 'News API key is invalid or expired'
            else:
                news_api_status = 'error'
                news_api_message = f'News API returned status {test_response.status_code}'
        except Exception as e:
            news_api_status = 'error'
            news_api_message = f'News API connection failed: {str(e)}'
        
        # Get all available API endpoints
        endpoints = [
            {
                'path': '/api/temperature',
                'method': 'GET',
                'description': 'Get historical temperature data'
            },
            {
                'path': '/api/sea-level',
                'method': 'GET',
                'description': 'Get historical sea level data'
            },
            {
                'path': '/api/temperature-predictions',
                'method': 'GET',
                'description': 'Get temperature predictions up to 2050'
            },
            {
                'path': '/api/sea-level-predictions',
                'method': 'GET',
                'description': 'Get sea level predictions up to 2050'
            },
            {
                'path': '/api/news',
                'method': 'GET',
                'description': 'Get recent climate change news articles'
            },
            {
                'path': '/api/admin/database-status',
                'method': 'GET',
                'description': 'Check database connection status'
            },
            {
                'path': '/api/admin/api-details',
                'method': 'GET',
                'description': 'Get API details and configuration'
            }
        ]
        
        return jsonify({
            'status': 'success',
            'api_base_url': 'http://127.0.0.1:5000',
            'total_endpoints': len(endpoints),
            'endpoints': endpoints,
            'news_api': {
                'status': news_api_status,
                'message': news_api_message,
                'url': NEWS_API_URL,
                'key_configured': bool(NEWS_API_KEY and NEWS_API_KEY != 'your_api_key_here')
            },
            'server_info': {
                'flask_version': '3.0.0',
                'python_version': '3.9+',
                'cors_enabled': True
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'message': f'Failed to get API details: {str(e)}'
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')
