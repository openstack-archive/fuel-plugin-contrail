# A helper to run fabric
define contrail::run_fabric (
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