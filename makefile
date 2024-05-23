default: build

readme:
	python make_readme.py

docs: readme
	./make-docs

build: docs
	rm dist/*
	python -m build
 
check_upload: build
	python -m twine check dist/*

test_upload: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*
