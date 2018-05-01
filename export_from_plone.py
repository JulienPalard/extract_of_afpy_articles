import base64
from DateTime import DateTime
import json
from Products.Five.browser import BrowserView
from Products.CMFCore.interfaces import IFolderish

EXPORT_ATTRIBUTES = ["portal_type", "id"]
EXPORT_BINARY = True


class ExportFolderAsJSON(BrowserView):
    """
    Exports the current context folder Archetypes as JSON.

    Returns downloadable JSON from the data.
    """

    def convert(self, value):
        """
        Convert value to more JSON friendly format.
        """
        if isinstance(value, DateTime):
            # Zope DateTime
            # https://pypi.python.org/pypi/DateTime/3.0.2
            return value.ISO8601()
        elif hasattr(value, "isBinary") and value.isBinary():

            if not EXPORT_BINARY:
                return None

            # Archetypes FileField and ImageField payloads
            # are binary as OFS.Image.File object
            data = getattr(value.data, "data", None)
            if not data:
                return None
            return base64.b64encode(data)
        else:
            # Passthrough
            return value

    def grabArchetypesData(self, obj):
        """
        Export Archetypes schemad data as dictionary object.

        Binary fields are encoded as BASE64.
        """
        data = {}
        for field in obj.Schema().fields():
            name = field.getName()
            value = field.getRaw(obj)
            data[name] = self.convert(value)
        return data

    def grabAttributes(self, obj):
        data = {}
        for key in EXPORT_ATTRIBUTES:
            data[key] = self.convert(getattr(obj, key, None))
        return data

    def export(self, folder, recursive=False):
        """
        Export content items.

        Possible to do recursively nesting into the children.

        :return: list of dictionaries
        """

        array = []
        for obj in folder.listFolderContents():
            data = self.grabArchetypesData(obj)
            data.update(self.grabAttributes(obj))

            if recursive:
                if IFolderish.providedBy(obj):
                    data["children"] = self.export(obj, True)

            array.append(data)

        return array

    def __call__(self):
        """
        """
        folder = self.context.aq_inner
        data = self.export(folder)
        pretty = json.dumps(data, sort_keys=True, indent='    ')
        self.request.response.setHeader("Content-type", "application/json")
        return pretty

folder = app['afpy.org'][sys.argv[1]]  # Either jobs or news
view = ExportFolderAsJSON(folder, None)
data = view.export(folder, recursive=True)
print(json.dumps(data, sort_keys=True, indent=4))
