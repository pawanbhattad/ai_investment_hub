import streamlit as st
import pandas as pd

# Handle plotly import with error catching
try:
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError as e:
    st.error(f"Plotly not available: {e}")
    PLOTLY_AVAILABLE = False

from datetime import datetime, timedelta
import yfinance as yf
from content import COMPANY_PROFILES, INVESTMENT_CATEGORIES, MARKET_INSIGHTS
import re

# Page configuration
st.set_page_config(
    page_title="AI Infrastructure Investment Hub | Stock Analysis & Research",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize mobile mode for responsive design
if 'mobile_mode' not in st.session_state:
    st.session_state['mobile_mode'] = False

# Custom CSS for mobile optimization and styling
st.markdown("""
<style>
    /* Global font consistency */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* Consistent paragraph and text sizing */
    .stMarkdown p, .stWrite p {
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 1em;
        font-weight: normal;
        font-style: normal;
        text-decoration: none;
    }

    /* Consistent headers */
    .stMarkdown h1 { font-size: 2em; font-weight: 600; margin-bottom: 0.5em; }
    .stMarkdown h2 { font-size: 1.5em; font-weight: 600; margin-bottom: 0.5em; }
    .stMarkdown h3 { font-size: 1.25em; font-weight: 600; margin-bottom: 0.5em; }
    .stMarkdown h4 { font-size: 1.1em; font-weight: 600; margin-bottom: 0.5em; }

    /* Prevent unwanted markdown formatting */
    .stMarkdown em { font-style: normal !important; }
    .stMarkdown strong { font-weight: 600; }
    .stMarkdown del { text-decoration: none; }
    .stMarkdown i { font-style: normal !important; }

    /* Ensure company overview text is consistent */
    .stMarkdown p {
        font-style: normal !important;
    }

    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        /* Global mobile optimizations */
        .stTabs [data-baseweb="tab-list"] {
            flex-wrap: wrap;
        }
        .stMarkdown p, .stWrite p {
            font-size: 14px;
        }
        
        /* Mobile-specific chart sizing with proper spacing */
        .stPlotlyChart {
            height: 300px !important;
            margin-bottom: 30px !important;
        }
        
        /* Ensure proper spacing after charts with higher specificity */
        .stApp .main .block-container .stPlotlyChart {
            margin-bottom: 30px !important;
        }
        
        /* Chart spacer containers */
        .chart-spacer {
            height: 30px !important;
            width: 100% !important;
            clear: both !important;
        }
        
        /* Section spacers */
        .section-spacer {
            height: 20px !important;
            width: 100% !important;
            clear: both !important;
        }
        
        /* Prevent content overlap on charts */
        [data-testid="stPlotlyChart"] + div {
            margin-top: 30px !important;
        }
        
        /* Period button optimizations for mobile */
        [data-testid="column"] {
            padding: 2px !important;
        }
        
        /* Touch-optimized buttons following 44px standards */
        .stButton > button {
            min-height: 44px !important;
            min-width: 44px !important;
            padding: 10px 12px !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            margin: 3px 0 !important;
            border-radius: 6px !important;
            touch-action: manipulation !important;
        }
        
        /* Period button grid for mobile - ensure proper touch targets */
        .period-buttons-flat [data-testid="column"],
        .comp-period-buttons-flat [data-testid="column"] {
            width: 25% !important;
            flex: 0 0 25% !important;
            padding: 3px !important;
        }
        
        /* Ensure all buttons meet touch standards */
        .stButton button {
            width: 100% !important;
            font-size: 12px !important;
            padding: 8px 6px !important;
            min-height: 44px !important;
            font-weight: 500 !important;
        }
        
        /* Chart type selector mobile optimization */
        .chart-type-mobile {
            margin-top: 8px !important;
        }
        
        /* Touch-optimized metric cards mobile layout */
        .metric-card {
            margin: 10px 0;
            padding: 16px 14px;
            min-height: 80px;
            border-radius: 8px;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            cursor: pointer;
        }
        
        .metric-card:hover, .metric-card:active {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        }
        
        .metric-value {
            font-size: 22px;
            font-weight: 600;
        }
        
        .metric-label {
            font-size: 13px;
            font-weight: 500;
        }
        
        /* Company cards mobile optimization */
        .company-card {
            height: 160px !important;
            margin: 6px 0 !important;
            padding: 12px !important;
        }
        
        /* Mobile navigation improvements */
        .stSelectbox > div > div {
            font-size: 14px;
        }
        
        /* Reduce excessive padding in mobile columns */
        [data-testid="column"] > div {
            padding-top: 0.5rem !important;
            padding-bottom: 0.5rem !important;
        }
        
        /* Touch-optimized financial metrics - flat 4-column layout */
        .financial-metrics-flat [data-testid="column"] {
            width: 25% !important;
            flex: 0 0 25% !important;
            padding: 4px !important;
            min-height: 44px !important;
        }
        
        /* Stack to 2 columns on very small screens */
        @media (max-width: 480px) {
            .financial-metrics-flat [data-testid="column"] {
                width: 50% !important;
                flex: 0 0 50% !important;
            }
        }
        
        /* Legacy support for old container class */
        .financial-metrics-container [data-testid="column"] {
            width: 50% !important;
            flex: 0 0 50% !important;
            padding: 4px !important;
        }
        
        /* Company info cards mobile - 2 columns */
        .company-info-container [data-testid="column"] {
            width: 50% !important;
            flex: 0 0 50% !important;
        }
        
        /* Market overview mobile - stack vertically */
        .market-overview-container [data-testid="column"] {
            width: 100% !important;
            flex: 0 0 100% !important;
            margin-bottom: 10px !important;
        }
        
        /* Investment category company cards - 2 per row on mobile */
        .stTabs [data-testid="column"] {
            width: 50% !important;
            flex: 0 0 50% !important;
            padding: 4px !important;
        }
        
        /* Override Streamlit's default column behavior on mobile */
        [data-testid="column"] {
            min-width: auto !important;
        }
        
        /* Specific mobile overrides for containers */
        @media (max-width: 768px) {
            .financial-metrics-container {
                display: flex !important;
                flex-wrap: wrap !important;
            }
            
            .company-info-container {
                display: flex !important;
                flex-wrap: wrap !important;
            }
        }
        
        /* Mobile expander optimization */
        .streamlit-expanderHeader {
            font-size: 16px !important;
        }
        
        /* Touch target optimization */
        button, select, input {
            min-height: 44px !important;
        }
        
        /* Responsive text sizing */
        h1 { font-size: 1.8em !important; }
        h2 { font-size: 1.4em !important; }
        h3 { font-size: 1.2em !important; }
        h4 { font-size: 1.1em !important; }
    }
    
    /* Tablet responsive design */
    @media (min-width: 769px) and (max-width: 1024px) {
        .stPlotlyChart {
            height: 450px !important;
        }
        
        .metric-card {
            padding: 18px 15px;
            min-height: 80px;
        }
        
        .company-card {
            height: 170px !important;
        }
    }

    /* Expandable sections */
    .expandable-header {
        cursor: pointer;
        padding: 10px;
        background-color: #f0f2f6;
        border-radius: 5px;
        margin: 5px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .expandable-header:hover {
        background-color: #e0e2e6;
    }

    /* Metric cards */
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px 15px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        min-height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        margin-bottom: 15px;
    }

    .metric-value {
        font-size: 24px;
        font-weight: 600;
        color: #1f77b4;
        margin-bottom: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    .metric-label {
        font-size: 14px;
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }

    /* Citation styling */
    .citation {
        font-size: 12px;
        color: #0066cc;
        vertical-align: super;
        cursor: pointer;
        text-decoration: none;
        position: relative;
    }

    .citation:hover {
        text-decoration: underline;
        color: #0052a3;
    }

    /* Tooltip styling for citations */
    .citation[title]:hover::after {
        content: attr(title);
        position: absolute;
        left: 100%;
        top: -5px;
        white-space: nowrap;
        background: #333;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 11px;
        z-index: 1000;
        margin-left: 5px;
        font-weight: normal;
    }

    /* Risk factor styling */
    .risk-high {
        color: #d32f2f;
        font-weight: bold;
    }

    .risk-medium {
        color: #f57c00;
        font-weight: bold;
    }

    .risk-low {
        color: #388e3c;
        font-weight: bold;
    }

    /* Company card styling - base */
    .company-card {
        border-radius: 10px;
        padding: 15px;
        margin: 8px 0;
        transition: box-shadow .3s, border-color .3s, background-color .3s;
        height: 180px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        overflow: hidden;
    }

    /* Default light theme styling */
    .company-card {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        color: #1e1e1e;
    }

    .company-card:hover {
        box-shadow: 0 6px 25px 0 rgba(0,0,0,0.1);
        border-color: #007bff;
        background-color: #f8f9fa;
    }

    /* Dark theme override using attribute selector */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .company-card,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .company-card {
        background-color: #1e1e1e !important;
        border: 1px solid #444 !important;
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .company-card:hover,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .company-card:hover {
        background-color: #2a2a2a !important;
        border-color: #007bff !important;
    }


    /* Category overview cards */
    .category-overview-card {
        background-color: #f0f2f6;
        color: #1e1e1e;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Dark theme overrides for metric and category cards */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .metric-card,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .metric-card {
        background-color: #1e1e1e !important;
        border: 1px solid #444 !important;
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .category-overview-card,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .category-overview-card {
        background-color: #1e1e1e !important;
        border: 1px solid #444 !important;
        color: #ffffff !important;
    }

    /* Text colors for light theme (default) */
    .company-name {
        color: #1e1e1e;
    }

    .ticker-span {
        color: #666;
    }

    .country-text {
        color: #666;
    }

    .market-cap {
        color: #1f77b4;
    }

    .metric-label {
        color: #666;
    }

    .metric-value {
        color: #1e1e1e;
    }

    .recommendation-box {
        border-top: 1px solid #e0e0e0;
        color: #1e1e1e;
    }

    /* Dark theme text color overrides */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .company-name,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .company-name {
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .ticker-span,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .ticker-span {
        color: #999 !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .country-text,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .country-text {
        color: #999 !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .market-cap,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .market-cap {
        color: #4dabf7 !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .metric-label,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .metric-label {
        color: #999 !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .metric-value,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .metric-value {
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .recommendation-box,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .recommendation-box {
        border-top: 1px solid #444 !important;
        color: #ffffff !important;
    }

    /* Dark theme for expandable headers */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .expandable-header,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .expandable-header {
        background-color: #1e1e1e !important;
        border: 1px solid #444 !important;
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .expandable-header:hover,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .expandable-header:hover {
        background-color: #2a2a2a !important;
    }

    /* Ensure all text in dark theme cards is visible */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .metric-card .metric-value,
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .metric-card .metric-label,
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .category-overview-card div,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .metric-card .metric-value,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .metric-card .metric-label,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .category-overview-card div {
        color: #ffffff !important;
    }

    /* Segmented control styling */
    .stSegmentedControl {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 4px;
    }

    /* Dark theme for segmented control */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .stSegmentedControl,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .stSegmentedControl {
        background-color: #1e1e1e !important;
    }

    .stSegmentedControl button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .stSegmentedControl button[data-active="true"] {
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Dark theme for active segmented control button */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .stSegmentedControl button[data-active="true"],
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .stSegmentedControl button[data-active="true"] {
        background-color: #2a2a2a !important;
        color: #ffffff !important;
    }

    /* Dark theme support for dataframes */
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .stDataFrame,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .stDataFrame {
        color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .stDataFrame td,
    [data-testid="stAppViewContainer"][style*="background-color: rgb(14, 17, 23)"] .stDataFrame th,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .stDataFrame td,
    [data-testid="stAppViewContainer"][style*="background: rgb(14, 17, 23)"] .stDataFrame th {
        color: #ffffff !important;
    }

    /* Chart controls */
    .chart-controls {
        display: flex;
        gap: 5px;
        margin-bottom: 10px;
    }

    .period-button {
        padding: 5px 12px;
        border-radius: 4px;
        font-size: 14px;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_currency_symbol(ticker):
    """Returns '₹' for Indian stocks (.NS), otherwise '$'."""
    if isinstance(ticker, str) and ticker.endswith(".NS"):
        return "₹"
    return "$"

def format_market_cap_with_currency(market_cap_str, ticker):
    """Convert market cap string to use appropriate currency symbol based on ticker."""
    if not market_cap_str:
        return market_cap_str

    # Get the appropriate currency symbol
    currency = get_currency_symbol(ticker)

    # Replace $ with the appropriate currency symbol
    if currency == "₹":
        return market_cap_str.replace("$", "₹")

    return market_cap_str

def format_large_number(num):
    if num is None or not isinstance(num, (int, float)) or num == 0:
        return "N/A"
    if abs(num) >= 1e12:
        return f"{num / 1e12:.2f}T"
    if abs(num) >= 1e9:
        return f"{num / 1e9:.2f}B"
    if abs(num) >= 1e6:
        return f"{num / 1e6:.2f}M"
    return f"{num:,.0f}"

@st.cache_data(ttl=300)
def fetch_stock_data(ticker, period="1y"):
    """Fetch stock data from Yahoo Finance with proper formatting."""
    try:
        # Handle Indian stocks
        indian_tickers = {
            "TATACOMM": "TATACOMM.NS",
            "NETWEB": "NETWEB.NS",
            "RAILTEL": "RAILTEL.NS",
            "TECHNOE": "TECHNOE.NS",
            "ANANTRAJ": "ANANTRAJ.NS",
            "MARINE": "MARINE.NS",
            "SIFY": None,
            "KIRLOSKAROIL": None
        }

        if ticker in indian_tickers:
            if indian_tickers[ticker] is None:
                return None, None, "Invalid ticker or no data found."
            formatted_ticker = indian_tickers[ticker]
        else:
            formatted_ticker = ticker

        stock = yf.Ticker(formatted_ticker)
        hist = stock.history(period=period)
        info = stock.info
        return info, hist, None
    except Exception as e:
        return None, None, f"Error fetching data for {ticker}: {e}"

def create_advanced_stock_chart(info, hist, ticker, chart_type="candlestick"):
    """Create an advanced stock chart with technical indicators."""
    
    if not PLOTLY_AVAILABLE:
        st.error("Plotly is required for charts but not available. Please check the deployment logs.")
        return None

    if hist is None or hist.empty:
        st.error(f"No historical data available for {ticker}")
        return None

    # Create figure with subplots
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=[0.7, 0.3],
        subplot_titles=(f"{ticker} Price Chart", "Volume")
    )

    # Main price chart based on chart type
    if chart_type == "candlestick":
        fig.add_trace(
            go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name="OHLC"
            ),
            row=1, col=1
        )
    elif chart_type == "area":
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist['Close'],
                fill='tozeroy',
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4', width=2),
                fillcolor='rgba(31, 119, 180, 0.3)'
            ),
            row=1, col=1
        )
    else:  # line chart
        fig.add_trace(
            go.Scatter(
                x=hist.index,
                y=hist['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )

    # Moving averages
    if len(hist) >= 20:
        ma20 = hist['Close'].rolling(window=20).mean()
        fig.add_trace(
            go.Scatter(x=hist.index, y=ma20, name="MA20", line=dict(color='orange', width=1)),
            row=1, col=1
        )

    if len(hist) >= 50:
        ma50 = hist['Close'].rolling(window=50).mean()
        fig.add_trace(
            go.Scatter(x=hist.index, y=ma50, name="MA50", line=dict(color='red', width=1)),
            row=1, col=1
        )

    # Volume bars
    colors = ['red' if row['Close'] < row['Open'] else 'green' for _, row in hist.iterrows()]
    fig.add_trace(
        go.Bar(x=hist.index, y=hist['Volume'], name="Volume", marker_color=colors),
        row=2, col=1
    )

    # Responsive chart height with improved mobile detection
    import streamlit as st
    
    # More sophisticated responsive height calculation
    # CSS media query-like behavior: assume mobile if not explicitly set
    is_mobile = st.session_state.get('mobile_mode', True)  # Default to mobile-friendly
    
    # Progressive height sizing
    if is_mobile:
        chart_height = 350  # Slightly taller for better mobile readability
        legend_size = 9
        font_size = 11
        margin_size = 25
    else:
        chart_height = 500
        legend_size = 10
        font_size = 12
        margin_size = 40
    
    # Update layout with responsive sizing
    fig.update_layout(
        height=chart_height,
        xaxis_rangeslider_visible=False,
        template="plotly_white",
        showlegend=True,
        legend=dict(
            x=0, y=1.02,  # Position legend above chart for mobile
            orientation="h" if is_mobile else "v",
            font=dict(size=legend_size),
            bgcolor="rgba(255,255,255,0.9)"
        ),
        margin=dict(
            l=margin_size, 
            r=margin_size, 
            t=40 if is_mobile else 50,  # Extra top margin for horizontal legend
            b=margin_size
        ),
        hovermode='x unified',
        font=dict(size=font_size),
        # Ensure responsive behavior
        autosize=True
    )

    # Dynamic Y-axis scaling
    if chart_type == "candlestick":
        price_min = hist['Low'].min()
        price_max = hist['High'].max()
    else:
        price_min = hist['Close'].min()
        price_max = hist['Close'].max()

    price_range = price_max - price_min
    price_padding = price_range * 0.05  # 5% padding

    fig.update_yaxes(
        title_text="Price",
        row=1, col=1,
        range=[price_min - price_padding, price_max + price_padding]
    )

    fig.update_yaxes(
        title_text="Volume",
        row=2, col=1,
        rangemode='tozero'
    )

    fig.update_xaxes(title_text="Date", row=2, col=1)

    return fig

def display_stock_metrics(info, hist):
    """Display stock metrics in a card layout."""
    if not info or hist.empty:
        st.warning("Could not retrieve stock metrics.")
        return

    ticker = info.get('symbol', '')
    currency = get_currency_symbol(ticker)

    latest_price = hist['Close'].iloc[-1]

    # Calculate changes
    if len(hist) >= 2:
        prev_close = hist['Close'].iloc[-2]
    else:
        prev_close = info.get('previousClose', latest_price)

    change = latest_price - prev_close
    change_pct = (change / prev_close) * 100 if prev_close else 0

    # Calculate 52-week range
    fifty_two_week_low = hist['Low'].tail(252).min() if len(hist) >= 252 else hist['Low'].min()
    fifty_two_week_high = hist['High'].tail(252).max() if len(hist) >= 252 else hist['High'].max()

    # Display metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Current Price",
            f"{currency}{latest_price:.2f}",
            delta=f"{change:+.2f} ({change_pct:+.2f}%)"
        )

    with col2:
        st.metric(
            "Market Cap",
            f"{currency}{format_large_number(info.get('marketCap'))}"
        )

    with col3:
        st.metric(
            "P/E Ratio",
            f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else "N/A"
        )

    with col4:
        st.metric(
            "52-Week Range",
            f"{currency}{fifty_two_week_low:.2f} - {currency}{fifty_two_week_high:.2f}"
        )

def display_metric_card(label, value, col):
    """Display a metric in a card format."""
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """, unsafe_allow_html=True)

def display_financial_metrics(metrics):
    """Display financial metrics in a mobile-responsive grid using flat structure."""
    st.markdown('<div class="financial-metrics-flat">', unsafe_allow_html=True)

    # Format values consistently
    def format_metric_value(value):
        if isinstance(value, (int, float)):
            if abs(value) > 100:
                return f"{value:,.0f}"
            else:
                return f"{value:.1f}"
        elif isinstance(value, str) and value != "N/A":
            # Clean up percentage signs and formatting
            return value.strip()
        return value

    metric_mapping = [
        ("P/E Ratio", format_metric_value(metrics.get("trailing_pe", "N/A"))),
        ("Forward P/E", format_metric_value(metrics.get("forward_pe", "N/A"))),
        ("PEG Ratio", format_metric_value(metrics.get("peg_ratio", "N/A"))),
        ("ROE", metrics.get("roe", "N/A")),
        ("Revenue Growth", metrics.get("revenue_growth_yoy", "N/A")),
        ("Free Cash Flow", metrics.get("free_cash_flow", "N/A")),
        ("Debt/Equity", format_metric_value(metrics.get("debt_to_equity", "N/A"))),
        ("Net Margin", metrics.get("net_margin", "N/A"))
    ]

    # Streamlit-native flat structure: Row 1 with 4 columns (no nesting)
    metric_row1_col1, metric_row1_col2, metric_row1_col3, metric_row1_col4 = st.columns(4)
    
    with metric_row1_col1:
        if len(metric_mapping) > 0:
            display_metric_card(metric_mapping[0][0], metric_mapping[0][1], metric_row1_col1)
    
    with metric_row1_col2:
        if len(metric_mapping) > 1:
            display_metric_card(metric_mapping[1][0], metric_mapping[1][1], metric_row1_col2)
    
    with metric_row1_col3:
        if len(metric_mapping) > 2:
            display_metric_card(metric_mapping[2][0], metric_mapping[2][1], metric_row1_col3)
    
    with metric_row1_col4:
        if len(metric_mapping) > 3:
            display_metric_card(metric_mapping[3][0], metric_mapping[3][1], metric_row1_col4)
    
    # Small spacing between rows
    st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
    
    # Streamlit-native flat structure: Row 2 with 4 columns (no nesting)
    metric_row2_col1, metric_row2_col2, metric_row2_col3, metric_row2_col4 = st.columns(4)
    
    with metric_row2_col1:
        if len(metric_mapping) > 4:
            display_metric_card(metric_mapping[4][0], metric_mapping[4][1], metric_row2_col1)
    
    with metric_row2_col2:
        if len(metric_mapping) > 5:
            display_metric_card(metric_mapping[5][0], metric_mapping[5][1], metric_row2_col2)
    
    with metric_row2_col3:
        if len(metric_mapping) > 6:
            display_metric_card(metric_mapping[6][0], metric_mapping[6][1], metric_row2_col3)
    
    with metric_row2_col4:
        if len(metric_mapping) > 7:
            display_metric_card(metric_mapping[7][0], metric_mapping[7][1], metric_row2_col4)
    
    st.markdown('</div>', unsafe_allow_html=True)

def get_citation_title(citation_text, url=None):
    """Extract a human-readable title from citation text."""
    # Remove citation number prefix if present
    text = re.sub(r'^\[\d+\]\s*', '', citation_text).strip()

    # If we have a URL, try to generate a meaningful title
    if url and url != '#':
        if 'nvidia' in url.lower() and 'investor' in url.lower():
            return "NVIDIA Investor Relations"
        elif 'amd' in url.lower() and 'ir.' in url.lower():
            return "AMD Investor Relations"
        elif 'intel' in url.lower():
            return "Intel Official"
        elif 'microsoft' in url.lower() or 'azure' in url.lower():
            return "Microsoft Azure"
        elif 'aws.amazon' in url.lower():
            return "AWS Documentation"
        elif 'google' in url.lower() or 'cloud.google' in url.lower():
            return "Google Cloud"
        elif 'stockanalysis.com' in url.lower():
            return "Stock Analysis Data"
        elif 'reuters.com' in url.lower():
            return "Reuters Report"
        elif 'bloomberg.com' in url.lower():
            return "Bloomberg Analysis"
        elif 'finance.yahoo' in url.lower():
            return "Yahoo Finance"
        elif 'seekingalpha.com' in url.lower():
            if 'transcript' in url.lower():
                return "Earnings Call Transcript"
            return "Seeking Alpha Analysis"
        elif 'mckinsey.com' in url.lower():
            if 'ai' in url.lower():
                return "McKinsey AI Report"
            return "McKinsey Research"
        elif 'gartner.com' in url.lower():
            return "Gartner Research"
        elif 'annual' in url.lower() or 'annual-report' in url.lower():
            return "Annual Report"
        elif 'quarterly' in url.lower() or 'earnings' in url.lower():
            return "Quarterly Earnings"
        elif 'nasscom' in url.lower():
            return "NASSCOM Report"
        elif 'commerce.gov' in url.lower():
            return "U.S. Commerce Dept"
        else:
            # Extract domain name for a cleaner title
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', url)
            if domain_match:
                domain = domain_match.group(1).split('.')[0]
                return domain.replace('-', ' ').title()

    # For non-URL citations, clean up the text
    if text.startswith('http'):
        # It's a URL without a description, extract domain
        domain_match = re.search(r'https?://(?:www\.)?([^/]+)', text)
        if domain_match:
            domain = domain_match.group(1).split('.')[0]
            return domain.replace('-', ' ').title()

    # Return shortened version of long text
    if len(text) > 40:
        return text[:37] + "..."
    return text if text else "Source"

def get_citation_url(citation_text, company_ticker=None):
    """Extract or generate appropriate URL for citation."""
    # First check if there's already a URL in the citation
    url_match = re.search(r'https?://[^\s\]]+', citation_text)
    if url_match:
        return url_match.group(0)

    # Map common citation patterns to appropriate URLs
    citation_lower = citation_text.lower()

    # Financial data sources
    if 'annual report' in citation_lower or 'investor relations' in citation_lower:
        ticker_map = {
            'NVDA': 'https://investor.nvidia.com/financial-info/annual-reports/',
            'AMD': 'https://ir.amd.com/financial-information/annual-reports',
            'INTC': 'https://www.intc.com/financial-info/annual-reports',
            'MSFT': 'https://www.microsoft.com/en-us/investor/reports/ar23/',
            'GOOGL': 'https://abc.xyz/investor/',
            'AMZN': 'https://ir.aboutamazon.com/annual-reports/',
            'ORCL': 'https://investor.oracle.com/financial-reporting/',
            'DELL': 'https://investors.delltechnologies.com/financial-information/annual-reports',
            'ANET': 'https://investors.arista.com/financials/annual-reports/',
            'AVGO': 'https://investors.broadcom.com/financial-information/annual-reports',
            'MU': 'https://investors.micron.com/financials/annual-reports/',
            'VRT': 'https://investors.vertiv.com/financials/annual-reports/',
            'FIX': 'https://comfortsystemsusa.com/investor-relations/',
            'EQIX': 'https://investor.equinix.com/financial-information/annual-reports/',
            'DLR': 'https://investor.digitalrealty.com/financial-information/annual-reports',
            'ETN': 'https://www.eaton.com/us/en-us/company/investor-relations.html',
            'GNRC': 'https://investors.generac.com/financial-information/annual-reports',
            'INFY': 'https://www.infosys.com/investors/reports-filings/annual-report.html',
            'TCS.NS': 'https://www.tcs.com/investor-relations/financial-information',
            'TATACOMM.NS': 'https://www.tatacommunications.com/investor-relations/',
            'SIFY': 'https://www.sifytechnologies.com/investors/',
            'RAILTEL.NS': 'https://www.railtelindia.com/investor-relations',
            'NETWEB.NS': 'https://www.netwebindia.com/investor-relations',
            'TECHNOE.NS': 'https://www.techno.co.in/investor-relations/',
            'ANANTRAJ.NS': 'https://www.anantrajlimited.com/investor-relations/',
            'MARINE.NS': 'https://www.marineelectricals.com/investor-relations/',
            'KIRLOSKAROIL.NS': 'https://www.kirloskaroilengines.com/investor-relations/'
        }
        if company_ticker in ticker_map:
            return ticker_map[company_ticker]

    # Earnings reports and calls
    if 'earnings call' in citation_lower or 'earnings transcript' in citation_lower:
        if company_ticker:
            base_ticker = company_ticker.split('.')[0].upper()
            if 'q1' in citation_lower or 'q2' in citation_lower or 'q3' in citation_lower or 'q4' in citation_lower:
                return f'https://seekingalpha.com/symbol/{base_ticker}/earnings/transcripts'
            return f'https://seekingalpha.com/symbol/{base_ticker}/earnings'
    if 'earnings' in citation_lower or 'quarterly' in citation_lower:
        if company_ticker:
            base_ticker = company_ticker.split('.')[0]  # Remove .NS suffix
            return f'https://stockanalysis.com/stocks/{base_ticker.lower()}/'

    # Technology/product documentation
    if 'technology' in citation_lower or 'product' in citation_lower or 'platform' in citation_lower:
        tech_map = {
            'nvidia': 'https://www.nvidia.com/en-us/data-center/',
            'amd': 'https://www.amd.com/en/technologies/data-center',
            'intel': 'https://www.intel.com/content/www/us/en/data-center/overview.html',
            'microsoft': 'https://azure.microsoft.com/en-us/solutions/ai/',
            'google': 'https://cloud.google.com/solutions/ai',
            'aws': 'https://aws.amazon.com/ai/'
        }
        for company, url in tech_map.items():
            if company in citation_lower:
                return url

    # Market research reports
    if 'mckinsey ai report 2025' in citation_lower:
        return 'https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai'
    if 'gartner' in citation_lower:
        if 'magic quadrant' in citation_lower:
            return 'https://www.gartner.com/en/research/magic-quadrant'
        return 'https://www.gartner.com/en/research'
    if 'idc' in citation_lower:
        if 'server market' in citation_lower:
            return 'https://www.idc.com/getdoc.jsp?containerId=prUS51505323'
        return 'https://www.idc.com/'
    if 'forrester' in citation_lower:
        return 'https://www.forrester.com/research/'
    if 'mckinsey' in citation_lower:
        return 'https://www.mckinsey.com/industries/technology-media-and-telecommunications/our-insights'
    if 'nasscom' in citation_lower:
        if 'indian it' in citation_lower:
            return 'https://nasscom.in/knowledge-center/publications/technology-sector-india-2025'
        return 'https://nasscom.in/knowledge-center/publications'

    # Specific partnerships and news
    if 'nvidia' in citation_lower and 'partnership' in citation_lower:
        return 'https://nvidianews.nvidia.com/news/'
    if 'microsoft' in citation_lower and ('azure' in citation_lower or 'partnership' in citation_lower):
        return 'https://azure.microsoft.com/en-us/blog/'
    if 'aws' in citation_lower or 'amazon' in citation_lower:
        return 'https://aws.amazon.com/blogs/aws/'

    # Government and regulatory
    if 'chips act' in citation_lower:
        return 'https://www.commerce.gov/chips'
    if 'data localization' in citation_lower or 'data protection' in citation_lower:
        if 'india' in citation_lower:
            return 'https://www.meity.gov.in/data-protection-framework'
        else:
            return 'https://gdpr.eu/'

    # Industry specific reports
    if 'dell\'oro' in citation_lower and 'ethernet' in citation_lower:
        return 'https://www.delloro.com/ethernet-switch-quarterly-report/'
    if 'mercury research' in citation_lower:
        return 'https://www.mercuryresearch.com/services/'
    if 'data center' in citation_lower and 'market' in citation_lower:
        return 'https://www.datacenterknowledge.com/research'
    if 'semiconductor' in citation_lower:
        if 'sia' in citation_lower or 'association' in citation_lower:
            return 'https://www.semiconductors.org/global-semiconductor-sales-report/'
        return 'https://www.semiconductors.org/resources/'
    if 'engineering news-record' in citation_lower or 'enr' in citation_lower:
        return 'https://www.enr.com/toplists'
    if 'frost & sullivan' in citation_lower:
        return 'https://www.frost.com/research/'
    if 'green street' in citation_lower and 'reit' in citation_lower:
        return 'https://www.greenstreet.com/insights'

    # Default to company investor relations or reputable source
    if company_ticker:
        base_ticker = company_ticker.split('.')[0].lower()
        if '.NS' in company_ticker:
            # Indian stocks
            return f'https://www.bseindia.com/stock-share-price/{base_ticker}'
        else:
            return f'https://finance.yahoo.com/quote/{company_ticker}'

    return '#'  # Fallback to anchor link

def get_context_aware_title(key, citation, url):
    """Generate a title based on the citation context key."""
    # Map citation keys to human-readable titles
    context_titles = {
        'market_cap': 'Market Capitalization Data',
        'azure_revenue': 'Microsoft Azure Revenue Report',
        'openai_partnership': 'OpenAI Partnership Announcement',
        'financial_metrics': 'Financial Statistics',
        'capex_plans': 'Capital Expenditure Plans',
        'copilot_pricing': 'Microsoft Copilot Pricing',
        'export_violations': 'Export Compliance Report',
        'innovations': 'Technology Innovations',
        'partnerships': 'Strategic Partnerships',
        'export_controls': 'Export Control Analysis',
        'revenue_growth': 'Revenue Growth Report',
        'mellanox_acquisition': 'Mellanox Acquisition Details',
        'h100_adoption': 'H100 GPU Information',
        'gaudi_performance': 'Intel Gaudi Performance',
        'chips_act': 'CHIPS Act Funding',
        'aws_gaudi': 'AWS Gaudi Instances',
        'arm_partnership': 'ARM Partnership Details',
        'sapphire_rapids': 'Sapphire Rapids Documentation',
        'cloud_profitability': 'Cloud Profitability Report',
        'ai_research': 'AI Research Paper',
        'tpu_advantage': 'TPU Technology Overview',
        'anthropic_investment': 'Anthropic Investment',
        'renewable_energy': 'Renewable Energy Report',
        'custom_chips': 'Custom AI Chips Overview',
        'anthropic_partnership': 'Anthropic Partnership',
        'ceo_letter': 'CEO Letter on AI',
        'infrastructure_scale': 'Infrastructure Scale',
        'hugging_face': 'Hugging Face Partnership',
        'nvidia_partnership': 'NVIDIA Partnership',
        'meta_customer': 'Meta Customer Win',
        'financial_growth': 'Financial Growth Report',
        'cohere_partnership': 'Cohere Partnership',
        'microsoft_azure': 'Microsoft Azure Integration',
        'financial_data': 'Financial Data',
        'market_share': 'Market Share Report',
        'technology': 'Technology Specifications',
        'competition': 'Competitive Analysis',
        'overview': 'Company Overview',
        'infrastructure': 'Infrastructure Details',
        'customer_wins': 'Customer Success Stories',
        'technical': 'Technical Capabilities',
        'manufacturing': 'Manufacturing Overview',
        'equinix': 'Equinix Certification',
        'market_position': 'Market Position Analysis',
        'emission_norms': 'Emission Standards',
        'q1_results': 'Q1 Earnings Results',
        'q2_results': 'Q2 Earnings Results',
        'skylus': 'Skylus.ai Platform',
        'defense': 'Defense Contracts',
        'make_in_india': 'Make in India Initiative',
        'dc_plans': 'Data Center Plans',
        'power_expertise': 'Power Engineering Expertise',
        'chennai_facility': 'Chennai Facility',
        'hyperscaler': 'Hyperscaler Opportunities',
        'transformation': 'Business Transformation',
        'asset_conversion': 'Asset Conversion Strategy',
        'land_details': 'Land Holdings Details',
        'customer_pipeline': 'Customer Pipeline',
        'ncr_market': 'NCR Market Analysis',
        'dlf_plans': 'DLF Data Center Plans',
        'policy': 'Government Policy',
        'expansion': 'Expansion Plans',
        'cloudinfinit': 'CloudInfinit Platform',
        'rabale': 'Rabale Data Center',
        'nvidia': 'NVIDIA Certification',
        'localization': 'Data Localization',
        'railwire': 'RailWire Broadband',
        'network': 'Network Infrastructure',
        'topaz': 'Topaz AI Platform',
        'ignio': 'ignio Platform',
        'sustainability': 'Sustainability Report',
        'sovereignty': 'Digital Sovereignty',
        'financials': 'Financial Report',
        'backlog': 'Order Backlog',
        'intel': 'Intel Fab Construction',
        'emcor': 'EMCOR Competition',
        'interconnection': 'Interconnection Index',
        'capacity': 'Facility Capacity',
        'customers': 'Customer Base',
        'alternatives': 'Market Alternatives',
        'regulations': 'Regulatory Environment',
        'pdx_platform': 'PDx Platform Overview',
        'portfolio': 'Property Portfolio',
        'asia_pacific': 'Asia Pacific Market',
        'gigaflex': 'Gigaflex Platform',
        'microsoft': 'Microsoft Partnership',
        'powell': 'Powell Industries',
        'ecostruxure': 'EcoStruxure Platform',
        'legrand': 'Legrand Solutions',
        'efficiency': 'Energy Efficiency',
        'earnings': 'Earnings Report',
        'mps_platform': 'MPS Platform',
        'bloom': 'Bloom Energy',
        'persistent': 'Persistent Systems',
        'geopolitics': 'Geopolitical Analysis',
        'competitors': 'Competitor Analysis',
        'peers': 'Peer Comparison',
        'gpx': 'GPX Data Centers',
        'powergrid': 'PowerGrid Infrastructure',
        'bharatnet': 'BharatNet Implementation',
        'dixon': 'Dixon Technologies',
        'sterling': 'Sterling & Wilson',
        'incentives': 'Government Incentives',
        'bharat_bijlee': 'Bharat Bijlee',
        'greaves': 'Greaves Cotton',
        'hbm': 'HBM Technology',
        'india_fab': 'India Fab Facility',
        'rambus': 'Rambus Technology',
        'china_ban': 'China Market Restrictions',
        'liquid_cooling': 'Liquid Cooling Solutions',
        'meta': 'Meta Partnership',
        'comfort': 'Comfort Systems',
        'oklo': 'Oklo Nuclear Partnership',
        'modular': 'Modular Construction',
        'optical': 'Optical Networking',
        'ai_revenue': 'AI Revenue Growth',
        'marvell': 'Marvell Technology',
        'cpu_innovations': 'CPU Innovations',
        'meta_partnership': 'Meta Partnership'
    }

    # Try to get a specific title from the context
    if key in context_titles:
        return context_titles[key]

    # Fallback to the original get_citation_title logic
    return get_citation_title(citation, url)

def parse_citations(text, citations_dict, company_ticker=None):
    """Parse text and add inline citations with proper links."""
    # Simple pattern to find [1], [2], etc.
    pattern = r'\[(\d+)\]'

    def replace_citation(match):
        num = match.group(1)
        # Find the corresponding citation
        for key, citation in citations_dict.items():
            if citation.startswith(f"[{num}]"):
                # Get appropriate URL
                url = get_citation_url(citation, company_ticker)
                if url and url != '#':
                    # Generate context-aware title based on the citation key
                    title = get_context_aware_title(key, citation, url)
                    return f'<a href="{url}" target="_blank" class="citation" title="{title}">[{num}]</a>'
        return f'<span class="citation">[{num}]</span>'

    return re.sub(pattern, replace_citation, text)

def display_company_comparison(selected_companies):
    """Display comparison table for selected companies."""
    if not selected_companies:
        st.warning("Please select companies to compare")
        return

    comparison_data = []

    for company_key in selected_companies:
        if company_key in COMPANY_PROFILES:
            company = COMPANY_PROFILES[company_key]
            metrics = company.get('detailed_metrics', {})

            row_data = {
                'Company': company['name'],
                'Ticker': company['ticker'],
                'Market Cap': format_market_cap_with_currency(company['market_cap'], company['ticker']),
                'P/E Ratio': metrics.get('trailing_pe', 'N/A'),
                'Forward P/E': metrics.get('forward_pe', 'N/A'),
                'ROE': metrics.get('roe', 'N/A'),
                'Revenue Growth': metrics.get('revenue_growth_yoy', 'N/A'),
                'Recommendation': company['investment_recommendation']
            }
            comparison_data.append(row_data)

    df = pd.DataFrame(comparison_data)

    # Style the dataframe
    def style_recommendation(val):
        if val == 'Buy':
            return 'background-color: #90EE90'
        elif val == 'Hold':
            return 'background-color: #FFFFE0'
        elif val == 'Sell':
            return 'background-color: #FFB6C1'
        return ''

    styled_df = df.style.applymap(style_recommendation, subset=['Recommendation'])
    st.dataframe(styled_df, use_container_width=True)

# Main app
def main():
    # Header
    st.title("💎 AI Infrastructure Investment Hub")
    st.markdown("### Your Gateway to Tech Stocks Powering the AI Revolution")

    # Market Overview
    with st.expander("📊 Market Overview", expanded=True):
        st.markdown('<div class="market-overview-container">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("AI Market Size (2024)", MARKET_INSIGHTS["ai_market_size"]["2024"])
            st.metric("Expected by 2030", MARKET_INSIGHTS["ai_market_size"]["2030"])
        with col2:
            st.metric("Market CAGR", MARKET_INSIGHTS["ai_market_size"]["cagr"])
            st.metric("Data Center Growth", MARKET_INSIGHTS["data_center_growth"]["capacity_increase"])
        with col3:
            st.metric("Power Consumption Growth", MARKET_INSIGHTS["data_center_growth"]["power_consumption"])
            source = MARKET_INSIGHTS["ai_market_size"]["source"]
            # Extract title and URL from the source string
            if "] " in source and source.startswith("["):
                title = source[1:source.index("]")]
                url = source[source.index("] ") + 2:]
                st.info(f"Source: [{title}]({url})")
            else:
                source_url = get_citation_url(source)
                st.info(f"Source: [{source}]({source_url})")
        st.markdown('</div>', unsafe_allow_html=True)

    # Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🏢 Company Analysis",
        "📈 Investment Categories",
        "🎯 Investment Strategy",
        "📊 Stock Comparison",
        "📚 Resources"
    ])

    with tab1:
        # Company selector
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_company = st.selectbox(
                "Select a company to analyze:",
                options=list(COMPANY_PROFILES.keys()),
                format_func=lambda x: f"{COMPANY_PROFILES[x]['name']} ({COMPANY_PROFILES[x]['ticker']})"
            )
        with col2:
            view_mode = st.radio("View", ["Summary", "Detailed"], horizontal=True)

        if selected_company:
            company = COMPANY_PROFILES[selected_company]

            # Company header
            st.markdown(f"## {company['name']} ({company['ticker']})")

            # Key info cards - mobile-responsive layout
            st.markdown('<div class="company-info-responsive">', unsafe_allow_html=True)
            
            # Row 1: Market Cap and Sector
            info_row1_col1, info_row1_col2 = st.columns(2)
            with info_row1_col1:
                formatted_market_cap = format_market_cap_with_currency(company['market_cap'], company.get('ticker', ''))
                st.metric("Market Cap", formatted_market_cap)
            with info_row1_col2:
                st.metric("Sector", company['sector'])
            
            # Small spacing
            st.markdown('<div style="height: 8px;"></div>', unsafe_allow_html=True)
            
            # Row 2: Country and Recommendation
            info_row2_col1, info_row2_col2 = st.columns(2)
            with info_row2_col1:
                st.metric("Country", company['country'])
            with info_row2_col2:
                recommendation_color = "🟢" if company['investment_recommendation'] == "Buy" else "🟡" if company['investment_recommendation'] == "Hold" else "🔴"
                st.metric("Recommendation", f"{recommendation_color} {company['investment_recommendation']}")
            
            st.markdown('</div>', unsafe_allow_html=True)

            # Stock chart section
            st.markdown("### 📈 Stock Performance")

            # Chart controls - responsive button layout
            periods = [
                ("1D", "1d"), ("5D", "5d"), ("1M", "1mo"), ("6M", "6mo"),
                ("YTD", "ytd"), ("1Y", "1y"), ("5Y", "5y"), ("MAX", "max")
            ]

            # Initialize session state
            if f'period_{company["ticker"]}' not in st.session_state:
                st.session_state[f'period_{company["ticker"]}'] = "1y"
            if f'chart_type_{company["ticker"]}' not in st.session_state:
                st.session_state[f'chart_type_{company["ticker"]}'] = "candlestick"

            # Streamlit-native flat period button layout
            st.markdown('<div class="period-buttons-flat">', unsafe_allow_html=True)
            
            # Row 1: 1D, 5D, 1M, 6M (flat structure - no nesting)
            period_row1_col1, period_row1_col2, period_row1_col3, period_row1_col4 = st.columns(4)
            
            with period_row1_col1:
                if st.button("1D", key=f"period_1d_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "1d" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "1d"
                    st.rerun()
            
            with period_row1_col2:
                if st.button("5D", key=f"period_5d_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "5d" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "5d"
                    st.rerun()
            
            with period_row1_col3:
                if st.button("1M", key=f"period_1mo_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "1mo" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "1mo"
                    st.rerun()
            
            with period_row1_col4:
                if st.button("6M", key=f"period_6mo_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "6mo" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "6mo"
                    st.rerun()
            
            # Small spacing between rows
            st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)
            
            # Row 2: YTD, 1Y, 5Y, MAX (flat structure - no nesting)
            period_row2_col1, period_row2_col2, period_row2_col3, period_row2_col4 = st.columns(4)
            
            with period_row2_col1:
                if st.button("YTD", key=f"period_ytd_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "ytd" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "ytd"
                    st.rerun()
            
            with period_row2_col2:
                if st.button("1Y", key=f"period_1y_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "1y" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "1y"
                    st.rerun()
            
            with period_row2_col3:
                if st.button("5Y", key=f"period_5y_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "5y" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "5y"
                    st.rerun()
            
            with period_row2_col4:
                if st.button("MAX", key=f"period_max_{company['ticker']}", 
                           type="primary" if st.session_state[f'period_{company["ticker"]}'] == "max" else "secondary",
                           use_container_width=True):
                    st.session_state[f'period_{company["ticker"]}'] = "max"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

            # Chart type selector - separate row for mobile
            chart_cols = st.columns([2, 1, 1])
            with chart_cols[0]:
                chart_type = st.selectbox(
                    "Chart Type",
                    ["Candlestick", "Area", "Line"],
                    key=f"chart_select_{company['ticker']}",
                    index=["Candlestick", "Area", "Line"].index(st.session_state[f'chart_type_{company["ticker"]}'].title()) if f'chart_type_{company["ticker"]}' in st.session_state else 0
                )
                if chart_type.lower() != st.session_state.get(f'chart_type_{company["ticker"]}', 'candlestick'):
                    st.session_state[f'chart_type_{company["ticker"]}'] = chart_type.lower()
                    st.rerun()

            # Fetch and display stock data
            info, hist, error = fetch_stock_data(company['ticker'], st.session_state[f'period_{company["ticker"]}'])

            if not error:
                display_stock_metrics(info, hist)
                chart = create_advanced_stock_chart(info, hist, company['ticker'], st.session_state[f'chart_type_{company["ticker"]}'])
                if chart:
                    st.plotly_chart(chart, use_container_width=True)
                    # Explicit spacing after chart to prevent overlay
                    st.markdown('<div class="chart-spacer" style="height: 30px;"></div>', unsafe_allow_html=True)
            else:
                st.error(error)

            # Additional spacing before sections
            st.markdown('<div class="section-spacer" style="height: 20px;"></div>', unsafe_allow_html=True)
            st.markdown("---")

            if view_mode == "Summary":
                # Summary view
                st.markdown("### 📋 Company Overview")
                # Display overview text without citations - remove citation numbers
                overview_text = company['overview']
                # Remove citation numbers like [1], [2], etc.
                overview_text = re.sub(r'\[\d+\]', '', overview_text)
                # Wrap in a div to ensure consistent styling
                st.markdown(f'<div style="font-style: normal !important;">{overview_text}</div>', unsafe_allow_html=True)

                # Financial highlights
                with st.expander("💰 Financial Highlights", expanded=True):
                    if 'detailed_metrics' in company:
                        display_financial_metrics(company['detailed_metrics'])
                    elif 'financial_analysis' in company:
                        # If no detailed_metrics, parse from financial_analysis
                        financial_text = company['financial_analysis']
                        lines = financial_text.split('\n')
                        cols = st.columns(3)
                        col_idx = 0
                        for line in lines[:6]:  # Show first 6 metrics
                            if ':' in line and line.strip() and not line.startswith('Market Cap:'):
                                parts = line.split(':', 1)
                                if len(parts) == 2:
                                    metric = parts[0].strip()
                                    value = parts[1].strip().replace('~', '').strip()
                                    with cols[col_idx % 3]:
                                        st.metric(metric, value)
                                    col_idx += 1

                # Key strengths and risks
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("### ✅ Key Strengths")
                    for strength in company['key_strengths'][:3]:
                        st.success(f"• {strength}")

                with col2:
                    st.markdown("### ⚠️ Risk Factors")
                    for risk in company['risk_factors'][:3]:
                        st.warning(f"• {risk}")

                # Investment rationale
                st.markdown("### 💡 Investment Rationale")
                st.info(company['recommendation_rationale'])

            else:  # Detailed view
                # Tabbed detailed analysis
                detail_tabs = st.tabs([
                    "🔬 Innovation",
                    "🏗️ Infrastructure",
                    "🤝 Partnerships",
                    "⚔️ Competition",
                    "📊 Financials",
                    "💎 Hidden Gems",
                    "🌍 Geopolitics",
                    "📑 Citations"
                ])

                with detail_tabs[0]:
                    st.markdown("### Innovations & Technological Moats")
                    st.write(company['innovations_moats'])
                    if 'products_specifications' in company:
                        st.markdown("#### Product Specifications")
                        for category, products in company['products_specifications'].items():
                            category_name = category.replace('_', ' ').title()
                            if isinstance(products, list):
                                # Display list items in a compact format with bullet points on same line
                                products_str = " • ".join(products)
                                st.markdown(f"**{category_name}:** {products_str}")
                            else:
                                st.markdown(f"**{category_name}:** {products}")

                with detail_tabs[1]:
                    st.markdown("### Infrastructure Capabilities")
                    st.write(company['infrastructure_capabilities'])

                with detail_tabs[2]:
                    st.markdown("### Partnerships & Customer Base")
                    st.write(company['partnerships_customers'])
                    if 'recent_developments' in company:
                        st.markdown("#### Recent Developments")
                        for key, value in company['recent_developments'].items():
                            # Try to extract and link any URLs in the development text
                            development_text = value
                            # Check if there's a URL pattern in the text
                            url_match = re.search(r'https?://[^\s]+', development_text)
                            if url_match:
                                url = url_match.group(0)
                                # Replace the URL with a markdown link
                                development_text = development_text.replace(url, f"[Read more]({url})")
                            else:
                                # Check if we have a citation for this development
                                citation_key = None
                                citations = company.get('citations', {})
                                
                                # Look for relevant citation keys that match this development
                                for cite_key in citations.keys():
                                    if (key.lower() in cite_key.lower() or 
                                        cite_key.lower() in key.lower() or
                                        any(word in cite_key.lower() for word in key.lower().split('_'))):
                                        citation_key = cite_key
                                        break
                                
                                # If we found a relevant citation, use its URL
                                if citation_key:
                                    citation_url = get_citation_url(citations[citation_key], company.get('ticker'))
                                    if citation_url and citation_url != '#':
                                        development_text = f"{value} ([Source]({citation_url}))"
                                    else:
                                        development_text = value  # No link if no valid URL
                                else:
                                    # No citation found, just show the text without any link
                                    development_text = value

                            st.info(f"**{key.replace('_', ' ').upper()}:** {development_text}")

                with detail_tabs[3]:
                    st.markdown("### Competitive Landscape")
                    st.write(company['competitive_landscape'])

                with detail_tabs[4]:
                    st.markdown("### Financial Analysis")
                    # Display the financial analysis text without the redundant metrics
                    financial_text = company['financial_analysis']
                    # Remove the "Market Cap:" line if it exists since it's already shown above
                    lines = financial_text.split('\n')
                    filtered_lines = [line for line in lines if not line.strip().startswith('Market Cap:')]

                    # Format the financial analysis text into a clean table-like display
                    st.markdown("#### Key Financial Metrics")

                    # Parse the financial data into a structured format
                    metrics_data = []
                    for line in filtered_lines:
                        if ':' in line and line.strip():
                            parts = line.split(':', 1)
                            if len(parts) == 2:
                                metric_name = parts[0].strip()
                                metric_value = parts[1].strip()
                                # Clean up common formatting issues
                                metric_value = metric_value.replace('~', '').strip()
                                metrics_data.append((metric_name, metric_value))

                    # Display in a clean 2-column layout
                    if metrics_data:
                        cols = st.columns(2)
                        for i, (metric, value) in enumerate(metrics_data):
                            with cols[i % 2]:
                                st.markdown(f"**{metric}**")
                                st.markdown(f"{value}")
                                st.markdown("")  # Add spacing

                    # Show financial highlights if they exist and are different from detailed_metrics
                    if 'financial_highlights' in company:
                        st.markdown("#### Key Financial Highlights")
                        for key, value in company['financial_highlights'].items():
                            # Only show if not already in detailed_metrics
                            if 'detailed_metrics' not in company or key not in company['detailed_metrics']:
                                st.metric(key.replace('_', ' ').title(), value)

                with detail_tabs[5]:
                    st.markdown("### Hidden Gems & Underappreciated Assets")
                    st.write(company['hidden_gems'])

                with detail_tabs[6]:
                    st.markdown("### Trade & Geopolitical Impact")
                    st.write(company['geopolitical_impact'])

                with detail_tabs[7]:
                    if 'citations' in company:
                        st.markdown("### Sources & Citations")
                        for key, citation in company['citations'].items():
                            url = get_citation_url(citation, company.get('ticker'))
                            display_key = key.replace('_', ' ').title()
                            if url and url != '#':
                                # Extract citation number
                                citation_parts = citation.split(']', 1)
                                if len(citation_parts) == 2:
                                    citation_num = citation_parts[0] + ']'
                                    # Get context-aware title for the link
                                    link_title = get_context_aware_title(key, citation, url)
                                    # Make the display key itself clickable
                                    st.markdown(f"- **[{display_key}]({url}):** {citation_num}", unsafe_allow_html=True)
                                else:
                                    st.markdown(f"- **[{display_key}]({url}):** {citation}")
                            else:
                                st.markdown(f"- **{display_key}:** {citation}")

    with tab2:
        st.markdown("## 📈 Investment Categories")
        st.markdown("*Strategic groupings of companies positioned to benefit from AI infrastructure growth*")

        # Quick overview cards for all categories
        st.markdown("### Category Overview")
        overview_cols = st.columns(len(INVESTMENT_CATEGORIES))

        category_icons = {
            "blue_chip": "👑",
            "high_growth": "🚀",
            "hidden_gems": "💎",
            "turnaround": "🔄",
            "india_focus": "🇮🇳"
        }

        for idx, (key, cat) in enumerate(INVESTMENT_CATEGORIES.items()):
            with overview_cols[idx]:
                icon = category_icons.get(key, "📊")
                st.markdown(f"""
                <div class="category-overview-card" style="text-align: center; padding: 10px; border-radius: 10px;">
                    <div style="font-size: 24px;">{icon}</div>
                    <div style="font-weight: 600; font-size: 14px; margin-top: 5px;">{cat['name']}</div>
                    <div style="font-size: 20px; color: #1f77b4; font-weight: bold; margin-top: 5px;">{len(cat['companies'])}</div>
                    <div style="font-size: 12px;">companies</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Category selector buttons
        category_keys = list(INVESTMENT_CATEGORIES.keys())
        category_names = [INVESTMENT_CATEGORIES[k]['name'] for k in category_keys]

        # Create a horizontal selector using tabs
        category_tabs = st.tabs(category_names)

        # Display content for each tab
        for idx, (tab, category_key) in enumerate(zip(category_tabs, category_keys)):
            with tab:
                category = INVESTMENT_CATEGORIES[category_key]

                # Display category overview in a nice card
                col1, col2 = st.columns([2, 1])

                with col1:
                    st.markdown(f"### {category['name']}")
                    st.markdown(f"*{category['description']}*")

                    # Characteristics in a compact format
                    st.markdown("**Key Characteristics:**")
                    char_cols = st.columns(2)
                    for i, char in enumerate(category['characteristics']):
                        with char_cols[i % 2]:
                            st.markdown(f"✓ {char}")

                with col2:
                    # Category metrics card
                    st.markdown("""
                    <div class="metric-card" style="text-align: center;">
                        <div class="metric-value" style="font-size: 36px;">""" + str(len(category['companies'])) + """</div>
                        <div class="metric-label">Companies</div>
                    </div>
                    """, unsafe_allow_html=True)

                # Companies grid with enhanced cards
                st.markdown("### 📊 Companies in this Category")

                # Create responsive grid - CSS will handle mobile layout
                companies_per_row = 4  # CSS will make this 2 on mobile
                company_rows = []
                for i in range(0, len(category['companies']), companies_per_row):
                    company_rows.append(category['companies'][i:i + companies_per_row])

                for row in company_rows:
                    cols = st.columns(companies_per_row)
                    for i, company_key in enumerate(row):
                        if company_key in COMPANY_PROFILES:
                            company = COMPANY_PROFILES[company_key]
                            with cols[i]:
                                # Enhanced company card
                                recommendation_emoji = "🟢" if company['investment_recommendation'] == "Buy" else "🟡" if company['investment_recommendation'] == "Hold" else "🔴"
                                metrics = company.get('detailed_metrics', {})
                                pe_ratio = metrics.get('trailing_pe', 'N/A')
                                roe = metrics.get('roe', 'N/A')

                                # Truncate long company names
                                company_name = company['name']
                                if len(company_name) > 20:
                                    company_name = company_name[:18] + "..."

                                st.markdown(f"""
                                <div class="company-card">
                                    <div>
                                        <h4 class="company-name" style="margin: 0 0 4px 0; font-size: 14px; line-height: 1.2;">
                                            {company_name} <span class="ticker-span" style="font-weight: normal;">({company['ticker']})</span>
                                        </h4>
                                        <p class="country-text" style="margin: 2px 0; font-size: 11px;">
                                            {company['country']}
                                        </p>
                                        <p class="market-cap" style="margin: 6px 0; font-size: 18px; font-weight: 600;">
                                            {format_market_cap_with_currency(company['market_cap'], company['ticker'])}
                                        </p>
                                    </div>
                                    <div>
                                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                                            <div style="display: flex; gap: 20px;">
                                                <div>
                                                    <span class="metric-label" style="font-size: 11px;">P/E:</span>
                                                    <span class="metric-value" style="font-size: 15px; font-weight: 600;">{pe_ratio}</span>
                                                </div>
                                                <div>
                                                    <span class="metric-label" style="font-size: 11px;">ROE:</span>
                                                    <span class="metric-value" style="font-size: 15px; font-weight: 600;">{roe}</span>
                                                </div>
                                            </div>
                                        </div>
                                        <div class="recommendation-box" style="text-align: center; font-size: 13px; padding-top: 4px;">
                                            <span style="font-size: 16px;">{recommendation_emoji}</span> <strong>{company['investment_recommendation']}</strong>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

                # Quick comparison view
                with st.expander("📊 Quick Comparison View", expanded=True):
                    # Create comparison dataframe
                    comparison_data = []
                    for company_key in category['companies']:
                        if company_key in COMPANY_PROFILES:
                            comp = COMPANY_PROFILES[company_key]
                            metrics = comp.get('detailed_metrics', {})
                            comparison_data.append({
                                'Company': comp['name'],
                                'Ticker': comp['ticker'],
                                'Market Cap': format_market_cap_with_currency(comp['market_cap'], comp['ticker']),
                                'P/E': metrics.get('trailing_pe', 'N/A'),
                                'ROE': metrics.get('roe', 'N/A'),
                                'Recommendation': comp['investment_recommendation']
                            })

                    if comparison_data:
                        df = pd.DataFrame(comparison_data)
                        st.dataframe(df, use_container_width=True, height=300)

    with tab3:
        st.markdown("## 🎯 Investment Strategy")

        # Strategy selector
        strategy = st.selectbox(
            "Select Investment Strategy:",
            ["Balanced AI Portfolio", "High Growth Focus", "Value & Turnaround", "Conservative Blue Chip"]
        )

        if strategy == "Balanced AI Portfolio":
            st.info("""
            **Balanced AI Portfolio Strategy**
            - 40% Blue Chip AI Leaders (NVDA, MSFT, GOOGL)
            - 30% High Growth Players (AMD, SMCI, ARISTA)
            - 20% Hidden Gems (VERTIV, FIX, EQIX)
            - 10% Turnaround Stories (INTC, ORCL)

            This strategy provides exposure to the full AI value chain while managing risk through diversification.
            """)
        elif strategy == "High Growth Focus":
            st.info("""
            **High Growth Focus Strategy**
            - 50% High Growth Players (AMD, SMCI, ARISTA, INFY)
            - 30% Emerging AI Companies (VERTIV, MICRON)
            - 20% Blue Chip for stability (NVDA, MSFT)

            Higher risk/reward profile targeting companies with >30% revenue growth.
            """)
        elif strategy == "Value & Turnaround":
            st.info("""
            **Value & Turnaround Strategy**
            - 40% Turnaround Stories (INTC, ORCL, DELL)
            - 30% Hidden Gems (EQIX, FIX, VERTIV)
            - 30% Stable cashflow (MSFT, GOOGL)

            Focus on undervalued companies with AI transformation potential.
            """)
        else:  # Conservative Blue Chip
            st.info("""
            **Conservative Blue Chip Strategy**
            - 40% MSFT (Cloud & AI leader)
            - 30% GOOGL (AI research pioneer)
            - 20% AMZN (AWS dominance)
            - 10% NVDA (AI chip leader)

            Lower volatility approach focusing on established market leaders.
            """)

        # Risk assessment
        st.markdown("### Risk Assessment")
        risk_factors = [
            ("Market Risk", "High", "AI spending could slow in economic downturn"),
            ("Competition Risk", "Medium", "New entrants and technology shifts"),
            ("Regulatory Risk", "Medium", "Export controls and AI regulations"),
            ("Execution Risk", "High", "Companies must deliver on AI promises"),
            ("Valuation Risk", "High", "Many stocks trading at premium multiples")
        ]

        for risk, level, description in risk_factors:
            level_class = f"risk-{level.lower()}"
            st.markdown(f"**{risk}:** <span class='{level_class}'>{level}</span> - {description}", unsafe_allow_html=True)

    with tab4:
        st.markdown("## 📊 Stock Comparison Dashboard")
        st.markdown("Compare multiple stocks side-by-side to analyze relative performance.")

        # Get all tickers
        all_tickers = [v['ticker'] for v in COMPANY_PROFILES.values() if v.get('ticker')]

        # Multi-select for comparison
        selected_tickers = st.multiselect(
            "Select stocks to compare (max 4):",
            all_tickers,
            default=["NVDA", "AMD"] if "NVDA" in all_tickers and "AMD" in all_tickers else all_tickers[:2],
            max_selections=4
        )

        if selected_tickers:
            # Responsive period selection for comparison
            periods = [
                ("1D", "1d"), ("5D", "5d"), ("1M", "1mo"), ("6M", "6mo"),
                ("YTD", "ytd"), ("1Y", "1y"), ("5Y", "5y"), ("MAX", "max")
            ]

            if 'comparison_period' not in st.session_state:
                st.session_state['comparison_period'] = "1y"

            # Streamlit-native flat comparison period button layout
            st.markdown('<div class="comp-period-buttons-flat">', unsafe_allow_html=True)
            
            # Row 1: 1D, 5D, 1M, 6M (flat structure - no nesting)
            comp_row1_col1, comp_row1_col2, comp_row1_col3, comp_row1_col4 = st.columns(4)
            
            with comp_row1_col1:
                if st.button("1D", key="comp_period_1d", 
                           type="primary" if st.session_state['comparison_period'] == "1d" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "1d"
                    st.rerun()
            
            with comp_row1_col2:
                if st.button("5D", key="comp_period_5d", 
                           type="primary" if st.session_state['comparison_period'] == "5d" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "5d"
                    st.rerun()
            
            with comp_row1_col3:
                if st.button("1M", key="comp_period_1mo", 
                           type="primary" if st.session_state['comparison_period'] == "1mo" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "1mo"
                    st.rerun()
            
            with comp_row1_col4:
                if st.button("6M", key="comp_period_6mo", 
                           type="primary" if st.session_state['comparison_period'] == "6mo" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "6mo"
                    st.rerun()
            
            # Small spacing between rows
            st.markdown('<div style="height: 6px;"></div>', unsafe_allow_html=True)
            
            # Row 2: YTD, 1Y, 5Y, MAX (flat structure - no nesting)
            comp_row2_col1, comp_row2_col2, comp_row2_col3, comp_row2_col4 = st.columns(4)
            
            with comp_row2_col1:
                if st.button("YTD", key="comp_period_ytd", 
                           type="primary" if st.session_state['comparison_period'] == "ytd" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "ytd"
                    st.rerun()
            
            with comp_row2_col2:
                if st.button("1Y", key="comp_period_1y", 
                           type="primary" if st.session_state['comparison_period'] == "1y" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "1y"
                    st.rerun()
            
            with comp_row2_col3:
                if st.button("5Y", key="comp_period_5y", 
                           type="primary" if st.session_state['comparison_period'] == "5y" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "5y"
                    st.rerun()
            
            with comp_row2_col4:
                if st.button("MAX", key="comp_period_max", 
                           type="primary" if st.session_state['comparison_period'] == "max" else "secondary", 
                           use_container_width=True):
                    st.session_state['comparison_period'] = "max"
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)

            # Chart type selector
            comp_chart_cols = st.columns([2, 1, 1])
            with comp_chart_cols[0]:
                chart_type = st.selectbox(
                    "Chart Type",
                    ["Line", "Area"],
                    key="comp_chart_type"
                )

            # Display individual charts
            if len(selected_tickers) == 1:
                # Single stock - full analysis
                ticker = selected_tickers[0]
                info, hist, error = fetch_stock_data(ticker, st.session_state['comparison_period'])

                if not error:
                    display_stock_metrics(info, hist)
                    chart = create_advanced_stock_chart(info, hist, ticker, chart_type.lower())
                    if chart:
                        st.plotly_chart(chart, use_container_width=True)
                else:
                    st.error(error)
            else:
                # Multiple stocks - comparison view
                # Normalized performance chart
                st.markdown("### 📈 Normalized Performance Comparison")
                
                if not PLOTLY_AVAILABLE:
                    st.error("Plotly is required for comparison charts but not available.")
                    return

                fig = go.Figure()
                all_data_available = True

                for ticker in selected_tickers:
                    info, hist, error = fetch_stock_data(ticker, st.session_state['comparison_period'])
                    if not error and hist is not None and not hist.empty:
                        # Normalize to 100 at start
                        normalized = (hist['Close'] / hist['Close'].iloc[0]) * 100

                        fig.add_trace(go.Scatter(
                            x=hist.index,
                            y=normalized,
                            mode='lines',
                            name=ticker,
                            line=dict(width=2)
                        ))
                    else:
                        all_data_available = False

                if all_data_available:
                    # Responsive chart height for comparison with consistent mobile logic
                    is_mobile_comp = st.session_state.get('mobile_mode', True)
                    
                    if is_mobile_comp:
                        comp_chart_height = 300
                        comp_font_size = 10
                        comp_margin = 25
                    else:
                        comp_chart_height = 400
                        comp_font_size = 12
                        comp_margin = 40
                    
                    fig.update_layout(
                        height=comp_chart_height,
                        title="Normalized Performance (Base = 100)",
                        yaxis_title="Relative Performance (%)",
                        xaxis_title="Date",
                        hovermode='x unified',
                        template="plotly_white",
                        margin=dict(
                            l=comp_margin,
                            r=comp_margin,
                            t=45 if is_mobile_comp else 50,
                            b=comp_margin
                        ),
                        font=dict(size=comp_font_size),
                        autosize=True
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    # Explicit spacing after comparison chart
                    st.markdown('<div class="chart-spacer" style="height: 30px;"></div>', unsafe_allow_html=True)

                # Side-by-side comparison table
                st.markdown("### 📊 Side-by-Side Comparison")

                comparison_data = []
                for ticker in selected_tickers:
                    info, hist, error = fetch_stock_data(ticker, '1y')
                    if not error and hist is not None and not hist.empty:
                        latest_price = hist['Close'].iloc[-1]
                        prev_close = hist['Close'].iloc[-2] if len(hist) >= 2 else latest_price
                        day_change_pct = ((latest_price - prev_close) / prev_close) * 100

                        # Year return
                        year_return = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100

                        currency_symbol = get_currency_symbol(ticker)
                        comparison_data.append({
                            'Ticker': ticker,
                            'Price': f"{currency_symbol}{latest_price:.2f}",
                            'Day Change %': f"{day_change_pct:+.2f}%",
                            'Year Return %': f"{year_return:+.2f}%",
                            'Market Cap': f"{currency_symbol}{format_large_number(info.get('marketCap', 0))}",
                            'P/E': f"{info.get('trailingPE', 'N/A'):.2f}" if isinstance(info.get('trailingPE'), (int, float)) else "N/A",
                            'Volume': format_large_number(info.get('volume', 0))
                        })

                if comparison_data:
                    df = pd.DataFrame(comparison_data)
                    st.dataframe(df, use_container_width=True)

                # Individual mini charts
                st.markdown("### 📊 Individual Charts")
                cols = st.columns(2)
                for i, ticker in enumerate(selected_tickers[:4]):
                    with cols[i % 2]:
                        info, hist, error = fetch_stock_data(ticker, st.session_state['comparison_period'])
                        if not error:
                            st.markdown(f"#### {ticker}")
                            mini_chart = create_advanced_stock_chart(info, hist, ticker, 'line')
                            if mini_chart:
                                # Responsive mini chart height with consistent mobile logic
                                is_mobile_mini = st.session_state.get('mobile_mode', True)
                                
                                if is_mobile_mini:
                                    mini_height = 250
                                    mini_margin = 15
                                else:
                                    mini_height = 300
                                    mini_margin = 25
                                
                                mini_chart.update_layout(
                                    height=mini_height, 
                                    showlegend=False,
                                    margin=dict(l=mini_margin, r=mini_margin, t=mini_margin, b=mini_margin),
                                    autosize=True
                                )
                                st.plotly_chart(mini_chart, use_container_width=True)
        else:
            st.info("👆 Please select at least one stock to begin comparison.")

    with tab5:
        st.markdown("## 📚 Resources & Information")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### 🔗 Useful Resources")
            st.markdown("""
            - [Yahoo Finance](https://finance.yahoo.com) - Stock data and news
            - [SEC EDGAR](https://www.sec.gov/edgar) - Company filings
            - [MarketWatch](https://www.marketwatch.com) - Market analysis
            - [Seeking Alpha](https://seekingalpha.com) - Investment research
            - [TradingView](https://www.tradingview.com) - Technical analysis
            """)

            st.markdown("### 📖 Investment Glossary")
            with st.expander("Common Terms"):
                st.markdown("""
                **P/E Ratio**: Price-to-Earnings ratio, valuation metric
                **Market Cap**: Total value of company's shares
                **ROE**: Return on Equity, profitability measure
                **PEG Ratio**: P/E ratio divided by growth rate
                **Free Cash Flow**: Cash generated after expenses
                """)

        with col2:
            st.markdown("### ⚠️ Risk Disclosure")
            st.warning("""
            **Important:** This platform is for educational and research purposes only.
            The information provided does not constitute financial advice. All investment
            decisions should be made after thorough personal research and consultation
            with qualified financial advisors. Past performance is not indicative of
            future results.
            """)

            st.markdown("### ℹ️ About This Platform")
            st.info("""
            This research hub provides comprehensive analysis of companies positioned
            to benefit from the AI infrastructure boom. Data is sourced from public
            financial reports and market research.

            **Last Updated:** August 2025
            """)

# Sidebar
with st.sidebar:
    st.markdown("### 📊 Quick Stats")
    total_companies = len(COMPANY_PROFILES)
    us_companies = sum(1 for c in COMPANY_PROFILES.values() if c['country'] in ['US', 'France/Global'])
    india_companies = sum(1 for c in COMPANY_PROFILES.values() if c['country'] == 'India')

    st.metric("Total Companies", total_companies)
    st.metric("US Companies", us_companies)
    st.metric("India Companies", india_companies)

    st.markdown("---")

    st.markdown("### 🎯 Investment Categories")
    for cat_key, cat_data in INVESTMENT_CATEGORIES.items():
        icon = {"blue_chip": "👑", "high_growth": "🚀", "hidden_gems": "💎", "turnaround": "🔄", "india_focus": "🇮🇳"}.get(cat_key, "📊")
        st.markdown(f"{icon} **{cat_data['name']}**")
        st.caption(f"{len(cat_data['companies'])} companies")

if __name__ == "__main__":
    main()
