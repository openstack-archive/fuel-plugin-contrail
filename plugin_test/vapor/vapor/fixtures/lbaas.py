# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import functools

import pytest
from stepler.third_party import utils

from vapor.helpers import lbaas


@pytest.fixture
def lbaas_steps(neutron_client):
    return lbaas.LBaaSSteps(neutron_client)


@pytest.fixture
def loadbalancer(request, lbaas_steps, net_subnet_router):
    """Fixture to create loadbalancer on default subnet."""
    name = next(utils.generate_ids('lb'))
    request.addfinalizer(
        functools.partial(lbaas_steps.cleanup_lbs, names=[name]))
    return lbaas_steps.create_lb(name, net_subnet_router[1])


@pytest.fixture
def lb_listener(request, lbaas_steps, loadbalancer):
    """Fixture to create lbaas HTTP listener."""
    name = next(utils.generate_ids('lb_listener'))
    request.addfinalizer(
        functools.partial(lbaas_steps.cleanup_listeners, names=[name]))
    return lbaas_steps.create_listener(
        name=name,
        loadbalancer=loadbalancer,
        protocol="HTTP",
        protocol_port=80)


@pytest.fixture
def lb_pool(request, lbaas_steps, lb_listener):
    """Fixture to create lbaas pool."""
    name = next(utils.generate_ids('lb_pool'))
    request.addfinalizer(
        functools.partial(lbaas_steps.cleanup_pools, names=[name]))
    return lbaas_steps.create_pool(
        name=name,
        listener=lb_listener,
        protocol="HTTP",
        lb_algorithm="ROUND_ROBIN")
