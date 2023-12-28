import grpc
from concurrent import futures
from PIL import Image
import numpy as np
from io import BytesIO
from image_pb2 import RotateImage, SampleImage
from image_pb2_grpc import ImageServerServicer, add_ImageServerServicer_to_server
import cv2
import image_pb2


def apply_mean_filter(image_data):
    # Create a copy of the image data to store the filtered result
        filtered_image = image_data.copy()

        # Get the number of channels in the image (3 for color images, 1 for grayscale)
        num_channels = image_data.shape[2] if len(image_data.shape) == 3 else 1

        # Define the size of the neighborhood for calculating the mean
        neighborhood_size = 3  # You can adjust this value as needed

        # Iterate over each pixel in the image
        for i in range(image_data.shape[0]):
            for j in range(image_data.shape[1]):
                # Get the neighborhood surrounding the current pixel
                neighborhood = image_data[max(0, i - neighborhood_size):min(image_data.shape[0], i + neighborhood_size + 1),
                                    max(0, j - neighborhood_size):min(image_data.shape[1], j + neighborhood_size + 1)]

                # Calculate the mean for each channel separately (for color images)
                if num_channels == 3:
                    for channel in range(num_channels):
                        filtered_image[i, j, channel] = np.mean(neighborhood[:, :, channel])
                # Calculate the mean for grayscale images
                else:
                    filtered_image[i, j] = np.mean(neighborhood)

        return filtered_image

class ImageServerServicerImpl(ImageServerServicer):
    def ImageRotation(self, request, context):
        try:
            # Check if the request is valid and represents an image
            if not request.image.data :
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid image data")
            # Convert the image data to a PIL Image object
            image = Image.open(BytesIO(request.image.data))
            # Rotate the image based on the requested rotation
            if request.rotation == RotateImage.NONE:
                rotated_image = image
            elif request.rotation == RotateImage.NINETY_DEG:
                rotated_image = image.rotate(90)
            elif request.rotation == RotateImage.ONE_EIGHTY_DEG:
                rotated_image = image.rotate(180)
            elif request.rotation == RotateImage.TWO_SEVENTY_DEG:
                rotated_image = image.rotate(270)
            # Convert the rotated image back to bytes
            rotated_image_bytes = BytesIO()
            rotated_image.save(rotated_image_bytes, format='JPEG')
            rotated_image_data = rotated_image_bytes.getvalue()
            # Create the response protobuf message
            response = SampleImage(
                color=request.image.color,
                data=rotated_image_data,
                width=rotated_image.width,
                height=rotated_image.height
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, "Error processing")
        
        return response
   
    
    
    def ApplyFilter(self, request, context):
    #     # Check if the request is valid and represents an image
        try:
            if not request.data:
                context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid image data")
            image = Image.open(BytesIO(request.data))
            image_data = np.array(image)

            # Apply mean filter to the image
            filtered_image = np.zeros_like(image_data, dtype=np.float32)
            for i in range(image_data.shape[0]):
                for j in range(image_data.shape[1]):
                    if image_data.ndim == 3:  # Color image (RGB channels)
                        for k in range(image_data.shape[2]):
                            min_i = max(0, i-1)
                            max_i = min(image_data.shape[0]-1, i+1)
                            min_j = max(0, j-1)
                            max_j = min(image_data.shape[1]-1, j+1)
                            filtered_image[i, j, k] = np.mean(image_data[min_i:max_i+1, min_j:max_j+1, k])
                    else:  # Grayscale image
                        min_i = max(0, i-1)
                        max_i = min(image_data.shape[0]-1, i+1)
                        min_j = max(0, j-1)
                        max_j = min(image_data.shape[1]-1, j+1)
                        filtered_image[i, j] = np.mean(image_data[min_i:max_i+1, min_j:max_j+1])

            # Convert the filtered image to the appropriate data type
            filtered_image = filtered_image.astype(np.uint8)

            # Create a PIL image from the filtered image data
            pil_image = Image.fromarray(filtered_image)

            # Get the width and height of the filtered image
            width, height = pil_image.size

            # Convert the filtered image to bytes
            filtered_image_bytes = BytesIO()
            pil_image.save(filtered_image_bytes, format='JPEG')
            filtered_image_data = filtered_image_bytes.getvalue()

            # Create the response protobuf message
            response = SampleImage(
                color=request.color,
                data=filtered_image_data,
                width=width,
                height=height
            )
        except Exception as e:
            context.abort(grpc.StatusCode.INTERNAL, "Error Processing")
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_ImageServerServicer_to_server(ImageServerServicerImpl(), server)
    server.add_insecure_port('[::]:50051')  # Specify the server port
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
