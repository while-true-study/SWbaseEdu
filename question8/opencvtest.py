import cv2
import numpy as np
import matplotlib.pyplot as plt


IMAGE_PATH = 'sample.jpg'
PEOPLE_IMAGE_PATH = 'people.jpg'
OBJECT_IMAGE_PATH = 'objects.jpg'


def show_image(title, image):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def load_image(image_path):
    image = cv2.imread(image_path)

    if image is None:
        raise FileNotFoundError(f'이미지를 찾을 수 없습니다: {image_path}')

    return image


def task_1_flip_rotate():
    image = load_image(IMAGE_PATH)

    show_image('Original Image', image)

    vertical_flip = cv2.flip(image, 0)
    show_image('Vertical Flip', vertical_flip)

    horizontal_flip = cv2.flip(image, 1)
    show_image('Horizontal Flip', horizontal_flip)

    rotate_90 = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    show_image('Rotate 90 Clockwise', rotate_90)

    rotate_180 = cv2.rotate(image, cv2.ROTATE_180)
    show_image('Rotate 180', rotate_180)

    up_sampled = cv2.pyrUp(image)
    show_image('Up Sampled 2x', up_sampled)


def task_2_resize_scale_crop():
    image = load_image(IMAGE_PATH)

    resized_640_480 = cv2.resize(image, (640, 480))
    show_image('Resize 640x480', resized_640_480)

    resized_1024_768 = cv2.resize(image, (1024, 768))
    show_image('Resize 1024x768', resized_1024_768)

    scaled_image = cv2.resize(image, None, fx=0.3, fy=0.7)
    show_image('Scale fx 0.3 fy 0.7', scaled_image)

    height, width = image.shape[:2]

    start_x = width // 4
    end_x = width * 3 // 4
    start_y = height // 4
    end_y = height * 3 // 4

    cropped_image = image[start_y:end_y, start_x:end_x].copy()
    show_image('Cropped Deep Copy', cropped_image)


def task_2_bonus_crop_people():
    image = load_image(PEOPLE_IMAGE_PATH)

    people_regions = [
        (50, 50, 150, 250),
        (200, 60, 300, 260),
        (350, 70, 450, 270),
    ]

    for index, region in enumerate(people_regions):
        x1, y1, x2, y2 = region
        person = image[y1:y2, x1:x2].copy()
        show_image(f'Person {index + 1}', person)


def task_3_color_inverse():
    image = load_image(IMAGE_PATH)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    show_image('Gray Image', gray_image)

    inverse_image = 255 - image
    show_image('Inverse Image', inverse_image)

    show_histogram(image, 'Original Histogram')
    show_histogram(inverse_image, 'Inverse Histogram')


def show_histogram(image, title):
    color_channels = ('b', 'g', 'r')

    plt.figure()
    plt.title(title)
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')

    for channel_index, color in enumerate(color_channels):
        histogram = cv2.calcHist(
            [image],
            [channel_index],
            None,
            [256],
            [0, 256],
        )
        plt.plot(histogram, color=color)

    plt.xlim([0, 256])
    plt.show()


def task_4_binary_edge_blur():
    image = load_image(IMAGE_PATH)

    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    _, binary_image = cv2.threshold(
        gray_image,
        127,
        255,
        cv2.THRESH_BINARY,
    )
    show_image('Binary Image', binary_image)

    sobel_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
    sobel_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
    sobel_image = cv2.magnitude(sobel_x, sobel_y)
    sobel_image = cv2.convertScaleAbs(sobel_image)
    show_image('Sobel Edge', sobel_image)

    laplacian_image = cv2.Laplacian(gray_image, cv2.CV_64F)
    laplacian_image = cv2.convertScaleAbs(laplacian_image)
    show_image('Laplacian Edge', laplacian_image)

    canny_image = cv2.Canny(gray_image, 100, 200)
    show_image('Canny Edge', canny_image)

    blur_image = cv2.GaussianBlur(image, (15, 15), 0)
    show_image('Gaussian Blur', blur_image)

    partial_blur_image = image.copy()
    height, width = image.shape[:2]

    x1 = width // 4
    x2 = width * 3 // 4
    y1 = height // 4
    y2 = height * 3 // 4

    target_area = partial_blur_image[y1:y2, x1:x2]
    blurred_area = cv2.GaussianBlur(target_area, (31, 31), 0)
    partial_blur_image[y1:y2, x1:x2] = blurred_area

    show_image('Partial Blur', partial_blur_image)


def task_5_hsv_channel():
    image = load_image(IMAGE_PATH)

    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    h_channel, s_channel, v_channel = cv2.split(hsv_image)

    show_image('H Channel', h_channel)
    show_image('S Channel', s_channel)
    show_image('V Channel', v_channel)

    b_channel, g_channel, r_channel = cv2.split(image)

    show_image('B Channel', b_channel)
    show_image('G Channel', g_channel)
    show_image('R Channel', r_channel)


def task_6_object_labeling():
    image = load_image(OBJECT_IMAGE_PATH)

    objects = [
        {
            'name': 'Object 1',
            'type': 'box',
            'box': (50, 80, 180, 220),
        },
        {
            'name': 'Object 2',
            'type': 'circle',
            'box': (230, 100, 360, 230),
        },
        {
            'name': 'Object 3',
            'type': 'triangle',
            'box': (400, 120, 530, 260),
        },
    ]

    for item in objects:
        name = item['name']
        object_type = item['type']
        x1, y1, x2, y2 = item['box']

        if object_type == 'box':
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

        elif object_type == 'circle':
            center_x = (x1 + x2) // 2
            center_y = (y1 + y2) // 2
            radius = min(x2 - x1, y2 - y1) // 2
            cv2.circle(image, (center_x, center_y), radius, (0, 0, 255), 2)

        elif object_type == 'triangle':
            points = np.array(
                [
                    [(x1 + x2) // 2, y1],
                    [x1, y2],
                    [x2, y2],
                ],
                np.int32,
            )
            cv2.polylines(image, [points], True, (0, 0, 255), 2)

        text_x = x1
        text_y = y1 - 30

        cv2.putText(
            image,
            name,
            (text_x, text_y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 0, 255),
            2,
        )

        cv2.line(
            image,
            (text_x, text_y + 10),
            (x1, y1),
            (0, 0, 255),
            2,
        )

    show_image('Object Labeling', image)


def main():
    task_1_flip_rotate()
    task_2_resize_scale_crop()
    task_2_bonus_crop_people()
    task_3_color_inverse()
    task_4_binary_edge_blur()
    task_5_hsv_channel()
    task_6_object_labeling()


if __name__ == '__main__':
    main()