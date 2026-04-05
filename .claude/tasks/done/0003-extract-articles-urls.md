# Problem to solve

The current program extract the working version for the homepage ("sommaire") and for the pages ("page_XX").

On each page, there are links to articles. We need to extract there links and populate the YAML.

To avoid redoing the extracting version from Internet Archive, we will create a new script that read the YAML as input.

For each page "PAGE" on the Internet Archive, we download the HTML and find the links to the articles. Then, we populate properly the tree with all pages and write the YAML with the articles.
