class contrail::testbed {
  file {'/opt/contrail/utils/fabfile/testbeds/testbed.py':
    ensure => present,
    content => template("contrail/testbed.py.erb")
  }
}
