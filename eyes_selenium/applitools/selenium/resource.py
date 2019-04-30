from os import path

here = path.dirname(path.abspath(__file__))


def get_resource(name):
    resource_dir = path.join(here, "resources")
    pth = path.join(resource_dir, name)
    with open(pth, "r") as f:
        return f.read()
