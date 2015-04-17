case $operatingsystem
{
    CentOS:
      {
        yumrepo {'mos': priority => 1, exclude => 'python-thrift,nodejs'} # Contrail requires newer python-thrift and nodejs from it's repo
        package {'yum-plugin-priorities': ensure => present }
      }
}
