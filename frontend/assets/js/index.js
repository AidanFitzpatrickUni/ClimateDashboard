const API_BASE = 'http://127.0.0.1:5000/api';

async function loadNews() {
    try {
        const response = await fetch(`${API_BASE}/news`);
        const data = await response.json();
        const container = document.getElementById('news-container');
        
        if (data.articles && data.articles.length > 0) {
            let html = '';
            data.articles.forEach(article => {
                const date = new Date(article.publishedAt).toLocaleDateString();
                html += `
                    <div style="margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #26408B;">
                        <h4 style="color: #DCAB6B; margin-bottom: 8px;">
                            <a href="${article.url}" target="_blank" style="color: #DCAB6B; text-decoration: none;">
                                ${article.title}
                            </a>
                        </h4>
                        <p style="color: #f0f0f0; margin-bottom: 5px; font-size: 0.9em;">
                            ${article.description || 'No description available.'}
                        </p>
                        <div style="color: #888; font-size: 0.8em;">
                            ${article.source} • ${date}
                        </div>
                    </div>
                `;
            });
            container.innerHTML = html;
        } else {
            container.innerHTML = '<p style="color: #f0f0f0;">No news articles available.</p>';
        }
    } catch (error) {
        console.error('Error loading news:', error);
        document.getElementById('news-container').innerHTML = 
            '<p style="color: #f0f0f0;">Error loading news. Make sure the Flask server is running.</p>';
    }
}

// Load news when page loads
loadNews();
