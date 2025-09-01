import requests, shutil, datetime, os, subprocess, time, platform, threading
from gui import GuiWindow

class Minerman:

    def __init__(self):
        
        self.osName = platform.system()
        self.currentDirectory = os.path.abspath(os.path.curdir)
        self.gameWindow: subprocess.Popen = None
        self.kill_event = threading.Event()
        self.stop_event = threading.Event()
        self.printThread: threading.Thread = None
        # Read config file or create one with default values if one does not exist.
        self.config = Minerman.readConfig()
        self.isServerRunning = True

    def readConfig():
        print('Reading config...')
        if os.path.exists('.config'):
            config = {}
            with open('.config', 'r') as configFile:
                for line in configFile:
                    if line.startswith('#'):
                        config[line] = ''
                    else:
                        key, value = line.partition('=')[::2]
                        if key == 'server-directory':
                            config[key.strip()] = value.strip().replace('\\', '/')
                        else:
                            config[key.strip()] = value.strip()
            # print(config)
        else:
            config = {'# Minecraft Server Updater config file created ' + datetime.datetime.now().strftime('%m/%d/%Y %I:%M%p') + '\n' : '', 'simulation-distance': '10', 'view-distance': '10', '# Note RAM 1024 = 1GB, 2048 = 2GB, 4086 = 4GB, 8162 = 8GB, etc...\n' : '','dedicated-ram': '1024', 'server-directory' : os.path.abspath(os.path.curdir).replace("\\", "/") + '/minecraftserver'}
            with open('.config', 'w') as configFile:
                for key in config:
                    if key.startswith('#'):
                        configFile.write(key)
                    else:
                        configFile.write(f'{key}={config[key]}\n')
        return config

    def writeConfig(self):
        print('Writing config files...')
        # Write config file
        # print(config)
        with open('.config', 'w') as configFile:
            for key in self.config:
                if key.startswith('#'):
                    configFile.write(key)
                else:
                    configFile.write(f'{key}={self.config[key]}\n')

        # Read properties file
        with open(self.config['server-directory'] + '/server.properties', 'r') as propsFile:
            lines = propsFile.readlines()
            for id, line in enumerate(lines):
                for key in self.config:
                    if line.startswith(key):
                        lines[id] = f'{key}={self.config[key]}\n'

        # Write properties file
        with open(self.config['server-directory'] + '/server.properties', 'w') as propsFile:
            # print(lines)
            propsFile.writelines(lines)

    def checkEula(self):
        print('Checking Eula...')
        with open(self.config['server-directory'] + '/eula.txt', 'r') as eula:
            lines = eula.readlines()
            for id, line in enumerate(lines):
                if line.startswith('eula='):
                    lineNum = id
                    key, value = line.partition('=')[::2]
                    value.strip()

        if value == 'false\n':
            line = 'eula=true\n'
            lines[lineNum] = line 
            print('Writing to eula...')
            with open(self.config['server-directory'] + '/eula.txt', 'w') as eula:
                print(lines)
                eula.writelines(lines)

    def downloadLatestServer(self, response :requests.Response = None):
        if not response:
            response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
            print('Version manifest response code:', response.status_code)
        if response.status_code == 200:
            responseJson = response.json()

            latestVersion = responseJson['latest']['release']

            for versions in responseJson['versions']:
                if versions['id'] == latestVersion:
                    # print(versions['url'])
                    # Get Url to download the latest server .jar file
                    response = requests.get(versions['url'])
                    print('download link response code:', response.status_code)
                    if response.status_code == 200:
                        responseJson = response.json()
                        serverUrl = responseJson['downloads']['server']['url']
                        # print(serverUrl)
                        # Download latest .jar file
                        if os.path.exists(self.config['server-directory']) == False:
                            os.mkdir(self.config['server-directory'])
                        open(self.config['server-directory'] + '/server.jar', 'wb').write(requests.get(serverUrl).content)
                        print('Download complete.')

    def startServer(self, firstRun :bool = False):
        print('Starting server...')
        os.chdir(self.config['server-directory'])
        if self.osName == 'Linux':
            # blank terminal opens to show server is running
            cmd = subprocess.Popen('java ' + '-Xms1024M -Xmx' + self.config['dedicated-ram'] + 'M ' + '-jar ' + self.config['server-directory'] + '/server.jar --nogui', creationflags=subprocess.CREATE_NEW_CONSOLE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            # No terminal opens, server runs in background
            # cmd = subprocess.Popen('java ' + '-Xms1024M -Xmx' + self.config['dedicated-ram'] + 'M ' + '-jar ' + self.config['server-directory'] + '/server.jar --nogui', stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
        elif self.osName == 'Windows':
            # blank terminal opens to show server is running
            cmd = subprocess.Popen('java ' + '-Xms1024M -Xmx' + self.config['dedicated-ram'] + 'M ' + '-jar ' + self.config['server-directory'] + '/server.jar --nogui', creationflags=subprocess.CREATE_NEW_CONSOLE, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            # No terminal opens, server runs in background
            # cmd = subprocess.Popen('java ' + '-Xms1024M -Xmx' + self.config['dedicated-ram'] + 'M ' + '-jar ' + self.config['server-directory'] + '/server.jar --nogui', stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            if firstRun:
                while os.path.exists(self.config['server-directory'] + '/eula.txt') == False:
                    cmd.communicate()
                    time.sleep(5)
                time.sleep(10)
                cmd.terminate()
                cmd.wait()
        os.chdir(self.currentDirectory)
        self.isServerRunning = True
        return cmd

    def stopServer(self):
        print('Stopping server...')
        self.gameWindow.stdin.write('/stop\n')
        self.gameWindow.stdin.flush()
        self.gameWindow.wait()

    def backupSever(self):
        print('Backing up server...')
        if os.path.exists(self.config['server-directory']):

        # Create backup of server folder
            shutil.copytree(self.config['server-directory'], self.config['server-directory'] + datetime.date.today().strftime("%Y%m%d"), dirs_exist_ok=True)

        else:
            raise FileNotFoundError(f"Backup failed: No such directory. {self.config['server-directory']}") 
        return

    def updateServer(self, info: list, cmd: subprocess.Popen):
        info[2] = True
        cmd.stdin.write('/list\n')
        cmd.stdin.flush()
        while info[2]:
            pass
        print(f'{info[1]} players online.')
        if info[1] == '0':
            # Get latest version number
            response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
            print('Version manifest response code:', response.status_code)
            if response.status_code == 200:
                responseJson = response.json()

                latestVersion = responseJson['latest']['release']

                if info[0] != latestVersion:
                # if info[0] == latestVersion:
                    print(f'Newer version of server found. Version {latestVersion}')
                    return response
                else:
                    print('Server is already at latest version.')
        else:
            print('Server not empty. Skipping update.')       
        
        return 0

    def gameWindowHandler(self, cmd: subprocess.Popen, stop_event: threading.Event, version: list, output: GuiWindow = None):
        try:
            while not stop_event.is_set():
                if stop_event.is_set():
                    exit(0)
                msg: str = cmd.stdout.readline()
                if msg != '':
                    print(msg.removesuffix('\n'))
                    if output != None:
                        output.printOutput(msg.removeprefix('\n'))
                    if msg.find('Starting minecraft server version') != -1:
                        # print(msg.split().pop())
                        version[0] = msg.split().pop()
                        # version[2] = False
                    if msg.endswith('players online: \n'):
                        version[1] = msg.split()[5]
                        version[2] = False
                else:
                    pass
        except Exception as e:
            pass
                
    # def normalStop(self):
    #     self.stopServer()
    #     # if self.gameWindow:
    #     #     self.gameWindow.terminate()
    #     #     self.gameWindow.wait()
    #     if self.printThread:
    #         self.stop_event.set()
    #         self.printThread.join()

    def mainLoop(self, scriptGui: GuiWindow = None):
        try:

            # Read Eula file and mark true if exists. If not start server to generate eula.
            if os.path.exists(self.config['server-directory'] + '/eula.txt') & os.path.exists(self.config['server-directory'] + '/server.jar'):
                self.checkEula()
                self.writeConfig()

            elif os.path.exists(self.config['server-directory'] + '/server.jar'):
                self.startServer(True)
                self.writeConfig()
                self.checkEula()

            else:
                self.downloadLatestServer()
                self.startServer(True)
                self.writeConfig()
                self.checkEula()

    
            self.gameWindow = self.startServer()
            gameInfo = ['', 0, True]

            self.printThread = threading.Thread(target=self.gameWindowHandler, args=(self.gameWindow, self.stop_event, gameInfo, scriptGui))
            self.printThread.start()

            # time.sleep(25)
            # gameWindow.stdin.write('/version\n')
            # gameWindow.stdin.flush()

            while True:
                for i in range(3600):
                    time.sleep(1)
                    if self.kill_event.is_set(): 
                        exit(0)

                latestVersion = self.updateServer(gameInfo, self.gameWindow)
                if latestVersion != 0:                    
                    self.stopServer()
                    self.stop_event.set()
                    self.printThread.join()
                    self.stop_event.clear()
                    self.backupSever()
                    self.downloadLatestServer(latestVersion)
                    self.gameWindow = self.startServer()
                    gameInfo = ['', 0, True]
                    self.printThread = threading.Thread(target=self.gameWindowHandler, args=(self.gameWindow, self.stop_event, gameInfo, scriptGui))
                    self.printThread.start() 
                




            #serverDirectory = "/home/kupar/gameservers/minecraft"
            # currentDirectory = "/home/kupar/gameservers"
            #logFilePath = "/home/kupar/gameservers/log.txt"
            # currentTime = datetime.datetime.now()   
            # laterTime = currentTime + datetime.timedelta(hours = 1)
            # laterTimeSecond = currentTime + datetime.timedelta(seconds = 1)

            # while True:
            # while currentTime < laterTime:
            #     currentTime = datetime.datetime.now()
                
                # if currentTime >= laterTimeSecond:
                #     print(currentTime)
                #     laterTimeSecond = currentTime + datetime.timedelta(seconds = 1)


            # laterTime = currentTime + datetime.timedelta(hours = 1)
            # gameWindow.stdout.flush()
            # time.sleep(25)
            # stopcmd = '/stop\n'
            # gameWindow.stdin.write(stopcmd.encode("utf-8"))
            # gameWindow.stdin.flush()
            # supercool = gameWindow.stdout.readlines()
            # print(supercool)
            #print('script finished')
            #exit(0)
            
        except SystemExit as e:
            self.stopServer()
            # if self.gameWindow:
            #     self.gameWindow.terminate()
            #     self.gameWindow.wait()
            if self.printThread:
                 self.stop_event.set()
                 self.printThread.join()
                 self.isServerRunning = False
            # print(e)    

        except Exception as e:
            print(e)
            if self.gameWindow:
                self.gameWindow.terminate()
                self.gameWindow.wait()
            if self.printThread:
                self.stop_event.set()
                self.printThread.join()
                self.isServerRunning = False
            #exit(1)

        except KeyboardInterrupt as k:
            print('Keyboard interrupt. Terminating...')
            if self.gameWindow:
                self.gameWindow.terminate()
                self.gameWindow.wait()
            if self.printThread:
                self.stop_event.set()
                self.printThread.join()
                self.isServerRunning = False
            #exit(1)

# try:
#     # Get status of minecraft server
#     response = requests.get('https://api.mcstatus.io/v2/status/java/kurtisparsons.com')
#     print('Server status response code:', response.status_code)
#     if response.status_code == 200:

#         responseJson = response.json()

#         serverVersion = responseJson['version']['name_raw']
#         playerCount = responseJson['players']['online']

#         if playerCount == 0:
#             # Get latest version number
#             response = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json')
#             print('Version manifest response code:', response.status_code)
#             if response.status_code == 200:
#                 responseJson = response.json()

#                 latestVersion = responseJson['latest']['release']

#                 # print(len(responseJson['versions']))

#                 if serverVersion != latestVersion:
#                     for versions in responseJson['versions']:
#                         if versions['id'] == latestVersion:
#                             # print(versions['url'])
#                             # Get Url to download the latest server .jar file
#                             response = requests.get(versions['url'])
#                             print('download link response code:', response.status_code)
#                             if response.status_code == 200:
#                                 responseJson = response.json()
#                                 serverUrl = responseJson['downloads']['server']['url']
#                                 # print(serverUrl)
#                                 # Download latest .jar file
#                                 open(currentDirectory + '/server.jar', 'wb').write(requests.get(serverUrl).content)
#                                 print('Download complete.')

#                                 # Bash Commands (stop server process) (wait for process to stop)
#                                 bashResult = subprocess.run("systemctl stop minecraft-server.service", shell=True, capture_output=True, text=True)
#                                 print(bashResult)
#                                 time.sleep(30)

#                                 # Copy server folder
#                                 if os.path.exists(serverDirectory):
#                                     # print(serverDirectory, datetime.date.today())
#                                     # Create backup of server folder
#                                     shutil.copytree(serverDirectory, serverDirectory + datetime.date.today().strftime("%Y%m%d"), dirs_exist_ok=True)
                                    
#                                     # Move new server file into existing directory
#                                     shutil.copy(currentDirectory + '/server.jar', serverDirectory)

#                                     # Bash commands (start server process)
#                                     bashResult = subprocess.run("systemctl start minecraft-server.service", shell=True, capture_output=True, text=True)
#                                     print(bashResult)
#                                     open(logFilePath, 'a').write(f'{datetime.datetime.now()}: Server succesfully updated to version: {latestVersion}\n')
                                    
#                                 else:
#                                     print('Server directory does not exist.')
#                                     open(logFilePath, 'a').write(f'{datetime.datetime.now()}: Server directory does not exist.\n')                               

#                 else:
#                     print(f'Server is up to date. Version: {serverVersion}')
#                     open(logFilePath, 'a').write(f'{datetime.datetime.now()}: Server is up to date. Version: {serverVersion}.\n')

#         else:
#             print('Server not empty.', playerCount, 'players in game.')
#             open(logFilePath, 'a').write(f'{datetime.datetime.now()}: Server not empty. {playerCount} players in game.\n')


# except Exception as e:
#     print('Unspecified Error')
#     print(e)
#     open(logFilePath, 'a').write(f'{datetime.datetime.now()}: ERROR: {e}\n')
