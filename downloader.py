import requests
from re import split
from tqdm import tqdm
from PIL import Image
from io import BytesIO
from pathlib import Path
from enum_params import *
from argparse import ArgumentParser
from api_key import image_search_api_key


BING_MAX_IMAGES = 150
image_search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
stocks_substring = " -shutterstock -dreamstime -bigstock -alamy -depositphotos -gettyimages -istock"
headers = {"Ocp-Apim-Subscription-Key": image_search_api_key}


def get_image(url, image_type, save_dir):
    # TODO: improve exceptions handling
    try:
        image_data = requests.get(url)
        image_data.raise_for_status()
    except Exception as e:
        print(f"Exception {e} while downloading image '{url}'")
        return

    name = Path(url).name.split('.')[0][:30]

    if not Path(url).suffix:
        if image_type == ImageType.transparent:
            name += '.png'
        elif image_type == ImageType.animated_gif or image_type == ImageType.animated_gif_secure:
            name += '.gif'
        else:
            name += '.jpg'
    else:
        name += split(r'\?|\:', Path(url).suffix)[0].lower()

    try:
        image = Image.open(BytesIO(image_data.content))

        if image_type == ImageType.transparent or image_type == ImageType.animated_gif or \
                image_type == ImageType.animated_gif_secure:
            image = image.convert('RGBA')
        else:
            image = image.convert('RGB')

        image.save(save_dir/name, quality=98)
    except Exception as e:
        print(f"Exception {e} while saving image '{url}'")
        return


def make_response(params, save_dir):
    response = requests.get(
        image_search_url, headers=headers, params=params)
    response.raise_for_status()
    search_results = response.json()

    image_urls = [img["contentUrl"] for img in search_results["value"]]

    for url in tqdm(image_urls):
        get_image(url, params["imageType"], save_dir)


def main():
    parser = ArgumentParser(description="Bing images downloader")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-q', '--query',
                       help='Search query, always required')
    group.add_argument('-qs', '--queries',
                       help='Search starts to look photos for all queries one by one preserving params, queries must be split by commas')
    group.add_argument('-qf', '--queries_file',
                       help='Path to queries file, queries must be one per each line')

    parser.add_argument('-d', '--destination', default='downloads',
                        help='Path to folder where images will be downloaded')
    parser.add_argument('-c', '--count', type=int, default=BING_MAX_IMAGES,
                        help=f'Images limit, maximum is {BING_MAX_IMAGES} and set as default')

    parser.add_argument('-st', '--filter_stocks', default=FilterStates.enabled.value, choices=FilterStates.get_values(),
                        help=f"Drops stock photos from response (default: %(default)s), choises are: %(choices)s")
    parser.add_argument('-it', '--type', default=ImageType.photo.value, choices=ImageType.get_values(),
                        help=f"Image type (default: %(default)s), choises are: %(choices)s")
    parser.add_argument('-ic', '--content', default=ImageContent.portrait.value, choices=ImageContent.get_values(),
                        help=f"Image content (default: %(default)s), choises are: %(choices)s")
    parser.add_argument('-is', '--size', default=ImageSize.large.value, choices=ImageSize.get_values(),
                        help=f"Image size (default: %(default)s), choises are: %(choices)s")

    parser.add_argument('--color', default=ImageColor.color_only.value, choices=ImageColor.get_values(),
                        help=f"Image color (default: %(default)s), choises are: %(choices)s")
    parser.add_argument('--aspect', choices=Aspect.get_values(),
                        help=f"Filters images by the following aspect ratios: %(choices)s")
    parser.add_argument('--min_width', type=int, default=1000,
                        help=f"Minimal image width (default: %(default)s)")
    parser.add_argument('--min_height', type=int, default=1000,
                        help=f"Minimal image height (default: %(default)s)")

    args = parser.parse_args()
    query = args.query
    queries = args.queries
    queries_path = args.queries_file

    save_dir = Path(args.destination)
    count = args.count
    filter_stocks = args.filter_stocks

    image_type = args.type
    image_content = args.content
    image_size = args.size

    color = args.color
    min_image_width = args.min_width
    min_image_height = args.min_height
    aspect = args.aspect

    if not save_dir.is_dir():
        save_dir.mkdir(parents=True)
        print(f'Directory {save_dir} created')

    params = {
        "count": count,
        # "license": "share",
        "minHeight": min_image_height,
        "minWidth": min_image_width,
        "size": image_size,
        # TODO: add more params
    }

    # TODO: optimize
    if image_type != ImageType.all_content.value:
        params["imageType"] = image_type

    if image_content != ImageContent.any_content.value:
        params["imageContent"] = image_content

    if color != ImageColor.all_content.value:
        params["color"] = color

    if aspect != Aspect.all_content.value:
        params["aspect"] = aspect

    stocks_filter = stocks_substring if filter_stocks == FilterStates.enabled.value else ''

    if query:
        params["q"] = query + stocks_filter
        make_response(params, save_dir)
        return
    elif queries_path:
        queries = [q.strip('\n') for q in open(queries_path).readlines()]
    else:
        queries = queries.split(',')

    for query in queries:
        query = query.lstrip()
        print(f"Download for query '{query}' started")
        params["q"] = query + stocks_filter
        make_response(params, save_dir)


if __name__ == "__main__":
    main()
