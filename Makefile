.DEFAULT_GOAL := build

source_code := src/

.PHONY: deps-python-code-quality
deps-python-code-quality: assert-ve
	ve/bin/pip install green
	ve/bin/pip install black
	ve/bin/pip install mypy
	ve/bin/pip install pylint
	ve/bin/pip install pycodestyle

.PHONY: deps-python
deps-python: assert-ve deps-python-code-quality
	ve/bin/pip install websockets
	ve/bin/pip install osc4py3

.PHONY: pylint
pylint:
	pylint $(source_code) --output-format=colorized

.PHONY: pycodestyle
pycodestyle:
	pycodestyle $(source_code)

.PHONY: mypy
mypy:
	mypy $(source_code) --strict --ignore-missing-imports

.PHONY: black-check
black-check:
	black -S $(source_code) --check
	black -S tests/**/*.py --check

.PHONY: lint
lint: mypy pylint black-check pycodestyle

.PHONY: black
black:
	black -S $(source_code)

.PHONY: test
test:
	python -m unittest

.PHONY: green
green:
	green -r -m 55

.PHONY: clean-deps-linux
clean-deps-linux:

.PHONY: clean-deps-macos
clean-deps-macos:

.PHONY: clean-os-deps
clean-os-deps:
ifeq ($(PLATFORM), darwin)
	make clean-deps-macos
else
	make clean-deps-linux
endif

.PHONY: clean-ve
clean-ve:
	rm -rf ve

.PHONY: clean-pycs
clean-pycs:
	find . -name '*.pyc' -delete

.PHONY: clean
clean: clean-ve clean-pycs clean-os-deps

.PHONY: ve
ve:
	[ -d ve ] || python3 -m venv ve

.PHONY: dist-macos
dist-macos:
	pyinstaller gui.py --onefile --name='Countdown Player' --osx-bundle-identifier com.benjiyork.countdown-player --windowed -y --icon=icons/iconfinder_1_next-play_1210566.icns

.PHONY: dist-linux
dist-linux: # Untested
	pyinstaller gui.py --onefile --name='Countdown Player' --windowed -y

.PHONY: dist
dist:
ifeq ($(PLATFORM), darwin)
	make dist-macos
else
	make dist-linux
endif


.PHONY: assert-ve
assert-ve:
	[[ `which python` =~ .*benji.* ]] || (printf '\nPlease source ve/bin/activate and try again.\n\n'; exit 1)

.PHONY: build
build: ve deps-python
