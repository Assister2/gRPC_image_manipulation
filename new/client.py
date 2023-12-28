import grpc
import image_pb2
import image_pb2_grpc
from google.protobuf import empty_pb2
import cv2
import os, io
import numpy as np


def send_image(stub, image_path):
    try:
        # Read the image
        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        # print("PATH",image_path, image)
        if image is None:
            print("Invalid image file")
            return

        # Create the request and send the image
        request = image_pb2.Image(data=cv2.imencode(".jpeg", image)[1].tobytes())
        print("RESPONSE in CLIENT REQUEST")
        response = stub.SendImage(request)
        print("RESPONSE in CLIENT RESPONSE", response)
        # Handle the response if needed
    except grpc.RpcError as e:
        print(f"Error sending image: {e.details()}")

def get_images(stub):
    try:

        request = empty_pb2.Empty()
        # print ("ASDASDAS", request)
        response_iterator = stub.GetImage(request)
        if not response_iterator:
            print("ERROR : RESPONSE")
            return
        for image in response_iterator:
            # Process and display the received image
            processed_image = cv2.imdecode(image.data, cv2.IMREAD_COLOR)
            if processed_image is not None:
                cv2.imshow("Processed Image", processed_image)
                cv2.waitKey(0)
            else:
                print("Invalid image received")
    except grpc.RpcError as e:
        print(f"Error getting images: {e.details()}")


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = image_pb2_grpc.ImageServiceStub(channel)
    current_dir = os.getcwd()
    image_paths = ['image.png', 'image1.jpeg', 'image2.jpeg']
    # image_paths = ['image.png']
    for image_path in image_paths:
        file_dir = os.path.join( current_dir, image_path)
        send_image(stub, image_path)

    get_images(stub)


if __name__ == '__main__':
    run()