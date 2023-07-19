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
        if not self.loaded and not hasattr(self, field):
            obj_fields = self._load()
            for k, v in obj_fields.items():
                setattr(self, k, v)
                self.loaded = True

        if not hasattr(self, field):
            raise ValueError('{} has no property {}'.format(self.get_type(), field))

        return getattr(self, field)

    def get_id(self):
        return self.id

    def __eq__(self, other):
        if type(other) is type(self):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)

    def get_name(self):
        return self._get('name')

    def get_description(self):
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

    def _create_from_nested_json(self, member: Union[str, list], nested_object_type):
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
        :return:
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
        return self._get('aliases')

    def get_review_status(self) -> str:
        return self._get('reviewStatus')

    def is_reviewed(self) -> bool:
        return 'reviewed' == self.get_review_status()

    def get_scenarios(self) -> List['Scenario']:
        res = []
        plain_scenarios = self._get('scenarios')
        for plain_scenario in plain_scenarios:
            res.append(Scenario(self.requester, **plain_scenario))
        return res

    # Attaches an already created Scenario to the object
    def add_scenario(self, scenario: 'Scenario'):
        headers = {'referer': self.id}
        payload = {'scenario': scenario.get_id()}
        res = self.requester.post_request(self.id, headers=headers, payload=payload, allow_redirects=True)
        return

    @abstractmethod
    def copy(self, package: 'Package', debug=False):
        """
        Copies the object into the given package
        """
        pass


# TODO change to reviewable
class Package(enviPathObject):

    def set_description(self, desc: str) -> None:
        payload = {
            'packageDescription': (None, desc),
        }
        self.requester.post_request(self.id, files=payload)
        setattr(self, "description", desc)

    def add_compound(self, smiles: str, name: str = None, description: str = None, inchi: str = None) -> 'Compound':
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
        return SimpleRule.create(self, smirks, name=name, description=description,
                                 reactant_filter_smarts=reactant_filter_smarts,
                                 product_filter_smarts=product_filter_smarts, immediate=immediate)

    def add_sequential_composite_rule(self, simple_rules: List['SimpleRule'], name: str = None, description: str = None,
                                      reactant_filter_smarts: str = None, product_filter_smarts: str = None,
                                      immediate: str = None) -> 'SequentialCompositeRule':
        return SequentialCompositeRule.create(self, simple_rules, name=name, description=description,
                                              reactant_filter_smarts=reactant_filter_smarts,
                                              product_filter_smarts=product_filter_smarts, immediate=immediate)

    def add_parallel_composite_rule(self, simple_rules: List['SimpleRule'], name: str = None, description: str = None,
                                    reactant_filter_smarts: str = None, product_filter_smarts: str = None,
                                    immediate: str = None) -> 'ParallelCompositeRule':
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

        :param smiles:
        :param name:
        :param description:
        :param root_node_only:
        :param setting:
        :return:
        """
        return Pathway.create(self, smiles, name, description, root_node_only, setting)

    def predict(self, smiles: str, name: str = None, description: str = None,
                root_node_only: bool = False, setting: 'Setting' = None) -> 'Pathway':
        """
        Alias for add_pathway()
        :param smiles:
        :param name:
        :param description:
        :param root_node_only:
        :param setting:
        :return:
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
        Copies all contents of this package into "target_package".
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
    def merge_packages(target: 'Package', sources: List['Package'], debug=False):
        for source in sources:
            source.copy(target, debug=debug)


