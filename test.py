import math
def haversine(lat1, lon1, lat2, lon2):
 R = 6371 # Radius of the Earth in km
 dLat = math.radians(lat2 - lat1)
 dLon = math.radians(lon2 - lon1)
 a = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) * math.sin(dLon / 2)
 c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
 d = R * c # Distance in km
 return d

print(haversine(51.5074, 0.1278, 40.7128, -74.0060)) # Calculate the distance between London and New York