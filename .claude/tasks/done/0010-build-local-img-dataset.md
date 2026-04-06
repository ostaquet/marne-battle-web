# Problem to solve

All HTML files from the original website have been downloaded locally in `assets/raw_html/`. These HTML files contain link to images hosted on the Internet Archive.

Example of image tag: `<img src="/web/20100516220948im_/http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"/>``

This task is about downloading and indexing all images from the HTML files store in `assets/raw_html/`.

The process is defined as below:

1. For each `*.htm` files found in `assets/raw_html/`
   1. Extract all `img` tag
   2. For each `img` tag
      1. Download the file in `src` by prefixing the relative URL with `https://web.archive.org`. For example: the tag `<img src="/web/20100516220948im_/http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"/>` will cause the download of `https://web.archive.org/web/20100516220948im_/http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg`. The download of this file must be Internet Archive friendly (use `wayback_api._fetch_from_wayback()`).
      2. The downloaded binary must be store in `assets/img` and keept the name of the file. For example: the tag `<img src="/web/20100516220948im_/http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"/>` will result in the file stored in `assets/img/bismarck.jpg`.
      3. The mapping between the source URL and the final file is stored in simple YAML file names `img_map.yaml`. For each entry, we have the `archive_url` and `local_filename`. For example: For example: the tag `<img src="/web/20100516220948im_/http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg"/>` the YAML will contain: `archive_url: /web/20100516220948im_/http://www.sambre-marne-yser.be/IMG/jpg/bismarck.jpg` and `local_filename: assets/img/bismarck.jpg`.

If there is a collision in the name of the saved file, check the MD5 of both file. If it is the same, consider that the file is the same and link to the same binary in the `img_map.yaml`.
