class contrail::setup (
  $node_name
  ) {

  define run_fabric (
    $hostgroup = undef,
    $taskname = $name,
    $command = undef,
  ) {
    Exec {
      cwd => '/opt/contrail/utils',
      path => '/bin:/usr/bin:/usr/local/bin',
      logoutput => 'on_failure',
    }
    case $hostgroup {
      control: {
        exec { "Run-fabric-command-on-${hostgroup}":
          command => "fab -P -R ${hostgroup} -- '${command}'",
        }
      }
      default: {
        exec { "Run-local-fabric-task-${taskname}":
          command => "fab ${taskname}",
        }
      }
    }
  }

  case $node_name {
    contrail-1: {
      run_fabric { 'install database':
        hostgroup => 'control',
      } ->
      run_fabric { 'setup_database':
        hostgroup => 'control',
      }

    }
  }

}