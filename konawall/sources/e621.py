import requests
import logging
from konawall.custom_print import kv_print
from konawall.custom_errors import RequestFailed
from konawall.module_loader import add_source
from konawall.downloader import download_files

"""
Turn a list of tags and a count into a list of URLs to download from

:param count: The number of images to provide download URLs for
:param user_tags: A list of tags to search for
:returns: A list of URLs to download from
"""
def request_posts(count: int, tags: list, config) -> list:
    api_key = config["api_key"]
    logging.debug(f"request_posts() called with count={count}, tags=[{', '.join(tags)}]")
    # Make sure we get a different result every time by using "order:random" as a tag
    if "order:random" not in tags:
        tags.append("order:random")
    # Tags are separated by a plus sign for this API
    tag_string: str = "+".join(tags)
    # Request URL for getting posts from the API
    url: str = f"https://e621.net/posts.json?limit={str(count)}&tags={tag_string}"
    logging.debug(f"Request URL: {url}")
    response = requests.get(url, headers={"User-Agent": "konachan-py/alpha (by katsmew on e621)"})
    # Check if the request was successful
    logging.debug("Status code: " + str(response.status_code))
    # List of URLs to download
    posts: list = []
    if response.status_code == 200:
        # Get the JSON data from the response
        json = response.json()
        for post in json["posts"]:
            # Give the user data about the post retrieved
            kv_print("Post ID", post["id"])
            kv_print("Author", post["uploader_id"])
            kv_print("Rating", post["rating"])
            kv_print("Resolution", f"{post['file']['width']}x{post['file']['height']}")
            kv_print("Tags", post["tags"])
            kv_print("URL", post["file"]["url"])
            # Append the URL to the list
            post["show_url"] = f"https://e621.net/posts/{post['id']}"
            posts.append(post)
    else:
        # Raise an exception if the request failed
        RequestFailed(response.status_code)
    return posts

"""
Download a number of images from Konachan given a list of tags and a count

:param count: The number of images to download
:param tags: A list of tags to search for
"""
@add_source("e621")
def handle(count: int, tags: list, config) -> list:
    logging.debug(f"handle_e621() called with count={count}, tags=[{', '.join(tags)}]")
    # Get a list of URLs to download
    posts: list = request_posts(count, tags, config)
    urls: list = []
    # Download the images
    for post in posts:
        urls.append(post["file"]["url"])
    files = download_files(urls)
    # Return the downloaded files
    return files, posts
