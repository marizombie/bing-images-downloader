from utils import *
from tqdm import tqdm
from pathlib import Path
from enum_params import *
from argparse import ArgumentParser


DEFAULT_TIMEOUT = 5
BING_BATCH_SIZE = 150
DEFAULT_IMAGES_COUNT = 600

images_search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
stocks_substring = " -shutterstock -dreamstime -bigstock -alamy -depositphotos -gettyimages -istock"


def get_image(index, url, image_type, save_dir):
    # TODO: improve exceptions handling
    try:
        image_data = download_session.get(url, timeout=DEFAULT_TIMEOUT)
        image_data.raise_for_status()
    except Exception as e:
        print(f"Exception while downloading image: {e}")
        return

    name = f'{index}._{get_name(url, image_type)}'
    save_image(name, image_data, image_type, save_dir)


def run_search(params):
    try:
        response = search_session.get(images_search_url, params=params)
        response.raise_for_status()
        search_results = response.json()
    except Exception as e:
        print(f"Exception {e} while searching for images")
        return
    return search_results


def request_images(query, params, save_dir, maximum_wanted):
    search_results = run_search(params)
    if not search_results:
        return

    image_urls = extract_urls(search_results)
    needed_images_len = params["count"]

    if maximum_wanted or needed_images_len > BING_BATCH_SIZE:
        total = search_results['totalEstimatedMatches'] if maximum_wanted else needed_images_len
        params["offset"] = 0
        # desc='Search...', bar_format=references_bar_format):
        for i in range(total // BING_BATCH_SIZE + 1):
            params["offset"] += BING_BATCH_SIZE
            search_results = run_search(params)
            if not search_results:
                continue
            image_urls += extract_urls(search_results)
            # TODO: check count on downloaded images, not here
            if len(image_urls) >= needed_images_len:
                image_urls = image_urls[:needed_images_len]
                break

    for i, url in tqdm(enumerate(image_urls), desc=f"Progress for query '{query}'", total=len(image_urls)):
        get_image(i, url, params["imageType"], save_dir)


def main():
    parser = ArgumentParser(description="Bing images downloader")

    query_group = parser.add_mutually_exclusive_group(required=True)
    query_group.add_argument('-q', '--query',
                             help='Search query, always required')
    query_group.add_argument('-qs', '--queries',
                             help='Search starts to look photos for all queries one by one preserving params, queries must be split by commas')
    query_group.add_argument('-qf', '--queries_file',
                             help='Path to queries file, queries must be one per each line')

    count_group = parser.add_mutually_exclusive_group()
    count_group.add_argument('-c', '--count', type=int, default=DEFAULT_IMAGES_COUNT,
                             help=f'Images to download (default: %(default)s)')
    count_group.add_argument('-m', '--maximum_download', default=False, action='store_true',
                             help=f'Download as many results as it is possible (default: %(default)s)')

    parser.add_argument('-d', '--destination', default='downloads',
                        help='Path to folder where images will be downloaded')
    parser.add_argument('-st', '--filter_stocks', default=True, action='store_true',
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
    maximum_wanted = args.maximum_download
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

    stocks_filter = stocks_substring if filter_stocks else ''

    if query:
        params["q"] = query + stocks_filter
        request_images(query, params, save_dir, maximum_wanted)
        return
    elif queries_path:
        queries = [q.strip('\n') for q in open(queries_path).readlines()]
    else:
        queries = queries.split(',')

    for query in tqdm(queries, desc='Common progress'):
        query = query.lstrip()
        # print(f"Download for query '{query}' started")
        params["q"] = query + stocks_filter
        request_images(query, params, save_dir, maximum_wanted)


if __name__ == "__main__":
    main()
    download_session.close()
    search_session.close()
