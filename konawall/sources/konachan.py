import requests
import logging
from custom_print import kv_print
from custom_errors import RequestFailed
from module_loader import add_source
from downloader import download_files

"""
Turn a list of tags and a count into a list of URLs to download from

:param count: The number of images to provide download URLs for
:param user_tags: A list of tags to search for
:returns: A list of URLs to download from
"""
def request_posts(count: int, tags: list) -> list:
    logging.debug(f"request_posts() called with count={count}, tags=[{', '.join(tags)}]")
    # Make sure we get a different result every time by using "order:random" as a tag
    if "order:random" not in tags:
        tags.append("order:random")
    # Tags are separated by a plus sign for this API
    tag_string: str = "+".join(tags)
    # Request URL for getting posts from the API
    url: str = f"https://konachan.com/post.json?limit={str(count)}&tags={tag_string}"
    logging.debug(f"Request URL: {url}")
    response = requests.get(url, headers={"User-Agent": "konachan-py/alpha"})
    # Check if the request was successful
    logging.debug("Status code: " + str(response.status_code))
    # List of URLs to download
    post_urls: list = []
    if response.status_code == 200:
        # Get the JSON data from the response
        json = response.json()
        for post in json:
            # Give the user data about the post retrieved
            kv_print("Post ID", post["id"])
            kv_print("Author", post["author"])
            kv_print("Rating", post["rating"])
            kv_print("Resolution", f"{post['width']}x{post['height']}")
            kv_print("Tags", post["tags"])
            kv_print("URL", post["file_url"])
            # Append the URL to the list
            post_urls.append(post["file_url"])
    else:
        # Raise an exception if the request failed
        RequestFailed(response.status_code)
    return post_urls

"""
Download a number of images from Konachan given a list of tags and a count

:param count: The number of images to download
:param tags: A list of tags to search for
"""
@add_source("konachan")
def handle(count: int, tags: list) -> list:
    logging.debug(f"handle_konachan() called with count={count}, tags=[{', '.join(tags)}]")
    # Get a list of URLs to download
    post_urls: list = request_posts(count, tags)
    # Download the images
    files = download_files(post_urls)
    # Return the downloaded files
    return files