#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from nailgun.db.sqlalchemy.models import *
from nailgun.db import db
from copy import deepcopy


def clear_restriction():
    for release in db().query(Release).all():
        release.wizard_metadata = deepcopy(release.wizard_metadata)
        for value in release.wizard_metadata['Network']['manager']['values']:
            try:
               if value['data'] == 'neutron-tun':
                  del value['restrictions']
                  db().commit()
            except:
                pass

def main():
    return clear_restriction()


if __name__ == "__main__":
    main()

