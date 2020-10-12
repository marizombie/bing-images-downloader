import requests
from tqdm import tqdm
from pathlib import Path
from argparse import ArgumentParser
from utils import get_name, get_image
from api_key import visual_search_api_key


visual_search_url = "https://api.cognitive.microsoft.com/bing/v7.0/images/visualsearch"
api_header = {"Ocp-Apim-Subscription-Key": visual_search_api_key}


def download_by_reference(url, save_dir):
    try:
        image = requests.get(url).content
    except Exception as e:
        print(f"Exception {e} while trying to get reference image '{url}'")
        return

    file = {'image': image}
    response = requests.post(
        visual_search_url, headers=api_header, files=file)

    try:
        response.raise_for_status()
    except Exception as e:
        print(f"Exception {e} while searching for similar images")
        return

    search_results = response.json()

    for tag in search_results['tags']:
        if tag['displayName'] == '':
            action_tag = tag
            break

    for action in action_tag['actions']:
        if action['actionType'] == 'VisualSearch':
            similars = action['data']['value']
            break

    for i, similar in tqdm(enumerate(similars), desc=f"Similars downloading...", total=len(similars)):
        get_image(i, similar['contentUrl'], save_dir)


if __name__ == "__main__":
    parser = ArgumentParser()
    similar_group = parser.add_mutually_exclusive_group(required=True)
    similar_group.add_argument('-si', '--similar_url',
                               help='Url of reference image to download similars')
    similar_group.add_argument('-f', '--file_path',
                               help='Path to file with similar search references')

    parser.add_argument('-d', '--destination', default='similar-downloads',
                        help='Path to folder where images will be downloaded')

    args = parser.parse_args()
    save_dir = Path(args.destination)
    similar_url = args.similar_url
    file_path = args.file_path

    if not save_dir.is_dir():
        save_dir.mkdir(parents=True)
        print(f'Directory {save_dir} created')

    if file_path:
        similar_urls = [url for url in open(file_path).readlines()]
        for url in similar_urls:
            download_by_reference(url, save_dir)
    else:
        download_by_reference(similar_url, save_dir)
