import tempfile
import logging
from PIL import Image

def combine_to_viewport(displays: list, files: list):
    # Create an image that is the size of the combined viewport, with offsets for each display
    max_width = max([display.x + display.width for display in displays])
    max_height = max([display.y + display.height for display in displays])
    combined = Image.new("RGB", (max_width, max_height))
    for i, file in enumerate(files):
        open_image = Image.open(file, "r")
        resized_image = open_image.resize((displays[i].width, displays[i].height))
        combined.paste(resized_image, (displays[i].x, displays[i].y))
    file = tempfile.NamedTemporaryFile(delete=False)
    logging.debug(f"Created temporary file {file.name} to save combined viewport image into")
    combined.save(file.name, format="PNG")
    return file
