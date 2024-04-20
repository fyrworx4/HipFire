import argparse
import subknitter
import configparser
import ansible_runner
import yaml
from colorama import Fore, Back, Style


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
                       default="hosts",
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
    parser.add_argument('--playbook',
                        type=str,
                        default="playbook.yml",
                        help="path to playbook.yml file (default=playbook.yml)"
    )
    parser.add_argument('--edit-vars',
                        type=str,
                        help="vars to edit, e.g. lin.lin_user:root"
    )
    parser.add_argument('--create-file',
                        type=str,
                        default="hosts",
                        help="filename to write inventory to if --create is used (default=hosts)"
    )

    args = parser.parse_args()
    ip_range = args.range
    win_hosts = args.win_hosts
    lin_hosts = args.lin_hosts
    hosts_file = args.file
    action = args.action
    playbook_file = args.playbook
    edit_vars = args.edit_vars
    create_file = args.create_file

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

    # --edit-vars into dict
    if edit_vars:
        try:
            key_values = []
            edit_vars_list = edit_vars.split(', ')
            for i, var in enumerate(edit_vars_list): 
                key_values.append(var.replace(" ",""))

            edit_vars_dict = {}
            for i in key_values:
                key, value = i.split(':')
                main_key, sub_key = key.split('.')

                if main_key not in edit_vars_dict:
                    edit_vars_dict[main_key] = {}

                edit_vars_dict[main_key][sub_key] = value
        except:
            parser.error("invalid syntax for --edit-vars")
    else:
        edit_vars_dict = None

    return ip_range, win_hosts, lin_hosts, hosts_file, action, playbook_file, edit_vars_dict, create_file


def flatten(list_of_lists):
    flattened_list = []
    for element in list_of_lists:
        if type(element) is list:
            for item in element:
                flattened_list.append(item)
        else:
            flattened_list.append(element)

    return flattened_list


def generate_hosts_file(ip_range, win_hosts, lin_hosts, create_file):
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
        'ansible_user': '"{{ win.ansible_user }}"',
        'ansible_password': '"{{ win.ansible_password }}"',
        'ansible_connection': 'winrm',
        'ansible_winrm_port': '5985',
        'ansible_winrm_transport': 'ntlm',
        'ansible_winrm_server_cert_validation': 'ignore'
    }

    lin_var_defaults = {
        'ansible_user': '"{{ lin.ansible_user }}"',
        'ansible_password': '"{{ lin.ansible_password }}"',
        'ansible_sudo_pass': '"{{ lin.ansible_sudo_pass }}"'
    }
    
    # write into hosts file
    config = configparser.ConfigParser(allow_no_value=True)
    config['win'] = win_hosts_dict
    config['lin'] = lin_hosts_dict
    config['win:vars'] = win_var_defaults
    config['lin:vars'] = lin_var_defaults

    with open(create_file, 'w') as configfile:
        config.write(configfile)


def generate_vars(edit_vars_dict):
    # obtain vars from vars.yml
    with open("vars.yml", 'r') as file:
        vars_dict = yaml.safe_load(file)

    if edit_vars_dict != None:
        print(f"[i] Option --edit-vars selected. Editing variables...")
        try:
            for key in edit_vars_dict:
                vars_to_replace = edit_vars_dict[key]
                
                for sub_key in vars_to_replace:
                    if sub_key in vars_dict[key]:
                        vars_dict[key][sub_key] = vars_to_replace[sub_key]
        except:
            raise KeyError("Variables supplied in --edit-vars are incorrect, check your command") from None

    return vars_dict

if __name__ == '__main__':

    # Define color variables
    RED = Fore.RED
    GREEN = Fore.GREEN
    BLUE = Fore.BLUE
    YELLOW = Fore.YELLOW
    MAGENTA = Fore.MAGENTA
    CYAN = Fore.CYAN
    WHITE = Fore.WHITE
    RESET = Fore.RESET

    # Define background color variables
    BG_RED = Back.RED
    BG_GREEN = Back.GREEN
    BG_BLUE = Back.BLUE
    BG_YELLOW = Back.YELLOW
    BG_MAGENTA = Back.MAGENTA
    BG_CYAN = Back.CYAN
    BG_WHITE = Back.WHITE
    BG_RESET = Back.RESET

    # Define style variables
    BOLD = Style.BRIGHT
    DIM = Style.DIM
    NORMAL = Style.NORMAL
    RESET_ALL = Style.RESET_ALL

    banner = rf'''{CYAN}
      (                                 _
       )                               /=>
      (  +____________________/\/\___ / /|
       .''._____________'._____      / /|/\
      : () :              :\ ----\|    \ )
       '..'______________.'0|----|      \
                        0_0/____/        \
                            |----    /----\
                           || -\\ --|      \
                           ||   || ||\      \
                            \\____// '|      \
     Bang! Bang!                     .'/       |
                                   .:/        |
                                   :/_________|{RESET_ALL}

    '''
    
    print(banner)

    ip_range, win_hosts, lin_hosts, hosts_file, action, playbook_file, edit_vars_dict, create_file = parse_args()
    
    try:
        if ip_range:
            print(f"{CYAN}[i]{RESET_ALL} Generating hosts file...")
            generate_hosts_file(ip_range, win_hosts, lin_hosts, create_file)
            print(f"{GREEN}[+]{RESET_ALL} Hosts file successfully generated.")
        elif hosts_file:
            print(f"{CYAN}[i]{RESET_ALL} Checking if selected hosts file is valid...")

    except:
        raise Exception(f"{RED}[-]{RESET_ALL} Something went wrong, check your syntax!")

    if action == 'fire':
        # run  ansible script
        vars_dict = generate_vars(edit_vars_dict)
        
        print(f"{CYAN}[i] {RED}Firing!!!{RESET_ALL}")

        result = ansible_runner.run(
            private_data_dir = '.',
            playbook = playbook_file,
            inventory = hosts_file,
            extravars = vars_dict
        )

        print(result.stdout.read())

        if result.status == 'successful':
            print(f"{GREEN}[+] {RESET_ALL}Playbook ran successfully.")
        else:
            print(f"{RED}[-] {RESET_ALL}Playbook execution failed")

    elif action == 'create':
        print(f"{CYAN}[i] {RESET_ALL}Create action selected, only creating hosts file in {create_file}")
        print(f"{CYAN}[i] {RESET_ALL}FYI if you used --edit-vars with -a create then the variables won't be saved")
