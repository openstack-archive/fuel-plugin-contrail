Puppet::Type.newtype(:wait_for_cassandra_keyspace) do
  desc "Wait for tables in a specific keyspace"

  newproperty(:ensure) do
    desc "Expected keyspace status"
    newvalues :present, :absent, :ready
  end

  newparam(:name) do
    desc "The name of keyspace"
    isnamevar
  end

  newparam(:tables) do
    desc "A list of tables which should be in keyspace"
    defaultto []
  end

  newparam(:host) do
    desc "A list of tables which should be in keyspace"

    validate do |host|
      fail "Host attrbitue shouldn't be empty string" if host.empty?
    end
  end

  newparam(:count) do
    desc 'How many times try to perform check?'
    newvalues(/\d+/)
    defaultto 10
    munge do |n|
      n.to_i
    end
  end

  newparam(:step) do
    desc 'How many seconds to wait between retries?'
    newvalues(/\d+/)
    defaultto 60
    munge do |n|
      n.to_i
    end
  end

  newparam(:timeout) do
    desc 'How long should we wait for a request to finish?'
    newvalues(/\d+/)
    defaultto 30
    munge do |n|
      n.to_i
    end
  end
end