class Scenario(enviPathObject):

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

        @param package: Package object in which the Scenario will be created
        @param name: Name of Scenario
        @param description: Description of Scenario
        @param scenariotype: Use predefined scenario type (possible: Soil, Sludge, Sediment, ..)
        @param additional_info: Scenario data content provided as a AdditionalInformation object
        @param referring_scenario_id: Provide referring scenario ID, a related scenario will be created
        @param collection_URI: attach an existing AdditionalInformation object to the scenario (by ID) - not working
        @return: Scenario object
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
        scenario_payload = {}

        if len(additional_information):
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

    def has_referring_scenario(self):
        try:
            return self._get('referringScenario') is not None
        except ValueError:
            return False

    def get_referring_scenario(self):
        return Scenario(self.requester, id=self._get('referringScenario')['scenarioId'])

    def get_additional_information(self) -> List['AdditionalInformation']:
        res = []
        if self._get('collection'):
            coll = self._get('collection')
            for val in coll.values():
                # e.g. acidity
                if isinstance(val, list):
                    for v in val:
                        try:
                            clz = AdditionalInformation.get_subclass_by_name(v['name'])
                        except ValueError:
                            clz = DummyAdditionalInformation
                        res.append(clz().parse(v['value']))
                else:
                    try:
                        clz = AdditionalInformation.get_subclass_by_name(val['name'])
                    except ValueError:
                        clz = DummyAdditionalInformation
                    res.append(clz().parse(val['value']))

        return res

    def copy(self, package: 'Package', debug=False, id_lookup={}):
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
        for structure in self.get_structures():
            if structure.is_default_structure():
                return structure
        raise ValueError("The compound does not have a default structure!")

    def get_smiles(self) -> str:
        return self.get_default_structure().get_smiles()

    def get_inchi(self) -> str:
        return self.get_default_structure().get_inchi()

    def copy(self, package: 'Package', debug=False):
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

    def add_alias(self, alias):
        payload = {
            'name': alias,
        }
        self.requester.post_request(self.id, payload=payload, allow_redirects=False)
        self.loaded = False
        if hasattr(self, 'alias'):
            delattr(self, 'alias')

    def get_charge(self) -> float:
        return float(self._get('charge'))

    def get_formula(self) -> str:
        return self._get('formula')

    def get_mass(self):
        return self._get('mass')

    def get_svg(self) -> str:
        return self.requester.get_request(self._get('image')).text

    def is_default_structure(self):
        return self._get('isDefaultStructure')

    def get_smiles(self) -> str:
        return self._get('smiles')

    def get_inchi(self) -> str:
        return self._get('InChI')

    def get_pathways(self) -> List['Pathway']:
        return self._create_from_nested_json('pathways', Pathway)

    def get_scenarios(self) -> List['Scenario']:
        return self._create_from_nested_json('scenarios', Scenario)

    def get_reactions(self) -> List['Reaction']:
        return self._create_from_nested_json('reactions', Reaction)

    def get_halflifes(self, scenario_type=None) -> List['HalfLife']:
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

    def is_multistep(self) -> bool:
        return "true" == self._get('multistep')

    def get_ec_numbers(self) -> List['ECNumber']:
        ec_numbers = self._get('ecNumbers')
        res = []
        for ec_number in ec_numbers:
            pathways = [Pathway(self.requester, id=pw['id']) for pw in ec_number['pathways']]
            res.append(ECNumber(ec_number['ecNumber'], ec_number['ecName'], pathways))
        return res

    def get_smirks(self) -> str:
        return self._get('smirks')

    def get_pathways(self) -> List['Pathway']:
        return self._get('pathways')

    def get_medline_references(self) -> List[object]:
        return self._get('medlineRefs')

    def get_educts(self) -> List['CompoundStructure']:
        return self._create_from_nested_json('educts', CompoundStructure)

    def get_products(self):
        return self._create_from_nested_json('products', CompoundStructure)

    def get_rule(self) -> Optional['Rule']:
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

    @staticmethod
    def create(package: Package, smirks: str = None, educt: CompoundStructure = None, product: CompoundStructure = None,
               name: str = None, description: str = None, rule: 'Rule' = None):

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

    def copy(self, package: 'Package', debug=False):
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

    def get_ec_numbers(self) -> List[object]:
        return self._get('ecNumbers')

    def included_in_composite_rule(self) -> List['Rule']:
        res = []
        for rule in self._get('includedInCompositeRule'):
            res.append(Rule(self, requester=self.requester, id=rule['id']))
        return res

    def is_composite_rule(self) -> bool:
        return self._get('isCompositeRule')

    def get_transformations(self) -> str:
        return self._get('transformations')

    def get_reactions(self) -> List['Reaction']:
        return self._create_from_nested_json('reactions', Reaction)

    def get_pathways(self) -> List['Pathway']:
        return self._create_from_nested_json('pathways', Pathway)

    def get_reactant_filter_smarts(self) -> str:
        return self._get('reactantFilterSmarts')

    def get_reactant_smarts(self) -> str:
        return self._get('reactantsSmarts')

    def get_product_filter_smarts(self) -> str:
        return self._get('productFilterSmarts')

    def get_product_smarts(self) -> str:
        return self._get('productsSmarts')

    def apply_to_compound(self, compound: Compound) -> List[str]:
        return self.apply_to_smiles(compound.get_default_structure().get_smiles())

    def apply_to_smiles(self, smiles) -> List[str]:
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

    @staticmethod
    def create(package: Package, smirks: str, name: str = None, description: str = None,
               reactant_filter_smarts: str = None, product_filter_smarts: str = None,
               immediate: str = None, rdkitrule: bool = None) -> 'SimpleRule':
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
        return self._get('smirks')

    def copy(self, package: 'Package', debug=False):
        # TODO immediate missing
        mapping = dict()

        sr = SimpleRule.create(package, smirks=self.get_smirks(), name=self.get_name(),
                               description=self.get_description(),
                               reactant_filter_smarts=self.get_reactant_filter_smarts(),
                               product_filter_smarts=self.get_product_filter_smarts())

        mapping[self.get_id()] = sr.get_id()
        return mapping, sr


class SequentialCompositeRule(Rule):
    @staticmethod
    def create(package: Package, simple_rules: List[SimpleRule], name: str = None, description: str = None,
               reactant_filter_smarts: str = None, product_filter_smarts: str = None,
               immediate: str = None) -> 'SequentialCompositeRule':

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

    def get_simple_rules(self):
        return self._create_from_nested_json('simpleRules', SimpleRule)

    def copy(self, package: 'Package', debug=False, id_lookup={}):
        # TODO
        pass


