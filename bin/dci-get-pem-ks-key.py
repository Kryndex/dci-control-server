#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2017 Red Hat, Inc
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import base64
import sys

import requests

try:
    from cryptography.hazmat.primitives.asymmetric.rsa import RSAPublicNumbers
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
except ImportError:
    print('Module cryptography not found')
    sys.exit(1)


"""The SSO server publish its public
key with the modulus and exponent. This script get the
public key from the SSO server and transform it to the PEM format.
The dci control server stores this value in its configuration file with the
key 'SSO_PUBLIC_KEY'.
"""


def get_pem_public_key_from_modulus_exponent(n, e):
    def _b64decode(data):
        # padding to have multiple of 4 characters
        if len(data) % 4:
            data = data + '=' * (len(data) % 4)
        data = data.encode('ascii')
        data = bytes(data)
        return long(base64.urlsafe_b64decode(data).encode('hex'), 16)
    modulus = _b64decode(n)
    exponent = _b64decode(e)
    numbers = RSAPublicNumbers(exponent, modulus)
    public_key = numbers.public_key(backend=default_backend())
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)


def main(sso_url, realm):
    url = '%s/auth/realms/%s/.well-known/openid-configuration' % (sso_url,
                                                                  realm)
    sso_config = requests.get(url).json()
    jwks_uri = sso_config['jwks_uri']
    sso_certs = requests.get(jwks_uri).json()
    n = sso_certs['keys'][0]['n']
    e = sso_certs['keys'][0]['e']
    print(get_pem_public_key_from_modulus_exponent(n, e))


if __name__ == '__main__':

    if len(sys.argv) < 3:
        usage = """
Usage:
$ %s SSO_URL REALM_NAME\n
Example:
$ %s http://localhost:8180 dci-test
                """ % (sys.argv[0], sys.argv[0])
        print(usage)
    else:
        main(sys.argv[1], sys.argv[2])
