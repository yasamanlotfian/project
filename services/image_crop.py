from PIL import Image


def crop_image(image: Image.Image, size: int = 800):

    width, height = image.size

    crop_size = min(width, height)


    left = (width - crop_size) // 2
    top = (height - crop_size) // 2

    right = left + crop_size
    bottom = top + crop_size


    image = image.crop(
        (left, top, right, bottom)
    )


    image = image.resize(
        (size, size),
        Image.Resampling.LANCZOS
    )

    return image