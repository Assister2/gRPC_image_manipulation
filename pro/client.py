import grpc
import image_pb2
import image_pb2_grpc

def send_image(stub, image_path, rotation):
    # Read the image file
    with open(image_path, 'rb') as f:
        image_data = f.read()

    # Create a sample_image message with the image data
    sample_image = image_pb2.sample_image(
        color=True,
        data=image_data,
        width=0,
        height=0
    )

    # Create a rotate_image message with the rotation and sample_image
    rotate_image = image_pb2.rotate_image(
        rotation=rotation,
        image=sample_image
    )

    # Send the request to the server and get the response
    response = stub.image_rotation(rotate_image)

    # Save the rotated image
    with open('rotated_image.jpg', 'wb') as f:
        f.write(response.data)

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = image_pb2_grpc.ImageServerStub(channel)

    # Send multiple series of images with different rotations
    image_paths = ['image1.jpg', 'image2.jpg', 'image3.jpg']
    rotations = [image_pb2.RotateImage.NINETY_DEG, image_pb2.RotateImage.ONE_EIGHT_DEG, image_pb2.RotateImage.TWO_SEVENTY_DEG]
    for image_path, rotation in zip(image_paths, rotations):
        send_image(stub, image_path, rotation)

if __name__ == '__main__':
    run()