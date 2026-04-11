# marne-battle-web

Migration of https://www.sambre-marne-yser.be/ from Spip to Jekyll static website.

## Setup

Create a virtual environment and install dependencies:

```bash
./scripts/venv.sh
```

The script automatically detects the environment and creates:

- `venv_docker/` when running in Docker containers
- `venv_local/` when running on local machines (e.g., MacBook)

This prevents conflicts between Docker and local environments.

## Tools available

### 1. Extracting pages from Internet Archive

The original website has a broken MySQL instance, making some pages inaccessible. We extract functional versions from the Internet Archive (2010-2015).

Run the extraction script:

```bash
source venv_local/bin/activate
python3 src/extract_pages.py
```

This will generate `assets/pages.yaml` containing the homepage and pages with their working archive.org URLs.

### 2. Extracting articles from Internet Archive

After extracting pages, run the article extraction script to find and add article links:

```bash
source venv_local/bin/activate
python3 src/extract_articles.py
```

This will:

1. Read the `assets/pages.yaml` file
2. Download HTML from each page's archive URL
3. Extract article links from the HTML
4. Find working archive snapshots for each article
5. Generate `assets/articles.yaml` with the complete structure

### 3. Building local HTML dataset

After extracting articles, download all HTML files locally for processing:

```bash
source venv_local/bin/activate
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

### 4. Building local image dataset

After downloading HTML files, extract and download all images:

```bash
source venv_local/bin/activate
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

### 5. Relinking HTML files

After downloading HTML and images, relink internal references to use local files:

```bash
source venv_local/bin/activate
python3 src/relink.py
```

This will:

1. Load external link mappings from `assets/link_map.yaml`
2. Load image mappings from `assets/img_map.yaml`
3. Process all HTML files in `assets/raw_html/`
4. Relink internal page links:
   - `sommaire.php3` → `homepage.htm`
   - `page_05.php3` → `page_05.htm`
   - `article=5.php3?id_article=99` → `article_05_99.htm`
5. Preserve external links defined in configuration (e.g., `http://www.spip.net/`)
6. Relink image references using `assets/img_map.yaml`:
   - Archive URLs → `../img/filename.jpg`
7. Save relinked HTML to `assets/html/`
8. Log unmatched links/images to `assets/relink.log`

The external links to preserve are configured in `assets/link_map.yaml`, making it easy to add or modify special URLs without changing the code.

### 6. Converting HTML to Markdown

After relinking, convert all HTML files to Markdown:

```bash
source venv_local/bin/activate
python3 src/convert_to_markdown.py
```

This will:

1. Read all HTML files from `assets/html/`
2. Extract content from the `<div id="main">` section
3. Convert HTML elements to Markdown:
   - Headings `<h1>`-`<h6>` → `#`-`######`
   - Paragraphs → plain text
   - Bullet paragraphs (with `spip_puce` images) → `- item`
   - Image blocks (`spip_documents`) → `![alt](src)` with captions
   - Links: `.htm` extensions → `.md`
   - Tables → Markdown table format
   - Horizontal rules `<hr/>` → `---`
4. Save Markdown files to `assets/md/`

## Development

### Running Tests

```bash
bash scripts/test.sh
```

### Running Linters & SAST

```bash
bash scripts/lint.sh
```

The project uses:

- **flake8** for code style (max line length: 88)
- **mypy** for type checking (strict mode)
- **bandit** for security checking

### Running dependencies vulnerability checks

```bash
bash scripts/snyk.sh
```

The project uses `snyk` in CLI mode to check the vulnerable paths in the dependencies.
