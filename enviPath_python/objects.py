# Copyright 2023 enviPath UG & Co. KG
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
# TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import re
import json
from abc import ABC, abstractmethod
from collections import namedtuple, defaultdict
from io import BytesIO
from typing import List, Optional, Union
from enviPath_python.enums import Endpoint, ClassifierType, FingerprinterType, AssociationType, EvaluationType, \
    Permission


class enviPathObject(ABC):
    """
    Base class for an enviPath object.
    """

    def __init__(self, requester, *args, **kwargs):
        """
        Constructor for any instance derived from enviPathObject.

        :param requester: The enviPathRequester used for getting this object.
        :param args: additional positional arguments.
        :param kwargs: additional named arguments. 'name' and 'id' are mandatory.
        """
        self.requester = requester
        # Make name optional to allow object creation with id only
        if 'name' in kwargs:
            self.name = kwargs['name']
        self.id = kwargs['id']
        self.loaded = False

    def get_type(self):
        """
        Gets the class name as string.

        :return: The class name as string. E.g. 'Package'
        """
        return type(self).__name__

    def __str__(self):
        """
        Simple string representation including type, name and id.

        :return: The object as string.
        """
        return '{}: {} ({})'.format(self.get_type(), self.get_name(), self.id)

    def __repr__(self):
        """
        Same as __str__.

        :return: same as __str__.
        """
        return str(self)

    def _get(self, field):
        """
        Tries to get a field of the object. As objects are only initialized with 'name' and 'id' all other
        fields must be fetched from the enviPath instance. This fetches data only once.
        If the field is missing after getting the data from the enviPath instance an exception is risen.
        Should only be called by 'public' functions as they should implement appropriate object creation if value
        of requested field is an enviPathObject instance again.

        :param field: The field of interest.
        :return: The value of the field.
        """
        if not self.loaded:
            obj_fields = self._load()
            for k, v in obj_fields.items():
                setattr(self, k, v)
                self.loaded = True
        if not hasattr(self, field):
            raise ValueError('{} has no property {}'.format(self.get_type(), field))

        return getattr(self, field)

    def get_id(self):
        """
        Get the id of the envipath object

        :return: The id of the object
        """
        return self.id

    def __eq__(self, other):
        if type(other) is type(self):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def get_name(self):
        """
        Get the name of the envipath object

        :return: The name of the object
        """
        return self._get('name')

    def get_description(self):
        """
        Get the description of the envipath object

        :return: The description of the object
        """
        return self._get('description')

    def _load(self):
        """
        Fetches data from the enviPath instance via the enviPathRequester provided at objects creation.

        :return: json containing the server response.
        """
        res = self.requester.get_request(self.id).json()
        return res

    def get_json(self):
        """
        Returns the objects plain JSON fetched from the instance.

        :return: A JSON object returned by the API.
        """
        return self.requester.get_json(self.id)

    def _create_from_nested_json(self, member: Union[str, list], nested_object_type) -> List:
        """
        Get a list of `nested_object_type` enviPath objects. Whenever member is a string, a get request
        takes place and retrieves the data available on `self.id` as a json, however `member` can also be a list of
        json whose information encodes the necessary properties to define a `nested_object_type`. In both cases, this
        function return a List of `nested_object_type` enviPath objects.

        :param member: The member or list of members that wants to accessed
        :param nested_object_type: the envipath object that wants to be created from the requested json data
        :return: list
        """
        res = []

        if isinstance(member, str):
            plain_objs = self._get(member)
        else:
            plain_objs = member

        for plain_obj in plain_objs:
            res.append(nested_object_type(self.requester, **plain_obj))
        return res

    def delete(self):
        """
        Deletes the object denoted by the internally maintained field `id`.

        :return: None
        """
        if not hasattr(self, 'id') or self.id is None:
            raise ValueError("Unable to delete object due to missing id!")
        self.requester.delete_request(self.id)
        self.id = None
        # Removed potential cached members
        for key in list(self.__dict__.keys()):
            self.__delattr__(key)

    def refresh(self):
        # TODO clear internal cache and fetch json again
        pass


class ReviewableEnviPathObject(enviPathObject, ABC):

    def get_aliases(self) -> List[str]:
        """
        Get the aliases of this object

        :return: A list of the aliases
        :rtype: list
        """
        return self._get('aliases')

    def get_review_status(self) -> str:
        """
        Gets if the current object has been reviewed.

        :return: A string where if the object is reviewed has value `'reviewed'`
        :rtype: str
        """
        return self._get('reviewStatus')

    def is_reviewed(self) -> bool:
        """
        Checks if the object has been review or not

        :return: `True` if the object is reviewed, else `False`
        :rtype: bool
        """
        return 'reviewed' == self.get_review_status()

    def get_scenarios(self) -> List['Scenario']:
        """
        Gets the scenarios of this object

        :return: A list of scenarios
        :rtype: list
        """
        res = []
        plain_scenarios = self._get('scenarios')
        for plain_scenario in plain_scenarios:
            res.append(Scenario(self.requester, **plain_scenario))
        return res

    # Attaches an already created Scenario to the object
    def add_scenario(self, scenario: 'Scenario') -> None:
        """
        Adds the given scenario to the current object

        :param scenario: the Scenario object to be added
        :type scenario: Scenario
        :return: None
        """
        headers = {'referer': self.id}
        payload = {'scenario': scenario.get_id()}
        res = self.requester.post_request(self.id, headers=headers, payload=payload, allow_redirects=True)
        return

    @abstractmethod
    def copy(self, package: 'Package', debug=False):
        """
        Copies the object into the given package

        :param package: the package to be copied to
        :type package: Package
        :param debug: whether to add more verbosity or not to the method
        :type debug: bool
        :return: None
        """
        pass


# TODO change to reviewable
class Package(enviPathObject):
    """
    Class that implements a package envipath object
    """
    def set_description(self, desc: str) -> None:
        """
        Sets the description of the package

        :param desc: the description of the package
        :type desc: str
        :return:
        """
        payload = {
            'packageDescription': (None, desc),
        }
        self.requester.post_request(self.id, files=payload)
        setattr(self, "description", desc)

    def add_compound(self, smiles: str, name: str = None, description: str = None, inchi: str = None) -> 'Compound':
        """
        Adds the compound to the package

        :param smiles: the SMILES of the compound
        :param name: the name of the compound
        :param description: the description of the compound
        :param inchi: the InChI of the compound
        :return: The enviPath Compound
        :rtype: Compound
        """
        return Compound.create(self, smiles, name=name, description=description, inchi=inchi)

    def get_compounds(self) -> List['Compound']:
        """
        Gets all compounds of the package.

        :return: List of Compound objects.
        """
        res = self.requester.get_objects(self.id + '/', Endpoint.COMPOUND)
        return res

    def add_simple_rule(self, smirks: str, name: str = None, description: str = None,
                        reactant_filter_smarts: str = None, product_filter_smarts: str = None,
                        immediate: str = None) -> 'SimpleRule':
        """
        Adds a SimpleRule to the package

        :param smirks: The SMIRKS of the simple rule
        :param name: The name of the rule
        :param description: The description of the rule
        :param reactant_filter_smarts: a filter for the reactant
        :param product_filter_smarts: a filter for the product
        :param immediate: the immediate of the SimpleRule
        :return: The SimpleRule that has been defined
        """
        return SimpleRule.create(self, smirks, name=name, description=description,
                                 reactant_filter_smarts=reactant_filter_smarts,
                                 product_filter_smarts=product_filter_smarts, immediate=immediate)

    def add_sequential_composite_rule(self, simple_rules: List['SimpleRule'], name: str = None, description: str = None,
                                      reactant_filter_smarts: str = None, product_filter_smarts: str = None,
                                      immediate: str = None) -> 'SequentialCompositeRule':
        """
        Adds a SequentialCompositeRule to the package

        :param simple_rules: A list of SimpleRule that compose the SequentialCompositeRule
        :param name: The name of the rule
        :param description: The description of the rule
        :param reactant_filter_smarts: a filter for the reactant
        :param product_filter_smarts: a filter for the product
        :param immediate: the immediate of the SequentialCompositeRule
        :return: The SequentialCompositeRule that has been defined
        """
        return SequentialCompositeRule.create(self, simple_rules, name=name, description=description,
                                              reactant_filter_smarts=reactant_filter_smarts,
                                              product_filter_smarts=product_filter_smarts, immediate=immediate)

    def add_parallel_composite_rule(self, simple_rules: List['SimpleRule'], name: str = None, description: str = None,
                                    reactant_filter_smarts: str = None, product_filter_smarts: str = None,
                                    immediate: str = None) -> 'ParallelCompositeRule':
        """
        Adds a ParallelCompositeRule to the package

        :param simple_rules: A list of SimpleRule that compose the ParallelCompositeRule
        :param name: The name of the rule
        :param description: The description of the rule
        :param reactant_filter_smarts: a filter for the reactant
        :param product_filter_smarts: a filter for the product
        :param immediate: the immediate of the ParallelCompositeRule
        :return: The ParallelCompositeRule that has been defined
        """
        return ParallelCompositeRule.create(self, simple_rules, name=name, description=description,
                                            reactant_filter_smarts=reactant_filter_smarts,
                                            product_filter_smarts=product_filter_smarts, immediate=immediate)

    def get_rules(self) -> List['Rule']:
        """
        Gets all rules of the package.

        :return: List of Rule objects.
        """
        res = self.requester.get_objects(self.id + '/', Endpoint.RULE)
        return res

    def add_reaction(self, smirks: str = None, educt: 'CompoundStructure' = None, product: 'CompoundStructure' = None,
                     name: str = None, description: str = None, rule: 'Rule' = None):
        """
        Adds a Reaction to the package

        :param smirks: The SMIRKS of the simple rule
        :param educt: The CompoundStructure of the reactants
        :param product: The CompoundStructure of the products
        :param name: The name of the rule
        :param description: The description of the Reaction
        :param rule: The rule with which the reaction is associated with
        :return: The Reaction that has been defined
        """
        return Reaction.create(self, smirks, educt, product, name, description, rule)

    def get_reactions(self) -> List['Reaction']:
        """
        Gets all reactions of the package.

        :return: List of Reaction objects.
        """
        res = self.requester.get_objects(self.id + '/', Endpoint.REACTION)
        return res

    def add_pathway(self, smiles: str, name: str = None, description: str = None,
                    root_node_only: bool = False, setting: 'Setting' = None) -> 'Pathway':
        """
        Adds a Pathway to the package

        :param smiles: Smiles of root node compound
        :param name: the name for the pathway
        :param description: the description of the pathway
        :param root_node_only: If False, goes to pathway prediction mode
        :param setting: Setting for pathway prediction
        :return: The Pathway that has been defined
        """
        return Pathway.create(self, smiles, name, description, root_node_only, setting)

    def predict(self, smiles: str, name: str = None, description: str = None,
                root_node_only: bool = False, setting: 'Setting' = None) -> 'Pathway':
        """
        Alias for add_pathway()

        :param smiles: Smiles of root node compound
        :param name: the name for the pathway
        :param description: the description of the pathway
        :param root_node_only: If False, goes to pathway prediction mode
        :param setting: Setting for pathway prediction
        :return: The Pathway that has been defined
        """
        return self.add_pathway(smiles, name, description, root_node_only, setting)

    def get_pathways(self) -> List['Pathway']:
        """
        Gets all pathways of the package.

        :return: List of Pathway objects.
        """
        res = self.requester.get_objects(self.id + '/', Endpoint.PATHWAY)
        return res

    def add_relative_reasoning(self, packages: List['Package'], classifier_type: ClassifierType,
                               eval_type: EvaluationType, association_type: AssociationType,
                               evaluation_packages: List['Package'] = None,
                               fingerprinter_type: FingerprinterType = FingerprinterType.ENVIPATH_FINGERPRINTER,
                               quickbuild: bool = True, use_p_cut: bool = False, cut_off: float = 0.5,
                               evaluate_later: bool = True, name: str = None) -> 'RelativeReasoning':
        """
        Create a relative reasoning object

        :param package: The package object in which the model is created
        :param packages: List of package objects on which the model is trained
        :param classifier_type: Classifier options:
                                Rule-Based : ClassifierType("RULEBASED")
                                Machine Learning-Based (MLC-BMaD) :  ClassifierType("MLCBMAD")
                                Machine Learning-Based (ECC) : ClassifierType("ECC")
        :param eval_type: Evaluation type:
            Single Generation : EvaluationType("single")
            Single + Multiple Generation : EvaluationType("multigen")
        :param association_type: Association type:
            AssociationType("DATABASED")
            AssociationType("CALCULATED"), default
        :param evaluation_packages: List of package objects on which the model is evaluated. If none, the classifier
            is evaluated in a 100-fold holdout model using a 90/10 split ratio.
        :param fingerprinter_type: Default: MACS Fingerprinter ("ENVIPATH_FINGERPRINTER")
        :param quickbuild: Faster evaluation, default: False
        :param use_p_cut:  Default: False
        :param cut_off: The cutoff threshold used in the evaluation. Default: 0.5
        :param evaluate_later: Only build the model, and not proceed to evaluation. Default: False
        :param name:  Name of the model
        :return: RelativeReasoning object
        """
        return RelativeReasoning.create(self, packages, classifier_type, eval_type, association_type,
                                        evaluation_packages=evaluation_packages, fingerprinter_type=fingerprinter_type,
                                        quickbuild=quickbuild, use_p_cut=use_p_cut, cut_off=cut_off,
                                        evaluate_later=evaluate_later, name=name)

    def get_relative_reasonings(self) -> List['RelativeReasoning']:
        """
        Gets all relative reasonings of the packages.

        :return: List of RelativeReasoning objects.
        """
        res = self.requester.get_objects(self.id + '/', Endpoint.RELATIVEREASONING)
        return res

    def get_scenarios(self) -> List['Scenario']:
        """
        Gets all scenarios of the package.

        :return: List of Scenario objects.
        """
        res = self.requester.get_objects(self.id + '/', Endpoint.SCENARIO)
        return res

    def export_as_json(self) -> dict:
        """
        Exports the entire package as json.

        :return: A dictionary containing all data stored in this package.
        """
        params = {
            'exportAsJson': 'true',
        }
        raw_content = self.requester.get_request(self.id, params=params, stream=True).content
        buffer = BytesIO(raw_content)
        buffer.seek(0)
        return json.loads(buffer.read().decode())

    def set_access_for_user(self, obj: Union['Group', 'User'], perm: Permission) -> None:
        """
        Gives `perm` permission to the list of user or groups `obj`

        :param obj: a list of user or groups to give access to
        :param perm: the permission to be given
        :return:
        """
        # Due to multipart/form-data add tuples as payload
        payload = {
            'permissions': (None, 'change'),
            'ppsURI': (None, obj.get_id()),
        }

        if perm == Permission.READ:
            payload['read'] = (None, 'on')

        if perm == Permission.WRITE:
            payload['write'] = (None, 'on')

        self.requester.post_request(self.id, files=payload, allow_redirects=False)

    # TODO typing for ep or being consistent with eP.requester...
    @staticmethod
    def create(ep, group: 'Group', name: str = None, description: str = None) -> 'Package':
        """
        Creates the package

        :param ep: an enviPath object
        :param group: the group to which assign the package
        :param name: the name of the package
        :param description: the description of the package
        :return: An enviPath_python Package with an allocated identifier on the enviPath server
        """
        # TODO add type hint for ep and get rid of cyclic import
        package_payload = dict()
        package_payload['groupURI'] = group.get_id()
        if name:
            package_payload['packageName'] = name
        if description:
            package_payload['packageDescription'] = description

        url = '{}{}'.format(ep.get_base_url(), Endpoint.PACKAGE.value)
        res = ep.requester.post_request(url, payload=package_payload, allow_redirects=False)
        res.raise_for_status()
        return Package(ep.requester, id=res.headers['Location'])

    def copy(self, target_package: 'Package', debug=False):
        """
        Copies the object into the given package

        :param package: the package to be copied to
        :type package: Package
        :param debug: whether to add more verbosity or not to the method
        :type debug: bool
        :return:
        """
        # source_id -> copy_id
        id_mapping = dict()

        # source_id -> source_scen_id
        scen_mapping = defaultdict(lambda: defaultdict(list))

        # Split scenarios into plain scenarios a.k.a. ones that do not have a ReferringScenarioAdditionalInformation
        # and ones that have such an AdditionalInformation, as the former one needs to be created first
        plain_scenarios = []
        referring_scenarios = []

        for scenario in self.get_scenarios():
            if scenario.has_referring_scenario():
                referring_scenarios.append(scenario)
            else:
                plain_scenarios.append(scenario)

        # Copy immediately
        for scenario in plain_scenarios:
            if debug:
                print('Copying {}...'.format(scenario.get_id()), end='')

            sub_mapping, _ = scenario.copy(target_package, debug=debug)
            id_mapping.update(**sub_mapping)

            if debug:
                print(' done -> {}'.format(sub_mapping[scenario.get_id()]))

        # Fix ReferringAdditionalInformation and copy
        for scenario in referring_scenarios:
            if debug:
                print('Copying {}...'.format(scenario.get_id()), end='')

            sub_mapping, _ = scenario.copy(target_package, debug=debug, id_lookup=id_mapping)
            id_mapping.update(**sub_mapping)

            if debug:
                print(' done -> {}'.format(sub_mapping[scenario.get_id()]))

        # Copy all compounds
        for compound in self.get_compounds():
            if debug:
                print('Copying {}...'.format(compound.get_id()), end='')

            sub_mapping, _, _ = compound.copy(target_package, debug=debug)
            for scen in compound.get_scenarios():
                scen_mapping[Compound][compound.get_id()].append(scen.get_id())
                for cs in compound.get_structures():
                    for scen in cs.get_scenarios():
                        scen_mapping[CompoundStructure][cs.get_id()].append(scen.get_id())
            id_mapping.update(**sub_mapping)

            if debug:
                print(' done -> {}'.format(sub_mapping[compound.get_id()]))

        # Copy all rules
        for rule in self.get_rules():
            if debug:
                print('Copying {}...'.format(rule.get_id()), end='')

            # TODO impl Rule.copy
            sub_mapping, _ = rule.copy(target_package, debug=debug)
            for scen in rule.get_scenarios():
                scen_mapping[Rule][rule.get_id()].append(scen.get_id())
            id_mapping.update(**sub_mapping)

            if debug:
                print(' done -> {}'.format(sub_mapping[rule.get_id()]))

        # Copy all pathways
        for pathway in self.get_pathways():
            if debug:
                print('Copying {}...'.format(pathway.get_id()), end='')

            # if pathway.get_id() != 'http://localhost:8080/package/f444f7ae-b9b9-469c-bfa8-e7b83eba42a9/pathway/ee26b1b7-53e4-4a1b-b212-b78435e392de':
            #     continue

            sub_mapping, _ = pathway.copy(target_package, debug=debug)
            for scen in pathway.get_scenarios():
                scen_mapping[Pathway][pathway.get_id()].append(scen.get_id())

            for e in pathway.get_edges():
                for scen in e.get_scenarios():
                    scen_mapping[Edge][e.get_id()].append(scen.get_id())

            for n in pathway.get_nodes():
                for scen in n.get_scenarios():
                    scen_mapping[Node][n.get_id()].append(scen.get_id())

            id_mapping.update(**sub_mapping)

            if debug:
                print(' done -> {}'.format(sub_mapping[pathway.get_id()]))

        # Copy all reactions
        for reaction in self.get_reactions():
            if debug:
                print('Copying {}...'.format(reaction.get_id()), end='')

            sub_mapping, _ = reaction.copy(target_package, debug=debug)
            for scen in reaction.get_scenarios():
                scen_mapping[Reaction][reaction.get_id()].append(scen.get_id())
            id_mapping.update(**sub_mapping)

            if debug:
                print(' done -> {}'.format(sub_mapping[reaction.get_id()]))

        # Assign scenarios to objects
        for obj in scen_mapping.keys():
            for source_obj_id, source_scen_ids in scen_mapping[obj].items():
                instance = obj(target_package.requester, id=id_mapping[source_obj_id])
                for source_scen_id in source_scen_ids:
                    if debug:
                        print('Linking {} to {}...'.format(id_mapping[source_scen_id], instance.get_id()), end='')

                    scen = Scenario(target_package.requester, id=id_mapping[source_scen_id])
                    instance.add_scenario(scen)

                    if debug:
                        print(' done')

    @staticmethod
    def merge_packages(target: 'Package', sources: List['Package'], debug=False) -> None:
        """
        Merges a list of packages to the `target` Package

        :param target: the Package where the merge wants to be performed
        :param sources: a list of Package
        :param debug: whether to add more verbosity or not to the method
        :return:
        """
        for source in sources:
            source.copy(target, debug=debug)

    def search(self, term: str):
        """
        Function designed to perform a search on an enviPath session on the given Package.

        :param term: the term with which the search wants to be performed
        :return: a dictionary of object identifiers
        """
        return self.requester.eP.search(term, self)


