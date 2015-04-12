import os
from PIL import Image, ImageOps
from pelican import logger


PENDING_THUMBNAILS = set()


def request_thumbnail(image, size, settings):
    if not size:
        size = settings['THUMBNAIL_DEFAULT_SIZE']

    if 'x' not in size:
        size = size + 'x' + size
    try:
        w, h = map(lambda v: 0 if not v else int(v), size.split('x', 1))
    except ValueError:
        logger.warning('Invalid size for thumbnail %s: %s (using 128x128)' % (image, size))
        w, h = 128, 128

    PENDING_THUMBNAILS.add((image, w, h))

    path, filename = os.path.split(image)
    filename = os.path.splitext(filename)[0]
    return os.path.join(settings['THUMBNAIL_OUTPUT_PATH'], path, '%dx%d' % (w, h), '%s.jpg' % filename)


def generate_thumbnails(pelican):
    global PENDING_THUMBNAILS

    settings = pelican.settings
    path_prefix = os.path.join(settings['PATH'], settings['ALBUM_PATH'])
    output_prefix = os.path.join(settings['OUTPUT_PATH'], settings['THUMBNAIL_OUTPUT_PATH'])
    for image, w, h in PENDING_THUMBNAILS:
        src = os.path.join(path_prefix, image)
        src_stat = os.stat(src)

        path, filename = os.path.split(image)
        filename = os.path.splitext(filename)[0]
        destdir = os.path.join(output_prefix, path, '%dx%d' % (w, h))
        if not os.path.isdir(destdir):
            os.makedirs(destdir)
        dest = os.path.join(destdir, '%s.jpg' % filename)

        if os.path.isfile(dest):
            dest_stat = os.stat(dest)
            if dest_stat.st_mtime == src_stat.st_mtime:
                logger.debug('Not generating %s' % dest)
                continue

        logger.info('Generating %s' % dest)

        im = Image.open(src)
        im_w, im_h = im.size
        if not w:
            w = int(im_w * (float(h) / im_h))
            im.thumbnail((w, h))
        elif not h:
            h = int(im_h * (float(w) / im_w))
            im.thumbnail((w, h))
        else:
            im = ImageOps.fit(im, (w, h), Image.ANTIALIAS)
        im.save(dest, 'JPEG', quality=60)
        os.utime(dest, (src_stat.st_atime, src_stat.st_mtime))

    PENDING_THUMBNAILS = set()
