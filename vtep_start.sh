#!/usr/bin/env bash
 
while getopts ":m:i:p:d:" opt; do
  case $opt in
    m)
      echo "Running in $OPTARG mode" >&2
      MODE=$OPTARG
      ;;
    i)
      HAPROXY_IP=$OPTARG
      ;;
    p)
      HAPROXY_PORT=$OPTARG
      ;;
    :)
      echo "Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

if [[ -z $MODE ]]; then
  echo "You need to specify mode with -m" >&2
fi

if [[ $MODE != 'pssl' && $MODE != 'tcp' ]]; then
  echo "You need to provide 'pssl' or 'tcp' with -m argument"
fi

if [[ $MODE = "pssl" ]]; then
  if [[ -z $HAPROXY_IP || -z $HAPROXY_PORT ]] ; then
    echo "In pssl mode:" >&2
    echo "Haproxy ip needs to be provided with -p option" >&2
    echo "Haproxy port needs to be provided with -p option" >&2
    exit 1
  else
    COMMAND="ssl:${HAPROXY_IP}:${HAPROXY_PORT}"
    CERTS_PATH='-p /var/db/certs/vtep_1-privkey.pem -c /var/db/certs/vtep_1-cert.pem -C /var/db/certs/cacert.pem'
  fi
else
  COMMAND='ptcp:6632'
fi

rm /etc/openvswitch/*.db
ovsdb-tool create /etc/openvswitch/ovs.db /usr/share/openvswitch/vswitch.ovsschema ; ovsdb-tool create /etc/openvswitch/vtep.db /usr/share/openvswitch/vtep.ovsschema
service openvswitch-switch stop
ovsdb-server --pidfile --detach --log-file --remote punix:/var/run/openvswitch/db.sock --remote=db:hardware_vtep,Global,managers --remote $COMMAND $CERTS_PATH /etc/openvswitch/ovs.db /etc/openvswitch/vtep.db
ovs-vswitchd --log-file --detach --pidfile unix:/var/run/openvswitch/db.sock 
ovsdb-client list-dbs unix:/var/run/openvswitch/db.sock
ovs-vsctl add-br TOR1
vtep-ctl add-ps TOR1
vtep-ctl set Physical_Switch TOR1 tunnel_ips=10.109.4.229
python /usr/share/openvswitch/scripts/ovs-vtep --log-file=/var/log/openvswitch/ovs-vtep.log --pidfile=/var/run/openvswitch/ovs-vtep.pid --detach TOR1
ip netns add ns1
ip link add nstap1 type veth peer name tortap1
ovs-vsctl add-port TOR1 tortap1
ip link set nstap1 netns ns1
ip netns exec ns1 ip link set dev nstap1 up
ip link set dev tortap1 up
ip netns exec ns1 ip link set nstap1 address 00:01:00:00:05:78

