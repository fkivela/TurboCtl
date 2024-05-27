default: build

files:
	python make_files.py

docs: files
	./make-docs

build: docs
    # The -f makes this work even if dist/ is empty.
	rm -f dist/*
	python -m build
 
check_upload: build
	python -m twine check dist/*

test_upload: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*
