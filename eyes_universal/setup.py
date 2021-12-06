from setuptools import setup
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel


class bdist_wheel(_bdist_wheel):
    def run(self):
        _, __, plat = _bdist_wheel.get_tag(self)
        if "macos" in plat:
            platform_bin[:] = ["bin/*-macos"]
        elif "linux" in plat:
            platform_bin[:] = ["bin/*-linux"]
        elif "win" in plat:
            platform_bin[:] = ["bin/*-win.exe"]
        _bdist_wheel.run(self)


platform_bin = ["bin/*"]

setup(
    package_data={"": platform_bin},
    cmdclass={"bdist_wheel": bdist_wheel},
)
