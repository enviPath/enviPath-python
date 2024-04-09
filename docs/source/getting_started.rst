Getting Started
===============

To use the enviPath-python package, it is helpful to know the main enviPath objects. We will introduce them in this
section.

enviPath
--------

The enviPath object requires the URL of the instance host in order to be initialized, this information will be then
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

Package is one of the most fundamental objects in enviPath. It is the object where collections of other objects, such as
Compounds, Reactions, Pathways, etc. are stored. A package can public or private, on the first case no login will be
required to access the data, however on the second case it will be necessary to do so. There is a dedicated
:ref:`tutorial<accessing_packages>` to show how to access both types of packages. Additionally, this
:ref:`tutorial<create_package>` will help you to see how to create a package and start to add data to it.

Compound
--------

A Compound is an enviPath object that is stored in a :ref:`Package` and basically stores different
:ref:`Compound Structure`. One of them is defined to be the default Compound Structure and that one is the one that
will be more easily accessible (for example, when the :meth:`enviPath_python.objects.Compound.get_smiles` is called). It can be
created using a valid `SMILES <https://pubs.acs.org/doi/abs/10.1021/ci00057a005>`_ on the
:meth:`enviPath_python.objects.Compound.create` method and whenever this happens,
this `smiles` gets passed to a default Compound Structure and both the Compound and its corresponding Compound Structure
are created. One way of thinking of an enviPath Compound is as a container of Compound Structures. A Compound is usually
assigned to a :ref:`Pathway` via a :ref:`Node` and additionally, a connection to other external databases (PubChem,
KEGG, etc.) can be triggered through the API. Compound and Compound Structure objects are created automatically with
pathway prediction and the latter get directly associated with a predicted :ref:`Node`.

Compound Structure
------------------

A Compound Structure object can be understood as the object that stores all the molecule related information, i.e. SMILES,
molecular weight, formula, etc. It is associated and stored under a single :ref:`Compound`. The logic behind the idea
of Compound Structure is that several molecules can be stored under the same Compound and, in this way, one could add
information about a carbon labelled Compound that has been used to identify a given Compound in an experimental set up
or to store different stereomers under the same Compound, etc. As in the case of the Compound they can also be created
by passing the SMILES but additionally one should also pass the parent, i.e. the Compound to which it will be associated
with.

Reaction
--------

A Reaction is an enviPath object that represents biotransformation reactions, it connects therefore a substrate or
set of substrates with a set of products, each of them represented as a :ref:`Compound Structure`. Usually reactions are
associated as well with a :ref:`Rule`. A Reaction can be created using
`SMIRKS <https://www.daylight.com/dayhtml/doc/theory/theory.smirks.html>`_ and its stored on the package level. For this
reason, a Reaction can either be created using either SMIRKS or by passing both a list of ``educt`` and ``preduct`` to
the :meth:`enviPath_python.objects.Reaction.create` method. Additionally, Reaction objects are created automatically with
pathway prediction and they get directly associated with a predicted :ref:`Edge`.

Rule
----

A biotransformation rule is a generalization of reactions and are used for the prediction of pathways. They do so by
leveraging SMIRKS Reaction Patterns that identify functional groups and apply the rule whenever the reactant filter pattern
condition is met. Because they are generalization of reactions, they can as well be associated with enzymes that
catalyze the associated reaction and their EC numbers can be retrieved using
:meth:`enviPath_python.objects.Rule.get_ec_numbers` method. On the
enviPath-python implementation of the Rule object, it was decided to represent it as an abstract class, however 3
distinct non-abstract classes inherit from it and can therefore be instantiated. Those are :meth:`enviPath_python.objects.SimpleRule`,
:meth:`enviPath_python.objects.SequentialCompositeRule` and :meth:`enviPath_python.objects.ParallelCompositeRule`.

Pathway
-------

A Pathway is an enviPath object that stores :ref:`Node` and :ref:`Edge` objects and represents a biodegradation
pathway. Being enviPath a database for biodegradation data makes Pathway one of the most fundamental objects to know.
Pathways can be generated manually by calling :meth:`enviPath_python.objects.Pathway.create` method, from there on
one can add to it nodes and edges using :meth:`enviPath_python.objects.Pathway.add_node` and
:meth:`enviPath_python.objects.Pathway.add_edge` methods, respectively. Pathways can also be predicted by, for
example, invoking the method :meth:`enviPath_python.objects.Package.predict`, which will use the provided
setting to extract the :ref:`Relative Reasoning` model and use it to predict new compounds based on the
set rules that it has been trained on.

Node
~~~~

The Node enviPath object represents a :ref:`Compound` on a :ref:`Pathway`. For this reason it has an associated
:ref:`Compound Structure`, that can be accessed through the :meth:`enviPath_python.objects.Node.get_default_structure`
method.

Edge
~~~~

The Edge enviPath object represents a :ref:`Reaction` on a :ref:`Pathway`, which can be accessed through the
:meth:`enviPath_python.objects.Edge.get_reaction` method. Additionally, its corresponding subtrate and products can be
obtained using :meth:`enviPath_python.objects.Edge.get_start_nodes` and :meth:`enviPath_python.objects.Edge.get_end_nodes`,
respectively.

Relative Reasoning
------------------

A Relative Reasoning enviPath object can be understood as the model that is used to generate pathway predictions. This
is a powerful object since it allows the user to generate direct predictions without the need of generating pathways.
This can be achieved for example with the method :meth:`enviPath_python.objects.RelativeReasoning.classify_smiles`

Scenario
--------

A Scenario enviPath object represents the experimental conditions that were used for a given biodegradation pathway.
Ideally it links to a reference article where the given experiment is thoroughly described. A Scenario can be attached
to **any** other enviPath object

Additional Information
~~~~~~~~~~~~~~~~~~~~~~

Additional Information objects store each a experimental condition, there are numerous classes that inherit from
:class:`enviPath_python.objects.AdditionalInformation`, to mention some
:class:`enviPath_python.objects.AcidityAdditionalInformation` or :class:`enviPath_python.objects.HalfLifeAdditionalInformation`.
This tutorial#TODO shows how one can access the information contained in a :ref:`Scenario` to retrieve their half lives.