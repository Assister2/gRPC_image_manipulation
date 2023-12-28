from PIL import Image


image = Image.open('image.jpg')

grayscale_image = image.convert('L')
bw_image = grayscale_image.point(lambda x: 0 if x < 128 else 255, mode='1')
rgba_image = image.convert('RGBA')


rgba_image.save('rgba_image.png')
grayscale_image.save('grayscale_image.jpg')
bw_image.save('bw_image.jpg')