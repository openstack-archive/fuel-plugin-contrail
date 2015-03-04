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
    $contrail::deployment_node: {
      #Database installation
      run_fabric { 'install_database': } ->
      run_fabric { 'setup_database': } ->
      notify{"Waiting for cassandra nodes: ${contrail::contrail_node_num}":} ->
      exec {'wait_for_cassandra':
        provider  => "shell",
        command   => "if [ `/usr/bin/nodetool status|grep ^UN|wc -l` -lt ${contrail::contrail_node_num} ]; then exit 1; fi",
        tries     => 10, # wait for whole cluster is up: 10 tries every 30 seconds = 5 min
        try_sleep => 30
      } -> 
      run_fabric { 'install_cfgm': } ->
      run_fabric { 'install_control': } ->
      run_fabric { 'install_collector': } ->
      run_fabric { 'install_webui': } ->
      #Some fixups
      run_fabric { 'setup_contrail_keepalived': } ->
      run_fabric { 'fixup_restart_haproxy_in_collector': } ->
      run_fabric { 'fix-service-tenant-name':
        hostgroup => 'control',
        command   => "sed -i '49s/service/services/g' /usr/local/lib/python2.7/dist-packages/contrail_provisioning/config/quantum_in_keystone_setup.py",
      } ->
      #Setting up the components
      run_fabric { 'setup_cfgm': } ->
      run_fabric { 'setup_control': } ->
      run_fabric { 'setup_collector': } ->
      run_fabric { 'setup_webui': }
    }
  }

}
