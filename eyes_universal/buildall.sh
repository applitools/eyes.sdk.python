python setup.py bdist_wheel --plat-name='macosx_10_7_x86_64'
rm -r build eyes_universal.egg-info
python setup.py bdist_wheel --plat-name='manylinux1_x86_64'
rm -r build eyes_universal.egg-info
python setup.py bdist_wheel --plat-name='win_amd64'
rm -r build eyes_universal.egg-info
