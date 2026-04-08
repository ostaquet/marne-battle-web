# marne-battle-web

Migration of https://www.sambre-marne-yser.be/ from Spip to Jekyll static website.

## Setup

Create a virtual environment and install dependencies:

```bash
./scripts/venv.sh
```

## Tools available

### Extracting pages from Internet Archive

The original website has a broken MySQL instance, making some pages inaccessible. We extract functional versions from the Internet Archive (2010-2015).

Run the extraction script:

```bash
source venv/bin/activate
python3 src/extract_pages.py
```

This will generate `assets/pages.yaml` containing the homepage and pages with their working archive.org URLs.

### Extracting articles from Internet Archive

After extracting pages, run the article extraction script to find and add article links:

```bash
source venv/bin/activate
python3 src/extract_articles.py
```

This will:

1. Read the `assets/pages.yaml` file
2. Download HTML from each page's archive URL
3. Extract article links from the HTML
4. Find working archive snapshots for each article
5. Generate `assets/articles.yaml` with the complete structure

### Building local HTML dataset

After extracting articles, download all HTML files locally for processing:

```bash
source venv/bin/activate
python3 src/download_html_dataset.py
```

This will:

1. Read the `assets/articles.yaml` file (or `assets/pages.yaml` if articles doesn't exist)
2. Download HTML from each archive URL
3. Save files to `assets/raw_html/` with appropriate filenames:
   - `homepage.htm` for the homepage
   - `page_XX.htm` for pages (where XX is the page number)
   - `article_XX_YY.htm` for articles (where XX is page, YY is article number)
4. Add `local_filename` field to each entry in the YAML
5. Save the updated structure to `assets/dataset.yaml`

This creates a local dataset for faster processing and reduces load on Internet Archive.

### Building local image dataset

After downloading HTML files, extract and download all images:

```bash
source venv/bin/activate
python3 src/download_img_dataset.py
```

This will:

1. Parse all HTML files in `assets/raw_html/`
2. Extract images from:
   - `<img>` tags with `src` attributes
   - `<a>` tags linking to image files (e.g., `.jpg`, `.png`, `.gif`)
3. For relative image links, find working snapshots on archive.org (2010-2015)
4. Download images from archive.org
5. Save images to `assets/img/` with original filenames
6. Create `assets/img_map.yaml` mapping archive URLs to local filenames
7. Handle filename collisions using MD5 checksums (reuses identical files)
8. Skip already downloaded images (resume capability)
9. Save progress after each image

### Relinking HTML files

After downloading HTML and images, relink internal references to use local files:

```bash
source venv/bin/activate
python3 src/relink.py
```

This will:

1. Process all HTML files in `assets/raw_html/`
2. Relink internal page links:
   - `sommaire.php3` → `homepage.htm`
   - `page_05.php3` → `page_05.htm`
   - `article=5.php3?id_article=99` → `article_05_99.htm`
3. Relink image references using `assets/img_map.yaml`:
   - Archive URLs → `../img/filename.jpg`
4. Save relinked HTML to `assets/html/`
5. Log unmatched links/images to `assets/relink.log`

## Development

### Running Tests

```bash
bash scripts/test.sh
```

### Running Linters

```bash
bash scripts/lint.sh
```

The project uses:

- **flake8** for code style (max line length: 88)
- **mypy** for type checking (strict mode)
