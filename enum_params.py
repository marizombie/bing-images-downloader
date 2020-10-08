from enum import Enum


class CustomEnum(Enum):
    @classmethod
    def get_values(cls):
        return [e.value for e in cls]


class ImageType(CustomEnum):
    photo = 'photo'
    clipart = 'clipart'
    sketch = 'line'
    transparent = 'transparent'
    shopping = 'shopping'  # needs more tests
    animated_gif = 'animatedGif'
    animated_gif_secure = 'animatedGifHttps'
    all_content = 'all'


class ImageContent(CustomEnum):
    face = 'face'
    portrait = 'portrait'
    any_content = 'any'


class ImageSize(CustomEnum):
    large = 'large'
    medium = 'medium'
    small = 'small'
    wallpaper = 'wallpaper'
    all_content = 'all'


class ImageColor(CustomEnum):
    color_only = 'colorOnly'
    monochrome = 'monochrome'
    all_content = 'all'
    # TODO: add accent color options


class Aspect(CustomEnum):
    square = 'square'
    wide = 'wide'
    tall = 'tall'
    all_content = 'all'
