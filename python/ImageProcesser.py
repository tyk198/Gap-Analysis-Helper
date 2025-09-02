import numpy as np
import cv2
import os
from typing import Union, List, Optional
import logging
import tkinter as tk

class ImageProcesser:
    def __init__(self, data):
        """
        Initialize the ImageProcesser with data and settings.
        
        Args:
            data: The data to process
            settings: ImageProcesserSettings containing processing configuration
            raw_image_folder_path: Path to raw images provided by owner class
        """
        
    
    @staticmethod
    def _read_image(file_path: Union[str, List[str]]) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Reads an image or up to 5 images from the specified path(s) using OpenCV.

        Images are read in BGR color format and returned as numpy arrays. If a list of paths
        is provided with more than 5 images, only the first 5 are read.

        Parameters:
            file_path (str | List[str]): A single path to an image or a list of paths.

        Returns:
            np.ndarray | List[np.ndarray]: The loaded image or a list of up to 5 loaded images in numpy format.

        Raises:
            ValueError: If any image fails to load.
            TypeError: If file_path is neither a string nor a list of strings.
        """
        if isinstance(file_path, str):
            img = cv2.imread(file_path)
            if img is None:
                raise ValueError(f"Failed to load image from {file_path}")
            return img
        elif isinstance(file_path, list):
            # Limit to first 5 paths if more are provided
            paths_to_read = file_path[:4]
            images = [cv2.imread(path) for path in paths_to_read]
            if any(img is None for img in images):
                raise ValueError("Failed to load one or more images from the provided paths")
            return images
        else:
            raise TypeError("file_path must be a string or a list of strings")

    @staticmethod
    def _combine_image(*images: 'np.ndarray', direction: str = "vertical") -> Optional['np.ndarray']:
        """
        Combines a sequence of images either vertically or horizontally.
        If images have different dimensions, it adds black padding to align them:
        - For vertical combination, pads shorter widths to match the widest image.
        - For horizontal combination, pads shorter heights to match the tallest image.
        All images are converted to 3-channel BGR if they are not already.

        Args:
            *images: A variable number of cv2 images (as numpy arrays).
            direction (str): Direction to combine images ("vertical" or "horizontal"). Default is "vertical".

        Returns:
            np.ndarray: A single combined cv2 image, or None if no valid images are provided.

        Raises:
            ValueError: If direction is not "vertical" or "horizontal", or if any input is not a valid numpy array.
        """
        logging.info(f"Combining {len(images)} images in {direction} direction")


        if direction not in ["vertical", "horizontal"]:
            logging.error(f"Invalid direction: {direction}. Must be 'vertical' or 'horizontal'.")
            raise ValueError("Direction must be 'vertical' or 'horizontal'.")

        max_width = 0
        max_height = 0
        processed_for_size_check = []
        for i, img in enumerate(images):
            if img is None:
                logging.warning(f"Image {i+1} is None and will be skipped.")
                continue
            if not isinstance(img, np.ndarray):
                logging.error(f"Image {i+1} is not a numpy array, got type: {type(img)}")
                raise ValueError(f"Image {i+1} must be a numpy array, got {type(img)}")
            if img.ndim == 2:
                img_3ch = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.ndim == 3 and img.shape[2] == 1:
                img_3ch = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.ndim == 3 and img.shape[2] == 3:
                img_3ch = img
            else:
                logging.error(f"Image {i+1} has an unsupported shape: {img.shape}")
                raise ValueError(f"Image {i+1} has an unsupported shape: {img.shape}")
            processed_for_size_check.append(img_3ch)
            if direction == "vertical":
                if img_3ch.shape[1] > max_width:
                    max_width = img_3ch.shape[1]
            else:  # horizontal
                if img_3ch.shape[0] > max_height:
                    max_height = img_3ch.shape[0]

        if not processed_for_size_check:
            logging.error("No valid images left to combine after validation.")
            return None

        # Pad images to match max width (for vertical) or max height (for horizontal)
        padded_images = []
        for i, img in enumerate(processed_for_size_check):
            h, w, _ = img.shape
            if direction == "vertical":
                if w < max_width:
                    padding = max_width - w
                    padded_img = cv2.copyMakeBorder(img, 0, 0, 0, padding, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                    logging.info(f"Padded image {i+1} with {padding} pixels to match max width {max_width}.")
                    padded_images.append(padded_img)
                else:
                    padded_images.append(img)
            else:  # horizontal
                if h < max_height:
                    padding = max_height - h
                    padded_img = cv2.copyMakeBorder(img, 0, padding, 0, 0, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                    logging.info(f"Padded image {i+1} with {padding} pixels to match max height {max_height}.")
                    padded_images.append(padded_img)
                else:
                    padded_images.append(img)

        # Stack images based on direction
        if direction == "vertical":
            combined_image = np.vstack(padded_images)
            logging.info(f"Successfully combined {len(padded_images)} images vertically. Combined shape: {combined_image.shape}")
        else:  # horizontal
            combined_image = np.hstack(padded_images)
            logging.info(f"Successfully combined {len(padded_images)} images horizontally. Combined shape: {combined_image.shape}")

        logging.info("Finished image combination.")
        return combined_image
    
    @staticmethod
    def _resize_keep_aspect(image, target_width=None):
        """
        Resize an image to a target width while keeping aspect ratio.

        :param image: Input image (OpenCV BGR format)
        :param target_width: Desired width in pixels (if None, defaults to 50% of screen width)
        :return: Resized image
        """
        # Get screen width if no target_width is given
        if target_width is None:
            root = tk.Tk()
            screen_width = root.winfo_screenwidth()
            root.destroy()
            target_width = int(screen_width * 0.5)  # Default 50% of screen width

        # Original dimensions
        orig_height, orig_width = image.shape[:2]

        # Calculate scale factor
        scale = target_width / orig_width

        # New height (keep aspect ratio)
        target_height = int(orig_height * scale)

        # Resize
        resized_image = cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_AREA)
        return resized_image
    
    @staticmethod
    def _overlay_text(text, image, position="top-left"):
        """
        Overlay text on an image with resolution-independent scaling.
        
        Args:
            text (str): Text to overlay (use \n for multiple lines).
            image (numpy.ndarray): Input OpenCV image.
            position (str): Where to put the text: "top-left", "top-right",
                            "bottom-left", or "bottom-right".
        
        Returns:
            numpy.ndarray: Image with text overlay.
        """
        img = image.copy()
        h, w = img.shape[:2]

        # Font scaling relative to image height
        font_scale = h / 600  # adjust base number if text too big/small
        thickness = max(1, int(font_scale * 2))
        font = cv2.FONT_HERSHEY_SIMPLEX

        # Padding from edges (relative to resolution)
        pad_x = int(w * 0.02)
        pad_y = int(h * 0.04)

        # Split into lines for multi-line text
        lines = text.split("\n")

        # Estimate line height
        line_height = int(cv2.getTextSize("Ag", font, font_scale, thickness)[0][1] * 1.5)

        # Determine starting coordinates based on position
        if position == "top-left":
            x, y = pad_x, pad_y
        elif position == "top-right":
            # For right alignment, shift x per line length
            max_line_width = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines)
            x, y = w - max_line_width - pad_x, pad_y
        elif position == "bottom-left":
            x, y = pad_x, h - pad_y - (line_height * (len(lines) - 1))
        elif position == "bottom-right":
            max_line_width = max(cv2.getTextSize(line, font, font_scale, thickness)[0][0] for line in lines)
            x, y = w - max_line_width - pad_x, h - pad_y - (line_height * (len(lines) - 1))
        else:
            raise ValueError("Invalid position. Choose from: top-left, top-right, bottom-left, bottom-right.")

        # Draw each line of text
        for i, line in enumerate(lines):
            y_line = y + (i * line_height)
            cv2.putText(img, line, (x, y_line), font, font_scale, (255, 0, 0), thickness, lineType=cv2.LINE_AA)

        return img


    @staticmethod
    def _crop_image_base_on_coordinate(
        image_input: Union[np.ndarray, List[np.ndarray]],
        x: float,
        y: float,
        FMsize: float
    ) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Crops a square region from an image or a list of images.

        Accepts either a single image or a list of images and applies the same
        cropping coordinates and size to all of them.

        Args:
            image_input (Union[np.ndarray, List[np.ndarray]]): A single OpenCV image
                or a list of OpenCV images (H x W x C).
            x (float): X coordinate for the center of the crop (left → right).
            y (float): Y coordinate for the center of the crop (top → bottom).
            FMsize (float): The desired width and height of the crop in pixels.

        Returns:
            Union[np.ndarray, List[np.ndarray]]: The cropped image or a list of
                cropped images, matching the input type.
        """
        # --- Define the core cropping logic for a single image ---
        def crop_single_image(image: np.ndarray) -> np.ndarray:
            # Ensure values are float for calculations
            _x = float(x)
            _y = float(y)
            _FMsize = float(FMsize)
            h, w = image.shape[:2]
            half = _FMsize 

            # Calculate initial bounds, rounding to nearest integer
            x1 = max(0, int(round(_x - half)))
            y1 = max(0, int(round(_y - half)))
            x2 = min(w, int(round(_x + half)))
            y2 = min(h, int(round(_y + half)))

            # Adjust bounds if the crop size is smaller than FMsize due to image edges
            target_size = int(round(_FMsize))
            if x2 - x1 < target_size:
                if x1 == 0:
                    x2 = min(w, target_size)  # Adjust right edge
                elif x2 == w:
                    x1 = max(0, w - target_size)  # Adjust left edge

            if y2 - y1 < target_size:
                if y1 == 0:
                    y2 = min(h, target_size)  # Adjust bottom edge
                elif y2 == h:
                    y1 = max(0, h - target_size)  # Adjust top edge
            
            return image[y1:y2, x1:x2]

        # --- Check input type and apply the logic accordingly ---
        if isinstance(image_input, list):
            # If the input is a list, apply the crop function to each image
            return [crop_single_image(img) for img in image_input]
        else:
            # If the input is a single image, process it directly
            return crop_single_image(image_input)

    @staticmethod
    def _combine_image_grid(*images: 'np.ndarray') -> Optional['np.ndarray']:
        """
        Combines up to 6 images into a 2x3 grid. If fewer than 6 images are provided, or if any input is None,
        the corresponding position is filled with a black image.
        Grid layout:
            Row 1: Image 1, Image 2, Image 3
            Row 2: Image 4, Image 5, Image 6
        Images are padded with black to align dimensions to the widest width and tallest height among all valid images.
        All images are converted to 3-channel BGR if they are not already.

        Args:
            *images: Up to 6 cv2 images (as numpy arrays). None inputs are replaced with black images.

        Returns:
            np.ndarray: A single combined cv2 image in a 2x3 grid, or None if no valid images are provided and no black images are needed.

        Raises:
            ValueError: If more than 6 images are provided, or if any non-None input is not a valid numpy array.
        """
        logging.info(f"Combining up to 6 images into a 2x3 grid, received {len(images)} images")

        # Validate number of images
        if len(images) > 6:
            logging.error(f"Expected up to 6 images, got {len(images)}")
            raise ValueError("Up to 6 images can be provided")

        # Validate inputs and convert to 3-channel BGR, find max width and height
        max_width = 0
        max_height = 0
        processed_images = []
        for i, img in enumerate(images[:6]):  # Process only up to 6 images
            if img is None:
                logging.info(f"Image {i+1} is None, will be replaced with a black image")
                processed_images.append(None)
                continue
            if not isinstance(img, np.ndarray):
                logging.error(f"Image {i+1} is not a numpy array, got type: {type(img)}")
                raise ValueError(f"Image {i+1} must be a numpy array, got {type(img)}")
            if img.ndim == 2:
                img_3ch = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.ndim == 3 and img.shape[2] == 1:
                img_3ch = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            elif img.ndim == 3 and img.shape[2] == 3:
                img_3ch = img
            else:
                logging.error(f"Image {i+1} has an unsupported shape: {img.shape}")
                raise ValueError(f"Image {i+1} has an unsupported shape: {img.shape}")
            processed_images.append(img_3ch)
            max_width = max(max_width, img_3ch.shape[1])
            max_height = max(max_height, img_3ch.shape[0])

        # If fewer than 6 images, fill remaining positions with None (for black images)
        while len(processed_images) < 6:
            logging.info(f"Filling position {len(processed_images)+1} with a black image (fewer than 6 images provided)")
            processed_images.append(None)

        # If no valid images were provided, return None
        if all(img is None for img in processed_images):
            logging.error("No valid images provided to combine")
            return None

        # Pad images to match max width and max height, or create black images
        padded_images = []
        for i, img in enumerate(processed_images):
            if img is None:
                black_image = np.zeros((max_height, max_width, 3), dtype=np.uint8)
                logging.info(f"Created black image for position {i+1} with shape: {black_image.shape}")
                padded_images.append(black_image)
            else:
                h, w, _ = img.shape
                pad_right = max_width - w
                pad_bottom = max_height - h
                if pad_right > 0 or pad_bottom > 0:
                    padded_img = cv2.copyMakeBorder(img, 0, pad_bottom, 0, pad_right, cv2.BORDER_CONSTANT, value=[0, 0, 0])
                    logging.info(f"Padded image {i+1} with {pad_right} right and {pad_bottom} bottom pixels")
                    padded_images.append(padded_img)
                else:
                    padded_images.append(img)

        # Arrange images in 2x3 grid
        row1 = np.hstack([padded_images[0], padded_images[1], padded_images[2]])
        row2 = np.hstack([padded_images[3], padded_images[4], padded_images[5]])
        combined_image = np.vstack([row1, row2])
        logging.info(f"Successfully combined images into 2x3 grid. Combined shape: {combined_image.shape}")

        logging.info("Finished grid image combination")
        return combined_image

    @staticmethod
    def _save_image_to_folder(save_folder, plot_image, title):
        """
        Saves a plot image to a specified folder with a dynamically generated filename.

        Args:
            save_folder (str): The path to the directory where the image will be saved.
            plot_image (numpy.ndarray): The image array to save (in BGR format).
            name_filter (str): The name used to generate the plot.
            state_filter (str): The state used to generate the plot (e.g., "BeforeFinalTest").
            top_bottom_filter (list): The top/bottom filter list used (e.g., ["top", "bottom"]).
        """

        os.makedirs(save_folder, exist_ok=True)
        filename = f"{title}.png"
        full_path = os.path.join(save_folder, filename)
        cv2.imwrite(full_path, plot_image)
        print(f" Image successfully saved to: {full_path}")

    @staticmethod
    def _show_image(image: 'np.ndarray', window_name: str = "Image Display", wait_time: int = 0, scale_resize = 1) -> None:
        """
        Displays a cv2 image on screen, centered and scaled appropriately.
        The window is closed upon any key press, mouse click, or timeout.

        Parameters:
            image (np.ndarray): The image to display as a numpy array (cv2 format).
            window_name (str): The name of the window to display the image (default: "Image Display").
            wait_time (int): Time to wait in milliseconds. 0 means wait indefinitely for user input (default: 0).

        Returns:
            None

        Raises:
            ValueError: If the input image is not a valid numpy array.
        """
        logging.info(f"Preparing to display image in window: {window_name}")
        if not isinstance(image, np.ndarray) or image.ndim not in [2, 3]:
            msg = "Input must be a 2D or 3D numpy array representing an image."
            logging.error(msg)
            raise ValueError(msg)

        try:
            # --- DYNAMIC SCREEN SIZE DETECTION ---
            root = tk.Tk()
            root.withdraw()
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()
            root.destroy()

            img_height, img_width = image.shape[:2]

            # --- IMPROVED SCALING LOGIC ---
            max_win_width = int(screen_width * 0.9)
            max_win_height = int(screen_height * 0.9)
            scale = min(max_win_width / img_width, max_win_height / img_height)
            if scale < 1.0:
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
            else:
                new_width = img_width * scale_resize
                new_height = img_height * scale_resize

            # --- CENTERING CALCULATION ---
            window_x = (screen_width - new_width) // 2
            window_y = (screen_height - new_height) // 2

            #window_x = window_x * 5
            #window_y = window_y * 5

            # --- WINDOW CREATION AND DISPLAY ---
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.moveWindow(window_name, window_x, window_y)
            cv2.resizeWindow(window_name, new_width, new_height)
            cv2.imshow(window_name, image)

            # --- SIMPLIFIED WAIT LOGIC ---
            mouse_clicked = False
            def mouse_callback(event, x, y, flags, param):
                nonlocal mouse_clicked
                if event == cv2.EVENT_LBUTTONDOWN:  # Left click - continue
                    mouse_clicked = True
                elif event == cv2.EVENT_RBUTTONDOWN:  # Right click - mark to exit
                    logging.info("Right-click detected. Will exit after processing.")
                    nonlocal exit_program
                    exit_program = True

            cv2.setMouseCallback(window_name, mouse_callback)

            # Flag to handle right-click exit
            exit_program = False

            # Wait for a key press, mouse click, or timeout
            if wait_time > 0:
                end_time = cv2.getTickCount() + (wait_time / 1000.0) * cv2.getTickFrequency()
                while cv2.getTickCount() < end_time:
                    if cv2.waitKey(1) != -1 or mouse_clicked:
                        break
            else:
                while True:
                    if cv2.waitKey(1) != -1 or mouse_clicked:
                        break

            logging.info(f"Closing window: {window_name}")

            if exit_program:
                logging.info("Exiting program due to right-click.")
                import sys
                sys.exit(0)

        finally:
            # Only destroy the window if it exists
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) >= 1:
                cv2.destroyWindow(window_name)

    @staticmethod
    def _match_white_red_image(state: str, foil: str, fov_number: int, raw_image_folder_path: str):
        """
        Matches white and red images based on state, foil, and FOV number in the specified folder structure, searching recursively.
        
        Args:
            state (str): The state name (subfolder under raw_image_folder_path).
            foil (str): The foil name (subfolder under state folder).
            fov_number ( int): The FOV number to match in the filename.
            raw_image_folder_path (str): The base path to the image folder.
        
        Returns:
            tuple: (white_image_path, red_image_path) or (None, None) if no match is found.
        """
        import os
        import glob

        # Sanitize inputs
        state = str(state).strip()
        foil = str(foil).strip()
        fov_number = int(fov_number)
        
        # Construct the expected folder path
        target_folder = os.path.join(raw_image_folder_path, state, foil)
        
        # Check if the target folder exists
        if not os.path.exists(target_folder):
            return None, None
        
        # Get all .jpeg files in the target folder recursively
        candidate_files = [f for f in glob.glob(os.path.join(target_folder, "**", "*.jpeg"), recursive=True)]
        
        found_white_path = None
        found_red_path = None
        
        # Iterate through files to find matching white and red images
        for file_path in candidate_files:
            filename = os.path.basename(file_path)
            try:
                # Extract FOV number from filename (assuming it's the last part before extension)
                stem = os.path.splitext(filename)[0]
                file_fov = int(stem.split('_')[-1])
                
                # Check if FOV number matches
                if file_fov != fov_number:
                    continue
                
                # Check image type (assuming '01' for white, '02' for red)
                filename_parts = filename.split('_')
                if len(filename_parts) > 2:
                    type_identifier = filename_parts[2]
                    if type_identifier == '01':
                        found_white_path = file_path
                    elif type_identifier == '02':
                        found_red_path = file_path
            except (ValueError, IndexError):
                continue
        
        return found_white_path, found_red_path

    @staticmethod
    def _match_all_name_white_images(state, fov,raw_image_folder_path: str) -> List[str]:
        """
        Finds all 'white' image file paths (type '01') that match a given
        IMAGE ID and FOV NUMBER.

        This function is guaranteed to only return paths for white images by performing three checks:
        1. The 'IMAGE ID' from the row must be present in the full file path.
        2. The 'FOV NUMBER' from the row must match the number at the end of the filename.
        3. The filename must contain the type identifier '01' as its third component
        when split by underscores (e.g., '..._..._01_...jpeg').

        Args:
            row (pd.Series): A pandas Series containing 'IMAGE ID' and 'FOV NUMBER'.
            raw_image_folder_path (str): The root path of the folder to search for images.

        Returns:
            List[str]: A list of all full file paths that match all three criteria.
                    Returns an empty list if no matches are found or if input is invalid.
        """

       # Walk the directory and collect files that pass all three checks.
        found_white_images = []
        for root, dirs, files in os.walk(raw_image_folder_path):
            for filename in files:
                # Basic file type check
                if not filename.lower().endswith('.jpeg'):
                    continue

                full_filepath = os.path.join(root, filename)

                # CHECK 1: The IMAGE ID must be in the path (based on your working function).
                if state not in full_filepath:
                    continue

                # CHECK 2: The FOV NUMBER must match the end of the filename.
                try:
                    stem = os.path.splitext(filename)[0]
                    file_fov = int(stem.split('_')[-1])
                    if file_fov != fov:
                        continue
                except (ValueError, IndexError):
                    # Skip if filename is not in the format ..._<number>.jpeg
                    continue

                # CHECK 3 (GUARANTEE): The file must be a 'white' image (type '01').
                filename_parts = filename.split('_')
                # The filename must have enough parts for an ID, and the third part must be '01'.
                if len(filename_parts) < 3 or filename_parts[2] != '01':
                    continue

                # --- End Matching Criteria ---

                # If a file passes all three checks, add it to the final list.
                found_white_images.append(full_filepath)
        return found_white_images
