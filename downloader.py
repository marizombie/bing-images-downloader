import requests
from tqdm import tqdm
from PIL import Image
from io import BytesIO
from pathlib import Path
from argparse import ArgumentParser
from api_key import image_search_api_key


BING_MAX_IMAGES = 150
image_search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/search"
stocks_substring = " -shutterstock -dreamstime -bigstock -alamy -depositphotos -gettyimages -istock"


if __name__ == "__main__":
    parser = ArgumentParser(description="Bing images downloader")
    parser.add_argument('-d', '--destination', default='downloads',
                        help='Path to folder where images will be downloaded')
    parser.add_argument('-c', '--count', type=int, default=BING_MAX_IMAGES,
                        help=f'Images limit, maximum is {BING_MAX_IMAGES} and set as default')
    parser.add_argument('-q', '--query', help='Search query')

    args = parser.parse_args()
    save_dir = Path(args.destination)
    count = args.count
    query = args.query + stocks_substring

    if not save_dir.is_dir():
        save_dir.mkdir(parents=True)
        print(f'Directory {save_dir} created')

    headers = {
        "Ocp-Apim-Subscription-Key": image_search_api_key,
    }

    params = {
        "q": query,
        "count": count,
        "imageType": "Photo",
        # "license": "share",
        #   "aspect": "tall",
        "color": "ColorOnly",
        "minHeight": 1000,
        "minWidth": 1000,
        "size": "Large",
        # "imageContent": "Portrait"
    }

    response = requests.get(
        image_search_url, headers=headers, params=params)

    response.raise_for_status()
    search_results = response.json()

    image_dict = [(img["name"].replace(' ', '_') + '.jpg', img["contentUrl"])
                  for img in search_results["value"]]

    for name, url in tqdm(image_dict):
        try:
            image_data = requests.get(url)
            image_data.raise_for_status()
        except Exception as e:
            print(f"Exception {e} while downloading image '{url}'")
            continue

        try:
            image = Image.open(BytesIO(image_data.content))
            image.save(save_dir/name, quality=98)
        except Exception as e:
            print(f"Exception {e} while saving image '{url}'")
            continue
