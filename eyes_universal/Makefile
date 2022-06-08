.PHONY: clean


dist:
	python -m pip install --upgrade wheel
	rm -rf applitools/eyes_universal/bin build eyes_universal.egg-info
	python setup.py --quiet build_py --os-name='macos' bdist_wheel --plat-name='macosx_10_7_x86_64'
	rm -rf applitools/eyes_universal/bin build eyes_universal.egg-info
	python setup.py --quiet build_py --os-name='macos' bdist_wheel --plat-name='macosx_11_0_arm64'
	rm -rf applitools/eyes_universal/bin build eyes_universal.egg-info
	python setup.py --quiet build_py --os-name='linux' bdist_wheel --plat-name='manylinux1_x86_64'
	rm -rf applitools/eyes_universal/bin build eyes_universal.egg-info
	python setup.py --quiet build_py --os-name='alpine' bdist_wheel --plat-name='musllinux_1_2_x86_64'
	rm -rf applitools/eyes_universal/bin build eyes_universal.egg-info
	python setup.py --quiet build_py --os-name='win.exe'   bdist_wheel --plat-name='win_amd64'
	rm -rf applitools/eyes_universal/bin build eyes_universal.egg-info


clean:
	rm -rf dist applitools/eyes_universal/bin build eyes_universal.egg-info
