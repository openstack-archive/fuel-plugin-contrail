class contrail::ssh ( $password_auth = 'yes',$root_login = 'yes' ) {
  exec { 'Update-PasswordAuthentication':
    path    => '/bin:/usr/bin',
    command => "sed -i -e 's/^PasswordAuthentication.*/PasswordAuthentication ${password_auth}/g' /etc/ssh/sshd_config",
    notify  => Service['ssh']
  }
  exec { 'Update-PermitRootLogin':
    path    => '/bin:/usr/bin',
    command => "sed -i -e 's/^PermitRootLogin.*/PermitRootLogin ${root_login}/g' /etc/ssh/sshd_config",
    notify  => Service['ssh']
  }
  service { 'ssh':
    ensure    => running,
  }
}
