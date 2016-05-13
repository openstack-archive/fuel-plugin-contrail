#!/bin/sh
PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

# Defaults
export REBOOT_TIMEOUT=${REBOOT_TIMEOUT:-5000}
export ALWAYS_CREATE_DIAGNOSTIC_SNAPSHOT=${ALWAYS_CREATE_DIAGNOSTIC_SNAPSHOT:-true}

<<<<<<< HEAD
# Export specified settings
if [ -z "$NODE_VOLUME_SIZE" ]; then export NODE_VOLUME_SIZE=350; fi
if [ -z "$OPENSTACK_RELEASE" ]; then export OPENSTACK_RELEASE=Ubuntu; fi
if [ -z "$ENV_NAME" ]; then export ENV_NAME="contrail"; fi
if [ -z "$ADMIN_NODE_MEMORY" ]; then export ADMIN_NODE_MEMORY=4096; fi
if [ -z "$ADMIN_NODE_CPU" ]; then export ADMIN_NODE_CPU=4; fi
if [ -z "$SLAVE_NODE_MEMORY" ]; then export SLAVE_NODE_MEMORY=4096; fi
if [ -z "$SLAVE_NODE_CPU" ]; then export SLAVE_NODE_CPU=4; fi

# Init and update submodule
git submodule update --init --recursive --remote
=======
>>>>>>> 95f59e6... The script for test run was updated

sudo /sbin/iptables -F
sudo /sbin/iptables -t nat -F
sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

ShowHelp() {
cat << EOF
System Tests Script

It can perform several actions depending on Jenkins JOB_NAME it's ran from
or it can take names from exported environment variables or command line options
if you do need to override them.

-w (dir)    - Path to workspace where fuelweb git repository was checked out.
              Uses Jenkins' WORKSPACE if not set
-e (name)   - Directly specify environment name used in tests
              Uses ENV_NAME variable is set.
-j (name)   - Name of this job. Determines ISO name, Task name and used by tests.
              Uses Jenkins' JOB_NAME if not set
-v          - Do not use virtual environment
-V (dir)    - Path to python virtual environment
-i (file)   - Full path to ISO file to build or use for tests.
              Made from iso dir and name if not set.
-o (str)    - Allows you any extra command line option to run test job if you
              want to use some parameters.
-a (str)    - Allows you to path NOSE_ATTR to the test job if you want
              to use some parameters.
-A (str)    - Allows you to path  NOSE_EVAL_ATTR if you want to enter attributes
              as python expressions.
-l (dir)    - Path to logs directory. Can be set by LOGS_DIR evironment variable.
              Uses WORKSPACE/logs if not set.
-k          - Keep previously created test environment before tests run
-K          - Keep test environment after tests are finished
-h          - Show this help page

Most variables uses guesing from Jenkins' job name but can be overriden
by exported variable before script is run or by one of command line options.

You can override following variables using export VARNAME="value" before running this script
WORKSPACE  - path to directory where Fuelweb repository was checked out by Jenkins or manually
JOB_NAME   - name of Jenkins job that determines which task should be done and ISO file name.
EOF
}

GetoptsVariables() {
  while getopts ":w:j:i:o:a:A:V:l:kKe:v:h" opt; do
    case $opt in
      w)
        WORKSPACE="${OPTARG}"
        ;;
      j)
        JOB_NAME="${OPTARG}"
        ;;
      i)
        ISO_PATH="${OPTARG}"
        ;;
      o)
        TEST_OPTIONS="${TEST_OPTIONS} ${OPTARG}"
        ;;
      a)
        NOSE_ATTR="${OPTARG}"
        ;;
      A)
        NOSE_EVAL_ATTR="${OPTARG}"
        ;;
      V)
        VENV_PATH="${OPTARG}"
        ;;
      l)
        LOGS_DIR="${OPTARG}"
        ;;
      k)
        KEEP_BEFORE="yes"
        ;;
      K)
        KEEP_AFTER="yes"
        ;;
      e)
        ENV_NAME="${OPTARG}"
        ;;
      v)
        VENV="no"
        ;;
      h)
        ShowHelp
        exit 0
        ;;
      \?)
        echo "Invalid option: -$OPTARG"
        ShowHelp
        exit $INVALIDOPTS_ERR
        ;;
      :)
        echo "Option -$OPTARG requires an argument."
        ShowHelp
        exit $INVALIDOPTS_ERR
        ;;
    esac
  done
}