class ParallelCompositeRule(Rule):
    @staticmethod
    def create(package: Package, simple_rules: List[SimpleRule], name: str = None, description: str = None,
               reactant_filter_smarts: str = None, product_filter_smarts: str = None,
               immediate: str = None) -> 'ParallelCompositeRule':

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

    def get_simple_rules(self):
        return self._create_from_nested_json('simpleRules', SimpleRule)

    def copy(self, package: 'Package', debug=False, id_lookup={}):
        # TODO
        pass


class RelativeReasoning(ReviewableEnviPathObject):

    @staticmethod
    def create(package: Package, packages: List[Package], classifier_type: ClassifierType,
               eval_type: EvaluationType, association_type: AssociationType,
               evaluation_packages: List[Package] = None,
               fingerprinter_type: FingerprinterType = FingerprinterType.ENVIPATH_FINGERPRINTER,
               quickbuild: bool = True, use_p_cut: bool = False, cut_off: float = 0.5,
               evaluate_later: bool = True, name: str = None) -> 'RelativeReasoning':

        """
        Create a relative reasoning object

        Keyword arguments:
            @param package: The package object in which the model is created
            @param packages: List of package objects on which the model is trained
            @param classifier_type: Classifier options:
                                    Rule-Based : ClassifierType("RULEBASED")
                                    Machine Learning-Based (MLC-BMaD) :  ClassifierType("MLCBMAD")
                                    Machine Learning-Based (ECC) : ClassifierType("ECC")
            @param eval_type: Evaluation type:
                                Single Generation : EvaluationType("single")
                                Single + Multiple Generation : EvaluationType("multigen")
            @param association_type: Association type:
                                        AssociationType("DATABASED")
                                        AssociationType("CALCULATED"), default
            @param evaluation_packages: List of package objects on which the model is evaluated. If none, the classifier
                                        is evaluated in a 100-fold holdout model using a 90/10 split ratio.
            @param fingerprinter_type: Default: MACS Fingerprinter ("ENVIPATH_FINGERPRINTER")
            @param quickbuild: Faster evaluation, default: False
            @param use_p_cut:  Default: False
            @param cut_off: The cutoff threshold used in the evaluation. Default: 0.5
            @param evaluate_later: Only build the model, and not proceed to evaluation. Default: False
            @param name:  Name of the model
            @return: RelativeReasoning object
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
        return self.classify_smiles(structure.get_smiles())

    def classify_smiles(self, smiles: str):
        params = {
            'smiles': smiles,
            'classify': 'ILikeCats'
        }
        return self.requester.get_request(self.id, params=params).json()


    def copy(self, package: 'Package'):
        # TODO
        pass


class Node(ReviewableEnviPathObject):

    def get_smiles(self):
        return self.get_default_structure().get_smiles()

    def get_halflifes(self) -> List['HalfLife']:
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
        return self._create_from_nested_json('structures', CompoundStructure)

    def get_default_structure(self) -> CompoundStructure:
        return CompoundStructure(self.requester, id=self._get('defaultStructure')['id'])

    def get_svg(self) -> str:
        return self.get_default_structure().get_svg()

    def get_depth(self) -> int:
        return self._get('depth')

    def get_ad_assessment(self) -> Optional['ADAssessment']:
        return self.requester.get_json(self.id + '?adassessment=true')

    @staticmethod
    def create(pathway: 'Pathway', smiles, name: str = None, description: str = None, depth: int = None) -> 'Node':
        """
        Creates a Node object within a pathway, returns the Node object.
        Similar to the Pathway.add_node() function, which does not return a Node object.
        @param pathway: parent pathway
        @return: Node object
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

    def copy(self, package: 'Package'):
        raise NotImplementedError("Copying of Nodes is implemented via Pathway.copy!")


