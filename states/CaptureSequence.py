import os
import shutil
import time
from datetime import datetime

from PIL import Image

from printer.printer import send_print_job
from states.DisplayTextState import DisplayTextState

from states.State import State
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
import cv2

assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets"))
output_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "output"))
captures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "captures"))
archive_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "archive"))

def place_next_duplicate(img1):
    final_image = Image.new("RGBA", (1200, 1800), (255, 255, 255, 255))
    final_image.paste(img1, (0, 0))
    final_image.paste(img1, (600, 0))
    return final_image


def remove_all_files(directory):
    for file_name in os.listdir(directory):
        file_path = os.path.join(directory, file_name)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"Cleaned: {file_path}")


def image_to_square(image_path):
    '''
    Converts an image path into a square PIL Image object cropped from center of img
    :param image_path:
    :return:
    '''
    with Image.open(image_path) as img:
        width, height = img.size
        if width != height:
            min_side = min(width, height)
            left = (width - min_side) // 2
            top = (height - min_side) // 2
            right = left + min_side
            bottom = top + min_side
            img = img.crop((left, top, right, bottom))
    return img


def image_to_center_crop_aspect(image_path, aspect_ratio):
    '''
    Crops the largest possible rectangle from the center of the image that matches the given aspect ratio.
    :param image_path: Path to the image.
    :param aspect_ratio: Desired aspect ratio (width / height).
    :return: Cropped PIL Image object.
    '''
    with Image.open(image_path) as img:
        width, height = img.size

        if width / height > aspect_ratio:
            crop_height = height
            crop_width = int(height * aspect_ratio)
        else:
            crop_width = width
            crop_height = int(width / aspect_ratio)

        left = (width - crop_width) // 2
        top = (height - crop_height) // 2
        right = left + crop_width
        bottom = top + crop_height

        img = img.crop((left, top, right, bottom))

    return img


def process_images(image_paths, template):
    '''
    Returns a list of PIL Image objects for the specified template
    :param image_paths:
    :param template:
    :return:
    '''
    if len(image_paths) != template.get("num_images"):
        raise Exception("Number of images does not match template size")
    final_images = []
    image_size = template.get("image_size")
    for image_path in image_paths:
        img = image_to_center_crop_aspect(image_path, (image_size[0] / image_size[1]))
        img = img.resize((image_size[0], image_size[1]))
        final_images.append(img)
    return final_images


def create_photo(image_paths, template, output_path):
    '''
    Creates final photobooth png image
    :param image_paths:
    :param template:
    :param output_path:
    :return:
    '''
    final_image = Image.new("RGBA", (600, 1800), (255, 255, 255, 255))
    processed_images = process_images(image_paths, template)
    image_size = template.get("image_size")
    pos = template.get("starting_pos")
    for image in processed_images:
        final_image.paste(image, pos)
        pos = (pos[0], pos[1] + image_size[1] + template.get("image_div"))

    border = Image.open(template.get("border")).convert("RGBA")
    final_image.paste(border, (0, 0), border)
    final_image = place_next_duplicate(final_image)
    final_image.save(output_path)
    print(f"Final image saved at: {output_path}")


def get_image_paths(directory):
    return sorted(
        [
            os.path.abspath(os.path.join(directory, f))
            for f in os.listdir(directory)
            if os.path.isfile(os.path.join(directory, f)) and not f.startswith('.')
        ]
    )


def move_files(source_dir, destination_dir):
    for file_name in os.listdir(source_dir):
        source_path = os.path.join(source_dir, file_name)
        destination_path = os.path.join(destination_dir, file_name)
        if os.path.isfile(source_path):
            shutil.move(source_path, destination_path)
            print(f"Moved: {source_path} -> {destination_path}")


