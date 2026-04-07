# Problem to solve

HTML pages and images have been downloaded from Internet Archive. All data is stored locally. However, the links between the pages and the links in the pages to the images are broken.

The objective of this task is to re-establish the links between the different items of the website.

The process is defined as below:

1. For each HTML file in `assets/raw_html/`
   1. Load the HTML file
   2. Replace all links to homepage, pages and articles to the local version.
      Example 1: The href tag `<a href="sommaire.php3">Accueil</a>` must be adapted to `<a href="homepage.htm">Accueil</a>`.
      Example 2: The href tag `<a href="page_05.php3">Batailles</a>` must be adapted to `<a href="page_05.htm">Batailles</a>`
      Example 3: The href tag `<a href="article=5.php3?id_article=99">(Lire la suite...)</a>` must be adapted to `<a href="article_05_99.htm">(Lire la suite...)</a>`
   3. Replace all references to images to the local version. The map is available in `assets/img_map.yaml`. The YAML map is composed by the URL as key and the filename as value (example: `/web/20100417163745im_/http://www.sambre-marne-yser.be/IMG/jpg/draagonsall3.jpg: draagonsall3.jpg`). Therefore, the `src` attribute of the `img` tag must be adapted. For example: `<img src="/web/20100417163822im_/http://www.sambre-marne-yser.be/IMG/jpg/plan__17.jpg" style="border-width: 0px;" width="600" height="652" alt="Plan XVII - 36.8 ko" title="Plan XVII - 36.8 ko"/>` becomes `<img src="../img/plan__17.jpg" style="border-width: 0px;" width="600" height="652" alt="Plan XVII - 36.8 ko" title="Plan XVII - 36.8 ko"/>`
   4. The resulting HTML file must be saved into `assets/html`.

For each `a` tag or `img` tag for which the program is not able to make a match, the program writes a line in the file `relink.log`. The line is composed by the HTML filename where we found the issue followed by the not found `href`. By example: `article_07_100.htm : https://web.archive.org/web/20100417231020/http://www.sambre-marne-yser.be/`. This will allow to investigate if it is an issue.

Notice that tag `a` with `href` ending with `://www.sambre-marne-yser.be/` is always mapped to `homepage.htm`.