CheckVariables() {

  # Common settings
  [ -z "${JOB_NAME}"  ] && { echo "Error! JOB_NAME is not set!" ; exit 1;  }
  [ -z "${ISO_PATH}"  ] && { echo "Error! ISO_PATH is not set!" ; exit 1;  }
  [ -z "${ENV_NAME}"  ] && { echo "Error! ENV_NAME is not set!" ; exit 1;  }
  [ -z "${WORKSPACE}" ] && { echo "Error! WORKSPACE is not set!"; exit 1;  }
  [ -z "${VENV_PATH}" ] && { echo "Error! virtualenv is not set!"; exit 1; }
  [ -z "${LOGS_DIR}"  ] && LOGS_DIR="${WORKSPACE}/logs" 

  # Fuel envronment settings
  [ -z $NODE_VOLUME_SIZE  ] &&  export NODE_VOLUME_SIZE=350
  [ -z $OPENSTACK_RELEASE ] &&  export OPENSTACK_RELEASE=Ubuntu
  [ -z $ENV_NAME          ] &&  export ENV_NAME="contrail"
  [ -z $ADMIN_NODE_MEMORY ] &&  export ADMIN_NODE_MEMORY=4096
  [ -z $ADMIN_NODE_CPU    ] &&  export ADMIN_NODE_CPU=4
  [ -z $SLAVE_NODE_MEMORY ] &&  export SLAVE_NODE_MEMORY=4096
  [ -z $SLAVE_NODE_CPU    ] &&  export SLAVE_NODE_CPU=4
  
  # vSphere settings
  [ -z "${VCENTER_USERNAME}"   ] && { echo "Error! VCENTER_USERNAME is not set!"; exit 1; }
  [ -z "${VCENTER_PASSWORD}"   ] && { echo "Error! VCENTER_PASSWORD is not set!"; exit 1; }
  [ -z "${VCENTER_USE}"        ] && export VCENTER_USE="true"  
  [ -z "${VCENTER_IP}"         ] && export VCENTER_IP="172.16.0.254"
  [ -z "${VCENTER_DATACENTER}" ] && export VC_DATACENTER="Datacenter"
  [ -z "${VCENTER_DATASTORE}"  ] && export VC_DATASTORE="nfs"
  [ -z "${VCENTER_CLUSTERS}"   ] && export VCENTER_CLUSTERS="Cluster1,Cluster2"

  # Workstation settings
  [ -z "${WORKSTATION_USERNAME}" ] && { echo "Error! WORKSTATION_USERNAME is not set!"; exit 1; }
  [ -z "${WORKSTATION_PASSWORD}" ] && { echo "Error! WORKSTATION_PASSWORD is not set!"; exit 1; }
  [ -z "${WORKSTATION_NODES}"    ] && export WORKSTATION_NODES="esxi1 esxi2 esxi3 vcenter trusty"
  [ -z "${WORKSTATION_IFS}"      ] && export WORKSTATION_IFS="vmnet1 vmnet2"
  [ -z "${WORKSTATION_SNAPSHOT}" ] && export WORKSTATION_SNAPSHOT="contrail"
  [ -z "${WORKSTATION_TIMEOUT}"  ] && export WORKSTATION_TIMEOUT=1 

  [ -z "${WORKSTATION_PUBLIC_GATEWAY}" ] && export WORKSTATION_PUBLIC_GATEWAY="172.16.0.1/24"
  [ -z "${NET_CREATION_TIMEOUT}" ] && export NET_CREATION_TIMEOUT=5
  
}

