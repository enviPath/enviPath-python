# Automatic documentation with Sphinx

In this small tutorial the framework of the automatic documentation wants to be explained. 
This tutorial is divided in 2 parts: the first one explains how to generate the documentation
automatically using sphinx and the second one to render the generated .rst files into the desired
format, here the generation of .html files will be explained.

Please note that if you are only interested in having the .html files, the first step is not needed, 
access directly to the [second part of the tutorial](#generation-of-html-files). 

## Sphinx-autodoc

1. Generate a virtual environment and activate it (using conda or venv, for instance).
2. Pip install sphinx ```pip install -U sphinx```
3. Run from the root folder on your terminal ```sphinx-apidoc -f -o docs/source enviPath_python```
4. Now the .rst files should have been generated on the docs/source folder and you should be ready to
   compile them into .html files.

## Generation of .html files

1. If you have skipped the first part of the tutorial, then create a virtual environment (with conda or venv) and activate it.
2. Move to the docs folder and run from the terminal ```make html```
3. You should find the .html files on the docs/build/html folder.
4. Open ```index.html``` with your favorite browser.

