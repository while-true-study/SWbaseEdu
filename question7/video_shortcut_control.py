from datetime import datetime
from pathlib import Path

import cv2


VIDEO_PATH = Path('videos/sample.mp4')

CAPTURE_DIR = Path('captures')
RECORD_DIR = Path('records')

WAIT_TIME = 33
ESC_KEY = 27
CTRL_Z_KEY = 26
CTRL_X_KEY = 24
CTRL_C_KEY = 3

DEFAULT_FPS = 30.0


def make_timestamp():
    return datetime.now().strftime('%Y%m%d_%H-%M-%S')


def make_directories():
    CAPTURE_DIR.mkdir(exist_ok=True)
    RECORD_DIR.mkdir(exist_ok=True)


def get_video_fps(capture):
    fps = capture.get(cv2.CAP_PROP_FPS)

    if fps <= 0:
        return DEFAULT_FPS

    return fps


def get_frame_size(frame):
    height, width = frame.shape[:2]
    return width, height


def save_frame(frame):
    file_name = f'{make_timestamp()}.png'
    file_path = CAPTURE_DIR / file_name

    is_success = cv2.imwrite(str(file_path), frame)

    if is_success:
        print(f'이미지 캡쳐 저장: {file_path}')
    else:
        print('이미지 캡쳐에 실패했습니다.')


def create_video_writer(file_path, codec_text, fps, frame_size):
    fourcc = cv2.VideoWriter_fourcc(*codec_text)
    writer = cv2.VideoWriter(str(file_path), fourcc, fps, frame_size)

    if not writer.isOpened():
        print(f'녹화 파일을 열 수 없습니다: {file_path}')
        return None

    return writer


def create_video_writers(base_name, fps, frame_size):
    writers = []

    mp4_path = RECORD_DIR / f'{base_name}.mp4'
    avi_path = RECORD_DIR / f'{base_name}.avi'

    codec_settings = (
        (mp4_path, 'mp4v'),
        (avi_path, 'XVID'),
    )

    for file_path, codec_text in codec_settings:
        writer = create_video_writer(
            file_path,
            codec_text,
            fps,
            frame_size,
        )

        if writer is not None:
            writers.append(writer)
            print(f'녹화 시작: {file_path}')

    return writers


def release_video_writers(writers):
    for writer in writers:
        writer.release()

    writers.clear()
    print('녹화 중지')


def handle_key(key, frame, fps, frame_size, writers):
    if key == ESC_KEY:
        return False

    if key == CTRL_Z_KEY:
        save_frame(frame)

    elif key == CTRL_X_KEY:
        if writers:
            print('이미 녹화 중입니다.')
            return True

        base_name = make_timestamp()
        writers.extend(create_video_writers(base_name, fps, frame_size))

        if not writers:
            print('녹화를 시작하지 못했습니다.')

    elif key == CTRL_C_KEY:
        if writers:
            release_video_writers(writers)
        else:
            print('현재 녹화 중이 아닙니다.')

    return True


def play_video_with_shortcuts(video_path):
    make_directories()

    capture = cv2.VideoCapture(str(video_path))

    if not capture.isOpened():
        print(f'동영상을 열 수 없습니다: {video_path}')
        return

    fps = get_video_fps(capture)
    writers = []
    window_name = 'video shortcut control'

    try:
        while True:
            is_read, frame = capture.read()

            if not is_read:
                break

            frame_size = get_frame_size(frame)

            if writers:
                for writer in writers:
                    writer.write(frame)

            cv2.imshow(window_name, frame)

            key = cv2.waitKey(WAIT_TIME) & 0xFF

            if key != 255:
                should_continue = handle_key(
                    key,
                    frame,
                    fps,
                    frame_size,
                    writers,
                )

                if not should_continue:
                    break

    except KeyboardInterrupt:
        print('프로그램이 강제로 종료되었습니다.')

    finally:
        if writers:
            release_video_writers(writers)

        capture.release()
        cv2.destroyAllWindows()


def main():
    play_video_with_shortcuts(VIDEO_PATH)


if __name__ == '__main__':
    main()