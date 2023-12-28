import grpc
from concurrent import futures
import image_pb2
import image_pb2_grpc
import cv2
import numpy as np

class ImageProcessingServicer(image_pb2_grpc.ImageServerServicer):
    def image_rotation(self, request, context):
        # Check if the received message is a valid image
        if not isinstance(request.image, image_pb2.sample_image):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid request. Expected an image.")

        # Convert the image data to a NumPy array
        image_data = np.frombuffer(request.image.data, dtype=np.uint8)

        # Decode the image using cv2.imdecode()
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        # Rotate the image based on the requested rotation
        if request.rotation == image_pb2.rotate_image.NONE:
            rotated_image = image
        elif request.rotation == image_pb2.rotate_image.NINETY_DEG:
            rotated_image = np.rot90(image, k=1)
        elif request.rotation == image_pb2.rotate_image.ONE_EIGHT_DEG:
            rotated_image = np.rot90(image, k=2)
        elif request.rotation == image_pb2.rotate_image.TWO_SEVENTY_DEG:
            rotated_image = np.rot90(image, k=3)

        # Convert the rotated image back to a byte array
        _, encoded_image = cv2.imencode('.jpg', rotated_image)
        encoded_image_data = encoded_image.tobytes()

        # Create a response message with the rotated image
        response = image_pb2.sample_image(
            color=True,
            data=encoded_image_data,
            width=rotated_image.shape[1],
            height=rotated_image.shape[0]
        )

        return response

    def apply_filter(self, request, context):
        # Check if the received message is a valid image
        if not isinstance(request, image_pb2.sample_image):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid request. Expected an image.")

        # Apply mean filter to the image
        # Add your mean filtering logic here

        # Create a response message with the filtered image
        response = image_pb2.sample_image(
            color=request.color,
            data=request.data,
            width=request.width,
            height=request.height
        )

        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_pb2_grpc.add_ImageServerServicer_to_server(ImageProcessingServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()