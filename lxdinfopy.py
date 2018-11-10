#!/usr/bin/python3

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


client = pylxd.Client()
containers = client.containers.all()
container_list = []  # List for collected information for printing

total_memory_used = 0  # Running sum of memory
clen = 4  # Max length of container name string; min=4 due to header 
mlen = 5  # Max length of memory string; min=5 due to header

# DATA GATHERING #############################################################

for c in containers:
    
    memory_info = c.api.state.get().json()['metadata']['memory']
    memory_used = memory_info['usage']
    total_memory_used += memory_used
      
    name_width = len(c.name)
    mem_width = len(hr_bytes(memory_used))
    
    clen = name_width if name_width > clen else clen
    mlen = mem_width if mem_width > mlen else mlen
    
    container_list.append((c.name, memory_used))

# PRINTING ###################################################################

# Figure our what the table width will be
table_width = len("|{:^{w}}|{:^{m}}|".format('', '', w=clen, m=mlen))

# Print header
print("|{:^{w}}|{:^{m}}|".format('Name', 'Usage', w=clen, m=mlen))
print("|{:-<{w}}+{:-<{m}}|".format('', '', w=clen, m=mlen))  # print hr

# Print memory use for each container
for c in container_list:
    name = c[0]
    usage = hr_bytes(c[1]) if c[1] > 0.0 else 'OFF'
    print("|{:<{w}}|{:>{m}}|".format(name, usage, w=clen, m=mlen))

# Print total memory use
print("|{:-<{w}}+{:-<{m}}|".format('', '', w=clen, m=mlen))  # print hr

totals = "|{:<{w}}|{:>{m}}|".format(
    "Total",
    hr_bytes(total_memory_used),
    w=clen,
    m=mlen)
 
print(totals)
