import streamlit as st
import requests
import pandas as pd
from streamlit_folium import folium_static
import folium

# Replace with your API keys
GEOAPIFY_API_KEY = "your_geoapify_api_key"
GOOGLE_PLACES_API_KEY = "your_google_places_api_key"
YOUTUBE_API_KEY = "your_youtube_api_key"

# Streamlit App Title
st.title("Travel Planner: Plan, Book, and Share")

# Sidebar Inputs
st.sidebar.header("Input Your Travel Preferences")
destination = st.sidebar.text_input("Destination", "Paris")
location = st.sidebar.text_input("Latitude,Longitude", "48.8566,2.3522")  # Default to Paris
radius = st.sidebar.slider("Search Radius (meters)", 1000, 10000, 5000)  # Default: 5km
query = st.sidebar.selectbox(
    "Places to Explore",
    ["tourism", "restaurant", "hotel", "entertainment"],
    index=0
)
st.sidebar.write("Adjust your preferences and click **Search** to begin.")

# Function to Fetch Places from GeoApify
def fetch_places(query, location, radius):
    url = f"https://api.geoapify.com/v2/places?categories={query}&filter=circle:{location},{radius}&apiKey={GEOAPIFY_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("features", [])
    else:
        st.error("Error fetching places from GeoApify.")
        return []

# Function to Fetch YouTube Videos
def fetch_youtube_videos(destination):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={destination} travel&type=video&key={YOUTUBE_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        st.error("Error fetching videos from YouTube.")
        return []

# Display Results for Search
if st.sidebar.button("Search"):
    st.header(f"Results for {destination}")

    # Fetch places
    st.subheader("Top Places of Interest")
    places = fetch_places(query, location, radius)
    if places:
        # Initialize map centered on location
        lat, lng = map(float, location.split(","))
        travel_map = folium.Map(location=[lat, lng], zoom_start=13)

        # Display places on the map
        place_list = []
        for place in places:
            name = place["properties"].get("name", "Unknown")
            category = place["properties"].get("categories", ["Unknown"])[0]
            lat = place["geometry"]["coordinates"][1]
            lng = place["geometry"]["coordinates"][0]
            address = place["properties"].get("address_line1", "Address unavailable")
            
            # Add marker to map
            folium.Marker(
                location=[lat, lng],
                popup=f"<b>{name}</b><br>{category}<br>{address}",
                tooltip=name,
            ).add_to(travel_map)

            # Append to list
            place_list.append({
                "Name": name,
                "Category": category,
                "Address": address
            })

        # Show map
        folium_static(travel_map)

        # Show place list as a table
        st.write("Places Table:")
        df = pd.DataFrame(place_list)
        st.dataframe(df)

    else:
        st.write("No places found for the given query.")

    # Fetch YouTube videos
    st.subheader("YouTube Travel Videos")
    videos = fetch_youtube_videos(destination)
    if videos:
        for video in videos[:3]:  # Show top 3 videos
            title = video["snippet"]["title"]
            video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
            st.markdown(f"[{title}]({video_url})")
    else:
        st.write("No videos found for this destination.")

# Itinerary Planner
st.header("Itinerary Planner")
selected_places = st.multiselect("Select Places for Your Itinerary", options=df["Name"].tolist() if 'df' in locals() else [])
if st.button("Generate Itinerary"):
    if selected_places:
        st.write("### Your Itinerary:")
        for i, place in enumerate(selected_places, 1):
            st.write(f"{i}. {place}")
    else:
        st.warning("Please select at least one place to generate an itinerary.")
