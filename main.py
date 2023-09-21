from BosonSDK import *
import serial
import time
import os
import cv2
import numpy as np
from camera_initialization import initialize_camera

# Function to create a save directory with an incremented number if it already exists
def create_save_directory(save_root, base_dir):
    n = 1
    while True:
        sub_dir = f"{base_dir}-{n}"
        save_dir = os.path.join(save_root, sub_dir)
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            return save_dir
        n += 1

# Function to capture frames and save as TIFF images
def capture_and_save_frames(myCam, save_dir, num_frames, duration):
    settings = FLR_CAPTURE_SETTINGS_T()
    settings.dataSrc = FLR_CAPTURE_SRC_E.FLR_CAPTURE_SRC_NUC
    settings.numFrames = num_frames
    settings.bufferIndex = 1
    myCam.colorLutSetControl(FLR_ENABLE_E.FLR_ENABLE)
    myCam.colorLutSetId(FLR_COLORLUT_ID_E.FLR_COLORLUT_0) #Choose te greyscale setting known for preserving data the best

    capture_15 = myCam.captureFrames(data=settings) #In our case we capture in 16bit, meaning we have two bytes of data for each pixel

    for k in range(2, num_frames + 1):
        all_pixels = []
        src = FLR_CAPTURE_SRC_E.FLR_CAPTURE_SRC_NUC
        rows, columns = myCam.memGetCaptureSizeSrc(src)[2], myCam.memGetCaptureSizeSrc(src)[3]
        resolution = rows * columns

        for i in range(0, (resolution) * 2, 256): #We go up to 256 Bytes because this is the max we could go to
            chunk_size = min(256, ((resolution) * 2) - i)
            buffer_data = myCam.memReadCaptureSrc(src, k, i, chunk_size)[1]
            pixels = []

            for j in range(0, chunk_size, 2):
                byte1, byte2 = buffer_data[j], buffer_data[j + 1]
                pixel_value = (byte1 << 8) | byte2
                pixels.append(pixel_value)

            all_pixels.extend(pixels)
            print(f"Frame {k}, pixel chunk number {i} out of {(resolution) * 2} chunks added")

        image_data = np.array(all_pixels, dtype=np.uint16).reshape(rows, columns)
        filename = f"{k}_image.tiff"
        save_path = os.path.join(save_dir, filename)
        cv2.imwrite(save_path, image_data)
        print(f"Saved 16-bit grayscale TIFF image number {k} to {save_path}")
        time.sleep(duration)


# Main function
def main():
    save_root = "/media/isabelle/def201ba-c1f0-4bb7-adc5-5412a496ee86/video"
    base_dir = "test-code"
    duration_of_test = 3  # 3 seconds per frame
    num_frames = 15

    myCam = initialize_camera()

    if myCam is not None:
        save_dir = create_save_directory(save_root, base_dir)
        capture_and_save_frames(myCam, save_dir, num_frames, duration_of_test)
        myCam.Close()
        print("Camera closed.")

if __name__ == "__main__":
    main()