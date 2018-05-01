import os
import sys
import json
from dateutil.parser import parse
from base64 import b64decode

from feedgenerator.django.utils.xmlutils import SimplerXMLGenerator
from feedgenerator import Atom1Feed


class StandaloneAtom(Atom1Feed):
    """https://tools.ietf.org/html/rfc4287#section-4.1.2
    """
    def __init__(self):
        self.items = []

    def write_extensions(self, handler):
        pass

    def write(self, outfile):
        handler = SimplerXMLGenerator(outfile, 'utf8')
        handler.startDocument()
        item = self.items[0]
        handler.startElement("entry", self.item_attributes(item))
        self.add_item_elements(handler, item)
        self.write_extensions(handler)
        handler.endElement("entry")


class Afpy_News(StandaloneAtom):
    def __init__(self, article):
        self.article = article
        super().__init__()

    def write_extensions(self, handler):
        handler.addQuickElement('location', self.article['location'])
        if 'image' in self.article and self.article['image']:
            handler.addQuickElement('link', "", {
                "href": self.article['id'] + '.jpg',
                "rel": "image"})


class Afpy_Job(StandaloneAtom):
    def __init__(self, article):
        self.article = article
        super().__init__()

    def write_extensions(self, handler):
        handler.addQuickElement('company', self.article['company'])
        handler.addQuickElement('address', '\n'.join(self.article['address']))
        handler.addQuickElement('contact', self.article['contact'])
        handler.addQuickElement('location', self.article['location'])
        handler.addQuickElement('phone', self.article['phone'])
        if self.article['remoteUrl']:
            handler.addQuickElement('link', "", {
                "href": self.article['remoteUrl'],
                "rel": "about"})
        if self.article['sourceUrl']:
            handler.addQuickElement('link', "", {
                "href": self.article['sourceUrl'],
                "rel": "via"})
        if 'image' in self.article and self.article['image']:
            handler.addQuickElement('link', "", {
                "href": self.article['id'] + '.jpg',
                "rel": "image"})


def afpy_to_atom(ifile, odir, atom_impl):
    with open(ifile) as ifile_handle:
        articles = json.load(ifile_handle)
    os.makedirs(odir, mode=0o755, exist_ok=True)
    for article in articles:
        atom = atom_impl(article)
        iri = f"https://www.afpy.org/jobs/{article['id']}"
        atom.add_item(title=article['title'],
                      link=iri,
                      description=article['description'],
                      author_name=', '.join(article['creators']),
                      author_email=article['email'] if 'email' in article else None,
                      pubdate=parse(article['creation_date']),
                      unique_id=iri,
                      content=article['text'],
                      updateddate=parse(article['modification_date']))
        opath = os.path.join(odir, article['id'] + '.xml')
        with open(opath, 'w') as ofile:
            atom.write(ofile)
        if 'image' in article and article['image']:
            image_opath = os.path.join(odir, article['id'] + '.jpg')
            with open(image_opath, 'wb') as image:
                image.write(b64decode(article['image']))


def main():
    ifile = sys.argv[1]
    odir = sys.argv[1].replace('.json', '/')
    if ifile == 'news.json':
        afpy_to_atom(ifile, odir, Afpy_News)
    else:
        afpy_to_atom(ifile, odir, Afpy_Job)


if __name__ == '__main__':
    main()
