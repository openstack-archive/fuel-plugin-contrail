require 'puppetlabs_spec_helper/module_spec_helper'
require 'puppet'

RSpec.configure do |config|
  config.mock_framework = :rspec
end

def puppet_debug_override
  return unless ENV['SPEC_PUPPET_DEBUG']
  Puppet::Util::Log.level = :debug
  Puppet::Util::Log.newdestination(:console)
end
