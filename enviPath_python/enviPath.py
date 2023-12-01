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
import copy
from collections.abc import Iterable
from typing import Union, List

import requests
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import *

from enviPath_python.objects import *


class enviPath(object):
    """
    Object representing enviPath functionality.
    """

    def __init__(self, base_url, proxies=None, adapter=None):
        """
        Constructor with instance specification.

        :param base_url: The url of the enviPath instance.
        :type base_url: str
        :param proxies: The proxy of the enviPath instance
        :type proxies: str, optional
        """
        self.BASE_URL = base_url if base_url.endswith('/') else base_url + '/'
        self.requester = enviPathRequester(self, proxies, adapter)

    def get_base_url(self) -> str:
        """
        Method to return the base url of the enviPath object

        :return: The base URL
        :rtype: str
        """
        return self.BASE_URL

    def login(self, username, password) -> None:
        """
        Performs login.

        :param username: The username.
        :type username: str
        :param password: The corresponding password.
        :type password: str
        """
        self.requester.login(self.BASE_URL, username, password)

    def logout(self) -> None:
        """
        Performs logout.

        :return: None
        """
        self.requester.logout(self.BASE_URL)

    def who_am_i(self) -> User:
        """
        Method to get the currently logged in user.

        :return: User object.
        :rtype: enviPath_python.objects.User
        """
        params = {
            'whoami': 'true',
        }
        url = self.BASE_URL + Endpoint.USER.value
        user_data = self.requester.get_request(url, params=params).json()[Endpoint.USER.value][0]
        return User(self.requester, **user_data)

    def search(self, term: str, packages: Union['Package', List['Package']]):
        """
        Function designed to perform a search on an enviPath session.

        :param term: the term with which the search wants to be performed
        :param packages: the packages where the search wants to be performed
        :return: a dictionary of object identifiers
        """
        params = {
            'packages[]': [p.get_id() for p in packages] if isinstance(packages, Iterable) else [packages.get_id()],
            'search': term,
        }

        res = self.requester.get_request('{}search'.format(self.BASE_URL), params=params)
        res.raise_for_status()

        data = res.json()

        result = {}
        for k, vals in data.items():
            objects = []
            for v in vals:
                # old search implementation returns object id in its plural form, remove trailing s
                objects.append(self.requester.get_object(v['id'], Endpoint(k.rstrip('s'))))

            result[k] = objects

        return result

    def get_package(self, package_id: str) -> Package:
        """
        Gets the specified package

        :param package_id: The identifier of the package
        :type package_id: str
        :return: A package object
        :rtype: enviPath_python.objects.Package
        """
        return Package(self.requester, **self.requester.get_json(package_id))

    def get_packages(self) -> List['Package']:
        """
        Gets all packages the logged in user has at least read permissions on.

        :return: List of Package objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.PACKAGE)

    def get_compound(self, compound_id) -> Compound:
        """
        Returns the compound matching with id `compound_id`

        :param compound_id: The identifier of the compound
        :type compound_id: str
        :return: The retrieved compound with matching compound id
        :rtype: enviPath_python.objects.Compound
        """
        return Compound(self.requester, **self.requester.get_json(compound_id))

    def get_compounds(self) -> List['Compound']:
        """
        Gets all compounds the logged in user has at least read permissions on.

        :return: List of Compound objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.COMPOUND)

    def get_reaction(self, reaction_id) -> Reaction:
        """
        Get the reaction with reaction identifier `reaction_id`

        :param reaction_id: The identifier for the reaction
        :type reaction_id: str
        :return: The reaction with matching id
        :rtype: enviPath_python.objects.Reaction
        """
        return Reaction(self.requester, **self.requester.get_json(reaction_id))

    def get_reactions(self) -> List['Reaction']:
        """
        Gets all reactions the logged in user has at least read permissions on.

        :return: List of Reaction objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.REACTION)

    def get_rule(self, rule_id) -> Rule:
        """
        Get the rule with identifier `rule_id`

        :param rule_id: The identifier of the rule
        :type rule_id: str
        :return: The rule with the corresponding id equivalent to `rule_id`
        :rtype: enviPath_python.objects.Rule
        """

        obj = self.requester.get_json(rule_id)

        clz = None
        if obj['identifier'] == Endpoint.SIMPLERULE.value:
            clz = SimpleRule
        elif obj['identifier'] == Endpoint.SEQUENTIALCOMPOSITERULE.value:
            clz = SequentialCompositeRule
        elif obj['identifier'] == Endpoint.PARALLELCOMPOSITERULE.value:
            clz = ParallelCompositeRule
        else:
            raise ValueError("Unknown Rule Type ({})".format(obj['identifier']))

        return clz(self.requester, **obj)

    def get_rules(self) -> List['Rule']:
        """
        Gets all rules the logged in user has at least read permissions on.

        :return: List of Reaction objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.RULE)

    def get_pathway(self, pathway_id) -> Pathway:
        """
        Get the pathway with identifier `pathway_id`

        :param pathway_id: The identifier of the pathway
        :type pathway_id: str
        :return: The pathway with matching id
        :rtype: enviPath_python.objects.Pathway
        """
        return Pathway(self.requester, **self.requester.get_json(pathway_id))

    def get_pathways(self) -> List['Pathway']:
        """
        Gets all pathways the logged in user has at least read permissions on.

        :return: List of Pathway objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.PATHWAY)

    def get_scenario(self, scenario_id) -> Scenario:
        """
        Get the pathway with identifier `scenario_id`

        :param scenario_id: The identifier of the scenario
        :type scenario_id: str
        :return: The scenario with matching id
        :rtype: enviPath_python.objects.Scenario
        """
        return Scenario(self.requester, **self.requester.get_json(scenario_id))

    def get_scenarios(self) -> List['Scenario']:
        """
        Gets all scenarios the logged in user has at least read permissions on.

        :return: List of Scenario objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.SCENARIO)

    def get_setting(self, setting_id) -> Setting:
        """
        Get the setting with identifier `setting_id`

        :param setting_id: The identifier of the setting
        :type setting_id: str
        :return: The setting with matching id
        :rtype: enviPath_python.objects.Setting
        """
        return Setting(self.requester, **self.requester.get_json(setting_id))

    def get_settings(self) -> List['Setting']:
        """
        Gets all settings the logged in user has at least read permissions on.

        :return: List of Settings objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.SETTING)

    def get_users(self) -> List['User']:
        """
        Gets all users the logged in user has at least read permissions on.

        :return: List of Settings objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.USER)

    def get_groups(self):
        """
        Gets all groups the logged in user has at least read permissions on.

        :return: List of Group objects.
        :rtype: List
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.GROUP)

    def create_package(self, group: 'Group', name: str = None, description: str = None) -> Package:
        """
        Function that creates an enviPath package

        :param group: The group that the package will belong to
        :type group: enviPath_python.objects.Group
        :param name: The name for the package
        :type name: str
        :param description: The description for the package
        :type description: str
        :return: The created package
        :rtype: enviPath_python.objects.Package
        """
        return Package.create(self, group, name=name, description=description)


class enviPathRequester(object):
    """
    Class performing all requests to the enviPath instance.
    """
    header = {'Accept': 'application/json'}

    ENDPOINT_OBJECT_MAPPING = {
        Endpoint.USER: User,
        Endpoint.PACKAGE: Package,
        Endpoint.COMPOUND: Compound,
        Endpoint.PATHWAY: Pathway,
        Endpoint.REACTION: Reaction,
        Endpoint.SCENARIO: Scenario,
        Endpoint.SETTING: Setting,
        Endpoint.RULE: Rule,
        Endpoint.SIMPLERULE: SimpleRule,
        Endpoint.SEQUENTIALCOMPOSITERULE: SequentialCompositeRule,
        Endpoint.PARALLELCOMPOSITERULE: ParallelCompositeRule,
        Endpoint.NODE: Node,
        Endpoint.EDGE: Edge,
        Endpoint.COMPOUNDSTRUCTURE: CompoundStructure,
        Endpoint.GROUP: Group,
        Endpoint.RELATIVEREASONING: RelativeReasoning,
    }

    def __init__(self, eP, proxies=None, adapter=None):
        """
        Setup session for cookies as well as avoiding unnecessary ssl-handshakes.
        """

        if adapter is None:
            adapter = HTTPAdapter()

        self.eP = eP
        self.session = Session()
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        if proxies:
            self.session.proxies = proxies

    def get_request(self, url, params=None, payload=None, **kwargs) -> requests.Response:
        """
        Convenient method to perform GET request to given url with optional query parameters and data.

        :param url: The url to retrieve data from.
        :type url: str
        :param params: Dictionary containing query parameters as key, value.
        :type params: dict or None
        :param payload: Data send within the body.
        :return: response object.
        :rtype: requests.Response
        """
        try:
            request = self._request('GET', url, params, payload, **kwargs)
        except SSLError:
            print('SSL error, trying again')
            request = self.get_request(url, params=None, payload=None, **kwargs)

        return request

    def post_request(self, url, params=None, payload=None, **kwargs) -> requests.Response:
        """
        Convenient method to perform POST request to given url with optional query parameters and data.

        :param url: The url for object creation, object manipulation.
        :type url: str
        :param params: Dictionary containing query parameters as key, value.
        :type params: dict
        :param payload: Data send within the body.
        :return: response object.
        :rtype: requests.Response
        """
        return self._request('POST', url, params, payload, **kwargs)

    def delete_request(self, url, params=None, payload=None, **kwargs) -> requests.Response:
        """
        Convenient method to perform DELETE request to given url with optional query parameters and data.

        :param url: The url for object deletion.
        :type url: str
        :param params: Dictionary containing query parameters as key, value.
        :type params: dict
        :param payload: Data send within the body.
        :return: response object.
        :rtype: requests.Response
        """
        return self._request('DELETE', url, params, payload, **kwargs)

    def _request(self, method, url, params=None, payload=None, **kwargs) -> requests.Response:
        """
        Method performing the actual request.

        :param method: HTTP method.
        :type method: str
        :param url: url for request.
        :type url: str
        :param params: Dictionary containing query parameters as key, value.
        :type params: dict
        :param payload: data to send.
        :return: response object.
        :rtype: requests.Response
        """
        default_headers = self.header
        if 'headers' in kwargs:
            default_headers = copy.deepcopy(default_headers)
            default_headers.update(**kwargs['headers'])
            del kwargs['headers']
        try:
            response = self.session.request(method, url, params=params, data=payload, headers=default_headers, **kwargs)
        except ConnectionError:
            import time
            time.sleep(10)
            response = self.session.request(method, url, params=params, data=payload, headers=default_headers, **kwargs)

        return response

    def get_json(self, envipath_id: str) -> dict:
        """
        Returns the response of the request in a json format

        :param envipath_id: The url where the get request wants to be performed
        :return: The json version of the response
        :rtype: json
        """
        return self.get_request(envipath_id).json()

    def login(self, url, username, password) -> None:
        """
        Performs login.

        :param url: Can be any valid enviPath url.
        :type url: str
        :param username: The username.
        :type username: str
        :param password: The corresponding password.
        :type password: str
        :return: None
        """
        data = {
            'hiddenMethod': 'login',
            'loginusername': username,
            'loginpassword': password,
        }
        res = self.post_request(url, payload=data)
        try:
            res.raise_for_status()
        except HTTPError:
            raise ValueError("Login Failed!")

    def logout(self, url) -> None:
        """
        Performs logout.

        :param url: Can be any valid enviPath url.
        :type url: str
        :return: None
        """
        data = {
            'hiddenMethod': 'logout',
        }
        self.post_request(url, payload=data)

    def get_objects(self, base_url, endpoint):
        """
        Generic get method to retrieve objects.

        :param base_url: The base URL
        :type base_url: str
        :param endpoint: Enum of Endpoint.
        :return: List of objects denoted by endpoint.
        """
        url = base_url + endpoint.value
        objs = self.get_request(url).json()

        # Handly malformed reponse in case there are not entries
        if len(objs) == 0 or ('object' in objs and len(objs['object']) == 0):
            return []

        # TODO delegate to get_object
        if endpoint == Endpoint.RULE:
            res = []
            for obj in objs[endpoint.value]:
                if obj['identifier'] == Endpoint.SIMPLERULE.value:
                    res.append(SimpleRule(self, **obj))
                elif obj['identifier'] == Endpoint.SEQUENTIALCOMPOSITERULE.value:
                    res.append(SequentialCompositeRule(self, **obj))
                elif obj['identifier'] == Endpoint.PARALLELCOMPOSITERULE.value:
                    res.append(ParallelCompositeRule(self, **obj))
                else:
                    raise ValueError("Unknown Rule Type ({})".format(obj['identifier']))
            return res
        elif endpoint.value in objs:
            return [self.ENDPOINT_OBJECT_MAPPING[endpoint](self, **obj) for obj in objs[endpoint.value]]
        else:
            raise ValueError("Cant map ({}) to objects".format(objs.keys()))

    def get_object(self, obj_id, endpoint):
        """
        Generic get method to retrieve objects.

        :param obj_id: The identifier for the object
        :type obj_id: str
        :param endpoint: The endpoint where to get the object
        :return: Object stored on the endpoint with id `obj_id` (if matched)
        """
        if endpoint == Endpoint.RULE:
            if Endpoint.SIMPLERULE.value in obj_id:
                return SimpleRule(self, id=obj_id)
            elif Endpoint.SEQUENTIALCOMPOSITERULE.value in obj_id:
                return SequentialCompositeRule(self, id=obj_id)
            elif Endpoint.PARALLELCOMPOSITERULE.value in obj_id:
                return ParallelCompositeRule(self, id=obj_id)
            else:
                raise ValueError("Unable to determine rule type for {}".format(obj_id))
        else:
            return self.ENDPOINT_OBJECT_MAPPING[endpoint](self, id=obj_id)