class Edge(ReviewableEnviPathObject):

    def get_start_nodes(self) -> List['Node']:
        return self._create_from_nested_json('startNodes', Node)

    def get_end_nodes(self) -> List['Node']:
        return self._create_from_nested_json('endNodes', Node)

    def get_reaction(self) -> Reaction:
        return Reaction(self.requester, id=self._get('reactionURI'))

    def get_reaction_name(self) -> str:
        return self._get('reactionName')

    def get_ec_numbers(self) -> List['ECNumber']:
        return self.get_reaction().get_ec_numbers()

    def get_rule(self) -> Optional['Rule']:
        return self.get_reaction().get_rule()

    @staticmethod
    def create(pathway: 'Pathway', smirks: str = None, educts: List['Node'] = None, products: List['Node'] = None,
               multistep: bool = False, description: str = None):
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

    def copy(self, package: 'Package'):
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

    def get_nodes(self) -> List[Node]:
        nodes = self._get('nodes')

        # Remove pseudo nodes
        non_pseudo_nodes = []
        for n in nodes:
            if n.get('pseudo', False):
                continue
            non_pseudo_nodes.append(n)

        return self._create_from_nested_json(non_pseudo_nodes, Node)

    def get_edges(self) -> List[Edge]:
        edges = self._get('links')

        # Remove pseudo edges
        non_pseudo_edges = []
        for e in edges:
            if e.get('pseudo', False):
                continue
            non_pseudo_edges.append(e)

        return self._create_from_nested_json(non_pseudo_edges, Edge)

    def get_name(self) -> str:
        return self._get('pathwayName')

    def is_up_to_date(self) -> bool:
        return self._get('upToDate')

    def lastmodified(self) -> int:
        return self._get('lastModified')

    def is_completed(self) -> bool:
        return "true" == self._get('completed')

    def has_failed(self) -> bool:
        return "error" == self._get('completed')

    def add_node(self, smiles, name: str = None, depth: int = None, description: str = None):
        """
        Adds a node to the pathway object, does NOT return the node.
        Very similar to the node create function, which returns a Node object.
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
        @param smirks: SMIRKS format of the reaction
        @param educts: compound URIs of educts, comma separated
        @param products: compound URIs of products, comma separated
        @param multistep: If needed, can be set to 'true'
        @param reason:
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

        @param package:
        @param smiles: Smiles of root node compound
        @param name:
        @param description:
        @param root_node_only: If False, goes to pathway prediction mode
        @param setting: Setting for pathway prediction
        @return: Pathway object
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

    def copy(self, target_package: 'Package', debug=False):
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
            if self.get_id() == 'http://localhost:8080/package/f444f7ae-b9b9-469c-bfa8-e7b83eba42a9/pathway/ee26b1b7-53e4-4a1b-b212-b78435e392de':
                print(edge.get_reaction().is_multistep())
            copied_edge = Edge.create(copied_pathway, educts=educts, products=products,
                                      multistep=edge.get_reaction().is_multistep())
            mapping[edge.get_id()] = copied_edge.get_id()

        return mapping, copied_pathway


class User(enviPathObject):

    def get_email(self) -> str:
        return self._get('email')

    def get_forename(self) -> str:
        return self._get('forename')

    def get_surname(self) -> str:
        return self._get('surname')

    def get_default_group(self) -> 'Group':
        return Group(self.requester, id=self._get("defaultGroup")['id'])

    def get_group(self, group_id):
        return Group(self.requester, id=group_id)

    def get_groups(self) -> List['Group']:
        return self._create_from_nested_json('groups', Group)

    def get_default_package(self) -> 'Package':
        return Package(self.requester, id=self._get("defaultPackage")['id'])

    def get_default_setting(self) -> Optional['Setting']:
        try:
            return Setting(self.requester, id=self._get("defaultSetting")['id'])
        except ValueError:
            return None

    def get_setting(self, setting_id):
        return Setting(self.requester, id=setting_id)

    def get_settings(self) -> List['Setting']:
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
        :return:
        """
        return User.create(ep, email, username, password)

    @staticmethod
    def activate(ep, username, token) -> bool:
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
from abc import ABC


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
        raise ValueError("DummyAdditionalInformation can't be validated!")

    @classmethod
    def parse(cls, data_string):
        return cls(data=data_string)


class OxygenDemandAdditionalInformation(AdditionalInformation):
    name = "oxygendemand"
    mandatories = ['oxygendemandType', 'oxygendemandInfluent', 'oxygendemandEffluent']

    # Setter
    def set_oxygendemandType(self, value):
        self.params["oxygendemandType"] = value

    def set_oxygendemandInfluent(self, value):
        self.params["oxygendemandInfluent"] = value

    def set_oxygendemandEffluent(self, value):
        self.params["oxygendemandEffluent"] = value

    # Getter
    def get_oxygendemandType(self):
        return self.params.get("oxygendemandType", None)

    def get_oxygendemandInfluent(self):
        return self.params.get("oxygendemandInfluent", None)

    def get_oxygendemandEffluent(self):
        return self.params.get("oxygendemandEffluent", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'oxygendemandType': data_string.split(';')[0],
            'oxygendemandInfluent': data_string.split(';')[1],
            'oxygendemandEffluent': data_string.split(';')[2],
        }
        return cls(**res)


class DissolvedOxygenConcentrationAdditionalInformation(AdditionalInformation):
    name = "Dissolvedoxygenconcentration"
    mandatories = ['DissolvedoxygenconcentrationLow', 'DissolvedoxygenconcentrationHigh']

    # Setter
    def set_DissolvedoxygenconcentrationLow(self, value):
        self.params["DissolvedoxygenconcentrationLow"] = value

    def set_DissolvedoxygenconcentrationHigh(self, value):
        self.params["DissolvedoxygenconcentrationHigh"] = value

    # Getter
    def get_DissolvedoxygenconcentrationLow(self):
        return self.params.get("DissolvedoxygenconcentrationLow", None)

    def get_DissolvedoxygenconcentrationHigh(self):
        return self.params.get("DissolvedoxygenconcentrationHigh", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'DissolvedoxygenconcentrationLow': data_string.split(';')[0],
            'DissolvedoxygenconcentrationHigh': data_string.split(';')[1],
        }
        return cls(**res)