class Scenario(enviPathObject):
    """
    Class for the Scenario enviPath object
    """
    def get_type(self):
        pass

    def set_type(self):
        pass

    @staticmethod
    def create(package: Package, name: str = None, description: str = None, date: str = None, scenariotype: str = None,
               additional_information: List['AdditionalInformation'] = None, referring_scenario_id: str = None,
               collection_URI: str = None) -> 'Scenario':
        """
        Creates a Scenario within the specified package. Scenario data can be added with class AdditionalInformation.

        :param package: Package object in which the Scenario will be created
        :param name: Name of Scenario
        :param description: Description of Scenario
        :param date: The date at which the scenario was created
        :param scenariotype: Use predefined scenario type (possible: Soil, Sludge, Sediment, ..)
        :param additional_information: Scenario data content provided as a AdditionalInformation object
        :param referring_scenario_id: Provide referring scenario ID, a related scenario will be created
        :param collection_URI: attach an existing AdditionalInformation object to the scenario (by ID) - not working
        :return: Scenario object
        """
        scenario_payload = {}
        # Create payload container
        if len(additional_information):
            scenario_payload['adInfoTypes[]'] = ','.join([ai.name for ai in additional_information])
            for ai in additional_information:
                # Will raise an error if invalid
                ai.validate()
                scenario_payload.update(**ai.params)
            scenario_payload['fullScenario'] = 'true'
        else:
            scenario_payload['fullScenario'] = 'false'

        # jsonredirect needs to be 'true'
        # This seems to be because a custom function is used in ScenarioServlet.java when returning the scenario URI
        scenario_payload['jsonredirect'] = 'true'

        # add meta information
        if name:
            scenario_payload['studyname'] = name
        if description:
            scenario_payload['studydescription'] = description
        if date:
            if len(date.split('-')) == 3:
                scenario_payload['dateYear'] = date.split('-')[0]
                scenario_payload['dateMonth'] = date.split('-')[1]
                scenario_payload['dateDay'] = date.split('-')[2]
            elif len(date.split('-')) == 2:  # only year and month
                scenario_payload['dateYear'] = date.split('-')[0]
                scenario_payload['dateMonth'] = date.split('-')[1]
            else:
                try:
                    # Check if its only a year
                    scenario_payload['dateYear'] = str(int(date))
                except ValueError:
                    raise ValueError(
                        "The date should be provided in the following format: YYYY-MM-DD but {} cant be parsed!".format(
                            date))

        if scenariotype:
            scenario_payload['type'] = scenariotype.capitalize()
        if referring_scenario_id:
            scenario_payload['addReferring'] = 'true'
            scenario_payload['referringScenario'] = referring_scenario_id
        if collection_URI:
            scenario_payload['collectionURI'] = collection_URI

        # post scenario to envipath
        url = '{}/{}'.format(package.get_id(), Endpoint.SCENARIO.value)
        res = package.requester.post_request(url, payload=scenario_payload, allow_redirects=False)
        res.raise_for_status()

        if referring_scenario_id:  # eP sends a different response for referring scenarios
            return Scenario(package.requester, id=res.headers['Location'])
        else:
            return Scenario(package.requester, id=res.json()['scenarioLocation'])

    def update_scenario(self, additional_information: List['AdditionalInformation']):
        """
        Updates an existing scenario

        :param additional_information: Scenario data content provided as a AdditionalInformation object
        :return: The updated scenario
        :rtype: Scenario
        """
        scenario_payload = {}

        if len(additional_information):
            self.loaded = False
            scenario_payload['adInfoTypes[]'] = ','.join([ai.name for ai in additional_information])
            for ai in additional_information:
                # Will raise an error if invalid
                ai.validate()
                scenario_payload.update(**ai.params)

        scenario_payload['updateScenario'] = 'true'
        scenario_payload['fullScenario'] = 'false'
        scenario_payload['jsonredirect'] = 'false'

        res = self.requester.post_request(self.get_id(), payload=scenario_payload, allow_redirects=False)
        res.raise_for_status()
        return Scenario(self.requester, id=self.id)

    def has_referring_scenario(self) -> bool:
        """
        Function to check whether referringScenario exists or not

        :return: True if it exists else False
        """
        try:
            return self._get('referringScenario') is not None
        except ValueError:
            return False

    def get_referring_scenario(self) -> 'Scenario':
        """
        Gets the referring scenario

        :return: A Scenario object
        """
        return Scenario(self.requester, id=self._get('referringScenario')['scenarioId'])

    def get_additional_information(self) -> List['AdditionalInformation']:
        """
        Gets the additional information from the existing Scenario

        :return: A list containing the AdditionalInformation
        """
        res = []
        if self._get('collection'):
            coll = self._get('collection')
            warnings = []
            for val in coll.values():
                # e.g. acidity
                if isinstance(val, list):
                    for v in val:
                        try:
                            clz = AdditionalInformation.get_subclass_by_name(v['name'])
                            c = clz().parse(v['value'])
                            c.params["unit"] = v["unit"]
                            res.append(c)
                        except NotImplementedError:
                            warnings.append(f"The class {v['name']} has not yet been implemented")
                        except Exception as e:
                            warnings.append(f"Error when trying to parse {clz.__name__}, raised error {e}")
                else:
                    try:
                        clz = AdditionalInformation.get_subclass_by_name(val['name'])
                        c = clz().parse(val['value'])
                        c.params["unit"] = val["unit"]
                        res.append(c)
                    except NotImplementedError:
                        warnings.append(f"The class {v['name']} has not yet been implemented")
                    except Exception as e:
                        warnings.append(f"Error when trying to parse {clz.__name__}, raised error {e}")
            if warnings:
                print(f"The following warnings appeared while parsing the scenario {self.get_id()}")
                for warning in warnings:
                    print(warning)

        return res

    def get_linked_objects(self) -> List['ReviewableEnviPathObject']:
        """
        Gets the objects that are linked to the current scenario.

        :return: A list of objects that have this scenario attached
        :rtype: List
        """
        res = []
        for obj in self._get('linkedTo'):
            res.append(self.requester.get_object(obj["id"], Endpoint(obj["identifier"])))
        return res

    def copy(self, package: 'Package', debug=False, id_lookup={}) -> (dict, 'Scenario'):
        """
        Copy the Scenario object

        :param package: the package where the Scenario wants to be added to
        :param debug: whether to have more verbosity (True) or not (False)
        :param id_lookup: in case the parent Scenario has a referring scenario, a dictionary that maps the id of the
            parent scenario to the referred one
        :return: a dictionary similar to `id_lookup` and the copied Scenario
        """
        mapping = dict()

        ais = self.get_additional_information()
        ais_to_add = []

        # TODO make it pretty :S

        if self.has_referring_scenario():
            ref_scenario = self.get_referring_scenario()
            ref_ais = ref_scenario.get_additional_information()

            # Assemble the ReferringScenarioAdditionalInformation by creating a new one with the adjusted id
            ais_to_add.append(
                ReferringScenarioAdditionalInformation(referringscenario=id_lookup[ref_scenario.get_id()]))

            for ai in ais:
                present_in_ref = False
                for ref_ai in ref_ais:
                    if ai.name == ref_ai.name:
                        if ai.params == ref_ai.params:
                            present_in_ref = True
                            # print("Wont add {} with params {} as its stored in ref".format(ai.name, ai.params))
                            break

                if not present_in_ref:
                    ais_to_add.append(ai)

        else:
            ais_to_add = ais

        from collections import Counter
        cnt = Counter([x.name for x in ais_to_add])
        post_poned_ais = []
        # check if multi ais such as acidity are present
        for k, v in cnt.items():
            if v > 1:
                for ai in ais_to_add:
                    post_poned_ais.append(ai)

        for ai in post_poned_ais:
            ais_to_add.remove(ai)

        # Create plain Scenario
        date = self._get('date')
        if date is None or date == 'no date':
            date = None

        name = self.get_name()
        # replaces " - (000XX)" with an empty string as this will be added by the server...
        name = re.sub(" - \(\d+\)$", '', name)

        # Create the copy!
        s = Scenario.create(package,
                            name=name,
                            description=self.get_description(),
                            date=date,
                            scenariotype=self._get('type'),
                            additional_information=ais_to_add,
                            referring_scenario_id=None,
                            collection_URI=None,
                            )

        # Add the remaining ones...
        for ai in post_poned_ais:
            # TODO check if list is the right choice...
            s.update_scenario([ai])

        mapping[self.get_id()] = s.get_id()

        return mapping, s


class Compound(ReviewableEnviPathObject):
    """
    Class that implements the Compound enviPath object
    """
    def add_structure(self, smiles, name=None, description=None, inchi=None, mol_file=None) -> 'CompoundStructure':
        return CompoundStructure.create(self, smiles, name=name, description=description, inchi=inchi,
                                        mol_file=mol_file)

    def get_structures(self) -> List['CompoundStructure']:
        """
        Gets all structures of this compound.

        :return: List of Structure objects.
        """
        res = []
        plain_structures = self._get('structures')
        for plain_structure in plain_structures:
            res.append(CompoundStructure(self.requester, **plain_structure))
        return res

    @staticmethod
    def create(parent: Package, smiles: str, name=None, description=None, inchi=None) -> 'Compound':
        """
        Creates a Compound enviPath object

        :param parent: the Package to which the Compound will belong to
        :param smiles: the SMILES of the Compound
        :param name: the name of the Compound
        :param description: the description of the Compound
        :param inchi: the InChI of the Compound
        :return: An enviPath Compound object
        """
        if not isinstance(parent, Package):
            raise ValueError("The parent of a compound has to be a package!")

        compound_payload = dict()
        compound_payload['compoundSmiles'] = smiles
        if name:
            if not re.match(r'compound \d{6}', name):
                compound_payload['compoundName'] = name

        if description:
            compound_payload['compoundDescription'] = description

        if inchi:
            compound_payload['inchi'] = inchi

        url = '{}/{}'.format(parent.get_id(), Endpoint.COMPOUND.value)
        res = parent.requester.post_request(url, payload=compound_payload, allow_redirects=False)
        res.raise_for_status()
        return Compound(parent.requester, id=res.headers['Location'])

    def get_default_structure(self) -> 'CompoundStructure':
        """
        Return its CompoundStructure if available

        :return: A CompoundStructure enviPath object
        """
        for structure in self.get_structures():
            if structure.is_default_structure():
                return structure
        raise ValueError("The compound does not have a default structure!")

    def get_smiles(self) -> str:
        """
        Returns the SMILES of the Compound

        :return: SMILES of the Compound
        """
        return self.get_default_structure().get_smiles()
    
    def get_pubchem_references(self) -> List[str]:
        """
        Retrieves the links to pubChem of similar compounds

        :return: A list of links to PubChem Compounds
        """
        return self._get('pubchemCompoundReferences')
    
    def get_external_references(self) -> dict:
        """
        Retrieves the links to external sources of similar compounds

        :return: A dictionary of links with keys being an identifier for the database
        """
        return self._get('externalReferences')

    def get_inchi(self) -> str:
        """
        Return the InChI of the Compound

        :return: InChI of the Compound
        """
        return self.get_default_structure().get_inchi()

    def copy(self, package: 'Package', debug=False) -> (dict, 'Compound', List['CompoundStructure']):
        """
        Copies the Compound object

        :param package: package to which the new object will belong to
        :param debug: whether to have more verbosity (True) or not (False)
        :return: a dictionary mapping the ids of the parent and copied object, a Compound object that is a copy
            of the parent one, and a List of all the CompoundStructure objects associated with the original Compound
        """
        mapping = dict()
        copied_compound = Compound.create(package, self.get_smiles(), self.get_name(), self.get_description(),
                                          self.get_inchi())

        mapping[self.get_id()] = copied_compound.get_id()

        copied_structures = []
        for structure in self.get_structures():
            copied_structure = CompoundStructure.create(copied_compound, structure.get_smiles(), structure.get_name(),
                                                        structure.get_description())
            copied_structures.append(copied_structure)
            mapping[structure.get_id()] = copied_structure.get_id()

        return mapping, copied_compound, copied_structures


class CompoundStructure(ReviewableEnviPathObject):
    """
    Class that implements the CompoundStructure enviPath object
    """
    def add_alias(self, alias):
        """
        Adds an alias to the CompoundStructure

        :param alias: the alias to be added
        :return:
        """
        payload = {
            'name': alias,
        }
        self.requester.post_request(self.id, payload=payload, allow_redirects=False)
        self.loaded = False
        if hasattr(self, 'alias'):
            delattr(self, 'alias')

    def get_charge(self) -> float:
        """
        Retrieves the charge of the CompoundStructure

        :return: Charge of CompoundStructure
        """
        return float(self._get('charge'))

    def get_formula(self) -> str:
        """
        Retrieves the formula of the CompoundStructure

        :return: Formula of CompoundStructure
        """
        return self._get('formula')

    def get_mass(self) -> float:
        """
        Retrieves the mass of the CompoundStructure

        :return: Mass of CompoundStructure
        """
        return self._get('mass')

    def get_svg(self) -> str:
        """
        Retrieves the image of the CompoundStructure

        :return: Image of CompoundStructure as text
        """
        return self.requester.get_request(self._get('image')).text

    def is_default_structure(self) -> bool:
        """
        Checks this structure is a default structure or not

        :return: boolean to whether CompoundStructure is a default one or not
        """
        return self._get('isDefaultStructure')

    def get_smiles(self) -> str:
        """
        Retrieves the SMILES of the CompoundStructure

        :return: SMILES of CompoundStructure
        """
        return self._get('smiles')

    def get_inchi(self) -> str:
        """
        Retrieves the InChI of the CompoundStructure

        :return: InChI of CompoundStructure
        """
        return self._get('InChI')

    def get_pathways(self) -> List['Pathway']:
        """
        Retrieves the pathways on which the CompoundStructure is involved

        :return: List of Pathway objects
        """
        return self._create_from_nested_json('pathways', Pathway)

    def get_scenarios(self) -> List['Scenario']:
        """
        Retrieves the scenarios on which the CompoundStructure is involved

        :return: List of Scenario objects
        """
        return self._create_from_nested_json('scenarios', Scenario)

    def get_reactions(self) -> List['Reaction']:
        """
        Retrieves the reactions on which the CompoundStructure is involved

        :return: List of Reaction objects
        """
        return self._create_from_nested_json('reactions', Reaction)
    
    def get_pubchem_references(self) -> List[str]:
        """
        Retrieves the links to pubChem of similar compounds

        :return: A list of links to PubChem Compounds
        """
        return self._get('pubchemCompoundReferences')
    
    def get_external_references(self) -> dict:
        """
        Retrieves the links to external sources of similar compounds

        :return: A dictionary of links with keys being an identifier for the database
        """
        return self._get('externalReferences')

    def get_halflifes(self, scenario_type: str = None) -> List['HalfLife']:
        """
        Retrieves the halflifes of the CompoundStructure

        :param scenario_type: a strng indicating the type of scenario
        :return: A list of HalfLife objects
        """
        res = []
        for hl in self._get('halflifes'):
            if scenario_type.lower() == 'soil':
                if hl['scenarioType'].lower() == 'soil':
                    res.append(HalfLife(scenarioId=hl['scenarioId'], scenarioName=hl['scenarioName'], hl=hl['hl'],
                                        hl_comment=hl['hlComment'], hl_fit=hl['hlFit'], hl_model=hl['hlModel'],
                                        source=hl['source']))
            elif scenario_type.lower() == 'sediment':
                raise NotImplementedError
            elif scenario_type.lower() == 'sludge':
                raise NotImplementedError
            else:
                print('Warning: A general get_halflifes function is currently not implemented')
                raise NotImplementedError
        return res

    @staticmethod
    def create(parent: Compound, smiles, name=None, description=None, inchi=None, mol_file=None) -> 'CompoundStructure':
        """
        Creates a CompoundStructure enviPath object

        :param parent: the Package to which the CompoundStructure will belong to
        :param smiles: the SMILES of the CompoundStructure
        :param name: the name of the CompoundStructure
        :param description: the description of the CompoundStructure
        :param inchi: the InChI of the CompoundStructure
        :param mol_file: the molecule file of the CompoundStructure
        :return: An enviPath CompoundStructure object
        """
        if not isinstance(parent, Compound):
            raise ValueError("The parent of a structure has to be a compound!")

        structure_payload = dict()
        structure_payload['smiles'] = smiles
        if name:
            if not re.match(r'structure \d{6}', name):
                structure_payload['name'] = name

        if description:
            structure_payload['description'] = description

        if inchi:
            structure_payload['inchi'] = inchi

        if mol_file:
            structure_payload['molfile'] = mol_file

        url = '{}/{}'.format(parent.get_id(), Endpoint.COMPOUNDSTRUCTURE.value)
        res = parent.requester.post_request(url, payload=structure_payload, allow_redirects=False)
        res.raise_for_status()
        return CompoundStructure(parent.requester, id=res.headers['Location'])

    def copy(self, package: 'Package', debug=False):
        raise NotImplementedError("Copying of CompoundStructures is implemented via Compound.copy!")


class Reaction(ReviewableEnviPathObject):
    """
    Class that implements an enviPath Reaction object
    """
    def is_multistep(self) -> bool:
        """
        Check for multistep reaction

        :return: True if multistep else False
        """
        return "true" == self._get('multistep')

    def get_ec_numbers(self) -> List['ECNumber']:
        """
        Gets the EC numbers of the reaction

        :return: List of ECNumber objects
        """
        ec_numbers = self._get('ecNumbers')
        res = []
        for ec_number in ec_numbers:
            pathways = [Pathway(self.requester, id=pw['id']) for pw in ec_number['pathways']]
            res.append(ECNumber(ec_number['ecNumber'], ec_number['ecName'], pathways))
        return res

    def get_smirks(self) -> str:
        """
        Gets the SMIRKS of the Reaction

        :return: SMIRKS of the Reaction
        """
        return self._get('smirks')

    def get_pathways(self) -> List['Pathway']:
        """
        Gets the pathways where this reaction is involved

        :return: A List of Pathway enviPath objects
        """
        return self._get('pathways')

    def get_medline_references(self) -> List[object]:
        """
        Gets medline references

        :return: A list of objects
        """
        return self._get('medlineRefs')

    def get_substrates(self) -> List['CompoundStructure']:
        """
        Retrieves the substrates of the reaction

        :return: A List of CompoundStructure
        """
        return self._create_from_nested_json('educts', CompoundStructure)

    def get_educts(self) -> List['CompoundStructure']:
        """
        DEPRECATED
        Retrieves the educts of the reaction

        :return: A List of CompoundStructure
        """
        return self._create_from_nested_json('educts', CompoundStructure)

    def get_products(self):
        """
        Retrieves the products of the reaction

        :return: A List of CompoundStructure
        """
        return self._create_from_nested_json('products', CompoundStructure)

    def get_rule(self) -> Optional['Rule']:
        """
        Retrieves the rule of the reaction

        :return: The Rule that describes the Reaction
        """
        try:
            rules = self._get('rules')
            if len(rules) == 0:
                return None
            if len(rules) > 1:
                raise Exception("More than one rule attached to reaction!")
            rule_type = Rule.get_rule_type(rules[0])
            return rule_type(self.requester, **rules[0])
        except ValueError:
            return None
    
    def get_rhea_references(self) -> List[str]:
        """
        Retrieves the links to Rhea for the given reaction

        :return: A list of links to rhea with similar reactions
        """
        return self._get('rheaReferences')

    @staticmethod
    def create(package: Package, smirks: str = None, educt: CompoundStructure = None, product: CompoundStructure = None,
               name: str = None, description: str = None, rule: 'Rule' = None) -> 'Reaction':
        """
        Create a Reaction enviPath object

        :param package: the Package to which the Reaction will belong to
        :param smirks: the SMIRKS of the Reaction
        :param educt: the educt of the Reaction
        :param product: the product of the Reaction
        :param name: the name of the Reaction
        :param description: the description of the Reaction
        :param rule: the rule that describes the Reaction (if any)
        :return: A Reaction enviPath object
        """

        if smirks is None and (educt is None or product is None):
            raise ValueError("Neither SMIRKS or educt/product must be provided")

        if smirks is not None and (educt is not None and product is not None):
            raise ValueError("SMIRKS and educt/product provided!")

        payload = {}

        if smirks:
            payload['smirks'] = smirks
        else:
            payload['educt'] = educt.get_id()
            payload['product'] = product.get_id()

        if rule:
            payload['rule'] = rule.get_id()

        if name:
            if not re.match(r'reaction \d{6}', name):
                payload['reactionName'] = name

        if description:
            payload['reactionDescription'] = description

        url = '{}/{}'.format(package.get_id(), Endpoint.REACTION.value)
        res = package.requester.post_request(url, payload=payload, allow_redirects=False)
        res.raise_for_status()
        return Reaction(package.requester, id=res.headers['Location'])

    def copy(self, package: 'Package', debug=False) -> (dict, 'Reaction'):
        """
        Copies the Reaction

        :param package: the Package to which the copied Reaction will belong to
        :param debug: whether to have more verbosity or not
        :return: a dictionary mapping the ids of the parent and copied object, a Reaction object that is a copy
            of the parent one
        """
        mapping = dict()

        params = {
            'package': package,
            'smirks': self.get_smirks(),
            'name': self.get_name(),
            'description': self.get_description(),
        }

        if self.get_rule():
            params['rule'] = self.get_rule()

        r = Reaction.create(**params)

        mapping[self.get_id()] = r.get_id()

        return mapping, r


class Rule(ReviewableEnviPathObject, ABC):
    """
    Class that implements an enviPath Rule
    """
    def get_ec_numbers(self) -> List[object]:
        """
        Gets the EC Numbers associated with the given rule

        :return: A list of objects representing EC Numbers
        """

        return self._get('ecNumbers')

    def included_in_composite_rule(self) -> List['Rule']:
        """
        Returns all the rules that are included on the current composite rule

        :return: A List of Rules in the current composite rule
        """
        res = []
        for rule in self._get('includedInCompositeRule'):
            res.append(Rule(self, requester=self.requester, id=rule['id']))
        return res

    def is_composite_rule(self) -> bool:
        """
        Check whether the rule is composite or not

        :return: True if it is, else False
        """
        return self._get('isCompositeRule')

    def get_transformations(self) -> str:
        """
        Retrieve a string defining the transformations where this rule is involved.

        :return: The transformations involved in the rule
        """
        return self._get('transformations')

    def get_reactions(self) -> List['Reaction']:
        """
        Retrieves the reactions associated with the given rule

        :return: A List of Reaction objects associated with the given rule
        """
        return self._create_from_nested_json('reactions', Reaction)

    def get_pathways(self) -> List['Pathway']:
        """
        Retrieves the pathways where this rule is used

        :return: The List of Pathway objects that include that rule
        """
        return self._create_from_nested_json('pathways', Pathway)

    def get_reactant_filter_smarts(self) -> str:
        """
        Retrieve the SMARTS filter used in reactants

        :return: A string defining that filter
        """
        return self._get('reactantFilterSmarts')

    def get_reactant_smarts(self) -> str:
        """
        Retrieves the SMARTS of the reactants

        :return: A string describing the reactant's SMARTS
        """
        return self._get('reactantsSmarts')

    def get_product_filter_smarts(self) -> str:
        """
        Retrieve the SMARTS filter used in products

        :return: A string defining that filter
        """
        return self._get('productFilterSmarts')

    def get_product_smarts(self) -> str:
        """
        Retrieves the SMARTS of the products

        :return: A string describing the product's SMARTS
        """
        return self._get('productsSmarts')

    def apply_to_compound(self, compound: Compound) -> List[str]:
        """
        Applies the given Rule to the specified Compound

        :param compound: The Compound to which the Rule wants to be applied
        :return: A List of strings defining all the possible transformations
        """
        return self.apply_to_smiles(compound.get_default_structure().get_smiles())

    def apply_to_smiles(self, smiles) -> List[str]:
        """
        Applies the given Rule to the specified SMILES

        :param smiles: The smiles to which the Rule wants to be applied
        :return: A List of strings defining all the possible transformations
        """
        payload = {
            'hiddenMethod': 'APPLYRULES',
            'compound': smiles
        }
        res = self.requester.post_request(self.get_id(), payload=payload)
        res.raise_for_status()
        result = []
        splitted = res.text.split()
        for split in splitted:
            if split:
                result.append(split)
        return result

    @staticmethod
    def get_rule_type(obj: dict):
        """
        Returns the type of rule

        :param obj: a dictionary that contains the information of the type of rule
        :return: The type of the Rule
        """
        if obj['identifier'] == Endpoint.SIMPLERULE.value:
            return SimpleRule
        elif obj['identifier'] == Endpoint.SEQUENTIALCOMPOSITERULE.value:
            return SequentialCompositeRule
        elif obj['identifier'] == Endpoint.PARALLELCOMPOSITERULE.value:
            return ParallelCompositeRule
        else:
            raise ValueError("Unknown rule type {}".format(obj['identifier']))

    @staticmethod
    @abstractmethod
    def create(package: Package, smirks: str, name: str = None, description: str = None,
               reactant_filter_smarts: str = None, product_filter_smarts: str = None):
        pass


class SimpleRule(Rule):
    """
    Class that implements an enviPath SimpleRule object
    """
    @staticmethod
    def create(package: Package, smirks: str, name: str = None, description: str = None,
               reactant_filter_smarts: str = None, product_filter_smarts: str = None,
               immediate: str = None, rdkitrule: bool = None) -> 'SimpleRule':
        """
        Creates a SimpleRule object

        :param package: the Package to which the SimpleRule will belong to
        :param smirks: the SMIRKS of the SimpleRule
        :param name: the name of the SimpleRule
        :param description: the description of the SimpleRule
        :param reactant_filter_smarts: the string that describes the SMARTS filter used for the reactants
        :param product_filter_smarts: the string that describes the SMARTS filter used for the products
        :param immediate: the string describing the immediate
        :param rdkitrule: a boolean stating whether the rule is a rdkit rule or not
        :return: A SimpleRule enviPath object
        """
        rule_payload = {
            'smirks': smirks,
        }

        if name:
            rule_payload['name'] = name

        if description:
            rule_payload['description'] = description

        if reactant_filter_smarts:
            rule_payload['reactantFilterSmarts'] = reactant_filter_smarts

        if product_filter_smarts:
            rule_payload['productFilterSmarts'] = product_filter_smarts

        if immediate:
            rule_payload['immediaterule'] = immediate

        if rdkitrule:
            rule_payload['rdkitrule'] = 'true' if rdkitrule else "false"

        url = '{}/{}'.format(package.get_id(), Endpoint.SIMPLERULE.value)
        res = package.requester.post_request(url, payload=rule_payload, allow_redirects=False)
        res.raise_for_status()
        return SimpleRule(package.requester, id=res.headers['Location'])

    def get_smirks(self) -> str:
        """
        Retrieves the SMIRKS of the SimpleRule

        :return: The SMIRKS of the SimpleRule in string format
        """
        return self._get('smirks')

    def copy(self, package: 'Package', debug=False):
        """
        Copies the SimpleRule

        :param package: the Package to which the SimpleRule will belong to
        :param debug: whether to have more verbosity or not
        :return: a dictionary mapping the ids of the parent and copied object, a SimpleRule object that is a copy
            of the parent one
        """
        # TODO immediate missing
        mapping = dict()

        sr = SimpleRule.create(package, smirks=self.get_smirks(), name=self.get_name(),
                               description=self.get_description(),
                               reactant_filter_smarts=self.get_reactant_filter_smarts(),
                               product_filter_smarts=self.get_product_filter_smarts())

        mapping[self.get_id()] = sr.get_id()
        return mapping, sr


