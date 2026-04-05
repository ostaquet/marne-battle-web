# Problem to solve

While using the scripts, we often received timeout and connection errors.

Typically:

```
requests.exceptions.ConnectionError: HTTPConnectionPool(host='web.archive.org', port=80): Max retries exceeded with url: /cdx/search/cdx?url=https%3A%2F%2Fwww.sambre-marne-yser.be%2Farticle%3D4.php3%3Fid_article%3D37&from=20100101&to=20151231&output=text&filter=statuscode%3A200 (Caused by NewConnectionError("HTTPConnection(host='web.archive.org', port=80): Failed to establish a new connection: [Errno 61] Connection refused"))
```

We should add some time.sleep to be gentle with Internet Archive.
