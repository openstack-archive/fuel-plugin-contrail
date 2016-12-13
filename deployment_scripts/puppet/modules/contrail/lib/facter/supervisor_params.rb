#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

# This facter returns the version and build for the python-contrail package.
# It may be used to detect a version of contrail used in the environment.

require 'hiera'
require 'puppet'
require 'puppet/util/inifile'

Facter.add("supervisor_params") do
  setcode do
    res = []
    vrouter_config  = '/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini'
    vrouter_section = 'program:contrail-vrouter-dpdk'
    mac_from_config = nil
    if File.exist?(vrouter_config)
      file  = Puppet::Util::IniConfig::PhysicalFile.new(vrouter_config)
      file.read
      config_vrouter_params = file.get_section(vrouter_section)['command'].split('--no-daemon')[-1].strip
      mac_from_config = config_vrouter_params.split.find { |param| param.include?('mac') }
      mac_from_config = mac_from_config.split(',').find { |param| param.include?('mac') }.split('=')
    end
    status = `status supervisor-vrouter 2>/dev/null`
    if $?.exitstatus and status.include?('stop/waiting')
      # NOTE (dukov) We do not need to gather data from system in case vrouter has started
      # Moreover these data may differ from data without vrouter service started
      bond_policy_map = {
        'layer2'   => 'l2',
        'layer3+4' => 'l34',
        'layer2+3' => 'l23',
        'encap2+3' => 'l23',
        'encap3+4' => 'l34',
      }
      hiera = Hiera.new(:config => '/etc/hiera.yaml')
      network_scheme = hiera.lookup('network_scheme', {}, {}, nil, :hash)

      phys_dev = vlan = ''
      network_scheme['transformations'].each do |trans|
        if trans['bridge'] == network_scheme['roles']['neutron/mesh']
          phys_dev, vlan = trans['name'].split('.')
          break
        end
      end

      bond_dir = "/sys/class/net/#{phys_dev}/bonding"
      add_vdev = false
      if File.exist?(bond_dir)
        # NOTE(dukov) This chunk of code will return a Hash with bond slaves info
        # Example
        #   {
        #    "enp67s0f1"=> {
        #      "numa_node"=>"1",
        #      "slave_pci"=>"0000:43:00.1"},
        #    "enp68s0f1"=> {
        #      "numa_node"=>"1",
        #      "slave_pci"=>"0000:44:00.1"}
        #   }
        bond_slaves = Hash[`cat #{bond_dir}/slaves`.split.sort.collect do |slave|
          slave_pci = `basename $(readlink /sys/class/net/#{slave}/device)`.chomp
          numa_node = `cat /sys/class/net/#{slave}/device/numa_node`.chomp
          [slave, {'numa_node' => numa_node == '-1' ? 0 : numa_node, 'slave_pci' => slave_pci}]
        end]

        add_vdev = !bond_slaves.values[-1]['numa_node'].empty?
      end

      # vdev
      if add_vdev
        res << '--vdev'
        vdev_values = []
        vdev_values << "eth_bond_#{phys_dev}"
        vdev_values << "mode=#{`cat #{bond_dir}/mode`.split()[1]}"

        bond_policy = `cat #{bond_dir}/xmit_hash_policy`.split()[0]
        vdev_values << "xmit_policy=#{bond_policy_map[bond_policy]}"
        vdev_values << "socket_id=#{bond_slaves.values[-1]['numa_node']}"

        # NOTE(dukov) we should not change mac here to avoid vrouter restart
        # which is why we need to grab this from Supervisor config
        mac = !!mac_from_config ? mac_from_config[1] : `cat /sys/class/net/#{bond_slaves.keys[-1]}/address`.chomp

        vdev_values << "mac=#{mac}"
        vdev_values << bond_slaves.values.map {|slave_info| "slave=#{slave_info['slave_pci']}"}.join(',')
        res << "\"#{vdev_values.join(',')}\""
      end

      # vlan_tci and vlan_fwd_intf_name
      if !!vlan
        res << "--vlan_tci \"#{vlan}\""
        res << "--vlan_fwd_intf_name \"#{phys_dev}\""
      end

      # socket-mem
      socket_mem = Dir["/sys/devices/system/node/node*/hugepages"].map{ |pages| 1024}.join(',')
      res << "--socket-mem #{socket_mem}" unless socket_mem.empty?
    else
      # NOTE(dukov) Let's get data from Supervisor configfile
      res << config_vrouter_params
    end

    res.join(' ')
  end
end
