# shopify-langchain

A Python agent powered by LangChain and OpenAI for interacting with Shopify stores using custom tools.

## Features

- Connects to Shopify via API using environment variables
- Retrieves product information and details
- Extensible with custom tools for store management
- Uses LangChain for agent workflow and OpenAI for LLM

## Setup

1. **Clone the repository**
2. **Create a virtual environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```
4. **Set environment variables**  
   Create a `.env` file with:
   ```
   OPENAI_API_BASE=your_openai_api_base_url
   OPENAI_API_KEY=your_openai_api_key
   SHOPIFY_SHOP_URL=yourshopname(without .shopify.com)
   SHOPIFY_ACCESS_TOKEN=your_shopify_access_token
   ```

## Usage

Run the agent:

```powershell
python shopify_agent.py
```

## Files

- `shopify_agent.py`: Main agent logic and workflow
- `shopify_tools.py`: Shopify API tools (get products, get product by ID, etc.)

## Requirements

- Python 3.12+
- LangChain
- langchain_openai
- python-dotenv
- shopify
