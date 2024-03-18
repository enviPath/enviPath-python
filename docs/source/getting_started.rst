Getting Started
===============

In order to be able to use this package at its highest potential, the main enviPath objects must be known and for this
reason, we will introduce them in this section.

enviPath
--------

The enviPath object requires the URL of the instance host in order to be initialized, this information will be then
passed to the subsequently generated objects in order to allow them to retrieve information from there. This is the
most essential object and it will be used on each of our tutorials. An example of how to initialize this object
is given in the following block of code:

.. code-block:: python

    from enviPath_python import enviPath

    eP = enviPath("https://envipath.org/")

Then, once this is done you will be able to access any enviPath object by just initializing the dedicated class for that
object and passing the ``eP.requester`` and a valid ID (URL) for that specific object. For example, if we want to access
now the `(+)-Camphor` Compound from EAWAG-BBD, we can do so, as follows:

.. code-block:: python

    camphor_URL = "https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1/compound/e4fe0464-864c-4cb3-9587-5a82d6dc67fa"
    compound = Compound(eP.requester, id=camphor_URL)


