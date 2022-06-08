export PATH:=$(shell pwd)/bin:${PATH}
# Run GUI apps in headless mode
export DISPLAY=:99.0
export APPLITOOLS_BATCH_ID=$(shell python -c "import uuid;print(str(uuid.uuid4()))")

install_dev_requirements: install_test_requirements install_packages_editable
	python -m pip install --upgrade pre-commit


install_packages_editable: eyes_universal eyes_selenium eyes_robotframework
	for PACK in $^; do echo cd $$PACK && python -m pip install --upgrade --editable $$PACK; done


install_eyes_selenium: eyes_selenium/dist eyes_robotframework/dist install_eyes_universal
	python -m pip install eyes_selenium/dist/*


install_eyes_robotframework: eyes_selenium/dist eyes_robotframework/dist install_eyes_universal
	python -m pip install eyes_selenium/dist/* eyes_robotframework/dist/*


install_eyes_universal: eyes_universal/dist
	python -m pip install --no-index --find-links=file:eyes_universal/dist/ eyes_universal


install_test_requirements:
	python -m pip install --requirement requirements-test.txt


uninstall:
	python -m pip uninstall -y eyes-robotframework eyes-selenium eyes-universal


publish_eyes_selenium: CHANGELOG := $(shell bash ./ci_scripts/extract_changelog.sh ${SDK_VERSION} CHANGELOG.md)
publish_eyes_selenium: TEST_COVERAGE_GAP := $(shell cat ./ci_scripts/testCoverageGap.txt)
publish_eyes_selenium: eyes_selenium/dist eyes_robotframework/dist install_publish_requirements
	bash ./ci_scripts/send_mail.sh python ${SDK_VERSION} "${CHANGELOG}" "${TEST_COVERAGE_GAP}"
	twine upload --verbose eyes_selenium/dist/*
	twine upload --verbose eyes_robotframework/dist/*


publish_testing_eyes_selenium: CHANGELOG := $(shell bash ./ci_scripts/extract_changelog.sh ${SDK_VERSION} CHANGELOG.md)
publish_testing_eyes_selenium: TEST_COVERAGE_GAP := $(shell cat ./ci_scripts/testCoverageGap.txt)
publish_testing_eyes_selenium: eyes_selenium/dist eyes_robotframework/dist install_publish_requirements
	echo bash ./ci_scripts/send_mail.sh python ${SDK_VERSION} "${CHANGELOG}" "${TEST_COVERAGE_GAP}"
	twine upload --verbose --repository testing eyes_selenium/dist/*
	twine upload --verbose --repository testing eyes_robotframework/dist/*


publish_eyes_universal: eyes_universal/dist install_publish_requirements
	twine upload --verbose eyes_universal/dist/*


publish_testing_eyes_universal: eyes_universal/dist install_publish_requirements
	twine upload --verbose --repository testing eyes_universal/dist/*


install_publish_requirements:
	python -m pip install twine


dist: eyes_universal/dist eyes_selenium/dist eyes_robotframework/dist


eyes_universal/dist:
	cd eyes_universal && make dist


eyes_selenium/dist:
	cd eyes_selenium && python setup.py --quiet sdist


eyes_robotframework/dist:
	cd eyes_robotframework && python setup.py --quiet sdist


clean:
	cd eyes_universal && make clean
	rm -rf eyes_selenium/dist eyes_selenium/eyes_selenium.egg-info
	rm -rf eyes_robotframework/dist eyes_robotframework/src/eyes_robotframework.egg-info
	rm -rf dist
	rm -rf bin


gen_robot_docs:
	python -m robot.libdoc --format html EyesLibrary docs/eyes_robotframework/keywords.html


eyes_selenium_unit_tests: install_eyes_robotframework install_test_requirements
	pytest -n6 tests/unit


eyes_selenium_installation_tests: install_eyes_robotframework install_test_requirements
	pytest tests/test_integration.py


eyes_selenium_generated_tests: install_eyes_selenium install_test_requirements
	chmod a+x ./coverage-tests/python_tests.sh
	npm run python:tests  --prefix ./coverage-tests


eyes_robotframework_functional_tests: install_xvfb install_eyes_robotframework install_test_requirements
	xvfb-run --auto-servernum pytest -n6 tests/functional/eyes_robotframework/test_integration.py::test_suite_web


eyes_selenium_functional_tests: install_eyes_selenium install_test_requirements
	pytest -n6 tests/functional/eyes_selenium/


bin/chromedriver: CHROMEDRIVER_VERSION := $(shell curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
bin/chromedriver:
	curl -sO https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
	mkdir -p bin
	unzip chromedriver_linux64.zip -d bin
	rm chromedriver_linux64.zip


install_xvfb:
	sudo apt-get install -y xvfb
