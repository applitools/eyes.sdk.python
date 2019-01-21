from pathlib import Path

here = Path('.').absolute()


def _packages_resolver(core=None, selenium=None, images=None):
    core_pkg, selenium_pkg, images_pkg = 'eyes_core', 'eyes_selenium', 'eyes_images'

    if core:
        pack = core_pkg
    elif selenium:
        pack = selenium_pkg
    elif images:
        pack = images_pkg
    else:
        return None
    return str(here / pack)


def test_setup_eyes_core(virtualenv):
    virtualenv.install_package(_packages_resolver(core=True),
                               build_egg=True)
    assert 'eyes-core' in virtualenv.installed_packages()


def test_setup_eyes_images(virtualenv):
    virtualenv.install_package(_packages_resolver(core=True),
                               build_egg=True)
    virtualenv.install_package(_packages_resolver(images=True),
                               build_egg=True)
    assert 'eyes-core' in virtualenv.installed_packages()
    assert 'eyes-images' in virtualenv.installed_packages()


# def test_setup_eyes_selenium(virtualenv):
#     virtualenv.install_package(_packages_resolver(core=True),
#                                build_egg=True)
#     virtualenv.install_package(_packages_resolver(selenium=True),
#                                build_egg=True)
#     assert 'eyes-core' in virtualenv.installed_packages()
#     assert 'eyes-selenium' in virtualenv.installed_packages()

def test_eyes_core_namespace_package(virtualenv):
    virtualenv.install_package(_packages_resolver(core=True),
                               build_egg=True)
    virtualenv.run('python -c "from applitools.core import *"')


def test_eyes_images_namespace_package(virtualenv):
    virtualenv.install_package(_packages_resolver(core=True),
                               build_egg=True)
    virtualenv.install_package(_packages_resolver(images=True),
                               build_egg=True)
    virtualenv.run('python -c "from applitools.images import *"')


# def test_eyes_selenium_namespace_package(virtualenv):
#     virtualenv.install_package(_packages_resolver(core=True),
#                                build_egg=True)
#     virtualenv.install_package(_packages_resolver(selenium=True),
#                                build_egg=True)
#     virtualenv.run('python -c "from applitools.selenium import *"')

