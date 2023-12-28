import grpc
from PIL import Image
from io import BytesIO
from image_pb2 import RotateImage, SampleImage
from image_pb2_grpc import ImageServerStub
import cv2
import numpy as np

def send_image_to_server(stub, image_file, rotation_degrees, apply_mean_filter):
    
    # Read the image file and convert it to bytes
    with open(image_file, 'rb') as file:
        image_data = file.read()

    # Create a gRPC channel and stub
    channel = grpc.insecure_channel('localhost:50051')  # Specify the server host and port
    stub = ImageServerStub(channel)
    image = SampleImage(color=True, data=image_data, width=0, height=0)
    request = RotateImage(rotation=rotation_degrees, image=image)

    response = stub.ImageRotation(request)
    rotated_image = Image.open(BytesIO(response.data))
    rotated_image.save('rotated_image.jpg')
    # Create the protobuf message
    # image_data_filter = cv2.imread(image_file)

    print("IMAGE_SOURCES")
    if(apply_mean_filter == True) :
        response = stub.ApplyFilter(image)
        # filtered_image = Image.open(BytesIO(response.data))
        # filtered_image.save('filtered_image.jpg')
    output_filename = image_path.split('.')[0] + '_output.jpg'
    with open(output_filename,'wb') as file:
        file.write(response.data)

if __name__ == '__main__':
    # send_image_to_server('image.jpg', 2, True)  
    channel = grpc.insecure_channel('localhost:50051')
    stub = ImageServerStub(channel)
    image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
    rotations = [3, 1, 2]
    apply_filters = [False, True, False]
    for image_path, rotation, apply_filter in zip(image_paths, rotations, apply_filters):
        send_image_to_server(stub, image_path, rotation, apply_filter)
    # image1 = cv2.imread('rotated_image.jpg')
    # mean_filtered = cv2.blur(image1, (5, 5))
    # cv2.imshow('Original Image', image1)
    # cv2.imshow('Mean Filtered Image', mean_filtered)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
