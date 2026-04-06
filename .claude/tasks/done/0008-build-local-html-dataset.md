# Problem to solve

The YAML `assets/articles.yaml` contains all links that compose the website to be restored.

The YAML file contains:

- `archive_url` which is the working file archived on Internet Archive.
- `official_url` which is the original URL of the file.

There are 3 types of pages (`type` in the YAML):

- `homepage` = the root of the website
- `page` = the first level
- `article` = the second level

As we have a clear view of all the valid and working links available on Internet Archive, it is important to download these HTML file locally to perform operations on it.

For each `archive_url` found in the YAML:

1. Download the file.
2. Store the file in `assets/raw_html/` with an appropriate filename.
   - Appropriate filename for `homepage` = `homepage.htm`.
   - Appropriate filename for `page` = `page_XX.htm` where `XX` is the number of the page.
   - Appropriate filename for `article` = `article_XX_YY.htm` where `XX` is the number of the linked page and `YY` the number of the article.
3. Add the appropriate filename in the YAML under the tag `local_filename`.
