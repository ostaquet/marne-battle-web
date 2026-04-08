# Notes

This is a human-readable note related to the project. Nothing fancy, just some thoughts and ideas that I would like to pursuit.

## Notes for myself

### Exploring the Internet Archive

Is a snapshot available on the Internet archive?

```bash
curl -X GET "https://archive.org/wayback/available?url=www.sambre-marne-yser.be"
```

How to get a list of available snapshots?

```bash
curl -X GET "http://web.archive.org/cdx/search/cdx?url=www.sambre-marne-yser.be"
```

## Work in progress

## Known issues

- In the html files, there are links to other pictures that failed the extract process (example in `article_03_04.htm`, the link to `IMG/jpg/olan_schlieffen2.jpg` was not relink properly). But the files are correctly downloaded locally.

## URLs

- https://sambre-marne-yser.be : the official URL of the website

## Future plans
