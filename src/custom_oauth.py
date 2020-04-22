#!/usr/bin/python3
import requests
import json

import generic

class OAuthClient():

    def __init__(self, config):
        self.client_id = self._get_valid_url_client_id(config["client_id"])
        self.scopes = self._get_valid_url_scopes(config["scopes"])
        self.sso_url = self._get_valid_https_url(config["sso_url"])
        self.redirect_uri = config["redirect_uri"]
        self.client_secret = config["client_secret"]
        self.post_logout_redirect_uri = config["post_logout_redirect_uri"]

    def _get_valid_url_client_id(self, client_id):
        return client_id.replace("@","%40")

    def _get_valid_url_scopes(self, scopes):
        return_scopes = ""
        for scope in scopes:
            return_scopes = return_scopes + scope + "%20"
        return_scopes = return_scopes.rstrip("%20")

        return return_scopes

    def _get_valid_https_url(self, url):
        if "http" not in url:
            return "https://" + url

    def get_login_url(self):
        return self.sso_url + "/oxauth/restv1/authorize?scope="+self.scopes+"&client_id="+self.client_id+"&redirect_uri="+self.redirect_uri+"&response_type=code"

    def get_token(self, code):
        token_endpoint = "/oxauth/restv1/token"

        payload = "grant_type=authorization_code&client_id="+self.client_id+"&code="+code+"&client_secret="+self.client_secret+"&scope="+self.scopes+"&redirect_uri="+self.redirect_uri
        headers = {"content-type": "application/x-www-form-urlencoded", 'cache-control': "no-cache"}
        
        response = requests.request("POST", self.sso_url + token_endpoint, data=payload, headers=headers, verify=False)
        return json.loads(response.text)

    def refresh_token(self, refresh_token):
        "Gets a new token, using a previous refresh token"
        token_endpoint = "/oxauth/restv1/token"

        payload = "grant_type=refresh_token&refresh_token="+refresh_token+"&client_id="+self.client_id+"&client_secret="+self.client_secret
        headers = {"content-type": "application/x-www-form-urlencoded", 'cache-control': "no-cache"}
        
        response = requests.request("POST", self.sso_url + token_endpoint, data=payload, headers=headers, verify=False)
        return json.loads(response.text)

    def get_user_info(self,access_token):
        user_info_endpoint = "/oxauth/restv1/userinfo"

        response = requests.request("GET", self.sso_url + user_info_endpoint+"?access_token="+access_token, verify=False)
        status = response.status_code
        if status > 199 and status < 300:
            return json.loads(response.text)
        else:
            return None

    def end_session_url(self, id_token):
        end_session_url = "/oxauth/restv1/end_session"

        return self.sso_url + end_session_url +"?post_logout_redirect_uri="+self.post_logout_redirect_uri+"&id_token_hint="+id_token