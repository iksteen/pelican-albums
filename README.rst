Pelican-Albums
==============

Pelican-Albums is a plugin for Pelican that helps you to easily manage your
photo albums (or galleries).

Features
--------

- Easily reference an image in your album path using {image}album/image.jpg.
- Automatically create a thumbnail for an image in your album path using
  ``{thumbnail}album/image.jpg`` or ``{thumbnail:NxN}album/image.jpg``.
- Automatically create album pages by adding a page to an album directory.

Installation
------------

To install pelican-albums to your pelican installation use::

    $ pip install pelican-albums

Then, add 'pelican_albums' to the plugin list in your publishconf.py::

    PLUGINS = ['pelican_albums']

Settings
--------

Pelican-albums provides a couple of settings:

- ``ALBUM_PATH`` ('images'): What directory inside ``content`` contains your
  albums.
- ``THUMBNAIL_OUTPUT_PATH`` ('images/thumbnails'): What directory inside
  ``output`` will be used to store thumbnails.
- ``THUMBNAIL_DEFAULT_SIZE`` ('192x192'): What the default size of a thumbnail
  should be.
- ``ALBUM_SAVE_AS`` ('albums/{slug}.html'): Where to store album indexes.
- ``ALBUM_URL`` ('albums/{slug}.html'):  The URL scheme to reference an album.

Albums
------

To create a new album, just create a new directory in the ``ALBUM_PATH`` (the
default is content/images) and place the images inside it. Please note that
pelican-albums does not offer facilities to rotate or resize the images for
you (except for thumbnails).

Thumbnails
----------

Pelican-albums will automatically generate the requested thumbnails at the
requested sizes. It will check the ``mtime`` of the original file to that
of the thumbnail to check if the thumbnail should be refreshed.

You can specify the size of a thumbnail on different places:

- Inside the {thumbnail} tag: {thumbnail:128x128}album/image.jpg
- In the metadata of the content: Thumbnail-Size: 128x128
- As a parameter to the ``album.thumbnail(size=None)`` in your templates.
- In the global pelican settings.

A thumbnail size specifier can have a number of different forms:

- *WIDTHxHEIGHT* -- Crop and resize an image until a thumbnail of these
  exact dimensions is the result (f.e. 192x192).
- *DIMENSION* -- Shorthand for *DIMENSIONxDIMENSION* (f.e. 192).
- *WIDTHx* -- Create a thumbnail with the given width but keep the original
  aspect ratio so the height might vary (f.e. 192x).
- *xHEIGHT* -- Create a thumbnail with the given height but keep the original
  aspect ratio so the width might vary (f.e. x192).

Album pages
-----------

By creating a page inside an album folder, a page will be generated using the
``album.html`` template. Both the ``album`` and the ``page`` will be available
inside the template. The ``page`` object works exactly as the regular pelican
page objects.

The ``album`` object has several properties:

- ``images`` -- The images contained in this album.
- ``albums`` -- A list of sub-albums (if any).
- ``pages`` -- The album pages for this album (you can create multiple pages
  for each album if you want).

album.html
----------

An example template for album pages::

    {% extends "base.html" %}
    {% block title %}{{ page.title }}{%endblock%}
    {% block content %}
    <article class="page">
        <header>
            <div class="title">
                {{ page.title }}
            </div>
        </header>
    
        <div class="entry-content">
            {{ page.content }}
        </div>
    
        <div class="album">
            {% for image in album.images %}
                <a href="{{ SITEURL }}/{{ image.url }}">
                    <img src="{{ SITEURL }}/{{ image.thumbnail(page.metadata.get('thumbnail-size')) }}"
                         title="{{ image.filename }}" />
                </a>
            {% endfor %}
        </div>
    </article>
    {% endblock %}
