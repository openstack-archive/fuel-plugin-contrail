require 'hiera'
require 'ipaddress'

#This fact is designed to return sticky MAC address for use on dpdk computes.
#The main idea that we generate hardware address from IP if bond is used for dpdk purposes.
#If dpdk interface is pure NIC - trying to get real NIC MAC and in case of fail - generate new.
Facter.add("dpdk_mac_address") do

  #Generate static MAC address from IP
  #172.29.154.113 -> 00:11:AC:1D:9A:71
  def mac_from_ip(ip)
    prefix='00:11:'
    ip_arr=ip.split('.')
    out=sprintf('%.2x:%.2x:%.2x:%.2x',ip_arr[0], ip_arr[1], ip_arr[2], ip_arr[3])
    prefix+out
  end

  def get_mac_for(iface)
    hmac=''
    #If NIC is still available in system read MAC from it
    if File.exist? "/sys/class/net/#{iface}/address"
      hmac=File.read("/sys/class/net/#{iface}/address")
      return hmac.chomp!
    end
    #If dpdk load interface, trying udev saved file
    if File.exist? "/etc/udev/rules.d/70-persistent-net.rules"
      File.foreach('/etc/udev/rules.d/70-persistent-net.rules') do |line, line_num|
        h=Hash.new
        if "#{line}".start_with?('SUBSYSTEM')
          line.gsub!(/\s/,'').gsub!(/==/, '=').split(',').each do |l|
            key, value = l.gsub('"','').split('=')
            h[key]=value
          end
          if h.has_key?('NAME') and h['NAME']==iface
            hmac=h.fetch('ATTR{address}', '')
            break
          end
        end
      end
    end
    hmac
  end

  setcode do
    mac = ''
    hiera = Hiera.new(:config => '/etc/hiera.yaml')
    network_scheme = hiera.lookup('network_scheme', {}, {}, nil, :hash)
    roles = hiera.lookup('roles', [], {}, nil, :array)

    #We need this fact only for dpdk computes
    if !roles.include? 'dpdk'
      break
    end

    phys_dev = ''
    network_scheme['transformations'].each do |trans|
      if trans['bridge'] == network_scheme['roles']['neutron/mesh']
        phys_dev = trans['name'].split('.')[0]
        break
      end
    end

    priv_ip = network_scheme['endpoints']['br-fw-admin']['IP'][0].split('/')[0]
    if !IPAddress.valid? priv_ip
      break
    end
    generated_mac=mac_from_ip(priv_ip)

    #For bonds we just generate static MAC
    if phys_dev.include? 'bond'
      mac=generated_mac
    #True hardware NIC
    else
      mac=get_mac_for(phys_dev)
      if mac.empty?
        mac=generated_mac
      end
    end
    mac
  end

end
