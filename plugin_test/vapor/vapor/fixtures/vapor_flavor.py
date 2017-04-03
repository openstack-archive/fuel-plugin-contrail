import pytest
from vapor import settings


@pytest.fixture
def vapor_flavor(request, create_flavor, flavor_steps):
    if settings.DPDK:    
        flavor_params = dict(ram=2048, vcpus=1, disk=10,
                   metadata={'hw:mem_page_size':'large'})
        flavor_params.update(getattr(request, 'param', {}))
        flavor_name, = utils.generate_ids('flavor')
        flavor = create_flavor(flavor_name, **flavor_params)
        metadata = flavor_params.get('metadata')
        flavor_steps.set_metadata(flavor, metadata)
        return flavor
    else:
    	flavor_params = dict(ram=512, vcpus=1, disk=5)
        flavor_params.update(getattr(request, 'param', {}))
        flavor_name, = utils.generate_ids('flavor')
        return create_flavor(flavor_name, **flavor_params)

@pytest.fixture
def public_vapor_flavor(create_flavor):
	if settings.DPDK:
		flavor_params = dict(ram=2048, vcpus=1, disk=10, is_public=True,
                   metadata={'hw:mem_page_size':'large'})
        flavor_params.update(getattr(request, 'param', {}))
        flavor_name, = utils.generate_ids('flavor')
        flavor = create_flavor(flavor_name, **flavor_params)
        metadata = flavor_params.get('metadata')
        flavor_steps.set_metadata(flavor, metadata)
        return flavo
    else:
        flavor_params = dict(ram=512, vcpus=1, disk=2, is_public=True)
        flavor_name, = utils.generate_ids('flavor')
        return create_flavor(flavor_name, **flavor_params)
