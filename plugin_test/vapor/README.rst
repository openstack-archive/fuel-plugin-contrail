Vapor
=====

Open Stack Contrail plugin test suite

Requirements
------------

It's strongly advised to use virtualenv and update pip, tox, virtualenv and setuptools.

.. code-block:: bash

    virtualenv venv
    . venv/bin/activate
    pip install -U pip tox virtualenv setuptools


Run tests
---------

.. code:: bash

    >> tox


Use Docker for run tests
------------------------

Build image

.. code-block:: bash
    docker build -t vapor-image .

Fill env file

.. code-block:: bash
    cat << EOF > env_file
    OS_USERNAME=admin
    OS_PASSWORD=admin
    OS_TENANT_NAME=admin
    OS_AUTH_URL=http://10.109.1.7:5000/v3

    # os-faults config
    OS_FAULTS_CLOUD_DRIVER=fuel
    OS_FAULTS_CLOUD_DRIVER_ADDRESS=10.109.0.2
    OS_FAULTS_CLOUD_DRIVER_KEYFILE=/opt/app/cloud.key
    OS_FAULTS_CLOUD_DRIVER_USERNAME=root

    CONTRAIL_ROLES_DISTRIBUTION_YAML=/opt/app/roles_distribution.yaml
    EOF

Set path to files

.. code-block:: bash
    PRIVATE_KEY=/path/to/cloud/private/key
    ROLES_DISTRIBUTION=/path/to/contrail/roles/distribution.yaml


Run tests

.. code-block:: bash
    docker run --net=host --rm -it \
        --env-file=env_file \
        -v $(pwd)/reports:/opt/app/test_reports \
        -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \
        -v ${PRIVATE_KEY}:/opt/app/cloud.key \
        -v ${ROLES_DISTRIBUTION}:/opt/app/roles_distribution.yaml \
        vapor-image

Results will be written to $(pwd)/reports folder

Run only some tests (look tests under vapor directory, filter by "smoke" in test/class/path, exit after first fail)

.. code-block:: bash
    docker run --net=host --rm -it \
        --env-file=env_file \
        -v $(pwd)/reports:/opt/app/test_reports \
        -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \
        -v ${PRIVATE_KEY}:/opt/app/cloud.key \
        -v ${ROLES_DISTRIBUTION}:/opt/app/roles_distribution.yaml \
        vapor-image vapor -k smoke -x

Use Docker for developing tests
-------------------------------

Build image (only for dependencies)

.. code-block:: bash
    docker build -t vapor-image .

Go to tests directory

.. code-block:: bash
    cd /path/to/repository


Copy private key and contrail roles files to current directory

.. code-block:: bash
    PRIVATE_KEY=cloud.key
    ROLES_DISTRIBUTION=roles.yaml
    cp /path/to/cloud/private/key $PRIVATE_KEY
    cp /path/to/contrail/roles/distribution.yaml $ROLES_DISTRIBUTION


Fill env file

.. code-block:: bash
    cat << EOF > env_file
    OS_USERNAME=admin
    OS_PASSWORD=admin
    OS_TENANT_NAME=admin
    OS_AUTH_URL=http://10.109.1.7:5000/v3

    # os-faults config
    OS_FAULTS_CLOUD_DRIVER=fuel
    OS_FAULTS_CLOUD_DRIVER_ADDRESS=10.109.0.2
    OS_FAULTS_CLOUD_DRIVER_KEYFILE=/opt/app/$PRIVATE_KEY
    OS_FAULTS_CLOUD_DRIVER_USERNAME=root

    CONTRAIL_ROLES_DISTRIBUTION_YAML=/opt/app/$ROLES_DISTRIBUTION
    EOF

Make any changes in current directory and run tests with changes

.. code-block:: bash
    docker run --net=host --rm -it \
        --env-file=env_file \
        -v $(pwd):/opt/app/ \
        -v /var/run/libvirt/libvirt-sock:/var/run/libvirt/libvirt-sock \
        vapor-image vapor -k test_smoke --pdb
