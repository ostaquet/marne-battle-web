# Problem to solve

The program `downmload_img_dataset.py` is working properly for a part of the URLs mentioned in the HTML files (`assets/raw_html/`).

Based on my analysis, the pictures integrated in the HTML pages with the `img` tag are properly downloaded.

However, there are links with the tag `a` that directs to image too.

Example in the file `assets/raw_html/article_05_58.htm`, the tag `<a href="IMG/jpg/mortagne_meurthe.jpg" class="spip_in">Lien vers carte de la trouée de Charmes</a>` is a link to a picture that is not downloaded in the `assets/img`.

The missing pictures are relative links, which means that we don't have the proper link to be downloaded from Internet Archive. The best way is to use the `wayback_api.py` and the `find_working_snapshot()` to get a working URL.
