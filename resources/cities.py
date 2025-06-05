"""
Static list of 60+ major cities (30 USA, 30+ international)
"""
CITIES = [
    # USA
    {"name": "New York", "lat": 40.7128, "lon": -74.0060},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298},
    {"name": "Houston", "lat": 29.7604, "lon": -95.3698},
    {"name": "Phoenix", "lat": 33.4484, "lon": -112.0740},
    {"name": "Philadelphia", "lat": 39.9526, "lon": -75.1652},
    {"name": "San Antonio", "lat": 29.4241, "lon": -98.4936},
    {"name": "San Diego", "lat": 32.7157, "lon": -117.1611},
    {"name": "Dallas", "lat": 32.7767, "lon": -96.7970},
    {"name": "San Jose", "lat": 37.3382, "lon": -121.8863},
    {"name": "Austin", "lat": 30.2672, "lon": -97.7431},
    {"name": "Jacksonville", "lat": 30.3322, "lon": -81.6557},
    {"name": "Fort Worth", "lat": 32.7555, "lon": -97.3308},
    {"name": "Columbus", "lat": 39.9612, "lon": -82.9988},
    {"name": "Charlotte", "lat": 35.2271, "lon": -80.8431},
    {"name": "San Francisco", "lat": 37.7749, "lon": -122.4194},
    {"name": "Indianapolis", "lat": 39.7684, "lon": -86.1581},
    {"name": "Seattle", "lat": 47.6062, "lon": -122.3321},
    {"name": "Denver", "lat": 39.7392, "lon": -104.9903},
    {"name": "Washington", "lat": 38.9072, "lon": -77.0369},
    {"name": "Boston", "lat": 42.3601, "lon": -71.0589},
    {"name": "El Paso", "lat": 31.7619, "lon": -106.4850},
    {"name": "Nashville", "lat": 36.1627, "lon": -86.7816},
    {"name": "Detroit", "lat": 42.3314, "lon": -83.0458},
    {"name": "Oklahoma City", "lat": 35.4634, "lon": -97.5151},
    {"name": "Portland", "lat": 45.5051, "lon": -122.6750},
    {"name": "Las Vegas", "lat": 36.1699, "lon": -115.1398},
    {"name": "Memphis", "lat": 35.1495, "lon": -90.0490},
    {"name": "Louisville", "lat": 38.2527, "lon": -85.7585},
    {"name": "Baltimore", "lat": 39.2904, "lon": -76.6122},
    # International
    {"name": "London", "lat": 51.5074, "lon": -0.1278},
    {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
    {"name": "Tokyo", "lat": 35.6895, "lon": 139.6917},
    {"name": "Beijing", "lat": 39.9042, "lon": 116.4074},
    {"name": "Moscow", "lat": 55.7558, "lon": 37.6173},
    {"name": "Berlin", "lat": 52.5200, "lon": 13.4050},
    {"name": "Madrid", "lat": 40.4168, "lon": -3.7038},
    {"name": "Rome", "lat": 41.9028, "lon": 12.4964},
    {"name": "Istanbul", "lat": 41.0082, "lon": 28.9784},
    {"name": "Cairo", "lat": 30.0444, "lon": 31.2357},
    {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
    {"name": "Toronto", "lat": 43.6532, "lon": -79.3832},
    {"name": "Mexico City", "lat": 19.4326, "lon": -99.1332},
    {"name": "Sao Paulo", "lat": -23.5505, "lon": -46.6333},
    {"name": "Buenos Aires", "lat": -34.6037, "lon": -58.3816},
    {"name": "Johannesburg", "lat": -26.2041, "lon": 28.0473},
    {"name": "Dubai", "lat": 25.2048, "lon": 55.2708},
    {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"name": "Hong Kong", "lat": 22.3193, "lon": 114.1694},
    {"name": "Bangkok", "lat": 13.7563, "lon": 100.5018},
    {"name": "Seoul", "lat": 37.5665, "lon": 126.9780},
    {"name": "Delhi", "lat": 28.6139, "lon": 77.2090},
    {"name": "Jakarta", "lat": -6.2088, "lon": 106.8456},
    {"name": "Lagos", "lat": 6.5244, "lon": 3.3792},
    {"name": "Nairobi", "lat": -1.2921, "lon": 36.8219},
    {"name": "Copenhagen", "lat": 55.6761, "lon": 12.5683},
    {"name": "Stockholm", "lat": 59.3293, "lon": 18.0686},
    {"name": "Helsinki", "lat": 60.1699, "lon": 24.9384},
    {"name": "Oslo", "lat": 59.9139, "lon": 10.7522},
    {"name": "Zurich", "lat": 47.3769, "lon": 8.5417},
]

def get_nearest_city(centroid, return_coords=False):
    # centroid: (lat, lon)
    min_dist = float('inf')
    nearest = None
    for city in CITIES:
        dist = (city['lat'] - centroid[0]) ** 2 + (city['lon'] - centroid[1]) ** 2
        if dist < min_dist:
            min_dist = dist
            nearest = city
    if return_coords:
        return nearest['name'], nearest['lat'], nearest['lon']
    else:
        return nearest['name']
