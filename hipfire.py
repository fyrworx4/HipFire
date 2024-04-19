import argparse
import subknitter
import configparser


def parse_args():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-r',
                       '--range',
                       type=str,
                       help="specify range of hosts"
    )
    group.add_argument('-f',
                       '--file',
                       type=str,
                       help="specify path to hosts file"
    )
    hosts = parser.add_argument_group()
    hosts.add_argument('-w',
                       '--win-hosts',
                       type=str,
                       help="comma-separated 4th octets of Windows hosts"
    )
    hosts.add_argument('-l',
                       '--lin-hosts',
                       type=str,
                       help="comma-separated 4th octets of Linux hosts"
    )
    parser.add_argument('-a',
                        '--action',
                        type=str,
                        required=True,
                        help="action to take"
    )

    args = parser.parse_args()
    ip_range = args.range
    win_hosts = args.win_hosts
    lin_hosts = args.lin_hosts
    hosts_file = args.file
    action = args.action

    # --range logic
    if ip_range:
        if win_hosts or lin_hosts:
            pass
        else:
            parser.error("--win-hosts or --lin-hosts required when using --range")
    elif hosts_file:
        pass
    # --action logic
    if "fire" in action:
        pass 
    elif "create" in action:
        pass 
    else:
        parser.error("invalid --action option")

    return ip_range, win_hosts, lin_hosts, hosts_file, action

def flatten(list_of_lists):
    flattened_list = []
    for element in list_of_lists:
        if type(element) is list:
            for item in element:
                flattened_list.append(item)
        else:
            flattened_list.append(element)

    return flattened_list

def generate_hosts_file(ip_range, win_hosts, lin_hosts):
    # convert win_hosts and lin_hosts to lists
    win_hosts_list = win_hosts.split(",")
    lin_hosts_list = lin_hosts.split(",")
    
    win_ips = []
    for i in win_hosts_list:
        win_ips.append(subknitter.gen_ip_addr(f"{ip_range}.{i}"))

    lin_ips = []
    for i in lin_hosts_list:
        lin_ips.append(subknitter.gen_ip_addr(f"{ip_range}.{i}"))

    win_ips = flatten(win_ips)
    lin_ips = flatten(lin_ips)
    
    
    win_hosts_dict = {}
    for i in win_ips:
        win_hosts_dict[f'{i}'] = None

    lin_hosts_dict = {}
    for i in lin_ips:
        lin_hosts_dict[f'{i}'] = None

    # configure defaults
    win_var_defaults = {
        'ansible_user': '"{{ windows.ansible_user }}"',
        'ansible_password': '"{{ windows.ansible_password }}"',
        'ansible_connection': 'winrm',
        'ansible_winrm_port': '5985',
        'ansible_winrm_transport': 'ntlm',
        'ansible_winrm_server_cert_validation': 'ignore'
    }

    lin_var_defaults = {
        'ansible_user': '"{{ linux.ansible_user }}"',
        'ansible_password': '"{{ linux.ansible_password }}"',
        'ansible_sudo_pass': '"{{ linux.ansible_sudo_pass }}"'
    }
    
    # write into hosts file
    config = configparser.ConfigParser(allow_no_value=True)
    config['windows'] = win_hosts_dict
    config['linux'] = lin_hosts_dict
    config['windows:vars'] = win_var_defaults
    config['linux:vars'] = lin_var_defaults

    with open('hosts', 'w') as configfile:
        config.write(configfile)

if __name__ == '__main__':
    ip_range, win_hosts, lin_hosts, hosts_file, action = parse_args()
    generate_hosts_file(ip_range, win_hosts, lin_hosts)
