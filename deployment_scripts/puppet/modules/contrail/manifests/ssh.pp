class contrail::ssh ( $password_auth = 'yes' ) {
  exec { 'Update-sshd-config':
    path    => '/bin:/usr/bin',
    command => "sed -i -e 's/^PasswordAuthentication.*/PasswordAuthentication ${password_auth}/g' /etc/ssh/sshd_config",
  }
  service { 'ssh':
    ensure    => running,
    subscribe => Exec['Update-sshd-config'],
  }
}