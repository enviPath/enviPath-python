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

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import *

from enviPath_python.objects import *


class enviPath(object):
    """
    Object representing enviPath functionality.
    """

    def __init__(self, base_url, proxies=None):
        """
        Constructor with instance specification.
        :param base_url: The url of the enviPath instance.
        """
        self.BASE_URL = base_url if base_url.endswith('/') else base_url + '/'
        self.requester = enviPathRequester(proxies)

    def get_base_url(self):
        return self.BASE_URL

    def login(self, username, password) -> None:
        """
        Performs login.
        :param username: The username.
        :param password: The corresponding password.
        :return: None
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
        """
        params = {
            'whoami': 'true',
        }
        url = self.BASE_URL + Endpoint.USER.value
        user_data = self.requester.get_request(url, params=params).json()[Endpoint.USER.value][0]
        return User(self.requester, **user_data)

    def get_package(self, package_id: str):
        """
        TODO
        :param package_id:
        :return:
        """
        return Package(self.requester, **self.requester.get_json(package_id))

    def get_packages(self) -> List['Package']:
        """
        Gets all packages the logged in user has at least read permissions on.
        :return: List of Package objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.PACKAGE)

    def get_compound(self, compound_id):
        """
        TODO
        :param compound_id:
        :return:
        """
        return Compound(self.requester, **self.requester.get_json(compound_id))

    def get_compounds(self) -> List['Compound']:
        """
        Gets all compounds the logged in user has at least read permissions on.
        :return: List of Compound objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.COMPOUND)

    def get_reaction(self, reaction_id):
        """

        :param reaction_id:
        :return:
        """
        return Reaction(self.requester, **self.requester.get_json(reaction_id))

    def get_reactions(self):
        """
        Gets all reactions the logged in user has at least read permissions on.
        :return: List of Reaction objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.REACTION)

    def get_rule(self, rule_id):
        """

        :param rule_id:
        :return:
        """
        return Rule(self.requester, **self.requester.get_json(rule_id))

    def get_rules(self):
        """
        Gets all rules the logged in user has at least read permissions on.
        :return: List of Reaction objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.RULE)

    def get_pathway(self, pathway_id):
        """

        :param pathway_id:
        :return:
        """
        return Pathway(self.requester, **self.requester.get_json(pathway_id))

    def get_pathways(self):
        """
        Gets all pathways the logged in user has at least read permissions on.
        :return: List of Pathway objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.PATHWAY)

    def get_scenario(self, scenario_id):
        """

        :param scenario_id:
        :return:
        """
        return Scenario(self.requester, **self.requester.get_json(scenario_id))

    def get_scenarios(self):
        """
        Gets all scenarios the logged in user has at least read permissions on.
        :return: List of Scenario objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.SCENARIO)

    def get_setting(self, setting_id):
        """
        :param setting_id:
        :return:
        """
        return Setting(self.requester, **self.requester.get_json(setting_id))

    def get_settings(self):
        """
        Gets all settings the logged in user has at least read permissions on.
        :return: List of Settings objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.SETTING)

    def get_users(self):
        """
        Gets all users the logged in user has at least read permissions on.
        :return: List of User objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.USER)

    def get_groups(self):
        """
        Gets all groups the logged in user has at least read permissions on.
        :return: List of Group objects.
        """
        return self.requester.get_objects(self.BASE_URL, Endpoint.GROUP)

    def create_package(self, group: 'Group', name: str = None, description: str = None) -> Package:
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

    def __init__(self, proxies=None):
        """
        Setup session for cookies as well as avoiding unnecessary ssl-handshakes.
        """
        self.session = Session()
        self.session.mount('http://', HTTPAdapter())
        self.session.mount('https://', HTTPAdapter())
        if proxies:
            self.session.proxies = proxies

    def get_request(self, url, params=None, payload=None, **kwargs):
        """
        Convenient method to perform GET request to given url with optional query parameters and data.
        :param url: The url to retrieve data from.
        :param params: Dictionary containing query parameters as key, value.
        :param payload: Data send within the body.
        :return: response object.
        """
        try:
            request = self._request('GET', url, params, payload, **kwargs)
        except SSLError:
            print('SSL error, trying again')
            request = self.get_request(url, params=None, payload=None, **kwargs)

        return request

    def post_request(self, url, params=None, payload=None, **kwargs):
        """
        Convenient method to perform POST request to given url with optional query parameters and data.
        :param url: The url for object creation, object manipulation.
        :param params: Dictionary containing query parameters as key, value.
        :param payload: Data send within the body.
        :return: response object.
        """
        return self._request('POST', url, params, payload, **kwargs)

    def delete_request(self, url, params=None, payload=None, **kwargs):
        """
        Convenient method to perform DELETE request to given url with optional query parameters and data.
        :param url: The url for object creation, object manipulation.
        :param params: Dictionary containing query parameters as key, value.
        :param payload: Data send within the body.
        :return: response object.
        """
        return self._request('DELETE', url, params, payload, **kwargs)

    def _request(self, method, url, params=None, payload=None, **kwargs):
        """
        Method performing the actual request.
        :param method: HTTP method.
        :param url: url for request.
        :param params: parameters to send.
        :param payload: data to send.
        :return: response object.
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

    def get_json(self, envipath_id: str):
        """
        TODO
        :param envipath_id:
        :return:
        """
        return self.get_request(envipath_id).json()

    def login(self, url, username, password):
        """
        Performs login,
        :param url: Can be any valid enviPath url.
        :param username: The username.
        :param password: The corresponding password.
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

    def logout(self, url):
        """
        Performs logout.
        :param url: Can be any valid enviPath url.
        :return: None
        """
        data = {
            'hiddenMethod': 'logout',
        }
        self.post_request(url, payload=data)

    def get_objects(self, base_url, endpoint):
        """
        Generic get method to retrieve objects.
        :param endpoint: Enum of Endpoint.
        :return: List of objects denoted by endpoint.
        """
        url = base_url + endpoint.value
        objs = self.get_request(url).json()

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
                    # TODO replace with logger....
                    print("Unknown Rule type...")
                    print(obj)
            return res
        elif endpoint.value in objs:
            return [self.ENDPOINT_OBJECT_MAPPING[endpoint](self, **obj) for obj in objs[endpoint.value]]
        else:
            # TODO replace with logger....
            print('Endpoint value not present in result...')
            print(objs)
            return []
