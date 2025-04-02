# AI Travel Planner

## Overview
AI Travel Planner is a **real-time route planning tool** that uses **Google Maps APIs** to:
- Generate **optimized routes** with waypoints.
- Provide **real-time traffic updates** every 5 minutes.
- Estimate **time-of-day traffic conditions** based on planned departure times.
- Display **color-coded traffic maps** for congestion visualization.
- Support a **React/Angular front-end** (coming soon).

## Project Structure
AI AGENTS/
-- backend/ # FastAPI back-end
            -- venv/ # Python virtual environment
            main.py # API entry point
            agent.py # Travel agent logic
            requirements.txt
-- frontend/ # React or Angular front-end (to be built)
            package.json
            -- src / # Front-end files to be built
-- .gitignore # Ignore unnecessary files
-- README.md # Documentation

## Installation & Setup
### ** Prerequisites **
Ensure you have the following installed:
- **Python 3.10+**
- **Node.js & npm** (front-end)
- **VS Code** (recommended)
- **Google Cloud API Key** (For Maps, Directions, and Traffic data)

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

## Running the Project
### Start the FastAPI Back-End
cd backend
uvicorn main:app --reload
Then, open http://127.0.0.1:8000/docs to access the API.

### Start the Front-End
cd frontend
npm install # For React/Angular dependencies
npm start   # React
ng serve    # Angular

## API Endpoints
/api/route          Get optimized route & waypoints     GET
/api/traffic        Get real-time traffic updates       GET
/api/map            Generate color-coded traffic map    GET


## License
This project is licensed under the MIT license.