## Bing Image Search downloader

To work with Image Search API use `downloader.py` script, put your bing image search API key to `api_key.py` near the script and assign it to `image_search_api_key` variable.  
Install requirements using `pip install -r requirements.txt`  

### Parameters
- query - specify one of the next three parameters to start your search, it is the only required parameter:
  - `-q` or `--query` - search key word(s)
  - `-qs` or `--queries` - multiple queries separated by comma, iamges for them will be downloaded one by one
  - `-qf` or `--queries_file` - path to file with multiple queries, one per line
- `-d` or `--destination` - path to folder for downloading images, by default creates `downloads` directory where script is launched
- `-c` or `--count` - downloading images quantity
- `-m` or `--maximum` - specifying this parameter you download all the possible images which were found using your query, although it can contain lots of duplicates closer to the end, **doesn't need value**
- `-st` or `--filter_stocks` - specifying this parameter you drop stock photos from downloads, **doesn't need value**
- `-it` or `--type` - image type, by default it is photo
- `-ic` or `--content`- image content, can be portrait, face or any
- `-is` or `--size` - image size
- `--color` - images accent color
- `--aspect` - aspect ratio
- `--min_width` - minimal width of downloading images
- `--min_height` - minimal height of downloading images

## Bing Visual Search downloader

To work with Visual Search API use `visual_downloader.py` script, put your bing visual search API key to `api_key.py` near the script and assign it to `visual_search_api_key` variable.  
Install requirements using `pip install -r requirements.txt`  

### Parameters
- Similar reference - specify one of the next parameters to start your search, it is the only required parameter:
  - `-si` or `--similar_url` - reference to what you want to download
  - `-f` or `--file_path` - path to file with multiple similar reference urls, one per line
- `-d` or `--destination` - path to folder for downloading images, by default creates `similar-downloads` directory where script is launched
