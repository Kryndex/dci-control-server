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


class Identity:
    """Class that offers helper methods to simplify permission management
    """

    def __init__(self, user, teams):
        for key in user.keys():
            setattr(self, key, user[key])

        self.teams = teams

    # TODO(spredzy): In order to avoid a huge refactor patch, the __getitem__
    # function is overloaded so it behaves like a dict and the code in place
    # can work transparently
    def __getitem__(self, key):
        return getattr(self, key)

    def is_in_team(self, team_id):
        """Ensure the user is in the specified team."""

        if self.is_super_admin():
            return True

        return team_id in self.teams

    def is_super_admin(self):
        """Ensure the user has the role SUPER_ADMIN."""

        return self.role_label == 'SUPER_ADMIN'

    def is_product_owner(self):
        """Ensure the user has the role PRODUCT_OWNER."""

        return self.role_label == 'PRODUCT_OWNER'

    def is_team_product_owner(self, team_id):
        """Ensure the user has the role PRODUCT_OWNER and belongs
           to the team."""

        return self.role_label == 'PRODUCT_OWNER' and \
            self.is_in_team(team_id)

    def is_admin(self):
        """Ensure the user has the role ADMIN."""

        return self.role_label == 'ADMIN'

    def is_team_admin(self, team_id):
        """Ensure the user has the role ADMIN and belongs to the team."""

        return self.role_label == 'ADMIN' and self.is_in_team(team_id)

    def is_regular_user(self):
        """Ensure the user has the role USER."""

        return self.role_label == 'USER'

    def is_remoteci(self):
        """Ensure ther resource has the role REMOTECI."""

        return self.role_label == 'REMOTECI'