import logging
import tempfile
import requests
from konawall.custom_print import kv_print

"""
Download files given a list of URLs

:param files: A list of URLs to download from
"""
def download_files(files: list) -> list:
    logging.debug(f"download_posts() called with files=[{', '.join(files)}]")
    # Keep a list of downloaded files
    downloaded_files: list = []
    # Download the images
    for i, url in enumerate(files):
        logging.debug(f"Downloading {url}")
        # Get the image data
        image = requests.get(url)
        # Create a temporary file to store the image
        image_file = tempfile.NamedTemporaryFile(delete=False)
        logging.debug(f"Created temporary file {image_file.name}")
        # Write the image data to the file
        image_file.write(image.content)
        # Close the file
        image_file.close()
        # Give the user data about the downloaded image
        kv_print(f"Image {str(i+1)}", image_file.name)
        # Add the file to the list of downloaded files
        downloaded_files.append(image_file.name)
    return downloaded_files