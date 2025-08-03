# Deployment Guide

## GitHub Pages (Static Landing Page)
The repository automatically deploys a static landing page to GitHub Pages at:
https://pawanbhattad.github.io/ai_investment_hub/

## Streamlit Cloud Deployment

### Option 1: Streamlit Cloud (Recommended)
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select the repository: `pawanbhattad/ai_investment_hub`
4. Set main file path: `app.py`
5. Deploy!

### Option 2: Hugging Face Spaces
1. Go to [huggingface.co/spaces](https://huggingface.co/spaces)
2. Create new Space with Streamlit SDK
3. Upload the files or connect GitHub repo
4. Your app will be available at: `https://huggingface.co/spaces/your-username/ai-investment-hub`

### Option 3: Local Development
```bash
git clone https://github.com/pawanbhattad/ai_investment_hub.git
cd ai_investment_hub
pip install -r requirements.txt
streamlit run app.py
```

## Environment Variables
No environment variables are required for basic functionality. The app uses Yahoo Finance API which doesn't require authentication.

## Dependencies
- Python 3.8+
- Streamlit 1.39.0+
- pandas 2.2.2+
- plotly 5.22.0+
- yfinance 0.2.28+

## Features Available After Deployment
- ✅ Real-time stock data via Yahoo Finance
- ✅ Interactive charts and visualizations
- ✅ Company comparison tools
- ✅ Dark/Light theme support
- ✅ Mobile-responsive design
- ✅ Citation system with links
- ✅ Investment category analysis

## Performance Notes
- First load may take 10-15 seconds due to data fetching
- Stock data is cached for 5 minutes to improve performance
- Charts render client-side for smooth interactions

## Troubleshooting
- If stock data doesn't load, check Yahoo Finance API status
- For deployment issues, ensure all files are present in the repository
- Mobile users: use landscape mode for best chart viewing experience