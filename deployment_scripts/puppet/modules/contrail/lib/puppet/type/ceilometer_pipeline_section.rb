Puppet::Type.newtype(:ceilometer_pipeline_section) do
  ensurable do
    defaultvalues
    defaultto :present
  end

  newparam(:name) do
    desc 'The unique name of the resource'
    isnamevar
  end

  newparam(:path) do
    validate do |value|
      fail 'The path should be absolute!' unless Puppet::Util.absolute_path? value
    end
  end

  newparam(:array_name) do
    desc 'The name of the array to search section in'
    defaultto { 'sources' }
  end

  newparam(:section_name) do
    desc 'The name of the section to update'
    defaultto { 'contrail_source' }
  end

  newparam(:data) do
    desc 'Directly pass the section structure'
    validate do |value|
      fail 'The data structure should be a hash!' unless value.is_a? Hash
    end
  end

end
