import os
import cv2
import tkinter as tk
from tkinter import filedialog, simpledialog
from moviepy.editor import VideoFileClip, concatenate_videoclips, ImageClip, CompositeVideoClip

def select_file(title, filetypes):
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(title=title, filetypes=filetypes)
    root.destroy()
    return file_path

def select_folder(title):
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title=title)
    root.destroy()
    return folder_path

def resize_clip(clip, target_height):
    width = int((clip.size[0] * target_height) / clip.size[1])
    return clip.resize((width, target_height))

def create_image_clip(image_path, duration, height):
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if image.shape[-1] == 4:
        image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGBA)
    else:
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    h, w, _ = image.shape
    scale_factor = height / h
    new_width = int(w * scale_factor)
    resized_image = cv2.resize(image, (new_width, height))
    return ImageClip(resized_image).set_duration(duration)

def process_note_folder(note_folder, intro_clip, outro_clip, background_image, target_height, image_duration):
    content_paths = [os.path.join(note_folder, f) for f in os.listdir(note_folder) if f.lower().endswith(('mp4', 'avi', 'mov', 'png', 'jpg', 'jpeg'))]
    
    content_clips = []
    for content_path in content_paths:
        if content_path.lower().endswith(('mp4', 'avi', 'mov')):
            clip = VideoFileClip(content_path)
            resized_clip = resize_clip(clip, target_height)
            content_clips.append(resized_clip)
        elif content_path.lower().endswith(('png', 'jpg', 'jpeg')):
            image_clip = create_image_clip(content_path, duration=image_duration, height=target_height)
            content_clips.append(image_clip)

    if content_clips:
        final_content_clip = concatenate_videoclips(content_clips, method="compose")
    else:
        return

    final_clip = concatenate_videoclips([intro_clip, final_content_clip, outro_clip], method="compose")

    final_clip_with_background = CompositeVideoClip([background_image.set_duration(final_clip.duration), final_clip.set_position('center')])

    final_clip_with_background = final_clip_with_background.without_audio()

    output_filename = os.path.basename(note_folder) + ".mp4"
    output_path = os.path.join(os.getcwd(), output_filename)
    final_clip_with_background.write_videofile(output_path, codec="libx264", fps=24)

    print(f"Video saved at {output_path}")


def get_image_duration():
    root = tk.Tk()
    root.withdraw()
    image_duration = simpledialog.askinteger("Image Duration", "Enter the duration of each image (in seconds):", minvalue=1, initialvalue=4)
    root.destroy()
    return image_duration

def main():
    intro_path = select_file("Select Intro Video", [("Video Files", "*.mp4 *.avi *.mov")])
    if not intro_path:
        print("No intro video selected. Exiting...")
        return

    outro_path = select_file("Select Outro Video", [("Video Files", "*.mp4 *.avi *.mov")])
    if not outro_path:
        print("No outro video selected. Exiting...")
        return

    background_path = select_file("Select Background Image", [("Image Files", "*.png *.jpg *.jpeg")])
    if not background_path:
        print("No background image selected. Exiting...")
        return

    parent_folder = select_folder("Select the parent folder containing note folders")
    if not parent_folder:
        print("No parent folder selected. Exiting...")
        return

    intro_clip = VideoFileClip(intro_path)
    outro_clip = VideoFileClip(outro_path)

    image_duration = get_image_duration()

    background_image = ImageClip(background_path)
    if background_image.size[0] != 1920 or background_image.size[1] != 1080:
        background_image = background_image.resize((1920, 1080))

    note_folders = [f.path for f in os.scandir(parent_folder) if f.is_dir()]
    for note_folder in note_folders:
        process_note_folder(note_folder, intro_clip, outro_clip, background_image, target_height=int(1080 * 0.6), image_duration=image_duration)

if __name__ == "__main__":
    main()
