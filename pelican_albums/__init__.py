from pelican import signals
from . import thumbnails, generator, content


def initialized(pelican):
    pelican.settings.setdefault('ALBUM_PATH', 'images')
    pelican.settings.setdefault('THUMBNAIL_OUTPUT_PATH', 'images/thumbnails')
    pelican.settings.setdefault('THUMBNAIL_DEFAULT_SIZE', '192x192')
    pelican.settings.setdefault('ALBUM_SAVE_AS', 'albums/{slug}.html')
    pelican.settings.setdefault('ALBUM_URL', 'albums/{slug}.html')


def register():
    signals.initialized.connect(initialized)
    signals.get_generators.connect(generator.get_generators)
    signals.content_object_init.connect(content.update_content)
    signals.finalized.connect(thumbnails.generate_thumbnails)
