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

import flask
from flask import json

from sqlalchemy import exc as sa_exc
from sqlalchemy import sql

from dci import auth
from dci import decorators
from dci.api.v1 import api
from dci.api.v1 import base
from dci.api.v1 import utils as v1_utils
from dci.common import audits
from dci.common import exceptions as dci_exc
from dci.common import schemas
from dci.common import utils
from dci.db import models

_TABLE = models.ROLES
_T_COLUMNS = v1_utils.get_columns_name_with_objects(_TABLE)
_EMBED_MANY = {
    'permissions': True
}


@api.route('/roles', methods=['POST'])
@decorators.login_required
@decorators.has_role(['SUPER_ADMIN'])
@audits.log
def create_roles(user):
    values = v1_utils.common_values_dict(user)
    values.update(schemas.role.post(flask.request.json))

    if not values['label']:
        values.update({'label': values['name'].upper()})

    query = _TABLE.insert().values(**values)

    try:
        flask.g.db_conn.execute(query)
    except sa_exc.IntegrityError:
        raise dci_exc.DCICreationConflict(_TABLE.name, 'name')

    return flask.Response(
        json.dumps({'role': values}), 201,
        headers={'ETag': values['etag']}, content_type='application/json'
    )


@api.route('/roles/<uuid:role_id>', methods=['PUT'])
@decorators.login_required
@decorators.has_role(['SUPER_ADMIN'])
@audits.log
def update_role(user, role_id):
    # get If-Match header
    if_match_etag = utils.check_and_get_etag(flask.request.headers)
    values = schemas.role.put(flask.request.json)
    v1_utils.verify_existence_and_get(role_id, _TABLE)

    values['etag'] = utils.gen_etag()
    where_clause = sql.and_(
        _TABLE.c.etag == if_match_etag,
        _TABLE.c.id == role_id
    )
    query = _TABLE.update().where(where_clause).values(**values)

    result = flask.g.db_conn.execute(query)

    if not result.rowcount:
        raise dci_exc.DCIConflict('Role', role_id)

    return flask.Response(None, 204, headers={'ETag': values['etag']},
                          content_type='application/json')


@api.route('/roles', methods=['GET'])
@decorators.login_required
def get_all_roles(user):
    args = schemas.args(flask.request.args.to_dict())
    query = v1_utils.QueryBuilder(_TABLE, args, _T_COLUMNS)

    query.add_extra_condition(_TABLE.c.state != 'archived')

    if not auth.is_admin(user):
        query.add_extra_condition(_TABLE.c.label != 'SUPER_ADMIN')

    if not (auth.is_admin(user) or
            user['role_id'] == auth.get_role_id('PRODUCT_OWNER')):
        query.add_extra_condition(_TABLE.c.label != 'PRODUCT_OWNER')

    if user['role_id'] == auth.get_role_id('USER'):
        query.add_extra_condition(_TABLE.c.id == user['role_id'])

    nb_rows = query.get_number_of_rows()
    rows = query.execute(fetchall=True)
    rows = v1_utils.format_result(rows, _TABLE.name, args['embed'],
                                  _EMBED_MANY)

    return flask.jsonify({'roles': rows, '_meta': {'count': nb_rows}})


@api.route('/roles/<uuid:role_id>', methods=['GET'])
@decorators.login_required
def get_role_by_id(user, role_id):
    role = v1_utils.verify_existence_and_get(role_id, _TABLE)

    if user.role_id != role_id and user.is_regular_user():
        raise auth.UNAUTHORIZED
    if not user.is_super_admin() and \
       auth.get_role_id('SUPER_ADMIN') == role_id:
        raise auth.UNAUTHORIZED

    return base.get_resource_by_id(user, role, _TABLE, _EMBED_MANY)


@api.route('/roles/<uuid:role_id>', methods=['DELETE'])
@decorators.login_required
@decorators.has_role(['SUPER_ADMIN'])
@audits.log
def delete_role_by_id(user, role_id):
    # get If-Match header
    if_match_etag = utils.check_and_get_etag(flask.request.headers)
    v1_utils.verify_existence_and_get(role_id, _TABLE)

    values = {'state': 'archived'}
    where_clause = sql.and_(
        _TABLE.c.etag == if_match_etag,
        _TABLE.c.id == role_id
    )
    query = _TABLE.update().where(where_clause).values(**values)
    result = flask.g.db_conn.execute(query)

    if not result.rowcount:
        raise dci_exc.DCIDeleteConflict('Role', role_id)

    return flask.Response(None, 204, content_type='application/json')


@api.route('/roles/purge', methods=['GET'])
@decorators.login_required
@decorators.has_role(['SUPER_ADMIN'])
def get_to_purge_archived_roles(user):
    return base.get_to_purge_archived_resources(user, _TABLE)


@api.route('/roles/purge', methods=['POST'])
@decorators.login_required
@decorators.has_role(['SUPER_ADMIN'])
def purge_archived_roles(user):
    return base.purge_archived_resources(user, _TABLE)


@api.route('/roles/<uuid:role_id>/permissions', methods=['POST'])
@decorators.login_required
@decorators.has_role(['SUPER_ADMIN'])
def add_permission_to_role(user, role_id):
    data_json = flask.request.json
    values = {'role_id': role_id,
              'permission_id': data_json.get('permission_id')}

    v1_utils.verify_existence_and_get(role_id, _TABLE)

    query = models.JOIN_ROLES_PERMISSIONS.insert().values(**values)
    try:
        flask.g.db_conn.execute(query)
    except sa_exc.IntegrityError:
        raise dci_exc.DCICreationConflict(_TABLE.name,
                                          'role_id, permission_id')
    result = json.dumps(values)
    return flask.Response(result, 201, content_type='application/json')


@api.route('/roles/<uuid:role_id>/permissions/<uuid:permission_id>',
           methods=['DELETE'])
@decorators.login_required
@decorators.has_role(['SUPER_ADMIN'])
def delete_permission_from_role(user, role_id, permission_id):
    v1_utils.verify_existence_and_get(role_id, _TABLE)

    JRP = models.JOIN_ROLES_PERMISSIONS
    where_clause = sql.and_(JRP.c.role_id == role_id,
                            JRP.c.permission_id == permission_id)
    query = JRP.delete().where(where_clause)
    result = flask.g.db_conn.execute(query)

    if not result.rowcount:
        raise dci_exc.DCIConflict('Role', role_id)

    return flask.Response(None, 204, content_type='application/json')
