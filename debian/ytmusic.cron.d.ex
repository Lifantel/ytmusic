#
# Regular cron jobs for the ytmusic package.
#
0 4	* * *	root	[ -x /usr/bin/ytmusic_maintenance ] && /usr/bin/ytmusic_maintenance
