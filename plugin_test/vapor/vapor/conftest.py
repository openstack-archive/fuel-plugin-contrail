# pytest settings and fixtures

from stepler.conftest import *  # noqa
from stepler.glance.fixtures import *  # noqa
from stepler.keystone.fixtures import *  # noqa
from stepler.neutron.fixtures import *  # noqa
from stepler.nova.fixtures import *  # noqa

from vapor.fixtures.contrail import *  # noqa
from vapor.fixtures.contrail_resources import *  # noqa
from vapor.fixtures.different_tenants_resources import *  # noqa
from vapor.fixtures.dns import *  # noqa
from vapor.fixtures.images import *  # noqa
from vapor.fixtures.instance_ip import *  # noqa
from vapor.fixtures.ipams import *  # noqa
from vapor.fixtures.networks import *  # noqa
from vapor.fixtures.nodes import *  # noqa
from vapor.fixtures.policies import *  # noqa
from vapor.fixtures.security_groups import *  # noqa
from vapor.fixtures.service_chain import *  # noqa
from vapor.fixtures.skip import *  # noqa
from vapor.fixtures.subnets import *  # noqa
from vapor.fixtures.system_services import *  # noqa
from vapor.fixtures.virtual_interface import *  # noqa

pytest_plugins = [
    'vapor.plugins.xfail',
]
