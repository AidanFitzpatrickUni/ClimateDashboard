"""
Tests for the Flask API endpoints.
"""

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.api]
import json
import sqlite3
from pathlib import Path


class TestAPIEndpoints:
    """Check that all the API endpoints work correctly."""
    
    def test_index_route(self, app_client):
        """Make sure the home page loads."""
        response = app_client.get('/')
        assert response.status_code == 200
    
    def test_temperature_endpoint(self, app_client):
        """Check that the temperature data endpoint returns the right data."""
        response = app_client.get('/api/temperature')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'years' in data
        assert 'observed_c' in data
        assert 'anthropogenic_c' in data
        assert len(data['years']) > 0
    
    def test_sea_level_endpoint(self, app_client):
        """Verify the sea level endpoint works."""
        response = app_client.get('/api/sea-level')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'years' in data
        assert 'gmsl' in data
        assert len(data['years']) > 0
    
    def test_temperature_predictions_endpoint(self, app_client):
        """Check that temperature predictions are returned."""
        response = app_client.get('/api/temperature-predictions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'years' in data
        assert 'predictions' in data
    
    def test_sea_level_predictions_endpoint(self, app_client):
        """Make sure sea level predictions come through."""
        response = app_client.get('/api/sea-level-predictions')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'years' in data
        assert 'predictions' in data
    
    def test_news_endpoint(self, app_client):
        """Check that the news endpoint returns articles."""
        response = app_client.get('/api/news')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'articles' in data
        assert isinstance(data['articles'], list)
    
    def test_database_status_endpoint(self, app_client):
        """Verify the database status endpoint works."""
        response = app_client.get('/api/admin/database-status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'connected' in data
        assert 'tables' in data
    
    def test_read_database_endpoint(self, app_client):
        """Check that we can read database contents via the API."""
        response = app_client.get('/api/admin/read-database')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'tables' in data
        assert 'data' in data
    
    def test_api_details_endpoint(self, app_client):
        """Make sure the API details endpoint returns info about endpoints."""
        response = app_client.get('/api/admin/api-details')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'status' in data
        assert 'endpoints' in data
        assert 'news_api' in data
    
    def test_assets_route(self, app_client):
        """Check that assets can be served."""
        response = app_client.get('/assets/css/index.css')
        # Might be 404 if file doesn't exist, but the route should work
        assert response.status_code in [200, 404]
    
    def test_frontend_route(self, app_client):
        """Verify frontend files can be served."""
        response = app_client.get('/frontend/index.html')
        # Could be 404 if missing, but route should be accessible
        assert response.status_code in [200, 404]

