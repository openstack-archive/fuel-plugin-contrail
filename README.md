Mirantis Fuel Contrail plugin
=============================

Compatible versions:

- Mirantis Fuel 7.0
- Juniper Contrail 3.0.2

How to build plugin:

- Install fuel plugin builder (fpb)
- Clone plugin repo and run fpb there:

    git clone https://github.com/openstack/fuel-plugin-contrail

    cd fuel-plugin-contrail/

    fpb --build .

- Check if file contrail-3.0-3.0.1-1.noarch.rpm was created.
