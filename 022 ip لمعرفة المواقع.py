#################
import requests
from time import *
import socket
import os
##################
def logo():
    print (' \033[1;34m   ▇▇▇◤▔▔▔▔▔▔▔◥▇▇▇         ')
    print(' \033[1;34m   ▇▇▇▏◥▇◣┊◢▇◤▕▇▇▇       ')
    print (' \033[1;34m   ▇▇▇▏▃▆▅▎▅▆▃▕▇▇▇          ')
    print (' \033[1;34m   ▇▇▇▏╱▔▕▎▔▔╲▕▇▇▇           ')
    print (' \033[1;34m   ▇▇▇◣◣▃▅▎▅▃◢◢▇▇▇           ')
    print (' \033[1;34m   ▇▇▇▇◣◥▅▅▅◤◢▇▇▇▇             ')
    print (' \033[1;34m   ▇▇▇▇▇◣╲▇╱◢▇▇▇▇▇      ')
    print (' \033[1;34m   ▇▇▇▇▇▇◣▇◢▇▇▇▇▇▇            \n')

lblue = "\033[96m"
red = "\033[91m"
grn = "\033[32m"
ylw = "\033[93m"
cyn = "\033[95m"
bn = "\033[94m"

def port(ip):
    try:
     os.system('nmap ',ip)
    except:
     os.system('pkg install nmap')
def option():
    os.system('clear')
    logo()
    print(f' {red}({ylw} 1 {red}) {lblue} Get IP With Url  !!? ')
    print(f' {red}({ylw} 2 {red}) {lblue} Get My IP !!? \n')
    d = int(input(f' {red}[{ylw} ! {red}] {lblue} Enter Number : '))
    if d == 1:
        web = input (f' {red}[{ylw} + {red}] {cyn} Enter url site : \033[1;37m')
        ip = socket.gethostbyname(web)
        print (f" {red}[{ylw} IP {red}] {ylw}  ",ip)
        input('\n  Enter Express to scane ..........  ')
        port(ip)
    elif d == 2:
        ip = requests.get("https://ifconfig.me/").text
        print(f" {red}[{ylw} IP {red}]{ylw} ",ip)
        input('\n\033[1;37m  Enter Express to scane ..........  ')
        port(ip)
    else:
        option()
if __name__ == "__main__":
    option()                