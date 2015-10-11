import operator
import os
from pelican import logger
from pelican.contents import Page
from pelican.generators import Generator
from PIL import Image as PILImage
from . import thumbnails

try:
    from pelican.contents import is_valid_content, Page
except ImportError:
    def is_valid_content(page, _):
        return page.is_valid()


class ImageContent(object):
    def __init__(self, album, filename, settings):
        self.album = album
        self.filename = filename
        self.settings = settings
        self.page = None

    @property
    def url(self):
        return self.album.url + '/' + self.filename

    def thumbnail(self, spec=''):
        return thumbnails.request_thumbnail(os.path.join(self.album.name, self.filename), spec, self.settings)


class Image(Page):
    default_template = 'image'
    image = None

    @property
    def prev(self):
        return self._prev_next(operator.sub)

    @property
    def next(self):
        return self._prev_next(operator.add)

    def _prev_next(self, op):
        images = self.image.album.images
        index = images.index(self.image)
        prev_index = op(index, 1) % len(images)
        return images[prev_index].page


class AlbumContent(object):
    def __init__(self, name, settings):
        self.name = name
        self.settings = settings
        self._images = {}
        self.albums = []
        self.pages = []

    @property
    def url(self):
        return (self.settings['ALBUM_PATH'] + '/' + self.name) if self.name else self.settings['ALBUM_PATH']

    def add_image(self, filename):
        image = ImageContent(self, filename, self.settings)
        self._images[filename] = image
        return image

    @property
    def images(self):
        return [self._images[image] for image in sorted(self._images.keys())]


class Album(Page):
    default_template = 'album'
    album = None

    @property
    def cover_image(self):
        try:
            # Cover set through page metadata.
            filename = self.cover
        except AttributeError:
            cover = self.album.images[0]
        else:
            cover = self.album._images[filename]
        return cover


class AlbumGenerator(Generator):
    album_pages = None
    image_pages = None

    def find_albums(self, path=(), parent=None):
        album_path = os.path.join(self.path, self.settings['ALBUM_PATH'], *path)

        location = '/'.join(path)
        album = AlbumContent(location, self.settings)
        if parent:
            parent.albums.append(album)

        # Images don't have titles, use the basename instead.
        image_settings = dict(self.settings, SLUGIFY_SOURCE='basename')

        for filename in os.listdir(album_path):
            f = os.path.join(album_path, filename)

            if os.path.isdir(f):
                self.find_albums(path + (filename,), album)
            else:
                try:
                    PILImage.open(file_path)
                    image = album.add_image(filename)
                    page = Image('', settings=image_settings, source_path=filename)
                    page.image = image
                    image.page = page
                    self.add_source_path(page)
                    self.image_pages.append(page)
                except IOError:
                    try:
                        page = self.readers.read_file(
                            base_path=self.path,
                            path=f,
                            content_class=Album,
                            context=self.context,
                        )
                        self.add_source_path(page)
                    except Exception as e:
                        logger.error('Could not process %s\n%s', f, e,
                                     exc_info=self.settings.get('DEBUG', False))
                        self._add_failed_source_path(f)
                        continue

                    if not is_valid_content(page, f):
                        self._add_failed_source_path(f)
                        continue

                    page.album = album
                    self.album_pages.append(page)
                    album.pages.append(page)

    def generate_context(self):
        self.album_pages = []
        self.image_pages = []
        self.find_albums()
        self.context['albums'] = [p for p in sorted(self.album_pages, key=operator.attrgetter('title'))]

    def generate_output(self, writer):
        for page in self.album_pages:
            writer.write_file(
                page.save_as, self.get_template(page.template),
                self.context, page=page, album=page.album,
                relative_urls=self.settings['RELATIVE_URLS'],
                override_output=hasattr(page, 'override_save_as'))
        for page in self.image_pages:
            writer.write_file(
                page.save_as, self.get_template(page.template),
                self.context, page=page, image=page.image,
                relative_urls=self.settings['RELATIVE_URLS'],
                override_output=hasattr(page, 'override_save_as'))


def get_generators(pelican):
    return AlbumGenerator
