# From plone to JSON

To refetch `jobs.json` and `news.json` I used a copy of the afpy.org
Plone following https://docs.plone.org/manage/deploying/copy.html
using Plone
([4.3.15](https://launchpad.net/plone/4.3/4.3.15/+download/Plone-4.3.15-UnifiedInstaller.tgz))
just had to add an extra try-except in
`/Products/Archetypes/ExtensibleMetadata.py` to run
`export_from_plone.py news` (`news` or `jobs`) without exceptions.


# From JSON to Atom

Use `plone_to_atom.py news.json` (`news.json` or `jobs.json`) to
transform the output of `export_from_plone.py` into stand-alone Entry
Documents [Atom](https://tools.ietf.org/html/rfc4287) in their
respective folders.
