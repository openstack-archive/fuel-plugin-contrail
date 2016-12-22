require 'timeout'

Puppet::Type.type(:wait_for_cassandra_keyspace).provide(:cqlsh) do
  desc "Wait for keyspace using cqlsh command"

  commands :cqlsh => 'cqlsh'

  def ensure
    pull_database_stats(resource[:name])

    if not @state[:keyspaces].include?(resource[:name])
      debug "State: absent"
      :absent
    else
      if @state[:keyspaces].include?(resource[:name]) and @resource[:tables] and include_all?(@resource[:tables], @state[:tables])
        debug "State: ready"
        :ready
      else
        debug "State: present"
        :present
      end
    end
  end

  def exists?
    true
  end

  def ensure=(value)
    debug "Start waiting/checking"

    @resource[:count].times do
      pull_database_stats(resource[:name])

      return true if resource_ready(value)

      debug "Sleep for #{@resource[:step]} seconds"
      sleep @resource[:step]
    end
  end

  # Private API

  #
  # Returns true if expected value matches actual
  #
  def resource_ready(value)
    case value
    when :absent
      not @state[:keyspaces].include?(resource[:name])
    when :present
      @state[:keyspaces].include?(resource[:name])
    when :ready
      @state[:keyspaces].include?(resource[:name]) and @resource[:tables] and include_all?(@resource[:tables], @state[:tables])
    end
  end

  def pull_database_stats(keyspace)
    @state = {
      :keyspaces => pull_keyspaces,
      :tables => pull_tables(keyspace)
    }
  end

  def cqlsh_client(args)
    Timeout::timeout(resource[:timeout]) do
      raw = cqlsh(args)
      debug("Raw response from cqlsh: #{raw.inspect}")
      raw.split.map { |el| if el =~ /^"([^"]+)"$/ then $1 else el end }
    end
  rescue Puppet::ExecutionFailure => e
    fail "Error: #{e.message}"
  end

  def pull_keyspaces
    cqlsh_client([@resource[:host], '-e', 'DESCRIBE KEYSPACES'])
  end

  def pull_tables(keyspace)
    cqlsh_client([@resource[:host], '-k', keyspace, '-e', 'DESCRIBE TABLES'])
  end

  def include_all?(_self, target)
    (_self & target).count == _self.count
  end
end