class SequentialCompositeRule(Rule):
    """
    Class that implements a SequentialCompositeRule enviPath object
    """
    @staticmethod
    def create(package: Package, simple_rules: List[SimpleRule], name: str = None, description: str = None,
               reactant_filter_smarts: str = None, product_filter_smarts: str = None,
               immediate: str = None) -> 'SequentialCompositeRule':
        """
        Creates a SequentialCompositeRule enviPath object

        :param package: the Package to which the SequentialCompositeRule will belong to
        :param simple_rules: a List of SimpleRule objects that are contained within the SequentialCompositeRule
        :param name: the name of the SequentialCompositeRule
        :param description: the description of the SequentialCompositeRule
        :param reactant_filter_smarts: the string that describes the SMARTS filter used for the reactants
        :param product_filter_smarts: the string that describes the SMARTS filter used for the products
        :param immediate: the string describing the immediate
        :return: A SequentialCompositeRule enviPath object
        """
        rule_payload = {
            'simpleRules[]': [r.get_id() for r in simple_rules],
        }

        if name:
            rule_payload['name'] = name

        if description:
            rule_payload['description'] = description

        if reactant_filter_smarts:
            rule_payload['reactantFilterSmarts'] = reactant_filter_smarts

        if product_filter_smarts:
            rule_payload['productFilterSmarts'] = product_filter_smarts

        if immediate:
            rule_payload['immediaterule'] = immediate

        url = '{}/{}'.format(package.get_id(), Endpoint.SEQUENTIALCOMPOSITERULE.value)
        res = package.requester.post_request(url, payload=rule_payload, allow_redirects=False)
        res.raise_for_status()
        return SequentialCompositeRule(package.requester, id=res.headers['Location'])

    def get_simple_rules(self) -> List['SimpleRule']:
        """
        Retrieves the SimpleRule objects contained within the SequentialCompositeRule

        :return: A List of all the SimpleRule objects contained within the SequentialCompositeRule
        """
        return self._create_from_nested_json('simpleRules', SimpleRule)

    def copy(self, package: 'Package', debug=False, id_lookup={}):
        # TODO
        pass


class ParallelCompositeRule(Rule):
    """
    Class that implements a ParallelCompositeRule enviPath object
    """
    @staticmethod
    def create(package: Package, simple_rules: List[SimpleRule], name: str = None, description: str = None,
               reactant_filter_smarts: str = None, product_filter_smarts: str = None,
               immediate: str = None) -> 'ParallelCompositeRule':
        """
        Creates a ParallelCompositeRule enviPath object

        :param package: the Package to which the ParallelCompositeRule will belong to
        :param simple_rules: a List of SimpleRule objects that are contained within the ParallelCompositeRule
        :param name: the name of the ParallelCompositeRule
        :param description: the description of the ParallelCompositeRule
        :param reactant_filter_smarts: the string that describes the SMARTS filter used for the reactants
        :param product_filter_smarts: the string that describes the SMARTS filter used for the products
        :param immediate: the string describing the immediate
        :return: A ParallelCompositeRule enviPath object
        """
        rule_payload = {
            'simpleRules[]': [r.get_id() for r in simple_rules],
        }

        if name:
            rule_payload['name'] = name

        if description:
            rule_payload['description'] = description

        if reactant_filter_smarts:
            rule_payload['reactantFilterSmarts'] = reactant_filter_smarts

        if product_filter_smarts:
            rule_payload['productFilterSmarts'] = product_filter_smarts

        if immediate:
            rule_payload['immediaterule'] = immediate

        url = '{}/{}'.format(package.get_id(), Endpoint.PARALLELCOMPOSITERULE.value)
        res = package.requester.post_request(url, payload=rule_payload, allow_redirects=False)
        res.raise_for_status()
        return ParallelCompositeRule(package.requester, id=res.headers['Location'])

    def get_simple_rules(self) -> List['SimpleRule']:
        """
        Retrieves the SimpleRule objects contained within the ParallelCompositeRule

        :return: A List of all the SimpleRule objects contained within the ParallelCompositeRule
        """
        return self._create_from_nested_json('simpleRules', SimpleRule)

    def copy(self, package: 'Package', debug=False, id_lookup={}):
        # TODO
        pass


class RelativeReasoning(ReviewableEnviPathObject):
    """
    Class that implements a RelativeReasoning enviPath object
    """
    @staticmethod
    def create(package: Package, packages: List[Package], classifier_type: ClassifierType,
               eval_type: EvaluationType, association_type: AssociationType,
               evaluation_packages: List[Package] = None,
               fingerprinter_type: FingerprinterType = FingerprinterType.ENVIPATH_FINGERPRINTER,
               quickbuild: bool = True, use_p_cut: bool = False, cut_off: float = 0.5,
               evaluate_later: bool = True, name: str = None) -> 'RelativeReasoning':

        """
        Create a relative reasoning object

        :param package: The package object in which the model is created
        :param packages: List of package objects on which the model is trained
        :param classifier_type: Classifier options:

            - Rule-Based : ClassifierType("RULEBASED")
            - Machine Learning-Based (MLC-BMaD) :  ClassifierType("MLCBMAD")
            - Machine Learning-Based (ECC) : ClassifierType("ECC")
        :param eval_type: Evaluation type:

            - Single Generation : EvaluationType("single")
            - Single + Multiple Generation : EvaluationType("multigen")
        :param association_type: Association type:

            - AssociationType("DATABASED")
            - AssociationType("CALCULATED"), default
        :param evaluation_packages: List of package objects on which the model is evaluated. If none, the classifier
            is evaluated in a 100-fold holdout model using a 90/10 split ratio.
        :param fingerprinter_type: Default: MACS Fingerprinter ("ENVIPATH_FINGERPRINTER")
        :param quickbuild: Faster evaluation, default: False
        :param use_p_cut:  Default: False
        :param cut_off: The cutoff threshold used in the evaluation. Default: 0.5
        :param evaluate_later: Only build the model, and not proceed to evaluation. Default: False
        :param name:  Name of the model
        :return: RelativeReasoning object
        """

        payload = {
            'fpType': fingerprinter_type.value,
            'clfType': classifier_type.value,
            'assocType': association_type.value,
            'quickBuild': 'on' if quickbuild else 'off',
            'evalLater': 'on' if evaluate_later else 'off',
            'evalType': eval_type.value,
            'packages': [p.get_id() for p in packages],
            'cut-off': cut_off,
        }

        if use_p_cut:
            payload['p-cut'] = 'on'

        if evaluation_packages:
            payload['evalPackages'] = [p.get_id() for p in evaluation_packages]

        if name:
            payload['modelName'] = name

        url = '{}/{}'.format(package.get_id(), Endpoint.RELATIVEREASONING.value)
        res = package.requester.post_request(url, payload=payload, allow_redirects=False)
        res.raise_for_status()
        return RelativeReasoning(package.requester, id=res.headers['Location'])

    def download_arff(self) -> str:
        params = {
            'downloadARFF': 'ILikeCats'
        }
        return self.requester.get_request(self.id, params=params).text

    def get_model_status(self) -> 'ModelStatus':
        params = {
            'status': "true",
        }
        return ModelStatus(**self.requester.get_request(self.id, params=params).json())

    def classify_structure(self, structure: CompoundStructure):
        """
        Uses the RelativeReasoning model to classify a given CompoundStructure

        :param structure: The CompoundStructure to classify
        :return: A JSON object with the classification response of the model
        """
        return self.classify_smiles(structure.get_smiles())

    def classify_smiles(self, smiles: str):
        params = {
            'smiles': smiles,
            'classify': 'ILikeCats'
        }
        return self.requester.get_request(self.id, params=params).json()

    def copy(self, package: 'Package', debug=False):
        """
        Copies the RelativeReasoning object

        :param package: the package where the object wants to be copied to
        :param debug: whether to have more verbosity or not
        :return: a copy of the current RelativeReasoning object
        """
        payload = {
            'hiddenMethod': 'COPY',
            'targetPackage': package.get_id(),
        }

        res = self.requester.post_request(self.get_id(), payload=payload)
        res.raise_for_status()
        return RelativeReasoning(self.requester, id=res.url)


class Node(ReviewableEnviPathObject):
    """
    Class that implements the Node enviPath object
    """
    def get_smiles(self) -> str:
        """
        Retrieves the SMILES of the Compound associated with the Node object

        :return: A string representing the SMILES of the Node's Component object
        """
        return self.get_default_structure().get_smiles()

    def get_halflifes(self) -> List['HalfLife']:
        """
        Retrieves the half-lifes of the Compound contained in Node object

        :return: List of HalfLife objects
        """
        #  TODO are they equal to HLs attached to CompoundStructure?
        res = []
        for hl in self._get('halflifes'):
            res.append(HalfLife(scenarioId=hl['scenarioId'], scenarioName=hl['scenarioName'], hl=hl['hl'],
                                hl_comment=hl['hlComment'], hl_fit=hl['hlFit'], hl_model=hl['hlModel'],
                                source=hl['source']))
        return res

    def get_proposed_values_scenarios(self) -> List['Scenario']:
        return self._create_from_nested_json('proposedValues', Scenario)

    def get_confidence_scenarios(self) -> List['Scenario']:
        return self._create_from_nested_json('confidenceScenarios', Scenario)

    def get_structures(self) -> List['CompoundStructure']:
        """
        Gets the List of all CompoundStructure objects contained in the Node

        :return: A List of CompoundStructure
        """
        return self._create_from_nested_json('structures', CompoundStructure)

    def get_default_structure(self) -> CompoundStructure:
        """
        Retrieves the default structure of the Compound contained in the Node

        :return: The default CompoundStructure of the Compound contained in the Node object
        """
        return CompoundStructure(self.requester, id=self._get('defaultStructure')['id'])

    def get_svg(self) -> str:
        """
        Gets the image representation of the Compound in a string format

        :return: A string that contains the image information of the Compound
        """
        return self.get_default_structure().get_svg()

    def get_depth(self) -> int:
        """
        Gets the depth of the Node

        :return: Integer representing the depth of the Node within the Pathway
        """
        return self._get('depth')

    def get_ad_assessment(self) -> Optional['ADAssessment']:
        return self.requester.get_json(self.id + '?adassessment=true')

    @staticmethod
    def create(pathway: 'Pathway', smiles, name: str = None, description: str = None, depth: int = None) -> 'Node':
        """
        Creates a Node object within a pathway, returns the Node object.
        Similar to the Pathway.add_node() function, which does not return a Node object.

        :param pathway: parent pathway
        :param smiles: the SMILES associated with the corresponding Node
        :param name: the name of the Node
        :param description: the description of the Node
        :param depth: the depth of the Node
        :return: Node object
        """
        headers = {
            'referer': ""
        }

        payload = {
            'nodeAsSmiles': smiles,
        }

        if name:
            payload['nodeName'] = name

        if description:
            payload['nodeReason'] = description

        if depth:
            payload['nodeDepth'] = depth

        # if scenario:
        #     payload['scenario'] = scenario.get_id()

        url = '{}/{}'.format(pathway.id, Endpoint.NODE.value)
        res = pathway.requester.post_request(url, headers=headers, payload=payload, allow_redirects=False)
        res.raise_for_status()
        return Node(pathway.requester, id=res.headers['Location'])

    def copy(self, package: 'Package', debug=False):
        raise NotImplementedError("Copying of Nodes is implemented via Pathway.copy!")


class Edge(ReviewableEnviPathObject):
    """
    Class the implements an Edge enviPath object
    """
    def get_start_nodes(self) -> List['Node']:
        """
        Retrieves the starting Node object of the Edge

        :return: A List of Node objects
        """
        return self._create_from_nested_json('startNodes', Node)

    def get_end_nodes(self) -> List['Node']:
        """
        Retrieves the end Node object of the Edge

        :return: A List of Node objects
        """
        return self._create_from_nested_json('endNodes', Node)

    def get_reaction(self) -> Reaction:
        """
        Retrieves the Reaction object associated with this Edge

        :return: A Reaction enviPath object
        """
        return Reaction(self.requester, id=self._get('reactionURI'))

    def get_reaction_name(self) -> str:
        """
        Retrieves the name of the Reaction object associated with this Edge

        :return: The name of the Reaction object
        """
        return self._get('reactionName')

    def get_ec_numbers(self) -> List['ECNumber']:
        """
        Returns the EC Numbers associated with the given Edge object

        :return: A List of ECNumber objects
        """
        return self.get_reaction().get_ec_numbers()

    def get_rule(self) -> Optional['Rule']:
        """
        Retrieves the Rule associated with the Edge

        :return: A Rule enviPath object
        """
        return self.get_reaction().get_rule()

    @staticmethod
    def create(pathway: 'Pathway', smirks: str = None, educts: List['Node'] = None, products: List['Node'] = None,
               multistep: bool = False, description: str = None):
        """
        Create an Edge enviPath object

        :param pathway: the Pathway object on which the Edge wants to be created
        :param smirks: the SMIRKS of the Edge
        :param educts: a list of Node objects where the Edge starts
        :param products: a list of Node objects where the Edge ends
        :param multistep: whether the Edge is a part of a multistep Reaction
        :param description: the description of the Edge
        :return: An Edge enviPath object
        """
        assert smirks or (products and educts), 'ERROR: To add an edge to the pathway, provide either a smirks ' \
                                                'or a pair of products and educts'
        payload = {}
        if smirks:
            payload['edgeAsSmirks'] = smirks

        if products and educts:
            payload['educts'] = ','.join([e.get_id() for e in educts])
            payload['products'] = ','.join([p.get_id() for p in products])

        if multistep:
            payload['multistep'] = "true"

        if description:
            payload['edgeReason'] = description

        url = '{}/{}'.format(pathway.id, Endpoint.EDGE.value)
        res = pathway.requester.post_request(url, payload=payload, allow_redirects=False)
        res.raise_for_status()
        return Edge(pathway.requester, id=res.headers['Location'])

    def copy(self, package: 'Package', debug=False):
        raise NotImplementedError("Copying of Edges is implemented via Pathway.copy!")


class Setting(enviPathObject):

    @staticmethod
    def create(ep, packages: List[Package], name: str = None, depth_limit: int = None, node_limit: int = None,
               relative_reasoning: RelativeReasoning = None, cut_off: float = 0.5,
               evaluation_type: EvaluationType = None, min_carbon: int = None,
               terminal_compounds: List[Compound] = None):

        payload = {
            'packages[]': [p.get_id() for p in packages]
        }

        if name:
            payload['settingName'] = name

        if depth_limit:
            payload['limdepth'] = "true"
            payload['depthNumber'] = depth_limit

        if node_limit:
            payload['limnode'] = "true"
            payload['nodeNumber'] = node_limit

        if min_carbon:
            payload['mincarbons'] = "true"
            payload['carbonNumber'] = min_carbon

        if relative_reasoning:
            payload['modelUri'] = relative_reasoning.get_id()
            payload['cutoff'] = cut_off
            payload['evalType'] = evaluation_type.value

        if terminal_compounds:
            payload['terminalcompounds[]'] = [c.get_id() for c in terminal_compounds]

        url = '{}{}'.format(ep.get_base_url(), Endpoint.SETTING.value)
        res = ep.requester.post_request(url, payload=payload, allow_redirects=False)
        res.raise_for_status()
        return Setting(ep.requester, id=res.headers['Location'])

    def set_name(self, name: str) -> None:
        payload = {
            'settingName': name
        }
        self.requester.post_request(self.id, payload=payload)
        setattr(self, "settingName", name)

    def get_included_packages(self) -> List['Package']:
        return self._create_from_nested_json('includedPackages', Package)

    def get_truncationstrategy(self) -> Optional['TruncationStrategy']:
        return TruncationStrategy(self.requester, self._get("truncationstrategy"))

    def add_package(self, package: 'Package'):
        return self.add_packages([package])

    def add_packages(self, packages: List['Package']):
        payload = {
            'addedPackages[]': [p.id for p in packages]
        }
        self.requester.post_request(self.id, payload=payload)
        # TODO modify local state

    def remove_package(self, package: 'Package'):
        return self.remove_packages([package])

    def remove_packages(self, packages: List['Package']):
        payload = {
            'removedPackages[]': [p.id for p in packages]
        }
        self.requester.post_request(self.id, payload=payload)
        # TODO modify local state

    def get_normalization_rules(self) -> List['NormalizationRule']:
        return self._create_from_nested_json('normalizationRules', NormalizationRule)

    def add_normalization_rule(self, smirks: str, name: str = None, description: str = None):
        NormalizationRule.create(self, smirks, name=name, description=description)
        if not smirks:
            raise ValueError("SMIRKS not set!")

        payload = {
            'smirks': smirks
        }

        if name:
            payload['ruleName'] = name

        if description:
            payload['ruleDesc'] = description

        self.requester.post_request(self.id, payload=payload)
        # TODO modify local state


class TruncationStrategy(enviPathObject):
    pass


class NormalizationRule(ReviewableEnviPathObject):

    @staticmethod
    def create(setting: 'Setting', smirks: str, name: str = None, description: str = None):
        if not smirks:
            raise ValueError("SMIRKS not set!")

        payload = {
            'smirks': smirks
        }

        if name:
            payload['ruleName'] = name

        if description:
            payload['ruleDesc'] = description

        setting.requester.post_request(setting.id, payload=payload)

    # TODO
    # {
    #   "aliases" : [ ] ,
    #   "description" : "no description" ,
    #   "ecNumbers" : [ ] ,
    #   "id" : "http://localhost:8080/setting/fc0d27ee-23bc-479c-96aa-06a05d0d92b4/simple-rule/ae1f5b7d-36d4-4309-9437-4fce69a35e83" ,
    #   "identifier" : "simple-rule" ,
    #   "includedInCompositeRule" : [ ] ,
    #   "isCompositeRule" : false ,
    #   "name" : "cyanate" ,
    #   "pathways" : [ ] ,
    #   "productFilterSmarts" : "" ,
    #   "productsSmarts" : "[#8-:1][C:2]#[N:3]" ,
    #   "reactantFilterSmarts" : "" ,
    #   "reactantsSmarts" : "[H][#8:1][C:2]#[N:3]" ,
    #   "reactions" : [ ] ,
    #   "reviewStatus" : "undefined" ,
    #   "scenarios" : [ ] ,
    #   "smirks" : "[H][#8:1][C:2]#[N:3]>>[#8-:1][C:2]#[N:3]" ,
    #   "transformations" : "Mappings:\nMap #1     at# 1  Charge = 0   -->  at# 0  Charge = -1         pIndex = 0\nMap #2     at# 2  Charge = 0   -->  at# 1  Charge = 0         pIndex = 1\nMap #3     at# 3  Charge = 0   -->  at# 2  Charge = 0         pIndex = 2\n"
    # }
    pass


class Pathway(ReviewableEnviPathObject):
    """
    Class that implements a Pathway enviPath object
    """
    def get_nodes(self) -> List[Node]:
        """
        Retrieves the nodes of the Pathway

        :return: a List of Node objects
        """
        nodes = self._get('nodes')

        # Remove pseudo nodes
        non_pseudo_nodes = []
        for n in nodes:
            if n.get('pseudo', False):
                continue
            non_pseudo_nodes.append(n)

        return self._create_from_nested_json(non_pseudo_nodes, Node)

    def get_edges(self) -> List[Edge]:
        """
        Retrieves the edges of the Pathway

        :return: a List of Edge objects
        """
        edges = self._get('links')

        # Remove pseudo edges
        non_pseudo_edges = []
        for e in edges:
            if e.get('pseudo', False):
                continue
            non_pseudo_edges.append(e)

        return self._create_from_nested_json(non_pseudo_edges, Edge)

    def get_name(self) -> str:
        """
        Retrieves the name of the Pathway

        :return: a string of the Pathway name
        """
        return self._get('pathwayName')

    def is_up_to_date(self) -> bool:
        """
        A boolean checking is the Pathway is up-to-date

        :return: True if it is, else False
        """
        return self._get('upToDate')

    def lastmodified(self) -> int:
        """
        An integer representing the time since last modification

        :return: The last time where it was modified as an integer
        """
        return self._get('lastModified')

    def is_completed(self) -> bool:
        """
        Checks if the Pathway prediction has been completed

        :return: True if it did, else False
        """
        status = self.requester.get_request('{}?status'.format(self.id)).json()
        return "true" == status['completed']

    def has_failed(self) -> bool:
        """
        Checks if the Pathway prediction has failed

        :return: True if it did, else False
        """
        status = self.requester.get_request('{}?status'.format(self.id)).json()
        return "error" == status['completed']

    def is_running(self):
        """
        Checks if the Pathway prediction is running

        :return: True if it did, else False
        """
        status = self.requester.get_request('{}?status'.format(self.id)).json()
        return "false" == status['completed']

    def add_node(self, smiles, name: str = None, depth: int = None, description: str = None):
        """
        Adds a node to the pathway object, does NOT return the node.
        Very similar to the node create function, which returns a Node object.

        :param smiles: the SMILES of the Node that wants to be added
        :param name: the name of the Node
        :param depth: the depth of the Node
        :param description: the description of the Node
        """
        headers = {
            'referer': self.id
        }

        payload = {
            'nodeAsSmiles': smiles,
        }

        if name is not None:
            payload['nodeName'] = name

        if description is not None:
            payload['nodeReason'] = description

        if depth is not None:
            payload['nodeDepth'] = depth

        url = '{}/{}'.format(self.id, Endpoint.NODE.value)
        res = self.requester.post_request(url, headers=headers, payload=payload, allow_redirects=False)
        res.raise_for_status()

        self.loaded = False
        if hasattr(self, 'nodes'):
            delattr(self, 'nodes')

    def add_edge(self, smirks: str = None, educts: str = None, products: str = None, multistep: bool = False,
                 description: str = None):
        """
        Adding an edge to an existing pathway. Either provide smirks, or educts AND products.

        :param smirks: SMIRKS format of the reaction
        :param educts: compound URIs of educts, comma separated
        :param products: compound URIs of products, comma separated
        :param multistep: If needed, can be set to 'true'
        :param description: The description of the Edge
        """
        headers = {'referer': self.id}
        assert smirks or (products and educts), 'ERROR: To add an edge to the pathway, provide either a smirks ' \
                                                'or a pair of products and educts'
        payload = {}
        if smirks:
            payload['edgeAsSmirks'] = smirks
        if products and educts:
            payload['educts'] = educts
            payload['products'] = products
        if multistep:
            payload['multistep'] = "true"
        if description:
            payload['edgeReason'] = description
        url = '{}/{}'.format(self.id, Endpoint.EDGE.value)
        self.requester.post_request(url, headers=headers, payload=payload, allow_redirects=False)
        self.loaded = False

    @staticmethod
    def create(package: Package, smiles: str, name: str = None, description: str = None,
               root_node_only: bool = False, setting: Setting = None):
        """
        Creates a Pathway enviPath object

        :param package: the Package where the Pathway wants to be added
        :param smiles: Smiles of root node compound
        :param name: the name of the Pathway
        :param description: the description of the Pathway
        :param root_node_only: If False, goes to pathway prediction mode
        :param setting: Setting for pathway prediction
        :return: Pathway enviPath object
        """
        payload = {'smilesinput': smiles}

        # TODO the API allows creation of Setting on the fly. Should we support that here?

        if name:
            payload['name'] = name

        if description:
            payload['description'] = description

        if root_node_only:
            payload['rootOnly'] = "true"

        if setting:
            payload['selectedSetting'] = setting.get_id()

        res = package.requester.post_request(package.id + '/' + Endpoint.PATHWAY.value, params=None,
                                             payload=payload, allow_redirects=False)
        res.raise_for_status()
        return Pathway(package.requester, id=res.headers['Location'])

    def copy(self, target_package: 'Package', debug=False) -> (dict, 'Pathway'):
        """
        Copies the Pathway to the target_package

        :param target_package: Package where the Pathway wants to be copied to
        :param debug: whether to add more verbosity or not to the method
        :return: a dictionary mapping the ids of the parent and copied object, a Pathway object that is a copy
            of the current one
        """
        mapping = dict()

        # Obtain d3json as it contains the nodes depth
        pw_json = self.get_json()
        depth_mapping = dict()

        for node in pw_json['nodes']:
            depth_mapping[node['id']] = node['depth']

        nodes_tmp = self.get_nodes()

        nodes = []
        for n in nodes_tmp:
            if 'edge' in n.get_id():
                continue
            nodes.append(n)

        # determine root node
        root_node = None
        for node in nodes:
            if depth_mapping[node.get_id()] == 0:
                root_node = node
                break

        pw_params = {
            'name': self.get_name(),
            'description': self.get_description(),
            'smiles': root_node.get_smiles(),
            'root_node_only': True,
        }

        # Create pathway only containing the root node
        copied_pathway = Pathway.create(target_package, **pw_params)

        mapping[self.get_id()] = copied_pathway.get_id()
        mapping[root_node.get_id()] = copied_pathway.get_nodes()[0].get_id()

        node_mapping = dict()
        node_mapping[root_node.get_id()] = copied_pathway.get_nodes()[0]

        # Add remaining nodes
        for node in nodes:
            if node == root_node:
                continue

            copied_node = Node.create(copied_pathway, smiles=node.get_smiles(), name=node.get_name(),
                                      description=node.get_description(), depth=depth_mapping[node.get_id()])

            mapping[node.get_id()] = copied_node.get_id()
            node_mapping[node.get_id()] = copied_node

        # Add edges
        for edge in self.get_edges():
            educts = [node_mapping[x.get_id()] for x in edge.get_start_nodes()]
            products = [node_mapping[x.get_id()] for x in edge.get_end_nodes()]
            copied_edge = Edge.create(copied_pathway, educts=educts, products=products,
                                      multistep=edge.get_reaction().is_multistep())
            mapping[edge.get_id()] = copied_edge.get_id()

        return mapping, copied_pathway


