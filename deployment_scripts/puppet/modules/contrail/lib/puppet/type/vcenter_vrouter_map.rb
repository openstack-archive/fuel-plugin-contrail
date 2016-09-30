require 'puppet/parameter/boolean'

Puppet::Type.newtype(:vcenter_vrouter_map) do

  ensurable do
    defaultvalues
    defaultto :present
  end

  newparam(:path) do
    desc 'Path to a file to store the Vcenter map'
    isnamevar
  end

  newparam(:username) do
    desc 'The Vcenter login username'
    defaultto do
      fail 'Vcenter username is required!'
    end
  end

  newparam(:password) do
    desc 'The Vcenter login password'
    defaultto do
      fail 'Vcenter password is required!'
    end
  end

  newparam(:vcenter_host) do
    desc 'The ip or host name of the Vcenter node'
    defaultto do
      fail 'Vcenter host is required!'
    end
  end

  newparam(:retry_count) do
    desc 'The number of retries'
    defaultto 10
    munge do |value|
      value.to_i
    end
  end

  newparam(:retry_sleep) do
    desc 'The sleep time between retries'
    defaultto 60
    munge do |value|
      value.to_i
    end
  end

  newparam(:ips, :array_matching => :all) do
    desc 'The list of VM ip addresses that should be added to the map'
    defaultto do
      fail 'List of the Contrail VM ips should not be empty!'
    end
  end

  newparam(:yaml, :boolean => true, :parent => Puppet::Parameter::Boolean) do
    desc 'Enable the YAML output format'
    defaultto false
  end

  newparam(:dvs, :boolean => true, :parent => Puppet::Parameter::Boolean) do
    desc 'Get DVS mappings YAML-format output'
    defaultto false
  end

end