RunTest() {
    [ ! -f "${LOGS_DIR}"  ] &&  mkdir -p $LOGS_DIR

    [ "${VENV}" == "yes" ] && . $VENV_PATH/bin/activate

    if [ "${KEEP_BEFORE}" != "yes" ]; then
      [ $(dos.py list | grep "^${ENV_NAME}\$") ] &&  dos.py erase "${ENV_NAME}"
    fi

    # gather additional option for this nose test run
    OPTS=""
    if [ -n "${NOSE_ATTR}" ]; then
        OPTS="${OPTS} -a ${NOSE_ATTR}"
    fi
    if [ -n "${NOSE_EVAL_ATTR}" ]; then
        OPTS="${OPTS} -A ${NOSE_EVAL_ATTR}"
    fi
    if [ -n "${TEST_OPTIONS}" ]; then
        OPTS="${OPTS} ${TEST_OPTIONS}"
    fi

    clean_old_bridges

    export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${WORKSPACE}"
    echo ${PYTHONPATH}
    python plugin_test/run_tests.py -q --nologcapture --with-xunit ${OPTS} &

    SYSTEST_PID=$!

<<<<<<< HEAD
  if [ "${DRY_RUN}" = "yes" ]; then
    ISO="${WORKSPACE}/build/iso/fuel.iso"
  else
    ISO="$(find "${WORKSPACE}/build/iso/"*".iso" | head -n 1)"
    # check that ISO file exists
    if [ ! -f "${ISO}" ]; then
      echo "Error! ISO file not found!"
      exit $NOISOFOUND_ERR
=======
    if ! ps -p $SYSTEST_PID > /dev/null
    then
      echo "System tests exited prematurely, aborting"
      exit 1
>>>>>>> 95f59e6... The script for test run was updated
    fi

    # Waiting for fuel-env's networks creation
    while [ $(virsh net-list | grep $ENV_NAME | wc -l) -ne 5 ]; do
      sleep $NET_CREATION_TIMEOUT
      if ! ps -p $SYSTEST_PID > /dev/null
      then
        echo System tests exited prematurely, aborting
        exit 1
      fi
    done
    sleep $NET_CREATION_TIMEOUT

    # Configre vcenter nodes and interfaces
    setup_net $ENV_NAME
    clean_iptables
    revert_ws "$WORKSTATION_NODES" || { echo "killing $SYSTEST_PID and its childs" && pkill --parent $SYSTEST_PID && kill $SYSTEST_PID && exit 1; }

    #fixme should use only one clean_iptables call
    clean_iptables

    echo waiting for system tests to finish
    wait $SYSTEST_PID

    export RES=$?
    echo ENVIRONMENT NAME is $ENV_NAME
    virsh net-dumpxml ${ENV_NAME}_admin | grep -P "(\d+\.){3}" -o | awk '{print "Fuel master node IP: "$0"2"}'

    echo Result is $RES

    [ "${KEEP_AFTER}" != "yes" ] && dos.py destroy "${ENV_NAME}"

    exit "${RES}"
}

