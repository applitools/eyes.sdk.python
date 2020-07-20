import codecs
from os import path

here = path.dirname(path.abspath(__file__))


def get_resource(name):
    resource_dir = path.join(here, "resources")
    pth = path.join(resource_dir, name)
    with codecs.open(pth, "r", encoding="utf-8") as f:
        return f.read()
