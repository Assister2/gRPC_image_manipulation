import cv2
import numpy as np

def mean_filter_color(image, kernel_size):
    # Splitting the image into color channels
    b, g, r = cv2.split(image)

    # Applying mean filter on each color channel
    b_filtered = cv2.blur(b, (kernel_size, kernel_size))
    g_filtered = cv2.blur(g, (kernel_size, kernel_size))
    r_filtered = cv2.blur(r, (kernel_size, kernel_size))

    # Merging the filtered color channels back into a single image
    filtered_image = cv2.merge((b_filtered, g_filtered, r_filtered))
    
    return filtered_image

# Reading the color image
image = cv2.imread('input_image.jpg')

# Applying the mean filter with kernel size 3
filtered_image = mean_filter_color(image, 3)

# Displaying the original and filtered images
cv2.imshow('Original Image', image)
cv2.imshow('Filtered Image', filtered_image)
cv2.waitKey(0)
cv2.destroyAllWindows()