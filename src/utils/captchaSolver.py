import base64, cv2
import matplotlib.pyplot as plt
import numpy as np
from scipy import ndimage
import matplotlib.patches as patches
from PIL import Image

def read_base64(uri):
   # encoded_data = uri.split(',')[1]
   nparr = np.fromstring(base64.b64decode(uri), np.uint8)
   img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   return img

def read_bytes(img_bytes, flags: int = cv2.IMREAD_COLOR):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img_np = cv2.imdecode(nparr, flags)
    return img_np


def find_image_in_captcha(captcha, images, is_testing: bool = False, method: int = cv2.TM_CCOEFF_NORMED, color_threshold: int = 210):
    # img_rm_bg = cv2.imread(captcha_path)
    img_rm_bg = read_bytes(captcha)
    img_rm_bg[img_rm_bg != 255] = 0
    if is_testing:
        cv2.imwrite("img_removed_bg.png", img_rm_bg)
    img_rm_bg_gray = cv2.cvtColor(img_rm_bg, cv2.COLOR_BGR2GRAY)
    if is_testing:
        cv2.imwrite("img_removed_bg_gray.png", img_rm_bg_gray)

    icons_rect_coordinates = find_bounding_box(img_rm_bg_gray, (20, 20), (200, 200), sort=False)
    icons = segment_pictures(img_rm_bg_gray, icons_rect_coordinates, (48, 48))
    if is_testing:
        draw_bounding_box(img_rm_bg_gray, icons_rect_coordinates, is_testing)

    targets = prepare_target_icons(images, is_testing)

    similarity_matrix = create_similarity_matrix(targets, icons)

    mapping = create_similarity_mapping(targets, icons, similarity_matrix)

    if is_testing:
        fig, ax = plt.subplots(1)
        ax.imshow(img_rm_bg_gray)
        draw_circles_around_targets(mapping, icons_rect_coordinates, ax)
        plt.savefig("result.png")
    return targets, icons_rect_coordinates, mapping


def prepare_target_icons(images, is_testing):
    targets = []
    for idx, image_path in enumerate(images):
        template_gray = read_bytes(image_path, cv2.IMREAD_UNCHANGED)
        # template_gray = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
        if template_gray.shape[2] == 4:  # we have an alpha channel
            a1 = ~template_gray[:, :, 3]  # extract and invert that alpha
            template_gray = cv2.add(cv2.merge([a1, a1, a1, a1]), template_gray)  # add up values (with clipping)
            template_gray = cv2.cvtColor(template_gray, cv2.COLOR_RGBA2RGB)  # strip alpha channel
            template_gray = cv2.cvtColor(template_gray, cv2.COLOR_RGB2GRAY)
        template_name = f"target_{idx + 1}"
        if is_testing:
            cv2.imwrite(f"{template_name}.png", template_gray)
        # template_gray_2 = cv2.imread(f"{template_name}.png", 0)
        template_gray_inv = cv2.bitwise_not(template_gray)
        if is_testing:
            cv2.imwrite(f"{template_name}_inv.png", template_gray_inv)
        targets.append(template_gray_inv)

    return targets


def create_similarity_matrix(targets, icons):
    similarity_matrix = []
    for target in targets:
        similarity_per_target = []
        for icon in icons:
            similarity_per_target.append(calculate_max_matching(target, icon, 1))
        similarity_matrix.append(similarity_per_target)
    return similarity_matrix


def create_similarity_mapping(targets, icons, similarity_matrix):
    # Calculate Mapping
    target_candidates = [False for _ in range(len(targets))]
    icon_candidates = [False for _ in range(len(icons))]

    mapping = {}

    # Sort the flatted similarity matrix in descending order, and assign the pair between target and icon if both of them
    # haven't been assigned.
    arr = np.array(similarity_matrix).flatten()
    arg_sorted = np.argsort(-arr)

    for e in arg_sorted:
        col = e // len(icons)
        row = e % len(icons)

        if target_candidates[col] is False and icon_candidates[row] is False:
            target_candidates[col], icon_candidates[row] = True, True
            mapping[col] = row

    return mapping


def draw_circles_around_targets(mapping, icons_rect_coordinates, ax):
    # Circling the most similar icon,
    # blue circle: first target
    # red circle: second target
    # yellow circle: third target
    # green circle: fourth target
    color_map = {1: 'b', 2: 'r', 3: 'y', 4: 'g'}
    for key in mapping:
        x, y, w, h = icons_rect_coordinates[mapping[key]]

        # x,y is the coordinate of top left hand corner
        # Bounding box is 70x70, so centre of circle = (x+70/2, y+70/2), i.e. (x+35, y+35)
        centre_x = x + (w // 2)
        centre_y = y + (h // 2)
        # Plot circle
        circle = plt.Circle((centre_x, centre_y), 20, color=color_map[key + 1], fill=False, linewidth=5)
        # Plot centre
        plt.plot([centre_x], [centre_y], marker='o', markersize=10, color="white")
        plt.text(centre_x, centre_y, key + 1, fontsize=10)
        ax.add_patch(circle)


# Rotate the icon by d degree each time and calculate the similarity between icon and target
def calculate_max_matching(target, icon, d):
    largest_val = 0
    for degree in range(0, 360, d):
        tmp = ndimage.rotate(target, degree, reshape=False)
        res = cv2.matchTemplate(icon, tmp, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > largest_val:
            largest_val = max_val
    return largest_val

def draw_bounding_box(pane, rect_coordinates, is_testing: bool):
    # Show bounding boxes

    # Create figure and axes
    fig, ax = plt.subplots(1)

    # Display the image
    ax.imshow(pane)

    # Create a Rectangle patch
    for e in rect_coordinates:
        (x, y, w, h) = e
        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

    if is_testing:
        plt.savefig("bounding_box.png")


def find_bounding_box(pane, bounding_box_lower_thresholds, bounding_box_upper_thresholds, sort=True):
    # thresholds: turple
    # dimension_resized: turple

    segmented_pictures = []
    rect_coordinates = []

    width_lower_threshold, height_lower_threshold = bounding_box_lower_thresholds
    width_upper_threshold, height_upper_threshold = bounding_box_upper_thresholds

    contours, hierarchy = cv2.findContours(pane, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    pane_copy = pane.copy()
    cv2.drawContours(pane_copy, contours, -1, (255, 0, 0), 3)
    cv2.imwrite("captcha_contours.png", pane_copy)

    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour)
        if h > height_lower_threshold and w > width_lower_threshold and h <= height_upper_threshold and w <= width_upper_threshold:
            rect_coordinates.append((x, y, w, h))

        else:
            continue
    if sort:
        x_coordinates = [x for (x, y, w, h) in rect_coordinates]
        rect_coordinates = [e for _, e in sorted(zip(x_coordinates, rect_coordinates))]
    return rect_coordinates


def segment_pictures(pane, rect_coordinates, dimension_resized, offset=2):
    segmented_pictures = []
    box_resized_width, box_resized_height = dimension_resized
    for rec_coordinate in rect_coordinates:
        (x, y, w, h) = rec_coordinate
        resized_pic = np.asarray(
            Image.fromarray(pane[max(0, y - offset):y + h + offset, max(0, x - offset):x + w + offset]).resize((box_resized_width, box_resized_height)))

        # if
        segmented_pictures.append(resized_pic)
    return segmented_pictures
