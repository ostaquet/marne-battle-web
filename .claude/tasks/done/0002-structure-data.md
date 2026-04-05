# Problem to solve

The structure of the website is defined based on dict[str, Any]. It is not clean and it is limited to structure the information.

Each page should be define in a structure Page, defined as below:

```
Page:
  - type (HOMEPAGE, PAGE, ARTICLE)
  - Officiel URL (examples: https://www.sambre-marne-yser.be/sommaire.php3, https://www.sambre-marne-yser.be/page_02.php3 or https://www.sambre-marne-yser.be/article=5.php3?id_article=55)
  - Archive URL (examples: examples: https://web.archive.org/web/20131029060500/http://sambre-marne-yser.be/sommaire.php3, https://web.archive.org/web/20131029061649/http://sambre-marne-yser.be/page_04.php3 or https://web.archive.org/web/20120704164517/http://www.sambre-marne-yser.be/article=4.php3?id_article=26)
  - Timestamp of the archive
  - list[Page] : Children pages
```
