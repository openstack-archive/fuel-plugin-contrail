include contrail
if $contrail::node_name =~ /^contrail.\d+$/ {
  class { 'contrail::ssh':
    password_auth => 'no',
    root_login    => 'without-password'
  }
}
