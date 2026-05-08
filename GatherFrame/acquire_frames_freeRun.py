from pypylon import pylon, genicam
import cv2
import os
import time
from concurrent.futures import ThreadPoolExecutor


def configure_camera_for_trigger(camera):
    camera.TriggerSelector.SetValue("FrameStart")
    camera.TriggerMode.SetValue("On")
    camera.TriggerSource.SetValue("Line2")
    camera.TriggerActivation.SetValue("AnyEdge")
    camera.ExposureTime.SetValue(5000)
    camera.ExposureAuto.SetValue("Off")


def configure_camera_for_freerun(camera):
    camera.TriggerMode.SetValue("Off")
    camera.AcquisitionFrameRateEnable.SetValue(True)
    camera.AcquisitionFrameRate.SetValue(40.0)
    camera.ExposureAuto.SetValue("Off")


def save_frame(frame, filepath):
    # Use minimal compression for faster saving
    cv2.imwrite(filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, 0])


def check_signal_level(camera):
    camera.LineSelector.SetValue("Line2")
    state = camera.LineStatus.GetValue()
    print(f"Line2 signal level: {'HIGH' if state else 'LOW'}")
    return state


def wait_for_trigger_and_run(camera, save_dir, max_frames=5000):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    frame_count = 0
    executor = ThreadPoolExecutor(max_workers=4)  # Adjust as needed

    while frame_count < max_frames:
        print("Waiting for signal edge (HIGH = start, LOW = stop)...")

        configure_camera_for_trigger(camera)
        camera.StartGrabbingMax(1)

        # Wait for edge trigger
        while True:
            try:
                result = camera.RetrieveResult(10000, pylon.TimeoutHandling_ThrowException)
                if result.GrabSucceeded():
                    print("Signal Edge Detected!")
                    result.Release()
                    break
            except genicam.TimeoutException:
                print("Still waiting for edge...")
                continue

        camera.StopGrabbing()

        # Check signal level
        signal_high = check_signal_level(camera)

        if signal_high:
            print("Signal is HIGH. Starting Free Run...")
            configure_camera_for_freerun(camera)
            camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

            start_time = time.time()
            fps_counter = 0

            while camera.IsGrabbing():
                grab_result = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)
                if grab_result.GrabSucceeded():
                    img = grab_result.GetArray()
                    filename = os.path.join(save_dir, f"frame_{frame_count:04d}.png")
                    executor.submit(save_frame, img, filename)
                    frame_count += 1
                    fps_counter += 1

                grab_result.Release()

                # Display FPS every second
                if time.time() - start_time >= 1.0:
                    print(f"FPS: {fps_counter}")
                    fps_counter = 0
                    start_time = time.time()

                # Stop if signal goes LOW
                if not check_signal_level(camera):
                    print("Signal went LOW. Stopping Free Run...")
                    break

            camera.StopGrabbing()

        else:
            print("Signal is LOW. Staying Idle...")

    executor.shutdown(wait=True)
    print(f"Finished. Total frames saved: {frame_count}")


def main():
    save_directory = "D:/TowingTankData/R1_E1_001"
    max_frames = 5000

    tl_factory = pylon.TlFactory.GetInstance()
    camera = pylon.InstantCamera(tl_factory.CreateFirstDevice())
    camera.Open()

    try:
        wait_for_trigger_and_run(camera, save_directory, max_frames)
    finally:
        camera.Close()
        print("Camera closed.")


if __name__ == "__main__":
    main()
