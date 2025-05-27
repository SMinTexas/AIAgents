import requests
urls = [
    # Food and drink
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/restaurant_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/cafe_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/bar_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/bakery_pinlet.svg",
    # Retail
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/shopping_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/bookstore_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/clothing_store_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/convenience_store_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/electronics_store_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/florist_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/grocery_or_supermarket_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/jewelry_store_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/liquor_store_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/pharmacy_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/shoe_store_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/shopping_mall_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/store_pinlet.svg",
    # Services
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/gas_station_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/lodging_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/hotel_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/car_rental_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/car_repair_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/car_wash_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/atm_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/bank_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/hospital_pinlet.svg",
    # Entertainment
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/aquarium_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/art_gallery_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/attraction_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/bowling_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/casino_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/movie_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/museum_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/nightclub_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/theater_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/zoo_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/stadium_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/park_pinlet.svg",
    # Transporation
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/airport_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/bus_station_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/subway_station_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/train_station_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/transit_station_pinlet.svg",
    # Municipal/generic/religious
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/city_hall_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/courthouse_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/fire_station_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/police_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/post_office_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/synagogue_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/church_pinlet.svg",
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/temple_pinlet.svg",
    # Emergency
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/hospital_pinlet.svg",
    # Fallback
    "https://maps.gstatic.com/mapfiles/place_api/icons/v2/generic_pinlet.svg"
]

for url in urls:
    try:
        r = requests.head(url)
        print(f"{url}: {r.status_code}")
    except Exception as e:
        print(f"{url}: ERROR {e}")