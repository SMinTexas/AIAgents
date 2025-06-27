# Environment Setup

This application requires several API keys to function properly. You need to create a `.env` file in the `backend/` directory with the following variables:

## Required Environment Variables

```bash
# Google Maps API Key - Required for geocoding, directions, and places
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here

# OpenAI API Key - Required for AI-powered recommendations
OPENAI_API_KEY=your_openai_api_key_here

# Azure OpenAI Endpoint - Required for AI-powered recommendations
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here

# Weather API Key - Required for weather information
WEATHER_API_KEY=your_weather_api_key_here
```

## How to Get API Keys

### Google Maps API Key
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Directions API
   - Places API
   - Geocoding API
4. Create credentials (API Key)
5. Restrict the API key to the enabled APIs for security

### Weather API Key
1. Go to [WeatherAPI.com](https://www.weatherapi.com/)
2. Sign up for a free account
3. Get your API key from the dashboard

### OpenAI API Key
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key

### Azure OpenAI Endpoint
1. Set up Azure OpenAI service in your Azure portal
2. Get the endpoint URL from your Azure OpenAI resource

## Setting Up the .env File

1. Create a file named `.env` in the `backend/` directory
2. Copy the template above and replace the placeholder values with your actual API keys
3. Save the file

## Testing the Setup

After setting up your .env file, you can test if the environment variables are loaded correctly by running:

```bash
cd backend
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print('All keys loaded:', all([os.getenv('GOOGLE_MAPS_API_KEY'), os.getenv('WEATHER_API_KEY'), os.getenv('OPENAI_API_KEY'), os.getenv('AZURE_OPENAI_ENDPOINT')]))"
```

This should return `True` if all keys are properly loaded. 