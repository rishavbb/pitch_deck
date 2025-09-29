# Pitch Deck Analyzer

A Python-based tool that analyzes startup pitch decks (PDF/PowerPoint) and generates comprehensive investment analysis reports using AI. Designed for investment managers focusing on early-stage startups.

## Features

- **Multi-format Support**: Analyzes PDF and PowerPoint (PPT/PPTX) pitch decks
- **AI-Powered Analysis**: Uses OpenRouter API with Claude 3.5 Sonnet for intelligent analysis
- **Image Analysis**: Processes visual content including charts, graphs, and diagrams from pitch decks
- **Image-Only PDF Support**: Handles scanned PDFs with no extractable text content
- **URL Research**: Extracts links and performs LLM-based research on companies and social media profiles
- **Investment Focus**: Tailored analysis for investment managers and VCs
- **Structured Reports**: Generates well-formatted markdown reports
- **No Web Scraping**: Only processes local files, no external data collection from your machine

## Installation

### Using Conda (Recommended)

1. Create and activate the conda environment:
```bash
conda env create -f environment.yml
conda activate pitch-deck-analyzer
```

### Using pip

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Setup

1. Get your OpenRouter API key from [openrouter.ai](https://openrouter.ai)

2. Set up your environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

Or set the environment variable directly:
```bash
export OPENROUTER_API_KEY="your_api_key_here"
```

## Usage

### Basic Usage

```bash
python main.py path/to/pitch_deck.pdf
```

### Advanced Usage

```bash
# Specify custom output file
python main.py pitch_deck.pdf --output my_analysis.md

# Use API key from command line
python main.py pitch_deck.pptx --api-key your_key_here
```

### Example

```bash
# Analyze the included sample pitch deck
python main.py "PptxGenJS Presentation - uber-pitch-deck.pdf"
```

## Analysis Output

The tool generates a comprehensive markdown report including:

1. **Company Overview** - Mission, vision, industry, development stage
2. **Business Model Analysis** - Revenue model, unit economics, scalability
3. **Market Analysis** - TAM/SAM/SOM, competitive landscape, market timing
4. **Product/Service Evaluation** - Value proposition, technology, competitive advantages
5. **Team Assessment** - Founder backgrounds, team composition, execution capability
6. **Financial Analysis** - Current status, projections, funding requirements
7. **Traction and Milestones** - Customer metrics, growth, partnerships
8. **Risk Assessment** - Market, execution, financial, and regulatory risks
9. **Investment Recommendation** - Overall attractiveness, strengths, concerns
10. **Additional Research Suggestions** - Due diligence areas, comparable companies
11. **Information Extracted from Online Research** - LLM-based research on URLs and companies found in the pitch deck

## Project Structure

```
pitch-deck-analyzer/
├── main.py                 # CLI entry point
├── src/
│   ├── analyzer.py         # Main orchestration logic
│   ├── report_generator.py # Markdown report generation
│   ├── extractors/         # Content extraction modules
│   │   ├── pdf_extractor.py
│   │   └── ppt_extractor.py
│   ├── utils/              # Utility modules
│   │   ├── image_processor.py  # Image processing and filtering
│   │   └── url_extractor.py    # URL extraction and categorization
│   └── ai/                 # AI integration
│       └── openrouter_client.py
├── environment.yml         # Conda environment
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
└── README.md              # This file
```

## Supported File Formats

- **PDF**: `.pdf` files
- **PowerPoint**: `.ppt` and `.pptx` files

## Requirements

- Python 3.11+
- OpenRouter API key (only paid service required)
- Internet connection for API calls

## Error Handling

The tool includes comprehensive error handling for:
- Missing or invalid files
- Unsupported file formats
- Content extraction failures
- API connection issues
- Report generation errors

## Privacy & Security

- **No Web Scraping**: Only processes local files
- **API Security**: Uses environment variables for API keys
- **Data Privacy**: Content is only sent to OpenRouter API, not stored elsewhere

## Troubleshooting

### Common Issues

1. **"OpenRouter API key is required"**
   - Set your API key in `.env` file or use `--api-key` argument

2. **"File not found"**
   - Check the file path and ensure the file exists

3. **"No text content found"**
   - For image-only PDFs, the tool will automatically analyze visual content
   - The system now supports scanned PDFs and image-based pitch decks

4. **API connection errors**
   - Check your internet connection
   - Verify your OpenRouter API key is valid
   - Ensure you have sufficient API credits

## Contributing

This tool is designed for local analysis only and does not include web scraping capabilities as requested. All analysis is performed by sending extracted text content to the OpenRouter API.

## License

This project is for educational and professional use in investment analysis.
