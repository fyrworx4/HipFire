import ipaddress

def gen_ip_addr(ip_range):
    # split IP range into octets
    octets = ip_range.split('.')

    # determine the octet with the range
    range_octet = None
    for i, octet in enumerate(octets):
        if '-' in octet:
            range_octet = i
            break

    # determine the start and end ranges
    start, end = map(int, octets[range_octet].split('-'))

    # generate the IP addresses
    ip_addresses = []
    for i in range(start, end + 1):
        octets[range_octet] = str(i) # only modify the range octet
        ip_address = '.'.join(octets)

        try:
            ipaddress.ip_address(ip_address)
            ip_addresses.append(ip_address)
        except ValueError:
            print(f"Invalid IP address: {ip_address}")

    return ip_addresses
