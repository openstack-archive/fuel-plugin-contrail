case $operatingsystem
{
    CentOS:
      {
        yumrepo {'mos': priority => 1}
        package {'yum-plugin-priorities': ensure => present }
      }
}
