# import os
# import requests

# def download_image(url, destination):
#     response = requests.get(url)
    
#     if response.status_code == 200:
#         with open(destination, 'wb') as file:
#             file.write(response.content)
#         print(f"Image downloaded successfully to {destination}")
#     else:
#         print(f"Failed to download image. Status code: {response.status_code}")

# google_image_url = "https://i.pinimg.com/564x/4e/3f/61/4e3f61a18a7118974423498fd28eb799.jpg"

# home_directory = os.path.expanduser("~")
# print(home_directory)
# downloads_folder = os.path.join(home_directory, "Downloads")
# destination_path = os.path.join(downloads_folder, "downloaded_image2.png")

# download_image(google_image_url, destination_path)
import os
import requests
from datetime import datetime

def download_image(url, destination_folder, filename=None):
    response = requests.get(url)
    
    if response.status_code == 200:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            filename = f"download_{timestamp}.png"
        
        destination_path = os.path.join(destination_folder, filename)

        with open(destination_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Image downloaded successfully to {destination_path}")
    else:
        print(f"Failed to download image. Status code: {response.status_code}")

google_image_url = "https://cdn.britannica.com/01/88401-050-26CBE648/American-crow.jpg"

downloads_folder = os.path.join(os.path.expanduser("~"), "Downloads")

download_image(google_image_url, downloads_folder)
