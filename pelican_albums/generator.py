import os
from pelican import logger
from pelican.contents import is_valid_content, Page
from pelican.generators import Generator
from PIL import Image
from . import thumbnails


class ImageContent(object):
    def __init__(self, album, filename, settings):
        self.album = album
        self.filename = filename
        self.settings = settings

    @property
    def url(self):
        return self.album.url + '/' + self.filename

    def thumbnail(self, spec=''):
        return thumbnails.request_thumbnail(os.path.join(self.album.name, self.filename), spec, self.settings)


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
        self._images[filename] = ImageContent(self, filename, self.settings)

    @property
    def images(self):
        return [self._images[image] for image in sorted(self._images.keys())]


class Album(Page):
    default_template = 'album'
    album = None


class AlbumGenerator(Generator):
    albums = None
    pages = None

    def find_albums(self, path=(), parent=None):
        album_path = os.path.join(self.path, self.settings['ALBUM_PATH'], *path)

        location = '/'.join(path)
        album = AlbumContent(location, self.settings)
        if parent:
            parent.albums.append(album)

        for filename in os.listdir(album_path):
            f = os.path.join(self.path, self.settings['ALBUM_PATH'], *path + (filename,))
            file_path = os.path.join(album_path, filename)

            if os.path.isdir(file_path):
                self.find_albums(path + (filename,), album)
            else:
                try:
                    Image.open(file_path)
                    album.add_image(filename)
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
                    self.pages.append(page)
                    album.pages.append(page)

    def generate_context(self):
        self.pages = []
        self.find_albums()
        self.context['albums'] = [p for p in sorted(self.pages, key=lambda p: p.metadata['title'])]

    def generate_output(self, writer):
        for page in self.pages:
            writer.write_file(
                page.save_as, self.get_template(page.template),
                self.context, page=page, album=page.album,
                relative_urls=self.settings['RELATIVE_URLS'],
                override_output=hasattr(page, 'override_save_as'))


def get_generators(pelican):
    return AlbumGenerator
