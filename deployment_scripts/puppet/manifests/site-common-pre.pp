include contrail

case $operatingsystem {
  'CentOS': {
    package {'yum-plugin-priorities': ensure => present }
    ## Do not change priority on non-contrail "base-os" hosts
    case $contrail::node_role {
      'base-os': {
        if $contrail::node_name =~ /^contrail.\d+$/ {
          # Contrail requires newer python-thrift and nodejs from it's repo
          yumrepo {'mos': priority => 1, exclude => 'python-thrift,nodejs'}
        }
      }
      default: {
        yumrepo {'mos': priority => 1}
      }
    }
  }
  'Ubuntu': {
    case $contrail::node_role {
      'base-os','compute': {
        file { '/etc/apt/preferences.d/contrail-pin-100':
          ensure => file,
          source => 'puppet:///modules/contrail/contrail-pin-100',
        }
      }
    }
  }
}