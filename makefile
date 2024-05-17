default: build

readme:
	python make_readme.py

docs: readme
	make-docs

build: docs
	rm dist/*
	python -m build

test_upload: build
	python -m twine upload --repository testpypi dist/*