class User(enviPathObject):
    """
    Class that implements a User enviPath object
    """
    def get_email(self) -> str:
        """
        Gets the email of the User

        :return: an email in string format
        """
        return self._get('email')

    def get_forename(self) -> str:
        """
        Gets the forename of the User

        :return: a forename in string format
        """
        return self._get('forename')

    def get_surname(self) -> str:
        """
        Gets the surname of the User

        :return: a surname in string format
        """
        return self._get('surname')

    def get_default_group(self) -> 'Group':
        """
        Gets the default Group of the User

        :return: A Group object to which the User belonged by default
        """
        return Group(self.requester, id=self._get("defaultGroup")['id'])

    def get_group(self, group_id) -> 'Group':
        """
        Gets the Group of the User

        :param group_id: The identifier of a Group object
        :return: The Group object to which the User belongs
        """
        return Group(self.requester, id=group_id)

    def get_groups(self) -> List['Group']:
        """
        Gets all the groups the User belongs to

        :return: a List of Group enviPath objects
        """
        return self._create_from_nested_json('groups', Group)

    def get_default_package(self) -> 'Package':
        """
        Gets the Package the User belonged by default

        :return: A Package enviPath object
        """
        return Package(self.requester, id=self._get("defaultPackage")['id'])

    def get_default_setting(self) -> Optional['Setting']:
        """
        Gets the Setting the User had by default

        :return: A Setting enviPath object
        """
        try:
            return Setting(self.requester, id=self._get("defaultSetting")['id'])
        except ValueError:
            return None

    def get_setting(self, setting_id):
        """
        Gets a Setting of the User

        :param setting_id: The identifier of a Setting object
        :return: The Setting object to which the User belongs
        """
        return Setting(self.requester, id=setting_id)

    def get_settings(self) -> List['Setting']:
        """
        Gets all the settings the User has

        :return: a List of Setting enviPath objects
        """
        return self._create_from_nested_json('settings', Setting)

    @staticmethod
    def create(ep, email: str, username: str, password: str):
        payload = {
            'username': username,
            'email': email,
            'password': password
        }
        raise NotImplementedError("Not (yet) implemented!")

    @staticmethod
    def register(ep, email: str, username: str, password: str):
        """
        Alias for 'create()'.

        :param ep: an enviPath object
        :param email: the email of the User that wants to be registered
        :param username: the username of the User
        :param password: the password of the User
        :return: A User enviPath object
        """
        return User.create(ep, email, username, password)

    @staticmethod
    def activate(ep, username, token) -> bool:
        """
        Activates the specified username

        :param ep: an enviPath object
        :param username: the username of the User that wants to be activated
        :param token: the activation token
        :return: True if the User was successfully activated, else False
        """
        params = {
            'username': username,
            'token': token
        }
        activation_url = '{}activation'.format(ep.BASE_URL)
        res = ep.requester.get_request(activation_url, params=params, allow_redirects=False)
        res.raise_for_status()
        return 'activationSuccessful' in res.headers['Location']


class Group(enviPathObject):

    def create(self, **kwargs):
        raise NotImplementedError("Not (yet) implemented!")


##################
# Helper Classes #
##################

HalfLife = namedtuple('HalfLife', 'scenarioName, scenarioId, hl, hl_comment, hl_fit, hl_model, source')
ModelStatus = namedtuple('ModelStatus', 'progress, status, statusMessage')


class ECNumber(object):

    def __init__(self, ec_number: str, ec_name: str, pathways: List['Pathway']):
        self.ec_number = ec_number
        self.ec_name = ec_name
        self.pathways = pathways


####################################
# Generated Additional Information #
####################################

class AdditionalInformation(ABC):
    name = None
    mandatories = []

    def __init__(self, *args, **kwargs):
        self.params = {}
        for k, v in kwargs.items():
            func = getattr(self, 'set_{}'.format(k))
            func(v)

    def validate(self):
        for m in self.mandatories:
            if self.params.get(m, None) is None:
                raise ValueError("{} not set".format(m))
        return self

    def get_unit(self):
        return self.params.get("unit")

    @classmethod
    def _parse_default(cls, data_string, keys):
        parts = data_string.split(";")
        if len(keys) != len(parts):
            raise ValueError("Unable to properly map {} and {}".format(parts, keys))

        return cls(**{k: v for k, v in zip(keys, parts)})

    @staticmethod
    def all_subclasses(cls):
        return set(cls.__subclasses__()).union(
            [s for c in cls.__subclasses__() for s in AdditionalInformation.all_subclasses(c)])

    @staticmethod
    def get_subclass_by_name(name):
        matching_clz = None
        for sub in AdditionalInformation.all_subclasses(AdditionalInformation):
            if sub.name == name:
                matching_clz = sub

        if matching_clz is None:
            raise ValueError("Unknown {} type {}".format(AdditionalInformation.__name__, name))

        return matching_clz


class DummyAdditionalInformation(AdditionalInformation):

    def validate(self):
        raise NotImplementedError("DummyAdditionalInformation can't be validated!")

    @classmethod
    def parse(cls, data_string):
        return cls(data=data_string)


class OxygenDemandAdditionalInformation(AdditionalInformation):
    """
    Creates the oxygen demand additional information object.

    This class represents additional information about oxygen demand,
    including the type, influent, and effluent values.
    """
    name = "oxygendemand"
    mandatories = ['oxygendemandType']
    allowed_types = ['Chemical Oxygen Demand (COD)', 'Biological Oxygen Demand (BOD5)']

    # Setter
    def set_oxygendemandType(self, value):
        """
        Sets the oxygen demand type.

        :param value: The value to set. Must be one of '', 'Chemical Oxygen Demand (COD)',
            'Biological Oxygen Demand (BOD5)'.
        :type value: str
        """
        if value not in self.allowed_types:
            raise ValueError(f"The value {value} does not belong to the set of allowed values {self.allowed_types}")
        self.params["oxygendemandType"] = value

    def set_oxygendemandInfluent(self, value):
        """
        Sets the influent oxygen demand.

        :param value: The influent value of the oxygen demand, measured in mg/L.
        :type value: float
        """

        self.params["oxygendemandInfluent"] = float(value)

    def set_oxygendemandEffluent(self, value):
        """
        Sets the effluent oxygen demand, m

        :param value: The effluent value of the oxygen demand, measured in mg/L.
        :type value: float
        """

        self.params["oxygendemandEffluent"] = float(value)

    # Getter
    def get_oxygendemandType(self):
        """
        Retrieves the oxygen demand type

        :return: The oxygen demand value of the influent if set; otherwise, None
        :rtype: str
        """
        return self.params.get("oxygendemandType", None)

    def get_oxygendemandInfluent(self):
        """
        Retrieves the influent oxygen demand value
        
        :return: The influent oxygen demand value if set; otherwise, None
        :rtype: float or None
        """
        return self.params.get("oxygendemandInfluent", None)

    def get_oxygendemandEffluent(self):
        """
        retrieves The effluent oxygen demand value

        :return: The effluent oxygen demand value if set; otherwise, None
        :rtype: float or None
        """
        return self.params.get("oxygendemandEffluent", None)

    # Parser 
    @classmethod
    def parse(cls, data_string):
        """
        Parses a semicolon-separated data_string and returns the instantiated additional information object.

        :param data_string: A semicolon separated string in the format '
            oxygendemandType;oxygendemandInfluent;oxygendemandEffluent'
        :type data_string: str
        :return: The additional information object instantiated with the parsed data.
        :rtype: OxygenDemandAdditionalInformation
        """
        parts = data_string.split(';')

        res = {'oxygendemandType': parts[0]}

        if len(parts) > 1 and parts[1] != '':
            res['oxygendemandInfluent'] = float(parts[1])

        if len(parts) > 2 and parts[2] != '':
            res['oxygendemandEffluent'] = float(parts[2])

        return cls(**res)


class DissolvedOxygenConcentrationAdditionalInformation(AdditionalInformation):
    """
    Creates a Dissolved Oxygen Concentration additional information object.

    This class represents additional information about dissolved oxygen concentration,
    including the lower and upper limits.
    """
    name = "Dissolvedoxygenconcentration"
    mandatories = ['DissolvedoxygenconcentrationLow', 'DissolvedoxygenconcentrationHigh']

    # Setter
    def set_DissolvedoxygenconcentrationLow(self, value):
        """
        Sets the lower limit for dissolved oxygen concentration.

        :param value: The lower limit of dissolved oxygen concentration, measured in mg/L.
        :type value: float
        """
        self.params["DissolvedoxygenconcentrationLow"] = float(value)

    def set_DissolvedoxygenconcentrationHigh(self, value):
        """
        Sets the upper limit for dissolved oxygen concentration.

        :param value: The upper limit of dissolved oxygen concentration, measured in mg/L.
        :type value: float
        """
        self.params["DissolvedoxygenconcentrationHigh"] = float(value)

    # Getter
    def get_DissolvedoxygenconcentrationLow(self):
        """
        Retrieves the lower limit for dissolved oxygen concentration.

        :return: The lower limit of dissolved oxygen concentration if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("DissolvedoxygenconcentrationLow", None)

    def get_DissolvedoxygenconcentrationHigh(self):
        """
        Retrieves the upper limit for dissolved oxygen concentration.

        :return: The upper limit of dissolved oxygen concentration if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("DissolvedoxygenconcentrationHigh", None)

    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing the low and high limits for dissolved oxygen concentration and returns the
        additional information object.

        :param data_string: A semicolon separated string in the format
            'DissolvedoxygenconcentrationLow;DissolvedoxygenconcentrationHigh'
        :type data_string: str
        :return: An instance of DissolvedOxygenConcentrationAdditionalInformation populated with the parsed data.
        :rtype: DissolvedOxygenConcentrationAdditionalInformation
        """
        low, high = data_string.split(';')
        res = {
            'DissolvedoxygenconcentrationLow': low,
            'DissolvedoxygenconcentrationHigh': high,
        }
        return cls(**res)


class EnzymeAdditionalInformation(AdditionalInformation):
    """
    Creates an Enzyme additional information object.

    This class represents additional information about enzymes.
    """
    name = "enzyme"
    mandatories = ["enzymeName", "enzymeECNumber"]

    # Setter
    def set_enzymeName(self, value):
        """
        Sets the enzyme name.

        :param value: The name of the enzyme.
        :type value: str
        """
        self.params["enzymeName"] = value

    def set_enzymeECNumber(self, value):
        """
        Sets the enzyme EC number.

        :param value: The EC number of the enzyme.
        :type value: str
        """
        self.params["enzymeECNumber"] = value

    # Getter
    def get_enzymeName(self):
        """
        Gets the enzyme name.

        :return: The name of the enzyme, or None if not set.
        :rtype: str or None
        """
        return self.params.get("enzymeName", None)

    def get_enzymeECNumber(self):
        """
        Gets the enzyme EC number.

        :return: The EC number of the enzyme, or None if not set.
        :rtype: str or None
        """
        return self.params.get("enzymeECNumber", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create an EnzymeAdditionalInformation instance.

        :param data_string: A string in the format 'enzymeName (enzymeECNumber)'.
        :type data_string: str
        :return: EnzymeAdditionalInformation instance.
        :rtype: EnzymeAdditionalInformation
        """
        start = data_string.find('(')
        end = data_string.find(')')
        res = {
            "enzymeName": data_string[:start].strip(),
            "enzymeECNumber": data_string[start + 1:end]
        }
        return cls(**res)


