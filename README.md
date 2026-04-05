# marne-battle-web

## Exploring the Internet Archive

Is a snapshot available on the Internet archive?

```
curl -X GET "https://archive.org/wayback/available?url=www.sambre-marne-yser.be"
```

How to get a list of available snapshots?

```
curl -X GET "http://web.archive.org/cdx/search/cdx?url=www.sambre-marne-yser.be"
```
