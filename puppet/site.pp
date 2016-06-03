node default {
	include setuphosts
}

class setuphosts($hostname, $ip, $host_aliases, $ensure) {
	host { $hostname:
		ip => $ip,
		host_aliases => $host_aliases,
		ensure => $ensure
	}
}
