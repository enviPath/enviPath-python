Objects
=======

To use the enviPath-python package, it is helpful to know the main enviPath objects. Some of these objects try to represent
common known chemical entities, such as compounds and reactions. However, they should be understood as a `programatic
way <https://realpython.com/python-classes/>`_ to represent those broadly known entities.

.. currentmodule:: enviPath_python.enviPath

enviPath
--------

The :class:`enviPath` object requires the URL of the instance host in order to be initialized, this information will be then
passed to the subsequently generated objects in order to allow them to retrieve information. This is the
most essential object and it will be used in each of our tutorials. An example of how to initialize this object
is given in the following block of code:

.. code-block:: python

    from enviPath_python import enviPath

    eP = enviPath("https://envipath.org/")

Once this is done you will be able to access any enviPath object by initializing the dedicated class for that
object and passing the ``eP.requester`` and a valid ID (URL) for that specific object. For example, if we want to access
now the `(+)-Camphor` compound from EAWAG-BBD, we can do so as follows:

.. code-block:: python

    from enviPath_python.objects import Compound

    camphor_URL = "https://envipath.org/package/32de3cf4-e3e6-4168-956e-32fa5ddb0ce1/compound/e4fe0464-864c-4cb3-9587-5a82d6dc67fa"
    compound = Compound(eP.requester, id=camphor_URL)



Package
-------

.. currentmodule:: enviPath_python.objects

:class:`Package` is one of the most fundamental objects in enviPath. It is the object where collections of other objects, such as
Compounds, Reactions, Pathways, etc. are stored. A package can be public or private, on the first case no login will be
required to access the data, however on the second case it will be necessary to do so. There is a dedicated
:ref:`tutorial<accessing_packages>` to show how to access both types of packages and yet another
:ref:`tutorial<create_package>` to help you see how to create a package and start to add data to it.

Compound
--------

A :class:`Compound` is an enviPath object within a :ref:`Package` and essentially stores all the molecular information
organized into :ref:`Compound Structure` objects. In other words, a Compound can be thought of as a container of Compound
Structures. A Compound can be
created using a valid `SMILES <https://pubs.acs.org/doi/abs/10.1021/ci00057a005>`_ with the
:meth:`Compound.create` method. After a Compound is created,
the ``smiles`` will be used to create a default Compound Structure.
The default Compound Structure can be
obtained with the :meth:`Compound.get_default_structure` method. This default structure will be accessed when the
:meth:`Compound.get_smiles` is called. Both Compounds and Compound Structures are created automatically with
:ref:`Pathway` prediction (:meth:`Package.predict`) and will be directly associated with a predicted :ref:`Node`.

Compound Structure
------------------

A :class:`CompoundStructure` object can be understood as the object that stores all the molecule related information, i.e. SMILES,
molecular weight, formula, etc. It is associated and stored under a single :ref:`Compound`. The logic behind the idea
of Compound Structure is that several molecules can be stored under the same Compound and, in this way, one could add
information about the carbon labelled chemical compound that was used to identify a given chemical compound in an experimental set up
or to store different stereomers under the same Compound. As in the case of the Compound they can also be created
by passing the SMILES but additionally one should also pass the parent, i.e. the :ref:`Compound` which will be associated
with.

Reaction
--------

A :class:`Reaction` is an enviPath object that represents biotransformation reaction, it connects substrates with
products, each of them represented as a :ref:`Compound Structure`. Usually reactions are
associated as well with a :ref:`Rule`. A user can create a Reaction using the :meth:`Reaction.create` method by specifying
a valid `SMIRKS <https://www.daylight.com/dayhtml/doc/theory/theory.smirks.html>`_ and the package where the Reaction
will be stored. A Reaction can also be created using a list of ``educt`` and ``product`` instead of a SMIRKS.
Additionally, Reaction objects are created automatically with
:ref:`Pathway` prediction and they get directly associated with a predicted :ref:`Edge`.

Rule
----

A :class:`Rule` enviPath object represents a biotransformation rule and are used for the prediction of pathways. They do so by
leveraging SMIRKS Reaction Patterns that identify functional groups and apply the rule whenever the reactant filter pattern
condition is met. Because they are generalization of reactions, they can as well be associated with enzymes that
catalyze the associated reaction and their EC numbers can be retrieved using the
:meth:`Rule.get_ec_numbers` method. On the
enviPath-python implementation of the Rule object, it was decided to represent it as an abstract class, however 3
distinct non-abstract classes inherit from it and can therefore be instantiated. Those are :meth:`SimpleRule`,
:meth:`SequentialCompositeRule` and :meth:`ParallelCompositeRule`.

Pathway
-------

A :class:`Pathway` is an enviPath object that represents a biodegradation pathway and stores the information of the compounds
and reactions involved in :ref:`Node` and :ref:`Edge` objects, respectively.
Being enviPath a database for biodegradation data makes Pathway one of the most fundamental objects to know.
Pathways can be generated manually by calling :meth:`Pathway.create` method, from there on
one can add compounds (nodes) and reactions (edges) to it using :meth:`Pathway.add_node` and
:meth:`Pathway.add_edge` methods, respectively. Pathways can also be predicted by invoking the method
:meth:`Package.predict`, which will use the provided
setting to extract the :ref:`Relative Reasoning` model and use it to predict new compounds based on the
set rules that it has been trained on.

Node
~~~~

The :class:`Node` enviPath object represents a :ref:`Compound` on a :ref:`Pathway`. For this reason it has an associated
:ref:`Compound Structure`, that can be accessed through the :meth:`Node.get_default_structure`
method.

Edge
~~~~

The :class:`Edge` enviPath object represents a :ref:`Reaction` on a :ref:`Pathway`, which can be accessed through the
:meth:`Edge.get_reaction` method. Additionally, its corresponding subtrate and products can be
obtained using :meth:`Edge.get_start_nodes` and :meth:`Edge.get_end_nodes`,
respectively.

Relative Reasoning
------------------

A :class:`RelativeReasoning` enviPath object can be understood as the model that is used to generate pathway predictions. This
is a powerful object since it allows the user to generate direct predictions without the need of generating pathways.
This can be achieved for example with the method :meth:`RelativeReasoning.classify_smiles`

Scenario
--------

A :class:`Scenario` enviPath object represents the experimental conditions that were used for a given biodegradation pathway.
Ideally it links to a reference article where the given experiment is thoroughly described. A Scenario can be attached
to **any** other enviPath object

Additional Information
~~~~~~~~~~~~~~~~~~~~~~

:class:`AdditionalInformation` objects store each a experimental condition, there are numerous classes that inherit from
:class:`AdditionalInformation`, to mention some
:class:`AcidityAdditionalInformation` or :class:`HalfLifeAdditionalInformation`.
This tutorial#TODO shows how one can access the information contained in a :ref:`Scenario` to retrieve their half lives.