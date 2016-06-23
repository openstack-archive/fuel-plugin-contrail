Puppet::Type.type(:contrail_vrouter_dpdk_ini_config).provide(
  :ini_setting,
  :parent => Puppet::Type.type(:ini_setting).provider(:ruby)
) do

  def section
    resource[:name].split('/', 2).first
  end

  def setting
    resource[:name].split('/', 2).last
  end

  def separator
    '='
  end

  def self.file_path
    '/etc/contrail/supervisord_vrouter_files/contrail-vrouter-dpdk.ini'
  end

end