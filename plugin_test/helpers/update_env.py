"""Copyright 2016 Mirantis, Inc.

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
License for the specific language governing permissions and limitations
under the License.
"""


from fuelweb_test.test.tests_upgrade.tests_install_mu_base import MUInstallBase

class MUInstall92(MUInstallBase):
    
    def prepare_env_for_update(obj):
        self.check_env_var()
        self.self._prepare_cluster_for_mu()

    def install_update(obj, cluster_id):
        self._check_for_potential_updates(cluster_id)
        self._install_mu(cluster_id, repos=self.repos)
        self._check_for_potential_updates(cluster_id, updated=True)
        self.fuel_web.verify_network(cluster_id)
