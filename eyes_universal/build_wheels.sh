_PYTHON_HOST_PLATFORM=macosx_10_7_x86_64 python setup.py bdist_wheel --plat-name=macosx_10_7_x86_64
rm -r applitools/eyes_universal/bin build eyes_universal.egg-info
_PYTHON_HOST_PLATFORM=manylinux1_x86_64 python setup.py bdist_wheel --plat-name=manylinux1_x86_64
rm -r applitools/eyes_universal/bin build eyes_universal.egg-info
_PYTHON_HOST_PLATFORM=win_amd64 python setup.py bdist_wheel --plat-name=win_amd64
rm -r applitools/eyes_universal/bin build eyes_universal.egg-info
