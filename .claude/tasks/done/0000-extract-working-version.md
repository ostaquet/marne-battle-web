# Problem to solve

The first step is to identify the different pages functionnal on the https://archive.org for the website https://www.sambre-marne-yser.be. The functional pages should be between 2010 and 2015.

A non-functional page contains the header below:

```
Site under construction

Warning: a technical problem (MySQL server) prevents access to this part of the site.

Thank you for your understanding.
```

We need a Python script to list in a YAML file:

- The ID of the page (examples: homepage, page2, article6)
- The officiel URL of the page (examples: https://www.sambre-marne-yser.be/sommaire.php3, https://www.sambre-marne-yser.be/page_02.php3 or https://www.sambre-marne-yser.be/article=5.php3?id_article=55)
- The URL of the functional page on archive.org for this page (examples: https://web.archive.org/web/20131029060500/http://sambre-marne-yser.be/sommaire.php3, https://web.archive.org/web/20131029061649/http://sambre-marne-yser.be/page_04.php3 or https://web.archive.org/web/20120704164517/http://www.sambre-marne-yser.be/article=4.php3?id_article=26)

The tree of the website must be kept in the YAML to ease the reading (root = homepage, then page under root, then articles under pages).