<<<<<<< HEAD
RunTest() {
    # Run test selected by task name

    # check if iso file exists
    if [ ! -f "${ISO_PATH}" ]; then
        if [ -z "${ISO_URL}" -a "${DRY_RUN}" != "yes" ]; then
            echo "Error! File ${ISO_PATH} not found and no ISO_URL (-U key) for downloading!"
            exit $NOISOFOUND_ERR
        else
            if [ "${DRY_RUN}" = "yes" ]; then
                echo wget -c "${ISO_URL}" -O "${ISO_PATH}"
            else
                echo "No ${ISO_PATH} found. Trying to download file."
                wget -c "${ISO_URL}" -O "${ISO_PATH}"
                rc=$?
                if [ $rc -ne 0 ]; then
                    echo "Failed to fetch ISO from ${ISO_URL}"
                    exit $ISODOWNLOAD_ERR
                fi
            fi
        fi
    fi
=======
#Define functions for VCenter configuration
add_interface_to_bridge() {
  env=$1
  net_name=$2
  nic=$3
  ip=$4
>>>>>>> 95f59e6... The script for test run was updated

  for net in $(virsh net-list | grep ${env}_${net_name} | awk '{print $1}'); do
    bridge=$(virsh net-info $net | grep -i bridge | awk '{print $2}')
    setup_bridge $bridge $nic $ip && echo $net_name bridge $bridge ready
  done
}

setup_bridge() {
  bridge=$1
  nic=$2
  ip=$3

  sudo /sbin/brctl stp $bridge off
  sudo /sbin/brctl addif $bridge $nic
  if [ ! -z "${ip}" ]; then
    #set if with existing ip down
    for itf in $(sudo ip -o addr show to $ip | cut -d' ' -f2); do
        echo deleting $ip from $itf
        sudo ip addr del dev $itf $ip
    done
    echo "adding $ip to $bridge"
    sudo /sbin/ip addr add $ip dev $bridge
    echo "$nic added to $bridge"
  fi

  sudo /sbin/ip link set dev $bridge up
  if sudo /sbin/iptables-save |grep $bridge | grep -i reject| grep -q FORWARD;then
    sudo /sbin/iptables -D FORWARD -o $bridge -j REJECT --reject-with icmp-port-unreachable
    sudo /sbin/iptables -D FORWARD -i $bridge -j REJECT --reject-with icmp-port-unreachable
  fi
}

clean_old_bridges() {
  bridge_info=$(/sbin/brctl show | grep -v "bridge name" | cut -f1 -d'	')
  for intf in $WORKSTATION_IFS; do
    for br in $bridge_info ; do
      /sbin/brctl show $br| grep -q $intf && sudo /sbin/brctl delif $br $intf \
        && sudo /sbin/ip link set dev $br down && echo $intf deleted from $br
    done
  done
}

<<<<<<< HEAD
    if [ ! -f "$LOGS_DIR" ]; then
      mkdir -p "$LOGS_DIR"
    fi
=======
clean_iptables() {
  sudo /sbin/iptables -F
  sudo /sbin/iptables -t nat -F
  sudo /sbin/iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
}
>>>>>>> 95f59e6... The script for test run was updated

# waiting for ending of parallel processes
wait() {
  while [ $(pgrep vmrun | wc -l) -ne 0 ] ; do
    [[ "${DEBUG}" == "true" ]] && echo $(pgrep vmrun)
    sleep $WORKSTATION_TIMEOUT
  done
}

<<<<<<< HEAD
    if [ "${KEEP_BEFORE}" != "yes" ]; then
      # remove previous environment
      if [ "${DRY_RUN}" = "yes" ]; then
        echo dos.py erase "${ENV_NAME}"
      else
        if dos.py list | grep "^${ENV_NAME}\$"; then
          dos.py erase "${ENV_NAME}"
        fi
      fi
    fi
=======
revert_ws() {
  nodes=$1
  snapshot=$WORKSTATION_SNAPSHOT
  cmd="vmrun -T ws-shared -h https://localhost:443/sdk -u ${WORKSTATION_USERNAME} -p ${WORKSTATION_PASSWORD}"
>>>>>>> 95f59e6... The script for test run was updated

  # reverting in parallel
  for node in $nodes; do
    echo "Reverting $node to $snapshot"
    $cmd revertToSnapshot "[standard] $node/$node.vmx" $snapshot || \
      { echo "Error: reverting of $node has failed";  exit 1; } &
  done

<<<<<<< HEAD
    # run python test set to create environments, deploy and test product
    if [ "${DRY_RUN}" = "yes" ]; then
        echo export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${WORKSPACE}"
        echo python plugin_test/run_tests.py -q --nologcapture --with-xunit ${OPTS}
    else
        export PYTHONPATH="${PYTHONPATH:+${PYTHONPATH}:}${WORKSPACE}"
        echo "${PYTHONPATH}"
        python plugin_test/run_tests.py -q --nologcapture --with-xunit ${OPTS}
=======
  wait
>>>>>>> 95f59e6... The script for test run was updated

  for node in $nodes; do
    echo "Starting $node"
    $cmd start "[standard] $node/$node.vmx" ||\
      echo "Error: $node failed to start" &
  done

  wait
}

setup_net() {
  env=$1
  add_interface_to_bridge $env private vmnet2
  add_interface_to_bridge $env public  vmnet1 $WORKSTATION_PUBLIC_GATEWAY 
}

# first we want to get variable from command line options
GetoptsVariables "${@}"

# check do we have all critical variables set
CheckVariables

[ -f ${WORKSPACE} ] && cd ${WORKSPACE} || { echo "${WORKSPACE} is not defined or doesn't exist"; exit 1; }

RunTest

