#!/usr/bin/python3
from eoepca_scim import *

import collections

class SCIMClient():

    def __init__(self, config):
        sso_url = self._get_valid_https_url(config["sso_url"])

        self.protected_attrs = config["protected_attributes"]
        self.blacklist_attrs = config["blacklist_attributes"]
        self.separator = config["separator_ui_attributes"]

        # If we don't have a client, auto-create one in SCIM
        if config["client_id"] == "" or config["client_secret"] == "":
            # TODO: Init / Register using scim library
            pass

        #self.scim_client = EOEPCA_Scim(sso_url, clientID=config["client_id"], clientSecret=config["client_secret"])
        self.scim_client = EOEPCA_Scim(sso_url)
        grantTypes=["client_credentials", "urn:ietf:params:oauth:grant-type:uma-ticket"]
        redirectURIs=["https://demoexample.gluu.org/login"]
        logoutURI="https://demoexample.gluu.org/logout"
        responseTypes=[]
        scopes=["openid", "oxd", "permission"]
        self.scim_client.registerClient("TestClient", grantTypes, redirectURIs, logoutURI, responseTypes, scopes)

    def _get_valid_https_url(self, url):
        if "http" not in url:
            return "https://" + url

    def changeAttributes(self, user_id, data):
        data = data.to_dict()
        for k, v in data.items():
            print(k,v)
            # TODO:
            # self.scim_client.editUserAttribute(user_id,k,v)

        return "", ""


    def getAttributes(self, user_id):
        err = ""
        # TODO:
        try:
            data = self.scim_client.getUserAttributes(user_id)
            print(data)
        except Exception as e:
            print(str(e))
            err = "Something went wrong while getting attributes: "+str(e)
            data = {}
            return {}, err

        #data = {'schemas': ['urn:ietf:params:scim:schemas:core:2.0:User'], 'id': '@!C28A.A0EC.7CA4.6154!0001!94C2.0974!0000!F237.2B41.BAB1.7A00', 'meta': {'resourceType': 'User', 'created': '2020-04-16T16:33:44.208Z', 'lastModified': '2020-04-21T18:47:29.649Z', 'location': 'https://demoexample.gluu.org/identity/restv1/scim/v2/Users/@!C28A.A0EC.7CA4.6154!0001!94C2.0974!0000!F237.2B41.BAB1.7A00'}, 'userName': 'tiago@test.com', 'name': {'familyName': 'M Fernandes', 'givenName': 'Tiago', 'middleName': 'M', 'formatted': 'Tiago Fernandes'}, 'displayName': 'Tiago', 'active': True, 'emails': [{'value': 'tiago@test.com', 'primary': False}]}

        return self._clean_attributes(data), err

    def _clean_attributes(self, data):

        ret = {"fixed": {},
               "editable": {}}
        data = self._purge_blacklist(data)

        for k,v in data.items():
            if isinstance(v, dict):
                for k,v in self._flatten({k:v}).items():
                    if k in self.protected_attrs:
                        ret["fixed"][k] = v
                    else:
                        ret["editable"][k] = v

            if k in self.protected_attrs:
                ret["fixed"][k] = v
            else:
                ret["editable"][k] = v

        return ret

    def _purge_blacklist(self, data):
        delete = []
        for k,v in data.items():
            if k in self.blacklist_attrs:
                delete.append(k)
            if isinstance(v, dict):
                data[k] = self._purge_blacklist(v)

        for k in delete: del data[k]

        return data

    def _flatten(self, d, parent_key=''):
        items = []
        for k, v in d.items():
            new_key = parent_key + self.separator + k if parent_key else k
            if isinstance(v, collections.MutableMapping):
                items.extend(self._flatten(v, new_key).items())
            else:
                items.append((new_key, v))
        return dict(items)