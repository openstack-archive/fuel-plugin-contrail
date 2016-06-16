Contrail Analytics Performance Tuning
=====================================

For large installations, the following changes are required to achieve better performance of contrail database.

By default, the analytics_ttl values are set to -1. We recommend changing the default number to ensure the best performance in highly scaled out environments. An example configuration is as follows:

#. /etc/cassandra/cassandra-env.sh
   ::

    -JVM_OPTS="$JVM_OPTS -XX:MaxTenuringThreshold=1"
    +JVM_OPTS="$JVM_OPTS -XX:MaxTenuringThreshold=30"

#. /etc/contrail/contrail-collector.conf
   ::

    analytics_config_audit_ttl=2160
    analytics_statistics_ttl=24
    analytics_flow_ttl=2

Note: Please restart the supervisor services ( supervisor-database, supervisor-analytics) after making these changes.
