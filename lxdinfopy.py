#!/usr/bin/env python3

import pylxd


# Print bytes in a friendlier way
# Source: https://stackoverflow.com/questions/1094841/
def hr_bytes(bites, suffix='B'):
    
    """ A method providing a more legible byte format """
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(bites) < 1024.0:
            return "%3.1f %s%s" % (bites, unit, suffix)
        bites /= 1024.0
    return "%.1f %s%s" % (bites, 'Yi', suffix)

# SETUP ######################################################################


try:
    client = pylxd.Client()
except:
    print('Looks like LXD isn\'t running or you don\'t have permissions.)')
    print('Exiting...')
    exit(1)

containers = client.containers.all()
container_list = []  # List for collected information for printing

total_memory_used = 0  # Running sum of memory
total_peak_potential = 0  # Running sum of peak memory
clen = 4  # Max length of container name string; min=4 due to header 
mlen = 5  # Max length of memory string; min=5 due to header
plen = 4  # Max length of peak memory string; min=4 due to header

# DATA GATHERING #############################################################

for c in containers:
    
    memory_info = c.api.state.get().json()['metadata']['memory']
    memory_used = memory_info['usage']
    total_memory_used += memory_used
    memory_peak = memory_info['usage_peak']
    total_peak_potential += memory_peak
      
    name_width = len(c.name)
    mem_width = len(hr_bytes(memory_used))
    peak_width = len(hr_bytes(memory_peak))
    
    clen = name_width if name_width > clen else clen
    mlen = mem_width if mem_width > mlen else mlen
    plen = peak_width if peak_width > plen else plen
    
    container_list.append((c.name, memory_used, memory_peak))

# PRINTING ###################################################################

# Figure our what the table width will be
table_width = len('|{:^{w}}|{:^{m}}|{:^{p}}|'.format('', '', '',
                                                     w=clen,
                                                     m=mlen,
                                                     p=plen))

# Print header
print('|{:^{w}}|{:^{m}}|{:^{p}}|'.format('Name', 'Usage', 'Peak',
                                         w=clen, m=mlen, p=plen))
print('|{:-<{w}}+{:-<{m}}|{:-<{p}}|'.format('', '', '',
                                            w=clen, m=mlen, p=plen))

# Print memory use for each container
for c in container_list:
    name = c[0]
    usage = hr_bytes(c[1]) if c[1] > 0.0 else 'OFF'
    peak = hr_bytes(c[2]) if c[2] > 0.0 else 'OFF'
    print('|{:<{w}}|{:>{m}}|{:>{p}}|'.format(name, usage, peak,
                                             w=clen, m=mlen, p=plen))

# Print total memory use
print('|{:-<{w}}+{:-<{m}}|{:-<{p}}|'.format('', '', '',
                                            w=clen, m=mlen, p=plen))

totals = '|{:<{w}}|{:>{m}}|{:>{p}}|'.format(
    'Total', hr_bytes(total_memory_used), hr_bytes(total_peak_potential),
    w=clen,
    m=mlen,
    p=plen)
 
print(totals)

