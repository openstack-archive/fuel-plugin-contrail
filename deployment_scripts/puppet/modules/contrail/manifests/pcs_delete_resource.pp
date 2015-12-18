# Define to delete PCS resources
define contrail::pcs_delete_resource {
  exec { "Delete-pcs-resource-${name}":
    command => "/usr/sbin/pcs resource delete clone_p_${name}",
    onlyif  => "/usr/sbin/crm resource show clone_p_${name}",
  }
}