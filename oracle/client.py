import grpc
from PIL import Image
from io import BytesIO
from image_pb2 import RotateImage, SampleImage
from image_pb2_grpc import ImageServerStub
import cv2
import numpy as np
import argparse

def check_request_validity(request):
         if not request.image.data:
             raise ValueError("Invalid image data")

def read_image_file(image_path):
    try:
        with open(image_path, 'rb') as f:
            image_data = f.read()
        return image_data
    except IOError as e:
        print("Error occurred while reading the image file:", e)
        return None

def send_image_to_server(stub, image_file, rotation_degrees, apply_mean_filter):
    
    # Read the image file and convert it to bytes
    image_data = read_image_file(image_file)
    # Create a gRPC channel and stub
    channel = grpc.insecure_channel('localhost:50051')  # Specify the server host and port
    stub = ImageServerStub(channel)
    image = SampleImage(color=True, data=image_data, width=0, height=0)
    # rotation_enum = get_rotation_enum(rotation_degrees)
    request = RotateImage(rotation=rotation_degrees, image=image)
    try:
        check_request_validity(request)
        response = stub.ImageRotation(request)
        rotated_image = Image.open(BytesIO(response.data))
        rotated_image.save('rotated_image.jpg')

        print("Rotation : ", image_file, rotation_degrees)
        if(apply_mean_filter == 'True') :
            print("Mean Filter :", image_file)
            response = stub.ApplyFilter(response)


        output_filename = image_path.split('.')[0] + '_output.jpg'
        with open(output_filename,'wb') as file:
            file.write(response.data)
    except grpc.RpcError as e:
        print("Erro occured during request transmission",e)
    except Exception as e:
        print("Error occurred during request processing:", e)    

def get_rotation_enum(rotation_str):
    if rotation_str == "NINETY_DEG":
        return RotateImage.NINETY_DEG
    elif rotation_str == "ONE_EIGHTY_DEG":
        return RotateImage.ONE_EIGHTY_DEG
    elif rotation_str == "TWO_SEVENTY_DEG":
        return RotateImage.TWO_SEVENTY_DEG
    else:
        raise ValueError("Unknown rotation label: " + rotation_str)    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Image Rotation and Filtering')
    parser.add_argument("image_args", nargs="+", help="file paths followed by degrees and mean filter")

    args = parser.parse_args()

    image_paths = args.image_args[::3]
    rotations = args.image_args[1::3]
    apply_filters = args.image_args[2::3]

    channel = grpc.insecure_channel('localhost:50051')
    stub = ImageServerStub(channel)

    for image_path, rotation, apply_filter in zip(image_paths, rotations, apply_filters):
        send_image_to_server(stub, image_path, rotation, apply_filter)