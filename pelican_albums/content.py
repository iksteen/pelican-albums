import os
import re
from pelican import logger
from pelican.utils import path_to_url
from .thumbnails import request_thumbnail


def build_url(content, path, settings):
    if not settings['RELATIVE_URLS']:
        return '/'.join((settings['SITEURL'], path_to_url(path)))
    else:
        return path_to_url(os.path.relpath(
            os.path.abspath(os.path.join(settings['PATH'], path)),
            os.path.dirname(content.source_path)
        ))


def update_content(content):
    if not content or not content._content:
        return content

    settings = content.settings
    album_path = settings['ALBUM_PATH']
    path_prefix = os.path.join(settings['PATH'], settings['ALBUM_PATH'])

    # Copied from contents.py in pelican
    intrasite_link_regex = settings['INTRASITE_LINK_REGEX']
    regex = r"""
        (?P<markup><\s*[^\>]*  # match tag with all url-value attributes
            (?:href|src)\s*=)

        (?P<quote>["\'])      # require value to be quoted
        (?P<path>{0}(?P<value>.*?))  # the url value
        \2""".format(intrasite_link_regex)
    hrefs = re.compile(regex, re.X)

    def replacer(m):
        what = m.group('what')
        value = m.group('value')
        origin = m.group('path')

        if what == 'thumbnail' or what.startswith('thumbnail:'):
            if what == 'thumbnail':
                size = content.metadata.get('thumbnail-size')
            else:
                size = what.split(':', 1)[1]

            image = os.path.join(path_prefix, value)
            if not os.path.isfile(image):
                logger.warning('Image does not exist: `%s\'.' % value)
            else:
                origin = build_url(content, request_thumbnail(value, size, settings), settings)
        elif what == 'image':
            image = os.path.join(path_prefix, value)
            if not os.path.isfile(image):
                logger.warning('Image does not exist: `%s\'.' % value)
            else:
                origin = build_url(content, os.path.join(album_path, value), settings)

        return ''.join((m.group('markup'), m.group('quote'), origin,
                        m.group('quote')))

    content._content = hrefs.sub(replacer, content._content)
    return content
