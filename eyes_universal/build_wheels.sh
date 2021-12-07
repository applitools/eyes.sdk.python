python setup.py build_py --os-names='macos' bdist_wheel --plat-name='macosx_10_7_x86_64'
rm -r applitools/eyes_universal/bin build eyes_universal.egg-info
python setup.py build_py --os-names='linux' bdist_wheel --plat-name='manylinux1_x86_64'
rm -r applitools/eyes_universal/bin build eyes_universal.egg-info
python setup.py build_py --os-names='win'   bdist_wheel --plat-name='win_amd64'
rm -r applitools/eyes_universal/bin build eyes_universal.egg-info
