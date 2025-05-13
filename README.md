# AI Travel Planner

## Overview
AI Travel Planner is a **real-time route planning tool** that uses **Google Maps APIs** to:
- Generate **optimized routes** with waypoints.
- Provide **weather information** for stops along the route.
- Display **recommendations** for attractions, food, and lodging.
- Support a **React front-end**.

## Project Structure
AI AGENTS/
-- backend/ # FastAPI back-end
            -- venv/ # Python virtual environment
            main.py # API entry point
            agent.py # Travel agent logic
            requirements.txt
-- frontend/ # React front-end
            package.json
            -- src / # Front-end files
-- .gitignore # Ignore unnecessary files
-- README.md # Documentation

## Installation & Setup
### ** Prerequisites **
Ensure you have the following installed:
- **Python 3.10+**
- **Node.js & npm** (front-end)
- **VS Code** (recommended)
- **Google Cloud API Key** (For Maps, Directions, and Places data)

### ** Clone the Repository **
```bash
git clone https://github.com/smurrayintx/????.git
cd ai-travel-planner
```

### Back-End (FastAPI)
cd backend
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

### Environment Variable(s)
- Create a .env file inside backend/ and add:
GOOGLE_MAPS_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
AZURE_OPENAI_ENDPOINT=your_azure_endpoint_here
WEATHER_API_KEY=your_weather_api_key_here

## Running the Project
### Start the FastAPI Back-End
cd backend
uvicorn main:app --reload
Then, open http://127.0.0.1:8000/docs to access the API.

### Start the Front-End
cd frontend
npm install # For React dependencies
npm start   # React

## API Endpoints
/api/plan_trip          Get optimized route & waypoints     POST
/api/weather            Get weather information             GET
/api/recommendations    Get recommendations for stops       GET


## License
This project is licensed under the MIT license.