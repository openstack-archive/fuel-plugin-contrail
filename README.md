Mirantis Fuel Contrail plugin
=============================

Compatible versions:

- Mirantis Fuel 9.2
- Juniper Contrail 3.1.0.0

How to build plugin:

- Install fuel plugin builder (fpb)
- Clone plugin repo and run fpb there:

    git clone https://github.com/openstack/fuel-plugin-contrail

    cd fuel-plugin-contrail/

    fpb --build .

- Check if file contrail-5.0-5.0.1-1.noarch.rpm was created.
