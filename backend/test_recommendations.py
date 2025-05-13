import asyncio
import importlib
from agents.recommendation_agent import RecommendationAgent
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Disable proxy settings
os.environ['HTTP_PROXY'] = ''
os.environ['HTTPS_PROXY'] = ''
os.environ['NO_PROXY'] = '*'

# Force reload the recommendation_agent module
import agents.recommendation_agent
importlib.reload(agents.recommendation_agent)
from agents.recommendation_agent import RecommendationAgent

async def test_recommendations():
    agent = RecommendationAgent()
    
    # Test locations
    locations = ["New Orleans, LA", "Pensacola, FL"]
    
    print("\n=== First Request (Cache MISS) ===")
    start_time = time.time()
    results1 = await agent.get_recommendations(locations)
    end_time = time.time()
    print(f"First request took: {end_time - start_time:.2f} seconds")
    
    print("\n=== Second Request (Cache HIT) ===")
    start_time = time.time()
    results2 = await agent.get_recommendations(locations)
    end_time = time.time()
    print(f"Second request took: {end_time - start_time:.2f} seconds")
    
    # Print results summary for both requests
    print("\n=== Results Summary ===")
    for loc in locations:
        print(f"\nLocation: {loc}")
        print("First Request:")
        print(f"  Restaurants: {len(results1[loc]['restaurants'])}")
        print(f"  Hotels: {len(results1[loc]['hotels'])}")
        print(f"  Attractions: {len(results1[loc]['attractions'])}")
        print("Second Request (Cached):")
        print(f"  Restaurants: {len(results2[loc]['restaurants'])}")
        print(f"  Hotels: {len(results2[loc]['hotels'])}")
        print(f"  Attractions: {len(results2[loc]['attractions'])}")
        
        # Verify data consistency
        is_consistent = (
            len(results1[loc]['restaurants']) == len(results2[loc]['restaurants']) and
            len(results1[loc]['hotels']) == len(results2[loc]['hotels']) and
            len(results1[loc]['attractions']) == len(results2[loc]['attractions'])
        )
        print(f"Cache Consistency: {'✓' if is_consistent else '✗'}")

if __name__ == "__main__":
    asyncio.run(test_recommendations()) 