class CaptureSequence(State):
    """
    Manages the GUI that runs the capture sequence for the photo booth.
    """
    def __init__(self, manager, template: dict, parent=None, ):
        super().__init__(manager, main_widget=CameraCaptureWidget(state=self,save_dir =captures_dir,template=template), sub_widget=None)
        remove_all_files(captures_dir)
        self.template = template

    def send_job(self, photo_output_path=None):
        images = get_image_paths(captures_dir)
        create_photo(images, self.template, f"{output_dir}/final_photo.png")
        print("Sending job")
        send_print_job(photo_output_path)

    def next_state(self) -> State:
        from states.Start import Start
        self.send_job()
        move_files(output_dir, archive_dir)
        final = lambda: DisplayTextState(manager=self.manager,
                                display_text="Thank you!",
                                timeout=10,
                                next=(lambda: Start(self.manager)))
        return DisplayTextState(manager=self.manager,
                                display_text="Printing...",
                                timeout=30,
                                next=final)


class CameraCaptureWidget(QWidget):
    def __init__(self, save_dir:str, template: dict, state: State, display_time=3, countdown_time=5, preview_time=3):
        super().__init__()
        self.display_time = display_time
        self.save_dir = save_dir
        self.template = template
        self.countdown_time = countdown_time
        self.preview_time = preview_time
        self.num_images = template.get("num_images")
        self.aspect_ratio = template.get("image_size")[0] / template.get("image_size")[1]
        self.photos_index = 0
        self.start_time = time.time()
        self.is_freezing = False
        self.state = state

        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open webcam.")

        self.setWindowTitle("Camera Capture")
        self.video_label = QLabel(self)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_label)
        self.setLayout(self.layout)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) #30ms

    def update_frame(self):
        if self.is_freezing:
            return

        elapsed_time = time.time() - self.start_time
        if elapsed_time < self.preview_time:
            ret, frame = self.cap.read()
            if not ret:
                return
            frame = self.crop_frame(frame)
            self.display_frame(frame)
            return

        if self.photos_index >= self.num_images:
            self.timer.stop()
            self.cap.release()
            self.state.notify_state_update()
            return

        ret, frame = self.cap.read()
        if not ret:
            return

        frame = self.crop_frame(frame)

        remaining_time = max(self.countdown_time - int(elapsed_time - self.preview_time), 0)

        if remaining_time == 0:
            frame = self.capture_photo(frame)
            self.display_frame(frame)
            self.is_freezing = True
            QTimer.singleShot(self.display_time * 1000, self.end_freeze) # Freeze frame for display_time

        elif remaining_time == 1:
            self.overlay_text(frame, "Smile!", position=(100, 200), font_scale=8, color=(0, 255, 0), thickness=8)
        else:
            self.overlay_text(frame, str(remaining_time - 1), position=(100, 200), font_scale=8, color=(255, 255, 255),
                              thickness=8)

        self.display_frame(frame)

    def end_freeze(self):
        """
        End the freeze mode and reset the timer.
        """
        self.is_freezing = False
        self.start_time = time.time()
        self.photos_index += 1

    def capture_photo(self, frame):
        timestamp = datetime.now().strftime("%m-%d-%H%M%S")
        photo_path = os.path.join(self.save_dir, f"photo{self.photos_index}-{timestamp}.jpg")
        cv2.imwrite(photo_path, frame)
        return frame

    def overlay_text(self, frame, text, position=(50, 50), font_scale=2, color=(0, 255, 0), thickness=3):
        cv2.putText(frame, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)

    def display_frame(self, frame):
        height, width, channel = frame.shape
        bytes_per_line = channel * width
        frame_bytes = frame.tobytes()
        qt_image = QImage(frame_bytes, width, height, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)

    def crop_frame(self, frame):
        frame_height, frame_width, _ = frame.shape

        if frame_width / frame_height > self.aspect_ratio:
            crop_height = frame_height
            crop_width = int(frame_height * self.aspect_ratio)
        else:
            crop_width = frame_width
            crop_height = int(frame_width / self.aspect_ratio)

        x = (frame_width - crop_width) // 2
        y = (frame_height - crop_height) // 2

        return frame[y:y + crop_height, x:x + crop_width]

