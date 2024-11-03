# Warren Buffett AI Financial Advisor 💰

An AI-powered financial advisor that analyzes stocks and provides insights using Warren Buffett's investment principles. The application uses Streamlit for the frontend and leverages various AI and financial APIs to provide analysis.

## Features

- Real-time financial analysis
- Stock performance metrics
- Warren Buffett-style investment insights
- Interactive chat interface
- Financial ratios calculation (ROE, ROIC, etc.)
- Intrinsic value calculation

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Required API Keys

You'll need to obtain the following API keys:

1. **Google API Key** - For Gemini Pro AI model
   - Get it from: [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **Financial Datasets API Key** - For financial data
   - Get it from: [Financial Modeling Prep](https://financialmodelingprep.com/developer/docs/)

3. **Tavily API Key** - For web search capabilities
   - Get it from: [Tavily](https://tavily.com/)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/haqqibrahim/warren-buffett-AI.git
cd warren-buffett-AI
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Set up your API keys:

Create a `.streamlit/secrets.toml` file and add your API keys as environment variables:
```toml
GOOGLE_API_KEY = "your_google_api_key"
FMP_API_KEY = "your_fmp_api_key"
TAVILY_API_KEY = "your_tavily_api_key"
```

## Usage

1. Start the Streamlit application:
```bash
streamlit run app.py
```

2. Open your web browser and navigate to `http://localhost:8501`

3. Enter a stock symbol or company name to get Warren Buffett-style analysis

## How It Works

The application combines multiple technologies to provide comprehensive financial analysis:

1. **Financial Data**: Fetches real-time market data and financial statements using Financial Modeling Prep API
2. **AI Analysis**: Uses Google's Gemini Pro to analyze financial data through Warren Buffett's investment lens
3. **Web Search**: Leverages Tavily API to gather recent news and market sentiment
4. **Financial Calculations**: Performs key ratio analysis and intrinsic value calculations

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/improvement`)
3. Make your changes
4. Commit your changes (`git commit -am 'Add new feature'`)
5. Push to the branch (`git push origin feature/improvement`)
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Inspired by Warren Buffett's investment principles
- Built with Streamlit and Google's Gemini Pro
- Financial data provided by Financial Modeling Prep
- Web search capabilities powered by Tavily

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/haqqibrahim/warren-buffett-AI/issues).