class OxygenUptakeRateAdditionalInformation(AdditionalInformation):
    name = "oxygenuptakerate"
    mandatories = ['oxygenuptakerateStart', 'oxygenuptakerateEnd']

    # Setter
    def set_oxygenuptakerateStart(self, value):
        self.params["oxygenuptakerateStart"] = value

    def set_oxygenuptakerateEnd(self, value):
        self.params["oxygenuptakerateEnd"] = value

    # Getter
    def get_oxygenuptakerateStart(self):
        return self.params.get("oxygenuptakerateStart", None)

    def get_oxygenuptakerateEnd(self):
        return self.params.get("oxygenuptakerateEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'oxygenuptakerateStart': data_string.split(';')[0],
            'oxygenuptakerateEnd': data_string.split(';')[1],
        }
        return cls(**res)


class AerationTypeAdditionalInformation(AdditionalInformation):
    name = "aerationtype"
    mandatories = ['aerationtype']

    # Setter
    def set_aerationtype(self, value):
        self.params["aerationtype"] = value

    # Getter
    def get_aerationtype(self):
        return self.params.get("aerationtype", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'aerationtype': data_string,
        }
        return cls(**res)


class SourceOfLiquidMatrixAdditionalInformation(AdditionalInformation):
    name = "sourceofliquidmatrix"
    mandatories = ['sourceofliquidmatrix']

    # Setter
    def set_sourceofliquidmatrix(self, value):
        self.params["sourceofliquidmatrix"] = value

    # Getter
    def get_sourceofliquidmatrix(self):
        return self.params.get("sourceofliquidmatrix", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'sourceofliquidmatrix': data_string,
        }
        return cls(**res)


