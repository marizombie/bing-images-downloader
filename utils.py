
from re import split
from PIL import Image
from io import BytesIO
from pathlib import Path
from requests import Session
from enum_params import ImageType
from api_key import image_search_api_key


DEFAULT_TIMEOUT = 5
# references_bar_format = "{l_bar}{bar} | [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
common_header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.110 Safari/537.36"
}
api_header = {"Ocp-Apim-Subscription-Key": image_search_api_key}

download_session = Session()
download_session.headers = common_header
search_session = Session()
search_session.headers = api_header


def is_png(image_type):
    return image_type == ImageType.transparent.value


def is_gif(image_type):
    return image_type == ImageType.animated_gif.value or \
        image_type == ImageType.animated_gif_secure.value


def extract_urls(search_results):
    return [img["contentUrl"] for img in search_results["value"]]


def get_name(url, image_type=None):
    name = Path(url).name.split('.')[0][:30]

    if not Path(url).suffix:
        if is_png(image_type):
            name += '.png'
        elif is_gif(image_type):
            name += '.gif'
        else:
            name += '.jpg'
    else:
        name += split(r'\?|\:|\&|\!', Path(url).suffix)[0].lower()

    return name


def save_image(name, image_data, image_type, save_dir):
    try:
        image = Image.open(BytesIO(image_data.content))

        if is_png(image_type) or is_gif(image_type):
            image = image.convert('RGBA')
        else:
            image = image.convert('RGB')

        image.save(save_dir/name, quality=98)
    except Exception as e:
        print(f"Exception {e} while saving image '{name}'")
        return


def get_image(index, url, save_dir, image_type=None):
    # TODO: improve exceptions handling
    try:
        image_data = download_session.get(url, timeout=DEFAULT_TIMEOUT)
        image_data.raise_for_status()
    except Exception as e:
        print(f"Exception while downloading image: {e}")
        return

    name = f'{index}._{get_name(url, image_type)}'
    save_image(name, image_data, image_type, save_dir)
