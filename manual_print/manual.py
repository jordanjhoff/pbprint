import os
from PIL import Image
from printer import *
from printer.printer import send_print_job
from states.CaptureSequence import create_photo, get_image_paths
from states.SelectTemplate import vinny_template

photo_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "manual_print"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))

#images = get_image_paths("window_photos")
#create_photo(images, vinny_template, f"{output_dir}/final_photo.png")
send_print_job(f"{output_dir}/final_photo.png")