class OxygenUptakeRateAdditionalInformation(AdditionalInformation):
    """
    Creates an Oxygen Uptake Rate additional information object.

    This class represents additional information about oxygen uptake rate,
    including the start and end values.
    """
    name = "oxygenuptakerate"
    mandatories = ['oxygenuptakerateStart', 'oxygenuptakerateEnd']

    # Setter
    def set_oxygenuptakerateStart(self, value):
        """
        Sets the start value for the oxygen uptake rate.

        :param value: The start value of the oxygen uptake rate, measured in mg/L/hr.
        :type value: float
        """
        self.params["oxygenuptakerateStart"] = float(value)

    def set_oxygenuptakerateEnd(self, value):
        """
        Sets the end value for the oxygen uptake rate.

        :param value: The end value of the oxygen uptake rate, measured in mg/L/hr.
        :type value: float
        """
        self.params["oxygenuptakerateEnd"] = float(value)

    # Getter
    def get_oxygenuptakerateStart(self):
        """
        Retrieves the start value for the oxygen uptake rate.

        :return: The start value of the oxygen uptake rate if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("oxygenuptakerateStart", None)

    def get_oxygenuptakerateEnd(self):
        """
        Retrieves the end value for the oxygen uptake rate.

        :return: The end value of the oxygen uptake rate if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("oxygenuptakerateEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing the start and end values for the oxygen uptake rate to initialize an instance.

        :param data_string: A semicolon separated string in the format 'oxygenuptakerateStart;oxygenuptakerateEnd' 
        :type data_string: str
        :return: An instance of OxygenUptakeRateAdditionalInformation populated with the parsed data.
        :rtype: OxygenUptakeRateAdditionalInformation
        """
        start, end = data_string.split(';')
        res = {
            'oxygenuptakerateStart': start,
            'oxygenuptakerateEnd': end,
        }
        return cls(**res)


class AerationTypeAdditionalInformation(AdditionalInformation):
    """
    Creates an Aeration Type additional information object.

    This class represents additional information about the type of aeration used in sludge data.
    """
    name = "aerationtype"
    mandatories = ['aerationtype']
    allowed_types = ["stirring", "shaking", "bubbling air", "bubbling air and stirring", "other"]

    # Setter
    def set_aerationtype(self, value):
        """
        Sets the type of aeration.

        :param value: The type of aeration. Must be one of the following "stirring", "shaking", "bubbling air",
            "bubbling air and stiring", "other"
        otherwise it could cause an error.
        :type value: str
        """
        if value not in self.allowed_types:
            raise ValueError(f"The value {value} is not one of the allowed values {self.allowed_types}")
        self.params["aerationtype"] = value

    # Getter
    def get_aerationtype(self):
        """
        Retrieves the type of aeration.

        :return: The type of aeration if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("aerationtype", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing the type of aeration to initialize an instance.

        :param data_string: A string in the form of 'aerationtype'.
        :type data_string: str
        :return: An instance of AerationTypeAdditionalInformation populated with the parsed data.
        :rtype: AerationTypeAdditionalInformation
        """
        res = {
            'aerationtype': data_string,
        }
        return cls(**res)


class PhosphorusContentAdditionalInformation(AdditionalInformation):
    """
    Creates an additional information object for phosphorus content.

    This class represents additional information about phosphorus content in influent and effluent.
    """
    name = "phosphoruscontent"
    mandatories = []

    # Setter
    def set_phosphoruscontentInfluent(self, value):
        """
        Sets the influent phosphorus content, measured in mg/L.

        :param value: The phosphorus content in influent.
        :type value: float
        """

        self.params["phosphoruscontentInfluent"] = float(value)

    def set_phosphoruscontentEffluent(self, value):
        """
        Sets the effluent phosphorus content.

        :param value: The phosphorus content in effluent, measured in mg/L.
        :type value: float
        """

        self.params["phosphoruscontentEffluent"] = float(value)

    # Getter
    def get_phosphoruscontentInfluent(self):
        """
        Retrieves the influent phosphorus content.

        :return: The phosphorus content in influent if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("phosphoruscontentInfluent", None)

    def get_phosphoruscontentEffluent(self):
        """
        Retrieves the effluent phosphorus content.

        :return: The phosphorus content in effluent if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("phosphoruscontentEffluent", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing phosphorus content information to initialize an instance.

        :param data_string: A semi-colon seperated string in the format
            'phosphoruscontentInfluent;phosphoruscontentEffluent' or just 'phosphoruscontentInfluent'.
        :type data_string: str
        :return: An instance of PhosphorusContentAdditionalInformation populated with the parsed data.
        :rtype: PhosphorusContentAdditionalInformation
        """
        parts = data_string.split(";")
        res = {}
        if parts[0] == "":
            res["phosphoruscontentEffluent"] = float(parts[1])
        elif parts[1] == "":
            res["phosphoruscontentInfluent"] = float(parts[0])
        else:
            res["phosphoruscontentInfluent"] = float(parts[0])
            res["phosphoruscontentEffluent"] = float(parts[1])
        return cls(**res)


class MinorMajorAdditionalInformation(AdditionalInformation):
    """
    Object that implements the Transformation product importance
    """
    name = "minormajor"
    mandatories = ['radiomin']
    allowed_values = ["minor", "major"]

    # Setter
    def set_radiomin(self, value):
        """
        Sets the value for the transformation product importance

        :param value: a text value similar to 'minor' or 'major'
        :type value: str
        """
        if value.lower() not in self.allowed_values:
            raise ValueError(f"{value} is not one the allowed_values {self.allowed_values}")
        self.params["radiomin"] = value.lower().capitalize()

    # Getter
    def get_radiomin(self):
        """
        Gets the value of transformation product importance

        :rtype: str
        """
        return self.params.get("radiomin", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to extract the value of radiomin

        :param data_string: the string containing the values of transformation product importance
        :type data_string: str
        :return: An instance of MinorMajorAdditionalInformation populated with the parsed data.
        :rtype: MinorMajorAdditionalInformation
        """
        return cls._parse_default(data_string, ['radiomin'])


class SludgeRetentionTimeAdditionalInformation(AdditionalInformation):
    """
    Creates a sludge retention time additional information object.

    This class represents additional information about sludge retention time.
    """
    name = "sludgeretentiontime"
    mandatories = ['sludgeretentiontimeType', 'sludgeretentiontime']
    allowed_values = ['sludge age', 'sludge retention time']

    # Setter
    def set_sludgeretentiontimeType(self, value):
        """
        Sets the type of sludge retention time.

        :param value: The type of sludge retention time, either 'sludge age' or 'sludge retention time'.
        :type value: str
        """
        if value not in self.allowed_values:
            raise ValueError(f"({value} is not an allowed sludge retention time type {self.allowed_values}")
        self.params["sludgeretentiontimeType"] = value

    def set_sludgeretentiontime(self, value):
        """
        Sets the sludge retention time.

        :param value: The sludge retention time, given in days.
        :type value: float
        """
        self.params["sludgeretentiontime"] = float(value)

    # Getter
    def get_sludgeretentiontimeType(self):
        """
        Get the type of sludge retention time.

        :return: The type of sludge retention time, or None if not set.
        :rtype: float or None
        """
        return self.params.get("sludgeretentiontimeType")

    def get_sludgeretentiontime(self):
        """
        Get the sludge retention time.

        :return: The sludge retention time, or None if not set.
        :rtype: str or float or None
        """
        return self.params.get("sludgeretentiontime")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SludgeRetentionTimeAdditionalInformation instance.

        :param data_string: A semicolon separated string in the format "sludgeretentiontimeType;sludgeretentiontime".
        :type data_string: str
        :return: SludgeRetentionTimeAdditionalInformation instance.
        :rtype: SludgeRetentionTimeAdditionalInformation
        """
        parts = data_string.split(";")

        res = {"sludgeretentiontimeType": parts[0],
               "sludgeretentiontime": float(parts[1])}
        return cls(**res)


class SoilClassificationAdditionalInformation(AdditionalInformation):
    """
    Creates a soil classification system additional information object.

    This class represents additional information about soil classification systems.
    """
    name = "soilclassificationsystem"
    mandatories = ["soilclassificationsystem"]
    allowed_values = ["USDA", "UK_ADAS", "UK ADAS", "UK", "DE", "International"]

    # Setter
    def set_soilclassificationsystem(self, value):
        """
        Sets the soil classification system.

        :param value: The soil classification system. Must be either 'USDA', 'UK_ADAS', 'UK', 'DE', 'International'.
        :type value: str
        """
        if value not in self.allowed_values:
            raise ValueError("{} is not allowed as soilclassificationsystem {}".format(value,
                                                                                       self.allowed_values))
        self.params["soilclassificationsystem"] = value

    # Getter
    def get_soilclassificationsystem(self):
        """
        Get the soil classification system.

        :return: The soil classification system, or None if not set.
        :rtype: str or None
        """
        return self.params.get("soilclassificationsystem")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SoilClassificationAdditionalInformation instance.

        :param data_string: String containing soil classification system data.
        :type data_string: str
        :return: SoilClassificationAdditionalInformation instance.
        :rtype: SoilClassificationAdditionalInformation
        """
        return cls._parse_default(data_string, ['soilclassificationsystem'])


class SoilSourceAdditionalInformation(AdditionalInformation):
    """
    Creates a soil source additional information object.

    This class represents additional information about soil source, which is the sample location of the soil.
    """
    name = "soilsource"
    mandatories = ["soilsourcedata"]

    # Setter
    def set_soilsourcedata(self, value):
        """
        Sets the soil source data.

        :param value: The soil source data.
        :type value: str
        """
        self.params["soilsourcedata"] = value

    # Getter
    def get_soilsourcedata(self):
        """
        Get the soil source data.

        :return: The soil source data, or None if not set.
        :rtype: str or None
        """
        return self.params.get("soilsourcedata")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SoilSourceAdditionalInformation instance.

        :param data_string: String containing soil source data.
        :type data_string: str
        :return: SoilSourceAdditionalInformation instance.
        :rtype: SoilSourceAdditionalInformation
        """
        return cls._parse_default(data_string, ['soilsourcedata'])


class SoilTexture1AdditionalInformation(AdditionalInformation):
    """
    Creates a soil texture additional information object.

    This class represents additional information about soil texture types. 
    Can also be used for classifying sludge and sediment types.
    """
    name = "soiltexture1"
    mandatories = ["soilTextureType"]
    allowed_types = [
        "CLAY", "SANDY CLAY", "SILTY CLAY", "SANDY CLAY LOAM", "SANDY LOAM",
        "SILTY CLAY LOAM", "SAND", "LOAMY SAND", "LOAM", "SILT LOAM", "SILT", "CLAY LOAM",
        "SILTY SAND", "SANDY SILT LOAM"
    ]

    # Setter
    def set_soilTextureType(self, value):
        """
        Sets the soil texture type.

        :param value: The soil texture type.
        :type value: str
        :raises ValueError: If the value is not one of the allowed soil texture types.
        """
        if value.upper() not in self.allowed_types:
            raise ValueError("{} is not an allowed soilTextureType {}".format(value, self.allowed_types))
        self.params["soilTextureType"] = value

    # Getter
    def get_soilTextureType(self):
        """
        Gets the soil texture type.

        :return: The soil texture type, or None if not set.
        :rtype: str or None
        """
        return self.params.get("soilTextureType")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SoilTexture1AdditionalInformation instance.

        :param data_string: String containing soil texture type data.
        :type data_string: str
        :return: SoilTexture1AdditionalInformation instance.
        :rtype: SoilTexture1AdditionalInformation
        """
        return cls._parse_default(data_string, ['soilTextureType'])


class SoilTexture2AdditionalInformation(AdditionalInformation):
    """
    Creates a soil texture additional information object.

    This class represents additional information about soil texture components: sand, silt, and clay.
    Can also be used for classifying sludge and sediment types.
    """
    name = "soiltexture2"
    mandatories = ["sand", "silt", "clay"]

    # Setter
    def set_sand(self, value):
        """
        Sets the percentage of sand in the soil.

        :param value: The sand percentage, measured in %.
        :type value: float
        """
        self.params["sand"] = float(value)

    def set_silt(self, value):
        """
        Sets the percentage of silt in the soil.

        :param value: The silt percentage, measured in %.
        :type value: float
        """
        self.params["silt"] = float(value)

    def set_clay(self, value):
        """
        Sets the percentage of clay in the soil.

        :param value: The clay percentage, measured in %.
        :type value: float
        """
        self.params["clay"] = float(value)

    # Getter 
    def get_sand(self):
        """
        Gets the percentage of sand in the soil.

        :return: The sand percentage, or None if not set.
        :rtype: float or None
        """
        return self.params.get("sand", None)

    def get_silt(self):
        """
        Gets the percentage of silt in the soil.

        :return: The silt percentage, or None if not set.
        :rtype: float or None
        """
        return self.params.get("silt", None)

    def get_clay(self):
        """
        Gets the percentage of clay in the soil.

        :return: The clay percentage, or None if not set.
        :rtype: float or None
        """
        return self.params.get("clay", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SoilTexture2AdditionalInformation instance.

        :param data_string: String containing soil texture data in the format 'Soil texture 2: 45.0% sand; 34.0% silt;
            34.0% clay'.
        :type data_string: str
        :return: SoilTexture2AdditionalInformation instance.
        :rtype: SoilTexture2AdditionalInformation
        """
        res = {}
        last_index = -1
        count = 0

        while True:
            index = data_string.find("%", last_index + 1)
            if index == -1:
                break
            last_index = index
            count += 1
            if count == 1:
                res["sand"] = float(data_string[index-4:index])
            elif count == 2:
                res["silt"] = float(data_string[index-4:index])
            elif count == 3:
                res["clay"] = float(data_string[index-4:index])

        return cls(**res)


class AmmoniaUptakeRateAdditionalInformation(AdditionalInformation):
    """
    Creates an AmmoniaUptakeRateAdditionalInformation object.

    This class represents additional information about the ammonia uptake rate,
    including the start and end values. Either start and/or end value must be defined.
    """
    name = "amionauptakerate"
    mandatories = []

    # Setter
    def set_amionauptakerateStart(self, value):
        """
        Sets the start value for ammonia uptake rate.

        :param value: The start value for ammonia uptake rate.
        :type value: float
        """

        self.params["amionauptakerateStart"] = float(value)

    def set_amionauptakerateEnd(self, value):
        """
        Sets the end value for ammonia uptake rate.

        :param value: The end value for ammonia uptake rate.
        :type value: float
        """

        self.params["amionauptakerateEnd"] = float(value)

    # Getter
    def get_amionauptakerateStart(self):
        """
        Retrieves the start value for ammonia uptake rate.

        :return: The start value for ammonia uptake rate if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("amionauptakerateStart", None)

    def get_amionauptakerateEnd(self):
        """
        Retrieves the end value for ammonia uptake rate.

        :return: The end value for ammonia uptake rate if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("amionauptakerateEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing ammonia uptake rate information to initialize an instance.

        :param data_string: A semicolon-separated string in the form of 'amionauptakerateStart;amionauptakerateEnd'
            either start and/or end value must be defined.
        :type data_string: str
        :return: An instance of AmmoniaUptakeRateAdditionalInformation populated with the parsed data.
        :rtype: AmmoniaUptakeRateAdditionalInformation
        """
        return cls._parse_default(data_string, ['amionauptakerateStart', 'amionauptakerateEnd'])


class TemperatureAdditionalInformation(AdditionalInformation):
    """
    Creates a TemperatureAdditionalInformation object.

    This class represents additional information about the temperature. 
    Minimal and maximal temperature values can be set.
    """
    name = "temperature"
    mandatories = ["temperatureMin"]

    # Setter
    def set_temperatureMin(self, value):
        """
        Sets the minimum temperature.

        :param value: The minimum temperature, measured in degrees Celsius.
        :type value: float
        """
        self.params["temperatureMin"] = float(value)

    def set_temperatureMax(self, value):
        """
        Sets the maximum temperature.

        :param value: The maximum temperature, measured in degrees Celsius.
        :type value: float
        """
        self.params["temperatureMax"] = float(value)

    # Getter
    def get_temperatureMin(self):
        """
        Gets the minimum temperature.

        :return: The minimum temperature if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("temperatureMin", None)

    def get_temperatureMax(self):
        """
        Gets the maximum temperature.

        :return: The maximum temperature if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("temperatureMax", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a TemperatureAdditionalInformation instance.

        :param data_string: A semicolon-separated string in the format 'temperatureMin;temperatureMax'.
        :type data_string: str
        :return: TemperatureAdditionalInformation instance.
        :rtype: TemperatureAdditionalInformation
        """
        return cls._parse_default(data_string, ['temperatureMin', 'temperatureMax'])


class TotalOrganicCarbonAdditionalInformation(AdditionalInformation):
    """
    Creates a TotalOrganicCarbonAdditionalInformation object.

    This class represents additional information about total organic carbon (TOC) values.
    """
    name = "totalorganiccarbon"
    mandatories = ["totalorganiccarbonStart"]

    # Setter
    def set_totalorganiccarbonStart(self, value):
        """
        Sets the start value for total organic carbon.

        :param value: The start value for total organic carbon, measured in percentage.
        :type value: float
        :raises ValueError: If the value is not a float.
        """
        self.params["totalorganiccarbonStart"] = float(value)

    def set_totalorganiccarbonEnd(self, value):
        """
        Sets the end value for total organic carbon.

        :param value: The end value for total organic carbon, measured in percentage.
        :type value: float
        :raises ValueError: If the value is not a float.
        """
        self.params["totalorganiccarbonEnd"] = float(value)

    # Getter
    def get_totalorganiccarbonStart(self):
        """
        Gets the start value for total organic carbon.

        :return: The start value for total organic carbon if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("totalorganiccarbonStart", None)

    def get_totalorganiccarbonEnd(self):
        """
        Gets the end value for total organic carbon.

        :return: The end value for total organic carbon if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("totalorganiccarbonEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a TotalOrganicCarbonAdditionalInformation instance.

        :param data_string: A semicolon-separated string in the format 'totalorganiccarbonStart;totalorganiccarbonEnd'.
        :type data_string: str
        :return: TotalOrganicCarbonAdditionalInformation instance.
        :rtype: TotalOrganicCarbonAdditionalInformation
        """
        return cls._parse_default(data_string, ["totalorganiccarbonStart", "totalorganiccarbonEnd"])


class TypeOfAdditionAdditionalInformation(AdditionalInformation):
    """
    Creates a Type of Addition additional information object.

    This class represents additional information about the type of compound addition which is either spiking in solvent,
        plating or some other type.
    """
    name = "typeofaddition"
    mandatories = ['typeofaddition']
    allowed_values = ['spiking in solvent', 'plating', 'other']

    # Setter
    def set_typeofaddition(self, value):
        """
        Sets the type of addition. Either 'spiking in solvent', 'plating', 'other'

        :param value: The type of addition.
        :type value: str
        """
        if value not in self.allowed_values:
            raise ValueError(f"{value} not an allowed addition type")
        self.params["typeofaddition"] = value

    # Getter
    def get_typeofaddition(self):
        """
        Gets the type of addition.

        :return: The type of addition if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("typeofaddition", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a TypeOfAdditionAdditionalInformation instance.

        :param data_string: A string containing the type of addition.
        :type data_string: str
        :return: TypeOfAdditionAdditionalInformation instance.
        :rtype: TypeOfAdditionAdditionalInformation
        """
        return cls._parse_default(data_string, ['typeofaddition'])


class NutrientsAdditionalInformation(AdditionalInformation):
    """
    Creates a nutrients additional information object.

    This class represents additional information about the addition of nutrients.
    """
    name = "additionofnutrients"
    mandatories = ['additionofnutrients']

    # Setter
    def set_additionofnutrients(self, value):
        """
        Sets the information about the addition of nutrients.

        :param value: The information about the addition of nutrients.
        :type value: str
        """
        self.params["additionofnutrients"] = value

    # Getter
    def get_additionofnutrients(self):
        """
        Retrieves the information about the addition of nutrients.

        :return: The information about the addition of nutrients if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("additionofnutrients", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing information about the addition of nutrients to initialize an instance.

        :param data_string: A string representing the information about the addition of nutrients.
        :type data_string: str
        :return: An instance of NutrientsAdditionalInformation populated with the parsed data.
        :rtype: NutrientsAdditionalInformation
        """
        return cls(**{'additionofnutrients': data_string})


class OMContentAdditionalInformation(AdditionalInformation):
    """
    Creates an organic matter (OM) content additional information object.

    This class represents additional information about organic matter content.
    """
    name = "omcontent"
    mandatories = []

    # Setter
    def set_omcontentInOM(self, value):
        """
        Sets the organic matter content measured in organic matter.

        :param value: The OM content measured in organic matter.
        :type value: float
        """
        self.params["omcontentInOM"] = float(value)

    def set_omcontentINOC(self, value):
        """
        Sets the organic matter content measured in organic carbon.

        :param value: The OM content, measured in organic carbon.
        :type value: float
        """
        self.params["omcontentINOC"] = float(value)

    # Getter
    def get_omcontentInOM(self):
        """
        Retrieves the OM content in OM.

        :return: The OM content in OM if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("omcontentInOM", None)

    def get_omcontentINOC(self):
        """
        Retrieves the OM content in OC.

        :return: The OM content in OC if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("omcontentINOC", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing OM content information to initialize an instance.

        :param data_string: A string in the format 'value;OC' or 'value;OM'.
        :type data_string: str
        :return: An instance of OMContentAdditionalInformation populated with the parsed data.
        :rtype: OMContentAdditionalInformation
        """
        parts = data_string.split(";")
        res = {}
        if len(parts) > 2:
            res = {
                "omcontentInOM": parts[0],
                "omcontentINOC": parts[2]
            }
        elif parts[1] in ["OM"]:
            res = {
                "omcontentInOM": parts[0]
            }
        elif parts[1] in ["OC"]:
            res = {
                "omcontentINOC": parts[0]
            }

        return cls(**res)


class OrganicCarbonWaterAdditionalInformation(AdditionalInformation):
    """
    Creates an organic carbon content additional information object.

    Represents additional information about organic carbon 
    in the water-layer of water-sediment studies such as TOC and DOC.
    Low (minimal) and high (maximal) values can be set. If only either low or high value is set, 
    then both low and high are set to this value.
    """
    name = "organiccarbonwater"
    mandatories = []

    # Setter
    def set_TOC_low(self, value):
        """
        Sets the low value of total organic carbon (TOC).
        Can be interpreted as minimal value.

        :param value: The low value of TOC, measured in mg/L.
        :type value: float
        """
        self.params["TOC_low"] = float(value)

    def set_TOC_high(self, value):
        """
        Sets the high value of total organic carbon (TOC).
        Can be interpreted as maximal value.

        :param value: The high value of TOC, measured in mg/L.
        :type value: float
        """
        self.params["TOC_high"] = float(value)

    def set_DOC_low(self, value):
        """
        Sets the low value of dissolved organic carbon (DOC).
        Can be interpreted as minimal value.

        :param value: The low value of DOC, measured in mg/L.
        :type value: float
        """
        self.params["DOC_low"] = float(value)

    def set_DOC_high(self, value):
        """
        Sets the high value of dissolved organic carbon (DOC).
        Can be interpreted as maximal value.

        :param value: The high value of DOC, measured in mg/L.
        :type value: float
        """
        self.params["DOC_high"] = float(value)

    # Getter
    def get_TOC_low(self):
        """
        Retrieves the low value of total organic carbon (TOC).

        :return: The low value of TOC if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("TOC_low", None)

    def get_TOC_high(self):
        """
        Retrieves the high value of total organic carbon (TOC).

        :return: The high value of TOC if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("TOC_high", None)

    def get_DOC_low(self):
        """
        Retrieves the low value of dissolved organic carbon (DOC).

        :return: The low value of DOC if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("DOC_low", None)

    def get_DOC_high(self):
        """
        Retrieves the high value of dissolved organic carbon (DOC).

        :return: The high value of DOC if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("DOC_high", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing organic carbon information to initialize an instance.

        :param data_string: A string in the format e.g 'TOC_low - TOC_low;NA'
        :type data_string: str
        :return: An instance of OrganicCarbonWaterAdditionalInformation populated with the parsed data.
        :rtype: OrganicCarbonWaterAdditionalInformation
        """
        res = {}
        parts = data_string.split(";")
        if parts[0] != "NA":
            res["TOC_low"], res["TOC_high"] = parts[0].split(" - ")
        if parts[1] != "NA":
            res["DOC_low"], res["DOC_high"] = parts[1].split(" - ")

        return cls(**res)


class OrganicContentAdditionalInformation(AdditionalInformation):
    """
    Creates an organic content additional information object.

    This class represents additional information about organic content in water-sediment studies such as organic matter
    (OM) and organic carbon (OC). Low (minimal) and high (maximal) values can be set. If only either low or high value
    is set, then both low and high are set to this value.
    """
    name = "organiccontent"
    mandatories = []

    # Setter
    def set_OC_content_low(self, value):
        """
        Sets the low value of organic carbon (OC) content.

        :param value: The low value of OC content.
        :type value: float
        """
        self.params["OC_content_low"] = float(value)

    def set_OC_content_high(self, value):
        """
        Sets the high value of organic carbon (OC) content.

        :param value: The high value of OC content.
        :type value: float
        """
        self.params["OC_content_high"] = float(value)

    def set_OM_content_low(self, value):
        """
        Sets the low value of organic matter (OM) content.

        :param value: The low value of OM content.
        :type value: float
        """
        self.params["OM_content_low"] = float(value)

    def set_OM_content_high(self, value):
        """
        Sets the high value of organic matter (OM) content.

        :param value: The high value of OM content.
        :type value: float
        """
        self.params["OM_content_high"] = float(value)

    # Getter
    def get_OC_content_low(self):
        """
        Retrieves the low value of organic carbon (OC) content.

        :return: The low value of OC content if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("OC_content_low", None)

    def get_OC_content_high(self):
        """
        Retrieves the high value of organic carbon (OC) content.

        :return: The high value of OC content if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("OC_content_high", None)

    def get_OM_content_low(self):
        """
        Retrieves the low value of organic matter (OM) content.

        :return: The low value of OM content if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("OM_content_low", None)

    def get_OM_content_high(self):
        """
        Retrieves the high value of organic matter (OM) content.

        :return: The high value of OM content if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("OM_content_high", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing organic content information to initialize an instance.

        :param data_string: A string in the format e.g 'OC_content_low - OC_content_high;NA' or
            'OC_content_low - OC_content_low;OM_content_low - OM_content_high'
        :type data_string: str
        :return: An instance of OrganicContentAdditionalInformation populated with the parsed data.
        :rtype: OrganicContentAdditionalInformation
        """
        res = {}
        parts = data_string.split(";")
        if parts[0] != "NA":
            res["OC_content_low"], res["OC_content_high"] = parts[0].split(" - ")
        if parts[1] != "NA":
            res["OM_content_low"], res["OM_content_high"] = parts[1].split(" - ")

        return cls(**res)


class InoculumSourceAdditionalInformation(AdditionalInformation):
    """
    Creates an InoculumSourceAdditionalInformation object.

    This class represents additional information about source of the inoculum.
    """
    name = "inoculumsource"
    mandatories = ['inoculumsource']

    # Setter
    def set_inoculumsource(self, value):
        """
        Sets the value for the inoculum source

        :param value: The source of the inoculum
        :type value: str
        """
        self.params["inoculumsource"] = value

    # Getter
    def get_inoculumsource(self):
        """
        Gets the value for the inoculum source

        :return: the value of the inoculum source
        :rtype: str
        """
        return self.params.get("inoculumsource", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing the source of the inoculum to initialize an instance.

        :param data_string: The source of the inoculum
        :type data_string: str
        """
        return cls._parse_default(data_string, ['inoculumsource'])


class DissolvedOrganicCarbonAdditionalInformation(AdditionalInformation):
    """
    Creates a dissolved organic carbon (DOC) additional information object.

    This class represents additional information about dissolved organic carbon (DOC).
    """
    name = "dissolvedorganiccarbon"
    mandatories = []

    # Setter
    def set_dissolvedorganiccarbonStart(self, value):
        """
        Sets the starting value of dissolved organic carbon.

        :param value: The starting value of dissolved organic carbon, measured in mg C/L.
        :type value: float
        """
        self.params["dissolvedorganiccarbonStart"] = float(value)

    def set_dissolvedorganiccarbonEnd(self, value):
        """
        Sets the ending value of dissolved organic carbon.

        :param value: The ending value of dissolved organic carbon, measured in mg C/L.
        :type value: float
        """
        self.params["dissolvedorganiccarbonEnd"] = float(value)

    # Getter
    def get_dissolvedorganiccarbonStart(self):
        """
        Retrieves the starting value of dissolved organic carbon.

        :return: The starting value of dissolved organic carbon if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("dissolvedorganiccarbonStart", None)

    def get_dissolvedorganiccarbonEnd(self):
        """
        Retrieves the ending value of dissolved organic carbon.

        :return: The ending value of dissolved organic carbon if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("dissolvedorganiccarbonEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing dissolved organic carbon information to initialize an instance.

        :param data_string: A semicolon-separated string in the format
            'dissolvedorganiccarbonStart;dissolvedorganiccarbonEnd'.
        :type data_string: str
        :return: An instance of DissolvedOrganicCarbonAdditionalInformation populated with the parsed data.
        :rtype: DissolvedOrganicCarbonAdditionalInformation
        """
        return cls._parse_default(data_string, ['dissolvedorganiccarbonStart', 'dissolvedorganiccarbonEnd'])


class NitrogenContentAdditionalInformation(AdditionalInformation):
    """
    Creates a nitrogen content additional information object.

    This class represents additional information about nitrogen content.
    """
    name = "nitrogencontent"
    mandatories = ['nitrogencontentType']
    allowed_types = ['NH4MINUSN', 'NTOT', 'NH&#8324-N']

    # Setter
    def set_nitrogencontentType(self, value):
        """
        Sets the type of nitrogen content.

        :param value: The type of nitrogen content. The allowed value are 'NH4MINUSN','NTOT', 'NH&#8324-N'
        """
        if value.upper() not in self.allowed_types:
            raise ValueError(f'{value} is not an allowed type or is written incorrectly -> {self.allowed_types}')
        self.params["nitrogencontentType"] = value.upper()

    def set_nitrogencontentInfluent(self, value):
        """
        Sets the influent nitrogen content.

        :param value: The nitrogen content in the influent, measured in mg/L.
        :type value: float
        """
        self.params["nitrogencontentInfluent"] = float(value)

    def set_nitrogencontentEffluent(self, value):
        """
        Sets the effluent nitrogen content.

        :param value: The nitrogen content in the effluent, measured in mg/L.
        :type value: float
        """
        self.params["nitrogencontentEffluent"] = float(value)

    # Getter
    def get_nitrogencontentType(self):
        """
        Retrieves the type of nitrogen content.

        :return: The type of nitrogen content if set; otherwise, None.
        :rtype: float
        
        """
        return self.params.get("nitrogencontentType", None)

    def get_nitrogencontentInfluent(self):
        """
        Retrieves the nitrogen content in the influent.

        :return: The nitrogen content in the influent if set; otherwise, None.
        :rtype: float                                                                       
        """
        return self.params.get("nitrogencontentInfluent", None)

    def get_nitrogencontentEffluent(self):
        """
        Retrieves the nitrogen content in the effluent.

        :return: The nitrogen content in the effluent if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("nitrogencontentEffluent", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing nitrogen content information to initialize an instance.

        :param data_string: A string in the format
            'nitrogencontentType;nitrogencontentInfluent;nitrogencontentEffluent'. Depends if both infleunt and
            effluent want to be passed.
        :type data_string: str
        :return: An instance of NitrogenContentAdditionalInformation populated with the parsed data.
        :rtype: NitrogenContentAdditionalInformation
        """
        parts = data_string.split(';')

        res = {'nitrogencontentType': parts[0]}

        if len(parts) > 1 and parts[1] != '':
            res['nitrogencontentInfluent'] = float(parts[1])

        if len(parts) > 2 and parts[2] != '':
            res['nitrogencontentEffluent'] = float(parts[2])

        return cls(**res)


class ReferringScenarioAdditionalInformation(AdditionalInformation):
    """
    Class that implements a Referring Scenario Additional Information object.

    A referring scenario is a scenario that refers to another one, from which it will extract information frm
    """
    name = "referringscenario"
    mandatories = ['referringscenario']

    # Setter
    def set_referringscenario(self, value):
        """
        Sets the referring scenario identifier

        :param value: the URL to the scenario it wants to refer to
        :type value: str
        """
        self.params["referringscenario"] = value

    # Getter
    def get_referringscenario(self):
        """
        Gets the scenario that it is being referred

        :return: The URL to the scenario being referred
        :rtype: str
        """
        return self.params.get("referringscenario", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['referringscenario'])


class ModelPredictionProbabilityAdditionalInformation(AdditionalInformation):
    name = "modelpredictionprob"
    mandatories = ['modelpredictionprob']

    # Setter
    def set_modelpredictionprob(self, value):
        self.params["modelpredictionprob"] = value

    # Getter
    def get_modelpredictionprob(self):
        return self.params.get("modelpredictionprob", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['modelpredictionprob'])


class RuleLikelihoodAdditionalInformation(AdditionalInformation):
    """
    Creates a Rule Likelihood additional information object.

    This class represents additional information about the likelihood of a rule.
    """
    name = "rulelikelihood"
    mandatories = ["ruleLikelihood"]
    allowed_values = ["VERY_LIKELY", "LIKELY", "POSSIBLE", "UNLIKELY", "VERY_UNLIKELY"]

    # Setter
    def set_ruleLikelihood(self, value):
        """
        Sets the rule likelihood.

        :param value: The likelihood of the rule, must be one of "VERY_LIKELY", "LIKELY",
            "POSSIBLE", "UNLIKELY", "VERY_UNLIKELY".
        :type value: str
        """
        if value.upper() not in self.allowed_values:
            raise ValueError(f"{value} is not in the set of allowed values {self.allowed_values}")
        self.params["ruleLikelihood"] = value.upper()

    # Getter
    def get_ruleLikelihood(self):
        """
        Gets the rule likelihood.

        :return: The rule likelihood, or None if not set.
        :rtype: str or None
        """
        return self.params.get("ruleLikelihood", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a RuleLikelihoodAdditionalInformation instance.

        :param data_string: A string containing the rule likelihood.
        :type data_string: str
        :return: RuleLikelihoodAdditionalInformation instance.
        :rtype: RuleLikelihoodAdditionalInformation
        """
        return cls._parse_default(data_string, ["ruleLikelihood"])


class ModelBayesPredictionProbabilityAdditionalInformation(AdditionalInformation):
    """
    Creates a Model Bayes Prediction Probability additional information object.

    This class represents additional information about the Bayesian prediction probability from a model.
    """
    name = "modelbayespredictionprob"
    mandatories = ['modelbayespredictionprob']

    # Setter
    def set_modelbayespredictionprob(self, value):
        self.params["modelbayespredictionprob"] = value

    # Getter
    def get_modelbayespredictionprob(self):
        """
        Gets the Bayesian prediction probability.

        :return: The Bayesian prediction probability, or None if not set.
        :rtype: float or None
        """
        return self.params.get("modelbayespredictionprob", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a ModelBayesPredictionProbabilityAdditionalInformation instance.

        :param data_string: A string containing the Bayesian prediction probability.
        :type data_string: str
        :return: ModelBayesPredictionProbabilityAdditionalInformation instance.
        :rtype: ModelBayesPredictionProbabilityAdditionalInformation
        """

        return cls._parse_default(data_string, ['modelbayespredictionprob'])


class HalfLifeAdditionalInformation(AdditionalInformation):
    """
    Creates a half-life additional information object.

    This class represents additional information about the half-life of a compound.
    """
    name = "halflife"
    mandatories = ['lower', 'upper']
    allowed_values = ['', 'reported', 'self-calculated', 'neither']

    # Setter
    def set_lower(self, value):
        """
        Sets the lower bound of the half-life.

        :param value: The lower bound of the half-life, measured in days.
        :type value: float
        """
        self.params["lower"] = float(value)

    def set_upper(self, value):
        """
        Sets the upper bound of the half-life.

        :param value: The upper bound of the half-life, measured in days.
        :type value: float
        """
        self.params["upper"] = float(value)

    def set_comment(self, value):
        """
        Sets a comment for the half-life information.

        :param value: A comment describing the half-life information.
        :type value: str
        """
        self.params["comment"] = value

    def set_source(self, value):
        """
        Sets the source of the half-life information.

        :param value: The source of the half-life information.
        :type value: str
        """
        if value not in self.allowed_values:
            raise ValueError(f"{value} is not an allowed source value")
        self.params["source"] = value

    def set_firstOrder(self, value):
        """
        Sets whether the half-life follows a first-order reaction.

        :param value: True if it's a first-order reaction, False otherwise.
        :type value: bool
        """
        self.params["firstOrder"] = value

    def set_fit(self, value):
        """
        Sets the fit value of the half-life.

        :param value: The fit value of the half-life.
        :type value: str
        """
        self.params["fit"] = value

    # Getter
    def get_lower(self):
        """
        Retrieves the lower bound of the half-life.

        :return: The lower bound of the half-life if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("lower", None)

    def get_upper(self):
        """
        Retrieves the upper bound of the half-life.

        :return: The upper bound of the half-life if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("upper", None)

    def get_comment(self):
        """
        Retrieves the comment for the half-life information.

        :return: The comment for the half-life information if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("comment", None)

    def get_source(self):
        """
        Retrieves the source of the half-life information.

        :return: The source of the half-life information if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("source", None)

    def get_firstOrder(self):
        """
        Retrieves whether the half-life follows a first-order reaction.

        :return: True if it's a first-order reaction, False otherwise; None if not set.
        :rtype: bool
        """
        return self.params.get("firstOrder", None)

    def get_fit(self):
        """
        Retrieves the fit value of the half-life.

        :return: The fit value of the half-life if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("fit", False)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing half-life information to initialize an instance.

        :param data_string: A string containing half-life information in the format 'model;fit;comment;lower -
            upper;source'
        :type data_string: str
        :return: An instance of HalfLifeAdditionalInformation populated with the parsed data.
        :rtype: HalfLifeAdditionalInformation
        """
        parts = data_string.split(';')
        dt50 = parts[3]
        res = {
            'firstOrder': True if parts[0] == 'SFO' else False,
            'fit': parts[1],
            'comment': parts[2],
            'lower': float(dt50.split(' - ')[0]),
            'upper': float(dt50.split(' - ')[1]),
            'source': parts[4],
        }

        return cls(**res)


class HalfLifeWaterSedimentAdditionalInformation(AdditionalInformation):
    """
    Creates a half-life water sediment additional information object.

    This class represents additional information about the half-life of a compound in water and sediment environments.
    """
    name = "halflife_ws"
    mandatories = ["total_low", "total_high"]
    allowed_values = ['', 'reported', 'self-calculated', 'neither']

    # Setter
    def set_total_low(self, value):
        """
        Sets the total low half-life value.

        :param value: The total low half-life value, meaured in days.
        :type value: float
        """
        self.params["total_low"] = float(value)

    def set_total_high(self, value):
        """
        Sets the total high half-life value.

        :param value: The total high half-life value, meaured in days.
        :type value: float
        """
        self.params["total_high"] = float(value)

    def set_water_low(self, value):
        """
        Sets the water low half-life value.

        :param value: The water low half-life value, meaured in days.
        :type value: float
        """
        self.params["water_low"] = float(value)

    def set_water_high(self, value):
        """
        Sets the water high half-life value.

        :param value: The water high half-life value, meaured in days.
        :type value: float
        """
        self.params["water_high"] = float(value)

    def set_sediment_low(self, value):
        """
        Sets the sediment low half-life value.

        :param value: The sediment low half-life value, meaured in days.
        :type value: float
        """
        self.params["sediment_low"] = float(value)

    def set_sediment_high(self, value):
        """
        Sets the sediment high half-life value.

        :param value: The sediment high half-life value, meaured in days.
        :type value: float
        """
        self.params["sediment_high"] = float(value)

    def set_fit_ws(self, value):
        """
        Sets the fit value for water and sediment.

        :param value: The fit value for water and sediment, meaured in days.
        :type value: str
        """
        self.params["fit_ws"] = value

    def set_model_ws(self, value):
        """
        Sets the model used for water and sediment half-life estimation.

        :param value: The model used for water and sediment half-life estimation.
        :type value: str
        """
        self.params["model_ws"] = value

    def set_comment_ws(self, value):
        """
        Sets a comment for the water and sediment half-life information.

        :param value: A comment describing the water and sediment half-life information.
        :type value: str
        """
        self.params["comment_ws"] = value

    def set_source_ws(self, value):
        """
        Sets the source of the water and sediment half-life information. 
        Allowed value are 'reported', 'self-calculated', 'neither'.

        :param value: The source of the water and sediment half-life information.
        :type value: str
        """
        if value not in self.allowed_values:
            raise ValueError(f"{value} is not an allowed source value")
        self.params["source_ws"] = value

    # Getter
    def get_total_low(self):
        """
        Retrieves the total low half-life value.

        :return: The total low half-life value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("total_low", None)

    def get_total_high(self):
        """
        Retrieves the total high half-life value.

        :return: The total high half-life value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("total_high", None)

    def get_water_low(self):
        """
        Retrieves the water low half-life value.

        :return: The water low half-life value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("water_low", None)

    def get_water_high(self):
        """
        Retrieves the water high half-life value.

        :return: The water high half-life value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("water_high", None)

    def get_sediment_low(self):
        """
        Retrieves the sediment low half-life value.

        :return: The sediment low half-life value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("sediment_low", None)

    def get_sediment_high(self):
        """
        Retrieves the sediment high half-life value.

        :return: The sediment high half-life value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("sediment_high", None)

    def get_fit_ws(self):
        """
        Retrieves the fit value for water and sediment.

        :return: The fit value for water and sediment if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("fit_ws", None)

    def get_model_ws(self):
        """
        Retrieves the model used for water and sediment half-life estimation.

        :return: The model used for water and sediment half-life estimation if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("model_ws", None)

    def get_comment_ws(self):
        """
        Retrieves the comment for the water and sediment half-life information.

        :return: The comment for the water and sediment half-life information if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("comment_ws", None)

    def get_source_ws(self):
        """
        Retrieves the source of the water and sediment half-life information.

        :return: The source of the water and sediment half-life information if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("source_ws", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing water and sediment half-life information to initialize an instance.

        :param data_string: A string containing water and sediment half-life information in the format
            'model;fit;comment;total_low - total_high;water_low - water_high;sediment_low - sediment_high;source'
        :type data_string: str
        :return: An instance of HalfLifeWaterSedimentAdditionalInformation populated with the parsed data.
        :rtype: HalfLifeWaterSedimentAdditionalInformation
        """
        parts = data_string.split(';')
        dt50_total = parts[3].split(' - ')
        dt50_water = parts[4].split(' - ')
        dt50_sediment = parts[5].split(' - ')

        res = {
            'model_ws': parts[0],
            'fit_ws': parts[1],
            'comment_ws': parts[2],
            'source_ws': parts[6],
        }

        if not dt50_total: res.update({'total_low': float(dt50_total[0]), 'total_high': float(dt50_total[1])})
        if not dt50_water: res.update({'water_low': float(dt50_water[0]), 'water_high': float(dt50_water[1])})
        if not dt50_sediment: res.update({'sediment_low': float(dt50_sediment[0]),
                                          'sediment_high': float(dt50_sediment[1])})
        return cls(**res)


class HumidityAdditionalInformation(AdditionalInformation):
    """
    Creates a humidity additional information object.

    This class represents additional information about experimental humidity.
    """
    name = "humidity"
    mandatories = ["expHumid"]

    # Setter
    def set_expHumid(self, value):
        """
        Sets the experimental humidity value.

        :param value: The experimental humidity value, represented as a percentage.
        :type value: float
        """
        self.params["expHumid"] = float(value)

    def set_humConditions(self, value):
        """
        Sets the experimental humidity conditions.

        :param value: The value for experimental conditions.
        :type value: str
        """
        self.params["humConditions"] = value

    # Getter
    def get_expHumid(self):
        """
        Retrieves the experimental humidity value.

        :return: The experimental humidity value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("expHumid", None)

    def get_humConditions(self):
        """
        Retrieves the experimental humidity conditions.

        :return: The experimental conditions value if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("humConditions", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing experimental humidity information to initialize an instance.

        :param data_string: A string representing the experimental humidity value.
        :type data_string: str
        :return: An instance of HumidityAdditionalInformation populated with the parsed data.
        :rtype: HumidityAdditionalInformation
        """
        parts = data_string.split(' - ')
        res = {'expHumid': parts[0]}
        if len(parts) > 1:
            res["humConditions"] = parts[1]
        return cls(**res)


class InitialMassSedimentAdditionalInformation(AdditionalInformation):
    """
    Creates an initial mass sediment additional information object.

    This class represents additional information about the initial mass of sediment.
    """
    name = "initialmasssediment"
    mandatories = ["initial_mass_sediment", "wet_or_dry"]
    allowed_values = ['WET', 'DRY']

    # Setter
    def set_initial_mass_sediment(self, value):
        """
        Sets the initial mass of sediment value.

        :param value: The initial mass of sediment, measured in g.
        :type value: float
        """
        self.params["initial_mass_sediment"] = float(value)

    def set_wet_or_dry(self, value):
        """
        Sets the wet or dry state of the sediment.

        :param value: The state of the sediment (either 'WET' or 'DRY').
        :type value: str
        """
        if value.upper() not in self.allowed_values:
            raise ValueError(f"{value} is not allowed. Must be either wet or dry")
        self.params["wet_or_dry"] = value.upper()

    # Getter
    def get_initial_mass_sediment(self):
        """
        Retrieves the initial mass of sediment value.

        :return: The initial mass of sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("initial_mass_sediment", None)

    def get_wet_or_dry(self):
        """
        Retrieves the wet or dry state of the sediment.

        :return: The wet or dry state if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("wet_or_dry", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing initial mass sediment information to initialize an instance.

        :param data_string: A semi-colon separated string in the format 'initial_mass_sediment;wet_or_dry'
        :type data_string: str
        :return: An instance of InitialMassSedimentAdditionalInformation populated with the parsed data.
        :rtype: InitialMassSedimentAdditionalInformation
        """
        return cls._parse_default(data_string, ['initial_mass_sediment', 'wet_or_dry'])


class InitialVolumeWaterAdditionalInformation(AdditionalInformation):
    """
    Creates an initial volume water additional information object.

    This class represents additional information about the initial volume of water.
    """
    name = "initialvolumewater"
    mandatories = ["initialvolumewater"]

    # Setter
    def set_initialvolumewater(self, value):
        """
        Sets the initial volume of water.

        :param value: The initial volume of water, measured in mL.
        :type value: float
        """
        self.params["initialvolumewater"] = float(value)

    # Getter
    def get_initialvolumewater(self):
        """
        Retrieves the initial volume of water.

        :return: The initial volume of water if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("initialvolumewater", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing initial volume water information to initialize an instance.

        :param data_string: A string representing the initial volume of water.
        :type data_string: str
        :return: An instance of InitialVolumeWaterAdditionalInformation populated with the parsed data.
        :rtype: InitialVolumeWaterAdditionalInformation
        :raises ValueError: If the provided value is not a float.
        """
        return cls._parse_default(data_string, ['initialvolumewater'])


class InitiatingOrganismAdditionalInformation(AdditionalInformation):
    """
    Creates an Initiating Organism additional information object.

    This class represents additional information about the initiating organism in a study.
    """
    name = "initorganism"
    mandatories = []

    # Setter
    def set_organism(self, value):
        """
        Sets the organism.

        :param value: The initiating organism.
        :type value: str
        """
        self.params["organism"] = value

    # Getter
    def get_organism(self):
        """
        Gets the organism.

        :return: The initiating organism, or None if not set.
        :rtype: str or None
        """
        return self.params.get("organism", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create an InitiatingOrganismAdditionalInformation instance.

        :param data_string: A string containing the initiating organism.
        :type data_string: str
        :return: InitiatingOrganismAdditionalInformation instance.
        :rtype: InitiatingOrganismAdditionalInformation
        """
        return cls._parse_default(data_string, ['organism'])


class LagPhaseAdditionalInformation(AdditionalInformation):
    """
    Creates a lag phase additional information object.

    This class represents additional information about the lag phase.
    """
    name = "lagphase"
    mandatories = ["lagphase"]

    # Setter
    def set_lagphase(self, value):
        """
        Sets the lag phase value.

        :param value: The lag phase value, represented in minutes.
        :type value: float
        """
        self.params["lagphase"] = float(value)

    # Getter
    def get_lagphase(self):
        """
        Retrieves the lag phase value.

        :return: The lag phase value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("lagphase", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing lag phase information to initialize an instance.

        :param data_string: A string representing the lag phase value.
        :type data_string: str
        :return: An instance of LagPhaseAdditionalInformation populated with the parsed data.
        :rtype: LagPhaseAdditionalInformation
        """
        return cls._parse_default(data_string, ['lagphase'])


class LocationAdditionalInformation(AdditionalInformation):
    """
    Creates a location additional information object.

    This class represents additional information about the scenario location.
    """
    name = "location"
    mandatories = ['location']

    # Setter
    def set_location(self, value):
        """
        Sets the location value.

        :param value: The location value.
        :type value: str
        """
        self.params["location"] = value

    # Getter
    def get_location(self):
        """
        Retrieves the location value.

        :return: The location value if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("location", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing location information to initialize an instance.

        :param data_string: A string representing the location value.
        :type data_string: str
        :return: An instance of LocationAdditionalInformation populated with the parsed data.
        :rtype: LocationAdditionalInformation
        """
        return cls._parse_default(data_string, ['location'])


class ProposedIntermediateAdditionalInformation(AdditionalInformation):
    """
    Creates a Proposed Intermediate additional information object.

    This class represents additional information about proposed intermediates in a study.
    """
    name = "proposedintermediate"
    mandatories = ['proposed']

    # Setter
    def set_proposed(self, value):
        """
        Sets the proposed intermediate.

        :param value: The proposed intermediate.
        :type value: str
        """
        self.params["proposed"] = value

    # Getter
    def get_proposed(self):
        """
        Gets the proposed intermediate.

        :return: The proposed intermediate, or None if not set.
        :rtype: str or None
        """
        return self.params.get("proposed", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a ProposedIntermediateAdditionalInformation instance.

        :param data_string: A string containing the proposed intermediate.
        :type data_string: str
        :return: ProposedIntermediateAdditionalInformation instance.
        :rtype: ProposedIntermediateAdditionalInformation
        """
        return cls._parse_default(data_string, ['proposed'])


class VolatileTSSAdditionalInformation(AdditionalInformation):
    """
    Creates a Volatile TSS (Total Suspended Solids) additional information object.

    This class represents additional information about the volatile TSS values. Start and/or End values can be set. 
    """
    name = "volatiletts"
    mandatories = []

    # Setter
    def set_volatilettsStart(self, value):
        """
        Sets the start value of volatile TSS.

        :param value: The start value of volatile TSS, measured in g/L.
        :type value: float
        """
        self.params["volatilettsStart"] = float(value)

    def set_volatilettsEnd(self, value):
        """
        Sets the end value of volatile TSS.

        :param value: The end value of volatile TSS, measured in g/L.
        :type value: float
        """
        self.params["volatilettsEnd"] = float(value)

    # Getter
    def get_volatilettsStart(self):
        """
        Gets the start value of volatile TSS.

        :return: The start value of volatile TSS, or None if not set.
        :rtype: float or None
        """
        return self.params.get("volatilettsStart", None)

    def get_volatilettsEnd(self):
        """
        Gets the end value of volatile TSS.

        :return: The end value of volatile TSS, or None if not set.
        :rtype: float or None
        """
        return self.params.get("volatilettsEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a VolatileTSSAdditionalInformation instance.

        :param data_string: A string containing volatile TSS data in the format 'start_value - end_value'.
        :type data_string: str
        :return: VolatileTSSAdditionalInformation instance.
        :rtype: VolatileTSSAdditionalInformation
        """
        parts = data_string.split(' - ')
        res = {
            'volatilettsStart': float(parts[0]),
            'volatilettsEnd': float(parts[1]),
        }

        return cls(**res)


class WaterStorageCapacityAdditionalInformation(AdditionalInformation):
    """
    Creates a Water Storage Capacity additional information object.

    This class represents additional information about water storage capacity in soil data.
    """
    name = "waterstoragecapacity"
    mandatories = []

    # Setter
    def set_wst(self, value):
        """
        Sets the water hold capacity.

        :param value: The water hold capacity, measured in g water/100g dry soil.
        :type value: float
        """

        self.params["wst"] = float(value)

    def set_maximumWaterstoragecapacity(self, value):
        """
        Sets the maximum water storage capacity.

        :param value: The maximum water storage capacity, measured in g water/100g dry soil.
        :type value: float
        """

        self.params["maximumWaterstoragecapacity"] = float(value)

    def set_wstConditions(self, value):
        """
        Sets the water storage threshold conditions.

        :param value: The water storage threshold conditions.
        :type value: str
        """
        self.params["wstConditions"] = value

    # Getter
    def get_wst(self):
        """
        Gets the water storage threshold (wst).

        :return: The water storage threshold, or None if not set.
        :rtype: float or None
        """
        return self.params.get("wst", None)

    def get_maximumWaterstoragecapacity(self):
        """
        Gets the maximum water storage capacity.

        :return: The maximum water storage capacity, or None if not set.
        :rtype: float or None
        """
        return self.params.get("maximumWaterstoragecapacity", None)

    def get_wstConditions(self):
        """
        Gets the water storage threshold conditions.

        :return: The water storage threshold conditions, or None if not set.
        :rtype: str or None
        """
        return self.params.get("wstConditions", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a WaterStorageCapacityAdditionalInformation instance.

        :param data_string: A string containing water storage capacity data in the format 
                            'wst - wstConditions - maximumWaterstoragecapacity'.
        :type data_string: str
        :return: WaterStorageCapacityAdditionalInformation instance.
        :rtype: WaterStorageCapacityAdditionalInformation
        """
        parts = data_string.split(' - ')
        res = {}
        if parts[0].lower() not in ["na", ""]:
            res["wst"] = parts[0]
        if parts[1].lower() not in ["na", ""]:
            res["wstConditions"] = parts[1]
        if parts[2].lower() not in ["na", ""]:
            res["maximumWaterstoragecapacity"] = parts[2]

        return cls(**res)


class AdditionalParametersMeasuredAdditionalInformation(AdditionalInformation):
    """
    Creates a Parameters Measured additional information object.

    This class represents additional information about measured parameters in a sample important for sludge data.
    """
    name = "addparametersmeasured"
    mandatories = []
    allowed_values = [
        "NH4+", "NH4-", "NH4-N", "NO3-", "NO2-", "Ntot", "PO43-", "P-tot", "DOC", "none", "NH&#8324&#8314",
        "NH&#8324&#8315", "NH&#8324-N", "NO&#8323&#8315", "NO&#8322&#8315", "N&#8348&#8338&#8348",
        "PO&#8324&#179&#8315", "P&#8348&#8338&#8348"
    ]

    # Setter
    def set_addparametersmeasured(self, value):
        """
        Sets the measured parameter.

        :param value: The parameter measured in the sample.
        :type value: str
        """
        if value not in self.allowed_values:
            raise ValueError(f"{value} is not an allowed parameter")
        self.params["addparametersmeasured"] = value

    # Getter
    def get_addparametersmeasured(self):
        """
        Gets the measured parameter.

        :return: The measured parameter, or None if not set.
        :rtype: str or None
        """
        return self.params.get("addparametersmeasured", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a ParametersMeasuredAdditionalInformation instance.

        :param data_string: A string containing the measured parameter data.
        :type data_string: str
        :return: ParametersMeasuredAdditionalInformation instance.
        :rtype: ParametersMeasuredAdditionalInformation
        """
        return cls._parse_default(data_string, ['addparametersmeasured'])


class ConfidenceLevelAdditionalInformation(AdditionalInformation):
    """
    Creates a Confidence Level additional information object.

    This class represents additional information about the confidence level of the data.
    """
    name = "confidencelevel"
    mandatories = ['radioconfidence']
    allowed_values = ["1", "2", "3", "4"]

    # Setter
    def set_radioconfidence(self, value):
        """
        Sets the confidence level. Either 1,2,3,4.

        :param value: The confidence level value.
        :type value: str
        """
        if str(value) not in self.allowed_values:
            raise ValueError(f"{value} is not an allowed confidence level: {self.allowed_values}")
        self.params["radioconfidence"] = str(value)

    # Getter
    def get_radioconfidence(self):
        """
        Gets the confidence level.

        :return: The confidence level, or None if not set.
        :rtype: str or None
        """
        return self.params.get("radioconfidence", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a ConfidenceLevelAdditionalInformation instance.

        :param data_string: A string containing confidence level data.
        :type data_string: str
        :return: ConfidenceLevelAdditionalInformation instance.
        :rtype: ConfidenceLevelAdditionalInformation
        """
        return cls._parse_default(data_string, ['radioconfidence'])


class BiologicalTreatmentTechnologyAdditionalInformation(AdditionalInformation):
    """
    Creates a biological treatment technology additional information object.

    This class represents additional information about biological treatment technology.
    """
    name = "biologicaltreatmenttechnology"
    mandatories = ['biologicaltreatmenttechnology']
    allowed_values = ['nitrification', 'nitrification & denitrification',
                      'nitrification & denitrification & biological phosphorus removal',
                      'nitrification & denitrification & chemical phosphorus removal', 'other']

    # Setter
    def set_biologicaltreatmenttechnology(self, value):
        """
        Sets the biological treatment technology value.

        :param value: The biological treatment technology.
        :type value: str
        """
        value = value.lower()
        if value in self.allowed_values:
            self.params["biologicaltreatmenttechnology"] = value
        else:
            raise ValueError(f"must be one of {self.allowed_values}.")

    # Getter
    def get_biologicaltreatmenttechnology(self):
        """
        Retrieves the biological treatment technology value.

        :return: The biological treatment technology value if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("biologicaltreatmenttechnology", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing biological treatment technology information to initialize an instance.

        :param data_string: A string containing the biological treatment technology.
        :type data_string: str
        :return: An instance of BiologicalTreatmentTechnologyAdditionalInformation populated with the parsed data.
        :rtype: BiologicalTreatmentTechnologyAdditionalInformation
        """
        return cls._parse_default(data_string, ['biologicaltreatmenttechnology'])


class BioreactorAdditionalInformation(AdditionalInformation):
    """
    Creates a bioreactor additional information object.

    This class represents additional information about a bioreactor, including its type and size.
    """
    name = "bioreactor"
    mandatories = ['bioreactortype']

    # Setter
    def set_bioreactortype(self, value):
        """
        Sets the bioreactor type.

        :param value: The type of the bioreactor.
        :type value: str
        """
        self.params["bioreactortype"] = value

    def set_bioreactorsize(self, value):
        """
        Sets the bioreactor size.

        :param value: The size of the bioreactor, measured in mL.
        :type value: float
        """

        self.params["bioreactorsize"] = float(value)

    # Getter
    def get_bioreactortype(self):
        """
        Retrieves the bioreactor type.

        :return: The bioreactor type if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("bioreactortype", None)

    def get_bioreactorsize(self):
        """
        Retrieves the bioreactor size.

        :return: The bioreactor size if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("bioreactorsize", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing bioreactor information to initialize an instance.

        :param data_string: A string in the format 'bioreactortype;bioreactorsize' or 'bioreactortype, bioreactorsize'
        :type data_string: str
        :return: An instance of BioreactorAdditionalInformation populated with the parsed data.
        :rtype: BioreactorAdditionalInformation
        """
        res = {}
        parts = data_string.split(';')

        if len(parts) > 1:
            res['bioreactortype'] = parts[0]
            res['bioreactorsize'] = parts[1]
        else:
            parts = data_string.split(', ')
            res['bioreactortype'] = parts[0]
            if parts[1] not in ['', 'NA']:
                res['bioreactorsize'] = parts[1]
        return cls(**res)


class BioMassAdditionalInformation(AdditionalInformation):
    """
    Creates a biomass additional information object. 
    This class is used to store and manage information about the microbial biomass measured at the start and end.
    """
    name = "biomass"
    mandatories = ['biomassStart', 'biomassEnd']

    # Setter
    def set_biomassStart(self, value):
        """
        Sets the starting microbial biomass.

        :param value: A numeric value representing the starting microbial biomass, measured in μg C/g soil
        """
        self.params["biomassStart"] = float(value)

    def set_biomassEnd(self, value):
        """
        Sets the ending microbial biomass.

        :param value: A numeric value representing the ending microbial biomass, measured in μg C/g soil
        """
        self.params["biomassEnd"] = float(value)

    # Getter
    def get_biomassStart(self):
        """
        Retrieves the starting microbial biomass.

        :return: The starting microbial biomass if set; otherwise, None.
        """
        return self.params.get("biomassStart", None)

    def get_biomassEnd(self):
        """
        Retrieves the ending microbial biomass.

        :return: The ending microbial biomass if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("biomassEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string to initialize a BioMassAdditionalInformation instance.

        :param data_string: A string in the format 'biomassStart - biomassEnd'.
        :return: An instance of BioMassAdditionalInformation with the specified start and end biomass values.
        """
        vals = data_string.split(" - ")
        return cls(biomassStart=float(vals[0]), biomassEnd=float(vals[1]))


class BioMassWaterSedimentAdditionalInformation(AdditionalInformation):
    """
    Creates a biomass water-sediment additional information object.

    This class represents additional information about the microbial biomass in water and sediment. 
    It is made especially for water-sediment studies and one can choose 'cells/g' or 'mg C/g' as measurement units for
    the sediment
    """
    name = "biomass_ws"
    mandatories = []

    # Setter
    def set_start_water_cells(self, value):
        """
        Sets the starting cell count for microbial biomass in water.

        :param value: The starting cell count for microbial biomass in water, measured in cells/mL.
        :type value: int
        """
        self.params["start_water_cells"] = float(value)

    def set_end_water_cells(self, value):
        """
        Sets the ending cell count for microbial biomass in water.

        :param value: The ending cell count for microbial biomass in water, measured in cells/mL
        :type value: int
        """
        self.params["end_water_cells"] = float(value)

    def set_start_sediment_cells(self, value):
        """
        Sets the starting cell count for microbial biomass in sediment.

        :param value: The starting cell count for microbial biomass in sediment, measured in cells/g.
        :type value: int
        """
        self.params["start_sediment_cells"] = float(value)

    def set_end_sediment_cells(self, value):
        """
        Sets the ending cell count for microbial biomass in sediment.

        :param value: The ending cell count for microbial biomass in sediment, measured in cells/g.
        :type value: int
        """
        self.params["end_sediment_cells"] = float(value)

    def set_start_sediment_mg(self, value):
        """
        Sets the starting microbial biomass mass in sediment when weight is given.

        :param value: The starting microbial biomass mass in sediment, measured in mg C/g.
        :type value: float
        """
        self.params["start_sediment_mg"] = float(value)

    def set_end_sediment_mg(self, value):
        """
        Sets the ending microbial biomass mass in sediment when weight is given.

        :param value: The ending microbial biomass mass in sediment, measured in mg C/g.
        :type value: float
        """
        self.params["end_sediment_mg"] = float(value)

    # Getter
    def get_start_water_cells(self):
        """
        Retrieves the starting cell count for microbial biomass in water.

        :return: The starting cell count for microbial biomass in water if set; otherwise, None.
        :rtype: int
        """
        return self.params.get("start_water_cells", None)

    def get_end_water_cells(self):
        """
        Retrieves the ending cell count for microbial biomass in water.

        :return: The ending cell count for microbial biomass in water if set; otherwise, None.
        :rtype: int
        """
        return self.params.get("end_water_cells", None)

    def get_start_sediment_cells(self):
        """
        Retrieves the starting cell count for microbial biomass in sediment.

        :return: The starting cell count for microbial biomass in sediment if set; otherwise, None.
        :rtype: int
        """
        return self.params.get("start_sediment_cells", None)

    def get_end_sediment_cells(self):
        """
        Retrieves the ending cell count for microbial biomass in sediment.

        :return: The ending cell count for microbial biomass in sediment if set; otherwise, None.
        :rtype: int
        """
        return self.params.get("end_sediment_cells", None)

    def get_start_sediment_mg(self):
        """
        Retrieves the starting microbial biomass mass in sediment.

        :return: The starting microbial biomass mass in sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("start_sediment_mg", None)

    def get_end_sediment_mg(self):
        """
        Retrieves the ending microbial biomass mass in sediment.

        :return: The ending microbial biomass mass in sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("end_sediment_mg", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing biomass information for water and sediment to initialize an instance.

        :param data_string: A semicolon-separated string in the Format 'start_water_cells -
            end_water_cells;start_sediment_cells - end_sediment_cells;start_sediment_mg - end_sediment_mg'
        :type data_string: str
        :return: An instance of BioMassWaterSedimentAdditionalInformation populated with the parsed data.
        :rtype: BioMassWaterSedimentAdditionalInformation
        """
        parts = data_string.split(";")
        res = {}

        for i in range(len(parts)):
            if parts[i] != "NA":
                vals = parts[i].split(" - ")
                if i == 0:
                    res["start_water_cells"] = float(vals[0])
                    res['end_water_cells'] = float(vals[1])
                elif i == 1:
                    res["start_sediment_cells"] = float(vals[0])
                    res['end_sediment_cells'] = float(vals[1])
                elif i == 2:
                    res["start_sediment_mg"] = float(vals[0])
                    res['end_sediment_mg'] = float(vals[1])

        return cls(**res)


class BulkDensityAdditionalInformation(AdditionalInformation):
    """
    Creates a bulk density additional information object.

    This class represents additional information about bulk density.
    """
    name = "bulkdens"
    mandatories = ["bulkdensity"]

    # Setter
    def set_bulkdensity(self, value):
        """
        Sets the bulk density value.

        :param value: The bulk density value, measured in g/cm3.
        :type value: float
        """
        self.params["bulkdensity"] = float(value)

    # Getter
    def get_bulkdensity(self):
        """
        Retrieves the bulk density value.

        :return: The bulk density value if set; otherwise, None.
        :rtype: int
        """
        return self.params.get("bulkdensity", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing bulk density information to initialize an instance.

        :param data_string: A string representing the bulk density value.
        :type data_string: str
        :return: An instance of BulkDensityAdditionalInformation populated with the parsed data.
        :rtype: BulkDensityAdditionalInformation
        """
        return cls._parse_default(data_string, ['bulkdensity'])


class CECAdditionalInformation(AdditionalInformation):
    """
    Creates a cation exchange capacity (CEC) additional information object.

    This class represents additional information about cation exchange capacity.
    """
    name = "cec"
    mandatories = ["cecdata"]

    # Setter
    def set_cecdata(self, value):
        """
        Sets the cation exchange capacity data.

        :param value: The cation exchange capacity data, measured in mEq/100g.
        :type value: float
        """
        self.params["cecdata"] = float(value)

    # Getter
    def get_cecdata(self):
        """
        Retrieves the cation exchange capacity data.

        :return: The cation exchange capacity data if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("cecdata", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing cation exchange capacity data to initialize an instance.

        :param data_string: A string representing the cation exchange capacity data.
        :type data_string: str
        :return: An instance of CECAdditionalInformation populated with the parsed data.
        :rtype: CECAdditionalInformation
        """
        return cls._parse_default(data_string, ['cecdata'])


class ColumnHeightAdditionalInformation(AdditionalInformation):
    """
    Creates a column height additional information object.

    This class represents additional information about column height.
    """
    name = "columnheight"
    mandatories = ["column_height_water", "column_height_sediment"]

    # Setter
    def set_column_height_water(self, value):
        """
        Sets the column height in water.

        :param value: The column height in water, measured in cm.
        :type value: float
        """
        self.params["column_height_water"] = float(value)

    def set_column_height_sediment(self, value):
        """
        Sets the column height in sediment.

        :param value: The column height in sediment, measured in cm.
        :type value: float
        """
        self.params["column_height_sediment"] = float(value)

    # Getter
    def get_column_height_water(self):
        """
        Retrieves the column height in water.

        :return: The column height in water if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("column_height_water", None)

    def get_column_height_sediment(self):
        """
        Retrieves the column height in sediment.

        :return: The column height in sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("column_height_sediment", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing column height information to initialize an instance.

        :param data_string: A semicolon-separated string in the format 'column_height_sediment;column_height_water'
        :type data_string: str
        :return: An instance of ColumnHeightAdditionalInformation populated with the parsed data.
        :rtype: ColumnHeightAdditionalInformation
        """
        return cls._parse_default(data_string, ['column_height_sediment', 'column_height_water'])


class FinalCompoundConcentrationAdditionalInformation(AdditionalInformation):
    """
    Creates a final compound concentration additional information object.

    This class represents additional information about the final compound concentration.
    """
    name = "finalcompoundconcentration"
    mandatories = ['finalcompoundconcentration']

    # Setter
    def set_finalcompoundconcentration(self, value):
        """
        Sets the final compound concentration value.

        :param value: The final compound concentration value, measured in μg/ L
        :type value: float
        :raises ValueError: If the provided value is not a float.
        """
        self.params["finalcompoundconcentration"] = float(value)

    # Getter
    def get_finalcompoundconcentration(self):
        """
        Retrieves the final compound concentration value.

        :return: The final compound concentration value if set; otherwise, None.
        :rtype: float
        """

        return self.params.get("finalcompoundconcentration", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing final compound concentration information to initialize an instance.

        :param data_string: A string representing the final compound concentration value.
        :type data_string: str
        :return: An instance of FinalCompoundConcentrationAdditionalInformation populated with the parsed data.
        :rtype: FinalCompoundConcentrationAdditionalInformation
        """
        return cls._parse_default(data_string, ['finalcompoundconcentration'])


class TSSAdditionalInformation(AdditionalInformation):
    """
    Creates a TSS (Total Suspended Solids) additional information object.

    This class represents additional information about the TSS values. Start and/or End values can be set.
    """
    name = "tts"
    mandatories = ['ttsStart', 'ttsEnd']

    # Setter
    def set_ttsStart(self, value):
        """
        Sets the start value of TSS.

        :param value: The start value of TSS, measured in g/L.
        :type value: float
        """
        self.params["ttsStart"] = float(value)

    def set_ttsEnd(self, value):
        """
        Sets the end value of TSS.

        :param value: The end value of TSS, measured in g/L.
        :type value: float
        """
        self.params["ttsEnd"] = float(value)

    # Getter
    def get_ttsStart(self):
        """
        Gets the start value of TSS.

        :return: The start value of TSS, or None if not set.
        :rtype: float or None
        """
        return self.params.get("ttsStart", None)

    def get_ttsEnd(self):
        """
        Gets the end value of volatile TSS.

        :return: The end value of TSS, or None if not set.
        :rtype: float or None
        """
        return self.params.get("ttsEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a TSSAdditionalInformation instance.

        :param data_string: A string containing TSS data in the format 'start_value - end_value'.
        :type data_string: str
        :return: TSSAdditionalInformation instance.
        :rtype: TSSAdditionalInformation
        """
        res = {
            'ttsStart': data_string.split(' - ')[0],
            'ttsEnd': data_string.split(' - ')[1],
        }
        return cls(**res)


class PurposeOfWWTPAdditionalInformation(AdditionalInformation):
    """
    Creates an additional information object for the purpose of a wastewater treatment plant (WWTP).

    This class represents additional information about the purpose of a waste water treatment plant.
    """
    name = "purposeofwwtp"
    mandatories = ['purposeofwwtp']
    allowed_values = ["municipal WW", "industrial WW", "hospital WW", "mixed WW (municipal & industrial)", "other"]

    # Setter
    def set_purposeofwwtp(self, value):
        """
        Sets the purpose of the WWTP.

        :param value: The purpose of the WWTP.
        :type value: str
        """

        if value not in self.allowed_values:
            raise ValueError(f"{value} is not an allowed value. Allowed values are: {', '.join(self.allowed_values)}")

        self.params["purposeofwwtp"] = value

    # Getter
    def get_purposeofwwtp(self):
        """
        Retrieves the purpose of the WWTP.

        :return: The purpose of the WWTP if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("purposeofwwtp", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing the purpose of WWTP information to initialize an instance.

        :param data_string: A string representing the purpose of the WWTP.
        :type data_string: str
        :return: An instance of PurposeOfWWTPAdditionalInformation populated with the parsed data.
        :rtype: PurposeOfWWTPAdditionalInformation
        """
        return cls._parse_default(data_string, ['purposeofwwtp'])


class RateConstantAdditionalInformation(AdditionalInformation):
    """
    Creates an additional information object for rate constant data.

    This class represents additional information about rate constant values. Either lower and/or higher can be set. 
    If only one is set, the other one takes the same value. 
    """
    name = "rateconstant"
    mandatories = ["rateconstantorder", "rateconstantlower"]
    allowed_order = ["Zero order", "First order", "Second order", "Pseudo first order"]
    allowed_corrected = ["", "sorption corrected", "abiotic degradation corrected",
                         "sorption corrected & abiotic degradation corrected"]

    # Setter
    def set_rateconstantlower(self, value):
        """
        Sets the lower rate constant value.

        :param value: The lower rate constant value.
        :type value: float
        """
        self.params["rateconstantlower"] = float(value)

    def set_rateconstantupper(self, value):
        """
        Sets the upper rate constant value.

        :param value: The upper rate constant value.
        :type value: float
        """
        self.params["rateconstantupper"] = float(value)

    def set_rateconstantorder(self, value):
        """
        Sets the order of the rate constant.

        :param value: The order of the rate constant. Must be either "Zero order", "First order",
            "Second order", "Pseudo first order".
        :type value: str
        """
        if value.lower().capitalize() not in self.allowed_order:
            raise ValueError(f"{value} is not a permitted rateconstant order. "
                             f"Only permitted order are : {self.allowed_order}")
        self.params["rateconstantorder"] = value.lower().capitalize()

    def set_rateconstantcorrected(self, value):
        """
        Sets the corrected rate constant value. 

        :param value: The corrected rate constant value. Must be either "", "sorption corrected",
            "abiotic degradation corrected", "sorption corrected & abiotic degradation corrected".
        :type value: str 
        """
        if value not in self.allowed_corrected:
            raise ValueError(f"{value} is not a permitted rateconstant corrected. "
                             f"Only permitted order are : {self.allowed_corrected}")
        self.params["rateconstantcorrected"] = value

    def set_rateconstantcomment(self, value):
        """
        Sets the comment related to the rate constant.

        :param value: The comment about the rate constant.
        :type value: str
        """
        self.params["rateconstantcomment"] = value

    # Getter
    def get_rateconstantlower(self):
        """
        Retrieves the lower rate constant value.

        :return: The lower rate constant value if set; otherwise, None.
        :rtype: float or None 
        """
        return self.params.get("rateconstantlower", None)

    def get_rateconstantupper(self):
        """
        Retrieves the upper rate constant value.

        :return: The upper rate constant value if set; otherwise, None.
        :rtype: float or None
        """
        return self.params.get("rateconstantupper", None)

    def get_rateconstantorder(self):
        """
        Retrieves the order of the rate constant.

        :return: The order of the rate constant if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("rateconstantorder", None)

    def get_rateconstantcorrected(self):
        """
        Retrieves the corrected rate constant value.

        :return: The corrected rate constant value if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("rateconstantcorrected", None)

    def get_rateconstantcomment(self):
        """
        Retrieves the comment related to the rate constant.

        :return: The comment about the rate constant if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("rateconstantcomment", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing rate constant information to initialize an instance.

        :param data_string: A semicolon separated string in the format
            'rateconstantorder;rateconstantcorrected;rateconstantlower - rateconstantupper;rateconstantcomment'.
        :type data_string: str
        :return: An instance of RateConstantAdditionalInformation populated with the parsed data.
        :rtype: RateConstantAdditionalInformation
        """
        parts = data_string.split(';')
        lower, upper = parts[2].split(' - ')

        res = {
            'rateconstantorder': parts[0],
            'rateconstantcorrected': parts[1],
            'rateconstantlower':  float(lower),
            'rateconstantupper': float(upper),
            'rateconstantcomment': parts[3]
        }

        return cls(**res)


class SampleLocationAdditionalInformation(AdditionalInformation):
    """
    Creates a sample location additional information object.

    This class represents additional information about the sample location of water-sediment studies.
    """
    name = "samplelocation"
    mandatories = ["samplelocation"]

    # Setter
    def set_samplelocation(self, value):
        """
        Sets the sample location.

        :param value: The sample location.
        :type value: str
        """
        self.params["samplelocation"] = value

    # Getter
    def get_samplelocation(self):
        """
        Retrieves the sample location.

        :return: The sample location if set; otherwise, None.
        :rtype: str or None
        """
        return self.params.get("samplelocation", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing sample location information to initialize an instance.

        :param data_string: A string representing the sample location.
        :type data_string: str
        :return: An instance of SampleLocationAdditionalInformation populated with the parsed data.
        :rtype: SampleLocationAdditionalInformation
        """
        return cls._parse_default(data_string, ['samplelocation'])


class SolventForCompoundSolutionAdditionalInformation(AdditionalInformation):
    """
    Creates a solvent for compound solution additional information object.

    This class represents additional information about solvents used for compound solutions.
    """
    name = "solventforcompoundsolution"
    mandatories = ['solventforcompoundsolution1']

    valid_solvents = {"MEOH": "MeOH", "ETOH": "EtOH", "H2O": "H&#8322O", "DMSO": "DMSO",
                      "ACETONE": "ACETONE", "H&#8322O": "H&#8322O"}

    # Setter
    def set_solventforcompoundsolution1(self, value):
        """
        Sets the first solvent used for compound solution.

        :param value: The first solvent used for compound solution. Valid solvents are "MeOH", "EtOH", "H2O",
            "DMSO", "acetone","H&#8322O".
        :type value: str
        """
        if value.upper() not in self.valid_solvents.keys():
            raise ValueError(f"{value} must be one of {', '.join(self.valid_solvents.keys())}.")
        self.params["solventforcompoundsolution1"] = self.valid_solvents[value.upper()]

    def set_solventforcompoundsolution2(self, value):
        """
        Sets the second solvent used for compound solution.

        :param value: The second solvent used for compound solution. Valid solvents are "MeOH", "EtOH", "H2O",
            "DMSO", "acetone","H&#8322O".
        :type value: str
        """
        if value.upper() not in self.valid_solvents.keys():
            raise ValueError(f"{value} must be one of {', '.join(self.valid_solvents.keys())}")
        self.params["solventforcompoundsolution2"] = self.valid_solvents[value.upper()]

    def set_solventforcompoundsolution3(self, value):
        """
        Sets the third solvent used for compound solution.

        :param value: The third solvent used for compound solution. Valid solvents are "MeOH", "EtOH", "H2O",
            "DMSO", "acetone","H&#8322O".
        :type value: str
        """
        if value.upper() not in self.valid_solvents.keys():
            raise ValueError(f"{value} must be one of {', '.join(self.valid_solvents.keys())}")
        self.params["solventforcompoundsolution3"] = self.valid_solvents[value.upper()]

    def set_proportion(self, value):
        """
        Sets the ratio of the solvents.

        :param value: the ratio in the form "1:3"
        :type value: str
        """
        self.params["proportion"] = value

    # Getter
    def get_solventforcompoundsolution1(self):
        """
        Get the first solvent used for compound solution.

        :return: The first solvent used for compound solution, or None if not set.
        :rtype: float or None
        """
        return self.params.get("solventforcompoundsolution1")

    def get_solventforcompoundsolution2(self):
        """
        Get the second solvent used for compound solution.

        :return: The second solvent used for compound solution, or None if not set.
        :rtype: float or None
        """
        return self.params.get("solventforcompoundsolution2")

    def get_solventforcompoundsolution3(self):
        """
        Get the third solvent used for compound solution.

        :return: The third solvent used for compound solution, or None if not set.
        :rtype: float or None
        """
        return self.params.get("solventforcompoundsolution3")

    def get_proportion(self):
        """
        Get the ratio of the solvents.

        :return: the ratio of the solvents
        :rtype: str
        """
        return self.params.get("proportion")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SolventForCompoundSolutionAdditionalInformation instance.

        :param data_string: Semicolon-separated string in the format e.g
            "solventforcompoundsolution1;solventforcompoundsolution2;solventforcompoundsolution3;proportion"
        :type data_string: str
        :return: SolventForCompoundSolutionAdditionalInformation instance.
        :rtype: SolventForCompoundSolutionAdditionalInformation
        """
        solvents = data_string.split(';')
        if len(solvents) == 1: return cls._parse_default(data_string, ["solventforcompoundsolution1"])
        res = {"proportion": solvents.pop(-1)}
        for i in range(len(solvents)):
            res['solventforcompoundsolution' + str(i+1)] = solvents[i]
        return cls(**res)


class SourceOfLiquidMatrixAdditionalInformation(AdditionalInformation):
    """
    Creates a source of liquid matrix additional information object.

    This class represents additional information about the source of a liquid matrix.
    """
    name = "sourceofliquidmatrix"
    mandatories = ['sourceofliquidmatrix']

    # Setter
    def set_sourceofliquidmatrix(self, value):
        """
        Sets the source of the liquid matrix.

        :param value: The source of the liquid matrix.
        :type value: str
        """
        self.params["sourceofliquidmatrix"] = value

    # Getter
    def get_sourceofliquidmatrix(self):
        """
        Gets the source of the liquid matrix.

        :return: The source of the liquid matrix, or None if not set.
        :rtype: str or None
        """
        return self.params.get("sourceofliquidmatrix", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SourceOfLiquidMatrixAdditionalInformation instance.

        :param data_string: String containing the source of the liquid matrix.
        :type data_string: str
        :return: SourceOfLiquidMatrixAdditionalInformation instance.
        :rtype: SourceOfLiquidMatrixAdditionalInformation
        """
        return cls(**{'sourceofliquidmatrix': data_string})


class SourceScenarioAdditionalInformation(AdditionalInformation):
    """
    Creates a source scenario additional information object.

    This class represents additional information about the source scenario represented as the scource scenario ID.
    """
    name = "sourcescenario"
    mandatories = ["sourcescenario"]

    # Setter
    def set_sourcescenario(self, value):
        """
        Sets the source scenarios.

        :param value: A comma-separated string joining all the URLs of the source scenarios.
        :type value: str
        """
        self.params["sourcescenario"] = value

    # Getter
    def get_sourcescenario(self):
        """
        Gets the source scenarios.

        :return: The source scenario, or None if not set.
        :rtype: str or None
        """
        return self.params.get("sourcescenario", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SourceScenarioAdditionalInformation instance.

        :param data_string: String containing the source scenario.
        :type data_string: str
        :return: SourceScenarioAdditionalInformation instance.
        :rtype: SourceScenarioAdditionalInformation
        """
        scenarios_data = data_string.split('|')
        sourcescenarios = []
        for scenario_data in scenarios_data:
            uri, name = scenario_data.split(";")
            sourcescenarios.append(uri)
        return cls(**{"sourcescenario": ",".join(sourcescenarios)})


class SpikeCompoundAdditionalInformation(AdditionalInformation):
    """
    Creates a Spike Compound additional information object.

    This class represents additional information about spike compounds. It takes either an existing compound or creates
    a new one using SMILES.
    """
    name = "spikecompound"
    mandatories = []

    # Setter
    def set_spikeComp(self, value):
        """
        Sets the spike compound information. 

        :param value: The spike compound information in the form of an existing compound ID or a smile (to create a new
            compound).
        :type value: str
        """
        self.params["spikeComp"] = value

    # Getter
    def get_spikeComp(self):
        """
        Gets the spike compound information.

        :return: The spike compound information, or None if not set.
        :rtype: str or None
        """
        return self.params.get("spikeComp", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SpikeCompoundAdditionalInformation instance.

        :param data_string: A string containing spike compound data.
        :type data_string: str
        :return: SpikeCompoundAdditionalInformation instance.
        :rtype: SpikeCompoundAdditionalInformation
        """
        return cls._parse_default(data_string, ['spikeComp'])


class SpikeConcentrationAdditionalInformation(AdditionalInformation):
    """
    Creates a Spike Concentration additional information object.

    This class represents additional information about spike concentrations.
    """
    name = "spikeconcentration"
    mandatories = ["spikeConcentration", "spikeconcentrationUnit"]

    map_units = {
        '&#956g/L': 'MUG_PER_L', '&#956g/kg wet soil' : 'MUG_PER_KG_WET', '&#956g/kg dry soil': 'MUG_PER_KG_DRY',
        'mg/L': 'MG_PER_L', 'mg/kg wet soil': 'MG_PER_KG_WET', 'mg/kg dry soil': 'MG_PER_KG_DRY', 'ppm': 'PPM'
    }

    # Setter
    def set_spikeConcentration(self, value):
        """
        Sets the spike concentration.

        :param value: The spike concentration value.
        :type value: float
        """
        self.params["spikeConcentration"] = float(value)

    def set_spikeconcentrationUnit(self, value):
        """
        Sets the unit for the spike concentration. Must be one of the following:
        'MUG_PER_L', 'MUG_PER_KG_WET', 'MUG_PER_KG_DRY', 'MG_PER_L', 'MG_PER_KG_WET', 'MG_PER_KG_DRY', 'PPM'

        :param value: The unit for the spike concentration.
        :type value: str
        """
        if value not in self.map_units.values():
            raise ValueError(f"The unit set {value} does not belong to the set "
                             f"of allowed units {self.map_units.values()}")
        self.params["spikeconcentrationUnit"] = value

    # Getter
    def get_spikeConcentration(self):
        """
        Gets the spike concentration.

        :return: The spike concentration value, or None if not set.
        :rtype: float or None
        """
        return self.params.get("spikeConcentration", None)

    def get_unit(self):
        return self.map_units[super().get_unit()]

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SpikeConcentrationAdditionalInformation instance.

        :param data_string: A string containing spike concentration data in the format 
                            'spikeConcentration;spikeconcentrationUnit'.
        :type data_string: str
        :return: SpikeConcentrationAdditionalInformation instance.
        :rtype: SpikeConcentrationAdditionalInformation
        """
        return cls._parse_default(data_string, ['spikeConcentration'])


class OriginalSludgeAmountAdditionalInformation(AdditionalInformation):
    """
    Creates an additional information object for original sludge amount.

    This class represents additional information about the initial amount of sludge.
    """
    name = "originalsludgeamount"
    mandatories = ['originalsludgeamount']

    # Setter
    def set_originalsludgeamount(self, value):
        """
        Sets the original sludge amount.

        :param value: The original sludge amount, measured in mL.
        :type value: float
        """
        self.params["originalsludgeamount"] = float(value)

    # Getter
    def get_originalsludgeamount(self):
        """
        Retrieves the original sludge amount.

        :return: The original sludge amount if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("originalsludgeamount", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing original sludge amount information to initialize an instance.

        :param data_string: A string representing the original sludge amount.
        :type data_string: str
        :return: An instance of OriginalSludgeAmountAdditionalInformation populated with the parsed data.
        :rtype: OriginalSludgeAmountAdditionalInformation
        """
        return cls._parse_default(data_string, ['originalsludgeamount'])


class OxygenContentWaterSedimentAdditionalInformation(AdditionalInformation):
    """
    Creates an additional information object for oxygen content in water and sediment.

    This class represents additional information about the oxygen content in water and sediment.
    Low (minimal) and high (maximal) values can be set. If only either low or high value is set, then both low and
    high are set to this value.
    """
    name = "oxygencontent"
    mandatories = []

    # Setter
    def set_oxygen_content_water_low(self, value):
        """
        Sets the low oxygen content in water.

        :param value: The low oxygen content in water, measured in mg/L.
        :type value: float
        """
        self.params["oxygen_content_water_low"] = float(value)

    def set_oxygen_content_water_high(self, value):
        """
        Sets the high oxygen content in water.

        :param value: The high oxygen content in water, measured in mg/L.
        :type value: float
        """
        self.params["oxygen_content_water_high"] = float(value)

    def set_oxygen_content_sediment_low(self, value):
        """
        Sets the low oxygen content in sediment.

        :param value: The low oxygen content in sediment, given in percentage.
        :type value: float
        """
        self.params["oxygen_content_sediment_low"] = float(value)

    def set_oxygen_content_sediment_high(self, value):
        """
        Sets the high oxygen content in sediment.

        :param value: The high oxygen content in sediment, given in percentage.
        :type value: float
        """
        self.params["oxygen_content_sediment_high"] = float(value)

    # Getter
    def get_oxygen_content_water_low(self):
        """
        Retrieves the low oxygen content in water.

        :return: The low oxygen content in water if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("oxygen_content_water_low", None)

    def get_oxygen_content_water_high(self):
        """
        Retrieves the high oxygen content in water.

        :return: The high oxygen content in water if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("oxygen_content_water_high", None)

    def get_oxygen_content_sediment_low(self):
        """
        Retrieves the low oxygen content in sediment.

        :return: The low oxygen content in sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("oxygen_content_sediment_low", None)

    def get_oxygen_content_sediment_high(self):
        """
        Retrieves the high oxygen content in sediment.

        :return: The high oxygen content in sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("oxygen_content_sediment_high", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing oxygen content information to initialize an instance.

        :param data_string: A string in the format 'NA - 
        :type data_string: str
        :return: An instance of OxygenContentWaterSedimentAdditionalInformation populated with the parsed data.
        :rtype: OxygenContentWaterSedimentAdditionalInformation
        """
        parts = data_string.split(";")
        res = {}

        if parts[0] != 'NA':
            res["oxygen_content_water_low"], res["oxygen_content_water_high"] = parts[0].split(" - ")
        if parts[1] != 'NA':
            res["oxygen_content_sediment_low"], res["oxygen_content_sediment_high"] = parts[1].split(" - ")

        return cls(**res)


class TypeOfAerationAdditionalInformation(AdditionalInformation):
    """
    Creates a Type of Aeration additional information object.

    This class represents additional information about the type of aeration.
    """
    name = "typeofaeration"
    mandatories = ['typeofaeration']
    allowed_values = ["stirring", "shaking", "bubbling air", "bubbling air and stirring", "other"]

    # Setter
    def set_typeofaeration(self, value):
        """
        Sets the type of aeration. Must be either "stirring", "shaking", "bubbling air", "bubbling air and stirring",
        "other".

        :param value: The type of aeration.
        :type value: str
        """
        if value not in self.allowed_values:
            raise ValueError(f"The value {value} is not in the set of allowed values {self.allowed_values}")
        self.params["typeofaeration"] = value

    # Getter
    def get_typeofaeration(self):
        """
        Gets the type of aeration.

        :return: The type of aeration, or None if not set.
        :rtype: str or None
        """
        return self.params.get("typeofaeration", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a TypeOfAerationAdditionalInformation instance.

        :param data_string: A string containing the type of aeration.
        :type data_string: str
        :return: TypeOfAerationAdditionalInformation instance.
        :rtype: TypeOfAerationAdditionalInformation
        """
        return cls._parse_default(data_string, ['typeofaeration'])


class AcidityAdditionalInformation(AdditionalInformation):
    """
    Creates an acidity additional information object.

    This class represents additional information about acidity,
    including the low pH, high pH, and type of acidity.
    """
    name = "acidity"
    mandatories = ['lowPh']
    allowed_values = ['', 'WATER', 'KCL', 'CACL2', 'CACL&#8322']

    # Setter
    def set_lowPh(self, value):
        """
        Sets the low pH value.

        :param value: The low pH value.
        :type value: float
        """
        self.params["lowPh"] = float(value)

    def set_highPh(self, value):
        """
        Sets the high pH value.

        :param value: The high pH value.
        :type value: float
        """
        self.params["highPh"] = float(value)

    def set_acidityType(self, value):
        """
        Sets the type of acidity.

        :param value: The type of acidity. Either '','WATER', 'KCL', 'CACL2'.
        :type value: str
        """
        if value.upper() not in self.allowed_values:
            raise ValueError(f"The value {value} is not in the set of allowed values {self.allowed_values}")
        self.params["acidityType"] = value.upper()

    # Getter
    def get_lowPh(self):
        """
        Retrieves the low pH value.

        :return: The low pH value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("lowPh", None)

    def get_highPh(self):
        """
        Retrieves the high pH value.

        :return: The high pH value if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("highPh", None)

    def get_acidityType(self):
        """
        Retrieves the type of acidity.

        :return: The type of acidity if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("acidityType", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing acidity information to initialize an instance.

        :param data_string: A semicolon separated string in the format 'lowPh - highPh;acidityType' 
        :type data_string: str
        :return: An instance of AcidityAdditionalInformation populated with the parsed data.
        :rtype: AcidityAdditionalInformation
        """
        parts = data_string.split(';')
        vals = parts[0].split(' - ')

        res = {
            'lowPh': float(vals[0]),
            'highPh': float(vals[1]) if len(vals) > 1 else float(vals[0]),
        }

        if len(parts) > 1:
            res['acidityType'] = parts[1]

        return cls(**res)


class AcidityWaterSedimentAdditionalInformation(AdditionalInformation):
    """
    Creates an acidity water-sediment additional information object.

    This class represents additional information about acidity in water and sediment,
    including the pH values for water and sediment, as well as the type of acidity.
    It is made especially for water-sediment studies
    """
    name = "acidity_ws"
    mandatories = []
    allowed_values = ['', 'WATER', 'KCL', 'CACL2', 'CACL&#8322']

    # Setter
    def set_pH_water_low(self, value):
        """
        Sets the low pH value for water.

        :param value: The low pH value for water.
        :type value: float
        """
        self.params["pH_water_low"] = float(value)

    def set_pH_water_high(self, value):
        """
        Sets the high pH value for water.

        :param value: The high pH value for water.
        :type value: float
        """
        self.params["pH_water_high"] = float(value)

    def set_pH_sediment_low(self, value):
        """
        Sets the low pH value for sediment.

        :param value: The low pH value for sediment.
        :type value: float
        """
        self.params["pH_sediment_low"] = float(value)

    def set_pH_sediment_high(self, value):
        """
        Sets the high pH value for sediment.

        :param value: The high pH value for sediment.
        :type value: float
        """
        self.params["pH_sediment_high"] = float(value)

    def set_acidityType(self, value):
        """
        Sets the type of acidity.

        :param value: The type of acidity. Possible values are '', 'WATER', 'KCL', 'CACL2'.
        :type value: str
        """
        if value.upper() not in self.allowed_values:
            raise ValueError(f"{value} is not allowed as acidityType.")
        self.params["acidityType"] = value.upper()

    # Getter
    def get_pH_water_low(self):
        """
        Retrieves the low pH value for water.

        :return: The low pH value for water if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("pH_water_low", None)

    def get_pH_water_high(self):
        """
        Retrieves the high pH value for water.

        :return: The high pH value for water if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("pH_water_high", None)

    def get_pH_sediment_low(self):
        """
        Retrieves the low pH value for sediment.

        :return: The low pH value for sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("pH_sediment_low", None)

    def get_pH_sediment_high(self):
        """
        Retrieves the high pH value for sediment.

        :return: The high pH value for sediment if set; otherwise, None.
        :rtype: float
        """
        return self.params.get("pH_sediment_high", None)

    def get_acidityType(self):
        """
        Retrieves the type of acidity.

        :return: The type of acidity if set; otherwise, None.
        :rtype: str
        """
        return self.params.get("acidityType", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses a string containing acidity information for water and sediment to initialize an instance.

        :param data_string: A semicolon-separated string in the form 'pH_water_low - pH_water_high;pH_sediment_low -
            pH_sediment_high;acidityType'
        :type data_string: str
        :return: An instance of AcidityWaterSedimentAdditionalInformation populated with the parsed data.
        :rtype: AcidityWaterSedimentAdditionalInformation
        """
        parts = data_string.split(';')
        res = {}
        if parts[0] != " - ":
            valw = parts[0].split(' - ')
            res['pH_water_low'] = float(valw[0])
            res['pH_water_high'] = float(valw[1]) if len(valw) > 1 else float(valw[0])

        if parts[1] != " - ":
            vals = parts[1].split(' - ')
            res['pH_sediment_low'] = float(vals[0])
            res['pH_sediment_high'] = float(vals[1]) if len(vals) > 1 else float(vals[0])

        if len(parts) > 2:
            res['acidityType'] = parts[2].upper()

        return cls(**res)


class RedoxAdditionalInformation(AdditionalInformation):
    """
    Creates an additional information object for redox properties.

    This class represents additional information about redox properties.
    """
    name = "redox"
    mandatories = ['redoxType']
    allowed_types = ['aerob', 'anaerob', 'anaerob: iron-reducing', 'anaerob: sulfate-reducing',
                     'anaerob: methanogenic conditions', 'oxic', 'nitrate-reducing']

    # Setter
    def set_redoxType(self, value):
        """
        Sets the redoxType parameter.

        :param value: The value of redoxType.
        :type value: str
        """
        if value.lower() not in self.allowed_types:
            raise ValueError(f"{value} is not allowed as redoxType. Valid types: {self.allowed_types}")
        self.params["redoxType"] = value

    # Getter
    def get_redoxType(self) -> Optional[str]:
        """
        Get the redoxType parameter.

        :return: The value of redoxType parameter, or None if not set.
        :rtype: str or None
        """
        return self.params.get("redoxType", None)

    # Parser
    @classmethod
    def parse(cls, data_string: str) -> 'RedoxAdditionalInformation':
        """
        Parses the data_string to create a RedoxAdditionalInformation instance.

        :param data_string: String containing redoxType data.
        :type data_string: str
        :return: RedoxAdditionalInformation instance.
        :rtype: RedoxAdditionalInformation
        """
        return cls._parse_default(data_string, ['redoxType'])


class RedoxPotentialAdditionalInformation(AdditionalInformation):
    """
    Creates a redox potential additional information class for redox potential data.

    This class represents additional information about redox potential values for water and sediment. 
    """
    name = "redoxpotential"
    mandatories = []

    # Setter
    def set_lowPotentialWater(self, value):
        """
        Sets the low redox potential for water.

        :param value: The low potential value for water, measured in mV.
        :type value: float
        """
        self.params["lowPotentialWater"] = float(value)

    def set_highPotentialWater(self, value):
        """
        Sets the high redox potential for water.

        :param value: The high potential value for water, measured in mV.
        :type value: float
        """
        self.params["highPotentialWater"] = float(value)

    def set_lowPotentialSediment(self, value):
        """
        Sets the low redox potential for sediment.

        :param value: The low potential value for sediment, measured in mV.
        :type value: float
        """
        self.params["lowPotentialSediment"] = float(value)

    def set_highPotentialSediment(self, value):
        """
        Sets the high redox potential for sediment.

        :param value: The high potential value for sediment, measured in mV.
        :type value: float
        """
        self.params["highPotentialSediment"] = float(value)

    # Getter
    def get_lowPotentialWater(self):
        """
        Get the low redox potential for water.

        :return: The low potential value for water, or None if not set.
        :rtype: float or None
        """
        return self.params.get("lowPotentialWater")

    def get_highPotentialWater(self):
        """
        Get the high redox potential for water.

        :return: The high potential value for water, or None if not set.
        :rtype: float or None
        """
        return self.params.get("highPotentialWater")

    def get_lowPotentialSediment(self):
        """
        Get the low redox potential for sediment.

        :return: The low potential value for sediment, or None if not set.
        :rtype: float or None
        """
        return self.params.get("lowPotentialSediment")

    def get_highPotentialSediment(self):
        """
        Get the high redox potential for sediment.

        :return: The high potential value for sediment, or None if not set.
        :rtype: float or None
        """
        return self.params.get("highPotentialSediment")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a RedoxPotentialAdditionalInformation instance.

        :param data_string: a semicolon separated string in the format 'lowPotentialWater -
            highPotentialWater;lowPotentialSediment - highPotentialSediment'
        :type data_string: str
        :return: RedoxPotentialAdditionalInformation instance.
        :rtype: RedoxPotentialAdditionalInformation
        """
        res = {}
        parts = data_string.split(";")
        if not parts[0] in ["NA"]:
            res["lowPotentialWater"] = float(parts[0].split(" - ")[0])
            res["highPotentialWater"] = float(parts[0].split(" - ")[1])

        if not parts[1] in ["NA"]:
            res["lowPotentialSediment"] = float(parts[1].split(" - ")[0])
            res["highPotentialSediment"] = float(parts[1].split(" - ")[1])

        return cls(**res)


class ReferenceAdditionalInformation(AdditionalInformation):
    """
    Creates a reference additional information object.
    
    It stores information about the PubMed ID or just any other reference.
    """
    name = "reference"
    mandatories = ["reference"]

    # Setter 
    def set_reference(self, value):
        """
        Sets the reference.

        :param value: The reference, either PubMed ID or any other reference.
        :type value: str
        """
        self.params["reference"] = value

    # Getter
    def get_reference(self):
        """
        Get the reference.

        :return: The reference, or None if not set.
        :rtype: str or None
        """
        return self.params.get("reference")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a ReferenceAdditionalInformation instance.

        :param data_string: String containing reference data.
        :type data_string: str
        :return: ReferenceAdditionalInformation instance.
        :rtype: ReferenceAdditionalInformation
        """
        return cls._parse_default(data_string, ['reference'])


class SamplingDepthAdditionalInformation(AdditionalInformation):
    """
    Creates a sampling depth additional information object.

    This class represents additional information about sampling depths.
    """
    name = "samplingdepth"
    mandatories = ["samplingDepthMin"]

    # Setter
    def set_samplingDepthMin(self, value):
        """
        Sets the minimum sampling depth.

        :param value: The minimum sampling depth, measured in cm.
        :type value: float
        """
        self.params["samplingDepthMin"] = float(value)

    def set_samplingDepthMax(self, value):
        """
        Sets the maximum sampling depth.

        :param value: The maximum sampling depth, measured in cm.
        :type value: float
        """
        self.params["samplingDepthMax"] = float(value)

    # Getter    
    def get_samplingDepthMin(self):
        """
        Get the minimum sampling depth.

        :return: The minimum sampling depth, or None if not set.
        :rtype: float or None
        """
        return self.params.get("samplingDepthMin")

    def get_samplingDepthMax(self):
        """
        Get the maximum sampling depth.

        :return: The maximum sampling depth, or None if not set.
        :rtype: float or None
        """
        return self.params.get("samplingDepthMax")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SamplingDepthAdditionalInformation instance.

        :param data_string: A semicolon separated string in the format "samplingDepthMin;samplingDepthMax"
        :type data_string: str
        :return: SamplingDepthAdditionalInformation instance.
        :rtype: SamplingDepthAdditionalInformation
        """
        parts = data_string.split(";")
        if len(parts) == 1:
            res = {
                "samplingDepthMin": float(parts[0]),
                "samplingDepthMax": float(parts[0])
            }
        else:
            res = {
                "samplingDepthMin": float(parts[0]),
                "samplingDepthMax": float(parts[1])
            }
        return cls(**res)


class SedimentPorosityAdditionalInformation(AdditionalInformation):
    """
    Creates a sediment porosity additional information object.
    
    This class represents additional information about sediment porosity.
    """
    name = "sedimentporosity"
    mandatories = ["sedimentporosity"]

    # Setter
    def set_sedimentporosity(self, value):
        """
        Sets the sediment porosity.

        :param value: The sediment porosity.
        :type value: float
        """
        self.params["sedimentporosity"] = float(value)

    # Getter
    def get_sedimentporosity(self):
        """
        Get the sediment porosity.

        :return: The sediment porosity, or None if not set.
        :rtype: str or None
        """
        return self.params.get("sedimentporosity")

    # Parser
    @classmethod
    def parse(cls, data_string):
        """
        Parses the data_string to create a SedimentPorosityAdditionalInformation instance.

        :param data_string: String containing sediment porosity data.
        :type data_string: str
        :return: SedimentPorosityAdditionalInformation instance.
        :rtype: SedimentPorosityAdditionalInformation
        """
        return cls._parse_default(data_string, ['sedimentporosity'])
