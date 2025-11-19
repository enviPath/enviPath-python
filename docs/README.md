# Automatic documentation with Sphinx

In this small tutorial the framework of the automatic documentation wants to be explained.

## Generation of .html files locally

1. Create a virtual environment (with conda or venv) and activate it.  For conda: 
   ```
   conda create -n "docs"
   conda activate docs
   ```
2. Move to the docs folder and run:
   ```
   pip install -r requirements.txt
   ```
   `myst-nb` module allows to create .html tutorial pages from raw jupyter notebooks (more info 
   [here](https://myst-nb.readthedocs.io/en/latest/quickstart.html)). `sphinx_copybutton` allows for a copy button to
   appear next to the code snippets on the jupyter-notebook-based tutorials.
3. On that same folder run: ```make html```
4. You should have the .html files on the docs/build/html folder.
5. Open ```index.html``` with your favorite browser.

## How to change change the webpage content

[Sphinx](https://www.sphinx-doc.org/en/master/) accepts pages in multiple formats, we are using here
[ReStructured Text (.rst)](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#rst-primer).
In order to edit the content of a page, you only have to go to the corresponding .rst file on source and edit its content.

This is valid also for tutorials, which are available as jupyter notebooks in source/tutorials directory. To learn
more about format specifics of these jupyter notebooks and how to best personalize them to your own taste, I recommend
checking out the [myst-nb](https://myst-nb.readthedocs.io/en/latest/quickstart.html) project.

## On readthedocs server

For the your changes to be available in the [readthedocs server](https://envipath-python.readthedocs.io/en/develop/) 
you only have to merge your changes to develop using a pull request. All the changes should automatically be updated. 
To check for the status of the docs build or to manually execute new docs builds, please check the readthedocs page for 
our [project](https://app.readthedocs.org/projects/envipath-python/builds/).
