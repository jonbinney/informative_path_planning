'''
Check glider logs on the dockserver to see when the glider pops up,
and then sound an alarm.
'''

while True:
    for glider_name in ['he-ha-pe', 'rusalka']:
        cmd = ['ssh', 'localuser@10.1.1.20', 'ls', '-1',
               '/var/opt/gmc/gliders/he-ha-pe/logs/']
                        
