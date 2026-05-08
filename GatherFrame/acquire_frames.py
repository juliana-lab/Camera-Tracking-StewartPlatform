
from pypylon import pylon
import cv2
import os
import numpy as np
from concurrent.futures import ThreadPoolExecutor


# Configure camera
def configure_camera():
    tl_factory = pylon.TlFactory.GetInstance()
    camera = pylon.InstantCamera()
    camera.Attach(tl_factory.CreateFirstDevice())
    camera.Open()

    # Set hardware trigger configuration
    camera.TriggerSelector.SetValue("FrameStart")
    camera.TriggerMode.SetValue("On")
    camera.TriggerSource.SetValue("Line2")
    camera.TriggerActivation.SetValue("RisingEdge")
    camera.ExposureTime.SetValue(5000)
    return camera


# Save a single frame to disk
def save_frame(frame, filepath):
    cv2.imwrite(filepath, frame)


# Frame acquisition and saving
def acquire_and_save_frames(camera, save_dir, max_frames=5000, frame_rate=32):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # Start camera grabbing
    camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    print("Camera started grabbing...")

    frame_count = 0
    with ThreadPoolExecutor() as executor:
        try:
            while frame_count < max_frames:
                grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if grab_result.GrabSucceeded():
                    img = grab_result.GetArray()

                    filename = os.path.join(save_dir, f"frame_{frame_count:04d}.png")

                    executor.submit(save_frame, img, filename)
                    frame_count += 1
                    #print(f"Frame {frame_count} saved: {filename}")

                grab_result.Release()
        except Exception as e:
            print(f"Error during acquisition: {e}")
        finally:
            camera.StopGrabbing()
            print(f"Acquisition completed. Total frames saved: {frame_count}")


# Main function
def main():
    save_directory = "D:/Z_TranslateWithMoCap/With_Arduino/0.5hzTest/03_31_2025/Test_001"  # Directory to save TIFF frames
    max_frames = 5000  # Maximum number of frames to acquire
    frame_rate = 32  # Frame rate in Hz

    # Configure the camera
    camera = configure_camera()

    try:
        # Acquire and save frames
        acquire_and_save_frames(camera, save_directory, max_frames, frame_rate)
    finally:
        # Close the camera
        camera.Close()
        print("Camera closed.")


if __name__ == "__main__":
    main()
