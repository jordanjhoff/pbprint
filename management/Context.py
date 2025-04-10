import os

assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))


vinny_template = {
    "name": "vinny",
    "num_images": 3,
    "image_size": (482, 435),
    "starting_pos": (59, 59),
     "image_div": 58,
     "border": f"{assets_dir}/vinny2.png",
    "orientation": "vertical",
    "date":"black"}

template_2 = {
    "name": "NA",
    "num_images": 4,
    "image_size": (482, 322),
    "starting_pos": (59, 59),
    "image_div": 58,
    "border": f"{assets_dir}/template_2.png",
    "orientation": "vertical",
    "date":"black"}

film_template = {
    "name": "film",
    "num_images": 3,
    "image_size": (414, 569),
    "starting_pos": (91, 23),
    "image_div": 10,
    "border": f"{assets_dir}/film_strip.png",
    "orientation": "horizontal",
    "date":False}

film2 = {
    "name": "film2",
    "num_images": 3,
    "image_size": (380, 580),
    "starting_pos": (110, 23),
    "image_div": 10,
    "border": f"{assets_dir}/film2.png",
    "orientation": "horizontal",
    "date":False}

pasta = {
    "name": "pasta",
    "num_images": 3,
    "image_size": (555, 431),
    "starting_pos": (20, 50),
    "image_div": 15,
    "border": f"{assets_dir}/pasta.png",
    "orientation": "vertical",
    "date":"black"}

vday = {
    "name": "vday",
    "num_images": 3,
     "image_size": (555, 431),
     "starting_pos": (20, 50),
     "image_div": 8,
     "border": f"{assets_dir}/vday.png",
     "orientation": "vertical",
     "date":"white"
}

doodle = {
    "name": "doodle",
    "num_images": 3,
    "image_size": (550, 429),
    "starting_pos": (20, 70),
    "image_div": 72,
    "border": f"{assets_dir}/doodle.png",
    "orientation": "vertical",
    "date":"white"
}

paddy = {
    "name": "paddy",
    "num_images": 3,
    "image_size": (482, 435),
    "starting_pos": (59, 59),
    "image_div": 58,
    "border": f"{assets_dir}/paddy.png",
    "orientation": "vertical",
    "date":False,
}

paddyrho = {
    "name": "paddyrho",
    "num_images": 3,
    "image_size": (482, 435),
    "starting_pos": (59, 59),
    "image_div": 58,
    "border": f"{assets_dir}/paddyrho.png",
    "orientation": "vertical",
    "date":False,
}

formal = {
    "name": "formal",
    "num_images": 3,
    "image_size": (482, 435),
    "starting_pos": (59, 59),
    "image_div": 58,
    "border": f"{assets_dir}/formal.png",
    "orientation": "vertical",
    "date":False,
}

class Config:
    """
    The configuration context that gets passed from state to state.

    Represents the initial config upon boot, but can be modified by the developer control state.
    """
    def __init__(self):
        self.template_group_main = [vinny_template, film2, doodle, formal]
        self.template_group_alt = [vinny_template, film2, doodle, vday, paddy, paddyrho]

        self.ACCEPT_PAYMENT = False
        self.PRICE = 3  # USD
        self.DEV_CODE = "2121919"
        self.CURRENT_TEMPLATES = self.template_group_main

        # Fine tune controls for calibrating print image
        self.VERTICAL_PADDING = 10 # pixels
        self.HORIZONTAL_PADDING = 20
        self.HORIZONTAL_SHIFT = 5
        self.VERTICAL_SHIFT = -6

        self.DELETE_IMAGES = False
