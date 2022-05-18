export PATH:=$(shell pwd)/bin:${PATH}
# Run GUI apps in headless mode
export DISPLAY=:99.0
export APPLITOOLS_BATCH_ID=$(shell python -c "import uuid;print(str(uuid.uuid4()))")

install_dev_requirements: install_test_requirements install_packages_editable
	python -m pip install --upgrade pre-commit bump2version


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


publish: eyes_selenium/dist eyes_robotframework/dist install_publish_requirements
	twine upload --verbose eyes_selenium/dist/*
	twine upload --verbose eyes_robotframework/dist/*


publish_testing: eyes_selenium/dist eyes_robotframework/dist install_publish_requirements
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


unit_tests: install_eyes_robotframework install_test_requirements
	pytest -n6 tests/unit


test_integration: install_eyes_robotframework install_test_requirements
	pytest tests/test_integration.py


generated_tests: install_eyes_selenium install_test_requirements
	chmod a+x ./coverage-tests/python_tests.sh
	npm run python:tests  --prefix ./coverage-tests


robotframework_tests: install_eyes_robotframework install_test_requirements
	pytest -n6 tests/functional/eyes_robotframework/test_integration.py::test_suite_web


selenium_tests: install_eyes_selenium install_test_requirements
	pytest -n6 tests/functional/eyes_selenium/


bin/chromedriver: CHROMEDRIVER_VERSION := $(shell curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
bin/chromedriver:
	curl -sO https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip
	mkdir -p bin
	unzip chromedriver_linux64.zip -d bin
	rm chromedriver_linux64.zip


kill_eyes_server:
	taskkill -f -im eyes-universal-win.exe || killall eyes-universal-macos || killall eyes-universal-linux


install_windows_node:
	choco install -y nodejs-lts


install_windows_python2:
	choco install python2 --version=2.7.18


install_windows_python_last:
	choco install python --version=3.10.4


install_windows_chrome:
	choco install googlechrome --x86 --ignore-checksums
	choco install chromedriver


verify_changelog:
	@if [[ ($$TRAVIS_TAG =~ ^v[0-9]+\.[0-9]+\.[0-9]+$$) ]] ;\
    then \
		SDK_VERSION=$$(echo $$TRAVIS_TAG | sed 's/[^.0-9]*//g') ;\
		CHANGELOG=$$(bash ./ci_scripts/extract_changelog.sh $$SDK_VERSION CHANGELOG.md) ;\
		if [[ -z "$$CHANGELOG" ]]; \
		then \
			echo "THE CHANGELOG IS NOT CORRECT" ;\
			exit 1 ;\
		fi ;\
	fi ;\
	echo TRAVIS_COMMIT=$$TRAVIS_COMMIT TRAVIS_TAG=$$TRAVIS_TAG SDK_VERSION=$$SDK_VERSION ;\
	echo APPLITOOLS_BATCH_ID=$$APPLITOOLS_BATCH_ID ;\
	echo $$CHANGELOG ;\


send_cron_report:
	if [[ $TRAVIS_EVENT_TYPE = cron ]] ;\
	then \
		echo "REPORTING..." ;\
		bash ./ci_scripts/all_tests_report.sh python ;\
		echo "REPORTED SUCCESSFULLY" ;\
	fi ;\


send_relese_mail: verify_changelog
	@SDK_VERSION=$$(echo $$TRAVIS_TAG | sed 's/[^.0-9]*//g') ;\
	CHANGELOG=$$(bash ./ci_scripts/extract_changelog.sh $$SDK_VERSION CHANGELOG.md) ;\
	COMMITTER_EMAIL="$$(git log -1 $$TRAVIS_COMMIT --pretty="%cE")" ;\
	if [[ ("$$ALLOWED_RELEASE_COMMITERS" =~ .*"$$COMMITTER_EMAIL".*) ]] ;\
	then \
		echo DEPLOY ;\
		TEST_COVERAGE_GAP=$$(cat ./ci_scripts/testCoverageGap.txt) ;\
		bash ./ci_scripts/send_mail.sh python "$TRAVIS_TAG" "$CHANGELOG" "$TEST_COVERAGE_GAP" ;\
	else \
		echo Committer $$COMMITTER_EMAIL is not allowed ;\
		exit 1 ;\
	fi ;\
