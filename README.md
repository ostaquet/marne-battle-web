# marne-battle-web

Migration of https://www.sambre-marne-yser.be/ from Spip to Jekyll static website.

## Setup

Create a virtual environment and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Extracting Working Versions

The original website has a broken MySQL instance, making some pages inaccessible. We extract functional versions from the Internet Archive (2010-2015).

Run the extraction script:

```bash
source venv/bin/activate
python extract_working_versions.py
```

This will generate `working_versions.yaml` containing the homepage and pages with their working archive.org URLs.

## Running Tests

```bash
source venv/bin/activate
pytest test_extract_working_versions.py -v
```

## Exploring the Internet Archive

Is a snapshot available on the Internet archive?

```bash
curl -X GET "https://archive.org/wayback/available?url=www.sambre-marne-yser.be"
```

How to get a list of available snapshots?

```bash
curl -X GET "http://web.archive.org/cdx/search/cdx?url=www.sambre-marne-yser.be"
```
