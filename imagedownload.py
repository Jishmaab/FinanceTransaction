import os
import requests

def download_image(url, destination):
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(destination, 'wb') as file:
            file.write(response.content)
        print(f"Image downloaded successfully to {destination}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

google_image_url = "https://e0.pxfuel.com/wallpapers/655/168/desktop-wallpaper-labrador-retriever-dog-labrador-dog.jpg"

home_directory = os.path.expanduser("~")

downloads_folder = os.path.join(home_directory, "Downloads")
destination_path = os.path.join(downloads_folder, "downloaded_image.png")

download_image(google_image_url, destination_path)
