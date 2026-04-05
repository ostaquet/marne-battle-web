# Problem to solve

The usage of `find_working_snapshot()` is costly in term of performance because the Internet Archive is limiting the access to the API.

In the function `extract_article_links_from_html()`, we currently extract the href that match a specific pattern. However, the href mentionned in the html file downloaded from Internet Archive contains a link on the internet archive with a timestamp that should work.

Instead of returning a built original URL, we should returns a list of object `ArticleLink` with the href as found in the file and the original url (built by extracting the end of the href and adding the root URL of the website).