class RateConstantAdditionalInformation(AdditionalInformation):
    name = "rateconstant"
    mandatories = ['rateconstantlower', 'rateconstantupper', 'rateconstantorder', 'rateconstantcorrected',
                   'rateconstantcomment']

    # Setter
    def set_rateconstantlower(self, value):
        self.params["rateconstantlower"] = value

    def set_rateconstantupper(self, value):
        self.params["rateconstantupper"] = value

    def set_rateconstantorder(self, value):
        self.params["rateconstantorder"] = value

    def set_rateconstantcorrected(self, value):
        self.params["rateconstantcorrected"] = value

    def set_rateconstantcomment(self, value):
        self.params["rateconstantcomment"] = value

    # Getter
    def get_rateconstantlower(self):
        return self.params.get("rateconstantlower", None)

    def get_rateconstantupper(self):
        return self.params.get("rateconstantupper", None)

    def get_rateconstantorder(self):
        return self.params.get("rateconstantorder", None)

    def get_rateconstantcorrected(self):
        return self.params.get("rateconstantcorrected", None)

    def get_rateconstantcomment(self):
        return self.params.get("rateconstantcomment", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        parts = data_string.split(';')
        # Sometimes the lower and upper bounds are wrongly concatenated
        # which yields in a wrong parameter assignement.
        malformed = ' - ' in parts[2]

        res = {
            'rateconstantorder': parts[0],
            'rateconstantcorrected': parts[1],
            'rateconstantlower': parts[2] if not malformed else parts[2].split(' - ')[0],
            'rateconstantupper': parts[3] if not malformed else parts[2].split(' - ')[1],
            'rateconstantcomment': parts[4] if not malformed else parts[3],
        }

        return cls(**res)


class PhosphorusContentAdditionalInformation(AdditionalInformation):
    name = "phosphoruscontent"
    mandatories = []

    # Setter
    def set_phosphoruscontentInfluent(self, value):
        self.params["phosphoruscontentInfluent"] = value

    def set_phosphoruscontentEffluent(self, value):
        self.params["phosphoruscontentEffluent"] = value

    # Getter
    def get_phosphoruscontentInfluent(self):
        return self.params.get("phosphoruscontentInfluent", None)

    def get_phosphoruscontentEffluent(self):
        return self.params.get("phosphoruscontentEffluent", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['phosphoruscontentInfluent', 'phosphoruscontentEffluent'])


class MinorMajorAdditionalInformation(AdditionalInformation):
    name = "minormajor"
    mandatories = ['radiomin']

    # Setter
    def set_radiomin(self, value):
        self.params["radiomin"] = value

    # Getter
    def get_radiomin(self):
        return self.params.get("radiomin", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['radiomin'])


class SludgeRetentionTimeAdditionalInformation(AdditionalInformation):
    name = "sludgeretentiontime"
    mandatories = ['sludgeretentiontimeType', 'sludgeretentiontime']

    # Setter
    def set_sludgeretentiontimeType(self, value):
        self.params["sludgeretentiontimeType"] = value

    def set_sludgeretentiontime(self, value):
        self.params["sludgeretentiontime"] = value

    # Getter
    def get_sludgeretentiontimeType(self):
        return self.params.get("sludgeretentiontimeType", None)

    def get_sludgeretentiontime(self):
        return self.params.get("sludgeretentiontime", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['sludgeretentiontimeType', 'sludgeretentiontime'])


class AmmoniaUptakeRateAdditionalInformation(AdditionalInformation):
    name = "amionauptakerate"
    mandatories = []

    # Setter
    def set_amionauptakerateStart(self, value):
        self.params["amionauptakerateStart"] = value

    def set_amionauptakerateEnd(self, value):
        self.params["amionauptakerateEnd"] = value

    # Getter
    def get_amionauptakerateStart(self):
        return self.params.get("amionauptakerateStart", None)

    def get_amionauptakerateEnd(self):
        return self.params.get("amionauptakerateEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['amionauptakerateStart', 'amionauptakerateEnd'])


class TemperatureAdditionalInformation(AdditionalInformation):
    name = "temperature"
    mandatories = []

    # Setter
    def set_temperatureMin(self, value):
        self.params["temperatureMin"] = value

    def set_temperatureMax(self, value):
        self.params["temperatureMax"] = value

    # Getter
    def get_temperatureMin(self):
        return self.params.get("temperatureMin", None)

    def get_temperatureMax(self):
        return self.params.get("temperatureMax", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'temperatureMin': data_string.split(';')[0],
            'temperatureMax': data_string.split(';')[1],
        }
        return cls(**res)


class NutrientsAdditionalInformation(AdditionalInformation):
    name = "additionofnutrients"
    mandatories = ['additionofnutrients']

    # Setter
    def set_additionofnutrients(self, value):
        self.params["additionofnutrients"] = value

    # Getter
    def get_additionofnutrients(self):
        return self.params.get("additionofnutrients", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'additionofnutrients': data_string,
        }
        return cls(**res)


class InoculumSourceAdditionalInformation(AdditionalInformation):
    name = "inoculumsource"
    mandatories = ['inoculumsource']

    # Setter
    def set_inoculumsource(self, value):
        self.params["inoculumsource"] = value

    # Getter
    def get_inoculumsource(self):
        return self.params.get("inoculumsource", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['inoculumsource'])


class DissolvedOrganicCarbonAdditionalInformation(AdditionalInformation):
    name = "dissolvedorganiccarbon"
    mandatories = []

    # Setter
    def set_dissolvedorganiccarbonStart(self, value):
        self.params["dissolvedorganiccarbonStart"] = value

    def set_dissolvedorganiccarbonEnd(self, value):
        self.params["dissolvedorganiccarbonEnd"] = value

    # Getter
    def get_dissolvedorganiccarbonStart(self):
        return self.params.get("dissolvedorganiccarbonStart", None)

    def get_dissolvedorganiccarbonEnd(self):
        return self.params.get("dissolvedorganiccarbonEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'dissolvedorganiccarbonStart': data_string.split(';')[0],
            'dissolvedorganiccarbonEnd': data_string.split(';')[1],
        }
        return cls(**res)


class NitrogenContentAdditionalInformation(AdditionalInformation):
    name = "nitrogencontent"
    mandatories = ['nitrogencontentType']

    # Setter
    def set_nitrogencontentType(self, value):
        self.params["nitrogencontentType"] = value

    def set_nitrogencontentInfluent(self, value):
        self.params["nitrogencontentInfluent"] = value

    def set_nitrogencontentEffluent(self, value):
        self.params["nitrogencontentEffluent"] = value

    # Getter
    def get_nitrogencontentType(self):
        return self.params.get("nitrogencontentType", None)

    def get_nitrogencontentInfluent(self):
        return self.params.get("nitrogencontentInfluent", None)

    def get_nitrogencontentEffluent(self):
        return self.params.get("nitrogencontentEffluent", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        parts = data_string.split(';')

        res = {
            'nitrogencontentType': parts[0]
        }
        if len(parts) > 1 and parts[1] != '':
            res['nitrogencontentInfluent'] = parts[1]

        if len(parts) > 2 and parts[2] != '':
            res['nitrogencontentEffluent'] = parts[2]

        return cls(**res)


class ReferringScenarioAdditionalInformation(AdditionalInformation):
    name = "referringscenario"
    mandatories = ['referringscenario']

    # Setter
    def set_referringscenario(self, value):
        self.params["referringscenario"] = value

    # Getter
    def get_referringscenario(self):
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


class ModelBayesPredictionProbabilityAdditionalInformation(AdditionalInformation):
    name = "modelbayespredictionprob"
    mandatories = ['modelbayespredictionprob']

    # Setter
    def set_modelbayespredictionprob(self, value):
        self.params["modelbayespredictionprob"] = value

    # Getter
    def get_modelbayespredictionprob(self):
        return self.params.get("modelbayespredictionprob", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['modelbayespredictionprob'])


class HalfLifeAdditionalInformation(AdditionalInformation):
    name = "halflife"
    mandatories = ['lower', 'upper']

    # Setter
    def set_lower(self, value):
        self.params["lower"] = value

    def set_upper(self, value):
        self.params["upper"] = value

    def set_comment(self, value):
        self.params["comment"] = value

    def set_source(self, value):
        self.params["source"] = value

    def set_firstOrder(self, value):
        self.params["firstOrder"] = value

    def set_model(self, value):
        self.params["model"] = value

    def set_fit(self, value):
        self.params["fit"] = value

    # Getter
    def get_lower(self):
        return self.params.get("lower", None)

    def get_upper(self):
        return self.params.get("upper", None)

    def get_comment(self):
        return self.params.get("comment", None)

    def get_source(self):
        return self.params.get("source", None)

    def get_firstOrder(self):
        return self.params.get("firstOrder", None)

    def get_model(self):
        return self.params.get("model", None)

    def get_fit(self):
        return self.params.get("fit", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        parts = data_string.split(';')
        dt50 = parts[3]

        res = {
            'model': parts[0],
            'fit': parts[1],
            'comment': parts[2],
            'lower': dt50.split(' - ')[0],
            'upper': dt50.split(' - ')[1],
            'source': parts[4],
        }

        return cls(**res)


class ProposedIntermediateAdditionalInformation(AdditionalInformation):
    name = "proposedintermediate"
    mandatories = ['proposed']

    # Setter
    def set_proposed(self, value):
        self.params["proposed"] = value

    # Getter
    def get_proposed(self):
        return self.params.get("proposed", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['proposed'])


class VolatileTSSAdditionalInformation(AdditionalInformation):
    name = "volatiletts"
    mandatories = ['volatilettsStart', 'volatilettsEnd']

    # Setter
    def set_volatilettsStart(self, value):
        self.params["volatilettsStart"] = value

    def set_volatilettsEnd(self, value):
        self.params["volatilettsEnd"] = value

    # Getter
    def get_volatilettsStart(self):
        return self.params.get("volatilettsStart", None)

    def get_volatilettsEnd(self):
        return self.params.get("volatilettsEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        parts = data_string.split(' - ')
        res = {
            'volatilettsStart': parts[0],
            'volatilettsEnd': parts[1],
        }

        return cls(**res)


class ConfidenceLevelAdditionalInformation(AdditionalInformation):
    name = "confidencelevel"
    mandatories = ['radioconfidence']

    # Setter
    def set_radioconfidence(self, value):
        self.params["radioconfidence"] = value

    # Getter
    def get_radioconfidence(self):
        return self.params.get("radioconfidence", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['radioconfidence'])


class BiologicalTreatmentTechnologyAdditionalInformation(AdditionalInformation):
    name = "biologicaltreatmenttechnology"
    mandatories = ['biologicaltreatmenttechnology']

    # Setter
    def set_biologicaltreatmenttechnology(self, value):
        self.params["biologicaltreatmenttechnology"] = value

    # Getter
    def get_biologicaltreatmenttechnology(self):
        return self.params.get("biologicaltreatmenttechnology", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['biologicaltreatmenttechnology'])


class BioreactorAdditionalInformation(AdditionalInformation):
    name = "bioreactor"
    mandatories = []

    # Setter
    def set_bioreactortype(self, value):
        self.params["bioreactortype"] = value

    def set_bioreactorsize(self, value):
        self.params["bioreactorsize"] = value

    # Getter
    def get_bioreactortype(self):
        return self.params.get("bioreactortype", None)

    def get_bioreactorsize(self):
        return self.params.get("bioreactorsize", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {}

        if len(data_string.split(';')) > 1:
            res['bioreactortype'] = data_string.split(';')[0]
            res['bioreactorsize'] = data_string.split(';')[1]
        else:
            res['bioreactortype'] = data_string.split(', ')[0]
            res['bioreactorsize'] = data_string.split(', ')[1]

        return cls(**res)


class FinalCompoundConcentrationAdditionalInformation(AdditionalInformation):
    name = "finalcompoundconcentration"
    mandatories = ['finalcompoundconcentration']

    # Setter
    def set_finalcompoundconcentration(self, value):
        self.params["finalcompoundconcentration"] = value

    # Getter
    def get_finalcompoundconcentration(self):
        return self.params.get("finalcompoundconcentration", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['finalcompoundconcentration'])


class TypeOfAdditionAdditionalInformation(AdditionalInformation):
    name = "typeofaddition"
    mandatories = ['typeofaddition']

    # Setter
    def set_typeofaddition(self, value):
        self.params["typeofaddition"] = value

    # Getter
    def get_typeofaddition(self):
        return self.params.get("typeofaddition", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['typeofaddition'])


class TSSAdditionInformation(AdditionalInformation):
    name = "tts"
    mandatories = ['ttsStart', 'ttsEnd']

    # Setter
    def set_ttsStart(self, value):
        self.params["ttsStart"] = value

    def set_ttsEnd(self, value):
        self.params["ttsEnd"] = value

    # Getter
    def get_ttsStart(self):
        return self.params.get("ttsStart", None)

    def get_ttsEnd(self):
        return self.params.get("ttsEnd", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        res = {
            'ttsStart': data_string.split(' - ')[0],
            'ttsEnd': data_string.split(' - ')[1],
        }
        return cls(**res)


class PurposeOfWWTPAdditionalInformation(AdditionalInformation):
    name = "purposeofwwtp"
    mandatories = ['purposeofwwtp']

    # Setter
    def set_purposeofwwtp(self, value):
        self.params["purposeofwwtp"] = value

    # Getter
    def get_purposeofwwtp(self):
        return self.params.get("purposeofwwtp", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['purposeofwwtp'])


class SolventForCompoundSolutionAdditionalInformation(AdditionalInformation):
    name = "solventforcompoundsolution"
    mandatories = ['solventforcompoundsolution1']

    # Setter
    def set_solventforcompoundsolution1(self, value):
        self.params["solventforcompoundsolution1"] = value

    def set_solventforcompoundsolution2(self, value):
        self.params["solventforcompoundsolution2"] = value

    def set_solventforcompoundsolution3(self, value):
        self.params["solventforcompoundsolution3"] = value

    # Getter
    def get_solventforcompoundsolution1(self):
        return self.params.get("solventforcompoundsolution1", None)

    def get_solventforcompoundsolution2(self):
        return self.params.get("solventforcompoundsolution2", None)

    def get_solventforcompoundsolution3(self):
        return self.params.get("solventforcompoundsolution3", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        if len(data_string.split(';')) == 1:
            res = {
                'solventforcompoundsolution1': data_string,
                'solventforcompoundsolution2': None,
                'solventforcompoundsolution3': None,
            }
        else:
            res = {
                'solventforcompoundsolution1': data_string.split(';')[0],
                'solventforcompoundsolution2': data_string.split(';')[1],
                'solventforcompoundsolution3': data_string.split(';')[2],
            }
        return cls(**res)


class OriginalSludgeAmountAdditionalInformation(AdditionalInformation):
    name = "originalsludgeamount"
    mandatories = ['originalsludgeamount']

    # Setter
    def set_originalsludgeamount(self, value):
        self.params["originalsludgeamount"] = value

    # Getter
    def get_originalsludgeamount(self):
        return self.params.get("originalsludgeamount", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['originalsludgeamount'])


class TypeOfAerationAdditionalInformation(AdditionalInformation):
    name = "typeofaeration"
    mandatories = ['typeofaeration']

    # Setter
    def set_typeofaeration(self, value):
        self.params["typeofaeration"] = value

    # Getter
    def get_typeofaeration(self):
        return self.params.get("typeofaeration", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['typeofaeration'])


class AcidityAdditionalInformation(AdditionalInformation):
    name = "acidity"
    mandatories = ['lowPh', 'highPh']

    # Setter
    def set_lowPh(self, value):
        self.params["lowPh"] = value

    def set_highPh(self, value):
        self.params["highPh"] = value

    def set_acidityType(self, value):
        if value.lower() not in [x.lower() for x in ['', 'WATER', 'KCL', 'CACL2']]:
            raise ValueError("{} is not allowed as acidityType".format(value))
        self.params["acidityType"] = value

    # Getter
    def get_lowPh(self):
        return self.params.get("lowPh", None)

    def get_highPh(self):
        return self.params.get("highPh", None)

    def get_acidityType(self):
        return self.params.get("acidityType", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        parts = data_string.split(';')
        vals = parts[0].split(' - ')

        res = {
            'lowPh': vals[0],
            'highPh': vals[1] if len(vals) > 1 else vals[0],
        }

        if len(parts) > 1:
            res['acidityType'] = parts[1]

        return cls(**res)


class RedoxAdditionalInformation(AdditionalInformation):
    name = "redox"
    mandatories = ['redoxType']

    # Setter
    def set_redoxType(self, value):
        if value.lower() not in [x.lower() for x in
                                 ['aerob', 'anaerob', 'anaerob: iron-reducing', 'anaerob: sulftate-reducing',
                                  'anaerob: methanogenic conditions', 'oxic', 'nitrate-reducing']]:
            raise ValueError("{} is not allowed as redoxType".format(value))
        self.params["redoxType"] = value

    # Getter
    def get_redoxType(self):
        return self.params.get("redoxType", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['redoxType'])


class LocationAdditionalInformation(AdditionalInformation):
    name = "location"
    mandatories = ['location']

    # Setter
    def set_location(self, value):
        self.params["location"] = value

    # Getter
    def get_location(self):
        return self.params.get("location", None)

    # Parser
    @classmethod
    def parse(cls, data_string):
        return cls._parse_default(data_string, ['location'])
