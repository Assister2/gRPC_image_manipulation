import grpc
from concurrent import futures
import image_pb2
import image_pb2_grpc
from google.protobuf import empty_pb2
from PIL import Image
import numpy as np
import cv2
import io


class ImageServiceServicer(image_pb2_grpc.ImageServiceServicer):
    def SendImage(self, request, context):
        try:
            print("REQUEST IN SERVER", request)
            image_data = np.frombuffer(request, dtype=np.uint8)
            # image = cv2.imdecode(request)
            image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)
            print("REQUEST IN IMDECODE", image)
            if image is None:
                context.set_details("Invalid image format")
                context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                return empty_pb2.Empty()

            # Apply the median filter to the image
            filtered_image = cv2.medianBlur(image, 5)

            # Make the image smaller
            resized_image = cv2.resize(filtered_image, (0, 0), fx=0.5, fy=0.5)

            # Save the processed image
            cv2.imwrite("processed_image.jpeg", resized_image)
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return empty_pb2.Empty()

        return empty_pb2.Empty()

    def GetImage(self, request, context):
        try:
            # Read the processed image
            image = cv2.imread("processed_image.jpeg", cv2.IMREAD_COLOR)
            if image is None:
                context.set_details("Processed image not found")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return

            # Stream the image to the client
            yield image_pb2.Image(data=cv2.imencode(".jpeg", image)[1].tobytes())
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    image_pb2_grpc.add_ImageServiceServicer_to_server(ImageServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    serve()