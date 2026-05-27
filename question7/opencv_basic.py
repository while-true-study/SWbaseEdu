from pathlib import Path

import cv2


IMAGE_DIR = Path('images')
VIDEO_DIR = Path('videos')

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp')
VIDEO_EXTENSIONS = ('.mp4',)

WAIT_TIME = 33
ESC_KEY = 27

CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


def get_files(directory, extensions):
    if not directory.exists():
        print(f'{directory} 폴더가 없습니다.')
        return []

    files = []

    for path in directory.iterdir():
        if path.is_file() and path.suffix.lower() in extensions:
            files.append(path)

    return files


def show_images():
    image_paths = get_files(IMAGE_DIR, IMAGE_EXTENSIONS)

    if not image_paths:
        print('출력할 이미지 파일이 없습니다.')
        return

    for image_path in image_paths:
        image = cv2.imread(str(image_path))

        if image is None:
            print(f'이미지를 열 수 없습니다: {image_path}')
            continue

        window_name = f'image: {image_path.name}'
        cv2.imshow(window_name, image)

        while True:
            key = cv2.waitKey(WAIT_TIME) & 0xFF

            if key != 255:
                break

        cv2.destroyWindow(window_name)

    cv2.destroyAllWindows()


def play_video(video_path):
    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        print(f'동영상을 열 수 없습니다: {video_path}')
        return

    window_name = f'video: {video_path.name}'

    while True:
        is_read, frame = capture.read()

        if not is_read:
            break

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(WAIT_TIME) & 0xFF

        if key == ESC_KEY:
            break

    capture.release()
    cv2.destroyWindow(window_name)


def show_videos():
    video_paths = get_files(VIDEO_DIR, VIDEO_EXTENSIONS)

    if not video_paths:
        print('출력할 mp4 파일이 없습니다.')
        return

    for video_path in video_paths:
        play_video(video_path)

    cv2.destroyAllWindows()


def show_camera():
    capture = cv2.VideoCapture(CAMERA_INDEX)

    if not capture.isOpened():
        print('카메라를 열 수 없습니다.')
        return

    capture.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    capture.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

    window_name = 'camera'

    while True:
        is_read, frame = capture.read()

        if not is_read:
            print('카메라 프레임을 읽을 수 없습니다.')
            break

        cv2.imshow(window_name, frame)

        key = cv2.waitKey(WAIT_TIME) & 0xFF

        if key == ESC_KEY:
            break

    capture.release()
    cv2.destroyAllWindows()


def main():
    show_images()
    show_videos()
    show_camera()


if __name__ == '__main__':
    main()