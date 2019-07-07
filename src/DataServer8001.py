import sys
import os
import rpyc
import time
import threading
from rpyc.utils.server import ThreadedServer

path = "./Server8001/"
timestamp4file = {}
value4file = {}
laststamp = {}

locks4file = {}

def ini_lock():
    fileList = os.listdir(path)
    for file in fileList:
        locks4file[file] = 0

class DataService(rpyc.Service):
    class exposed_Replica():
        def exposed_done(self, file):
            if file in laststamp:
                del laststamp[file]
            if file in value4file:
                del value4file[file]
            if file in timestamp4file:
                del timestamp4file[file]

        def exposed_accept(self, file, value, timestamp):
            if file not in value4file and file not in timestamp4file:
                sign = True
                value4file[file] = value
                timestamp4file[file] = timestamp

                if file not in locks4file: #用于创建时加锁
                    locks4file[file] = 1
                else:
                    while locks4file[file] != 0: #修改时加锁
                        time.sleep(0.1)

                locks4file[file] = 1
                with open(path+file, 'w') as f:
                    print('要写入的值是:',value)
                    f.write(value)
                locks4file[file] = 0

            elif timestamp4file[file] < timestamp:
                sign = True
                timestamp4file[file] = timestamp
            else:
                sign = False
                pass
            return sign, path + file, value4file[file], timestamp4file[file]


        def exposed_confirm(self, file, value, timestamp):
            if file not in value4file and file not in timestamp4file:
                return True, None, None
            else:
                return True, value4file[file], timestamp4file[file]

        def isExist(self,file):
            fileList = os.listdir(path)
            print(type(fileList), fileList)
            if file in fileList:
                return True
            else:
                return False

        def exposed_list(self):
            fileList = os.listdir(path)
            ret = ''
            for file in fileList:
                ret += file +'\n'
            return ret

        def exposed_create(self, file, value):
            global files
            if self.isExist(file):
                return False, "'" + file + "' exists, please pick another name!"
            else:
                conn = rpyc.connect("localhost", port = 8000)
                master = conn.root.Master()
                sign = master.prepare(file, value)
                if sign:
                    str = 'Create ' + file + ' Successfully!'
                else:
                    str = 'Fail to create'
                return sign, str

        def exposed_get(self, file):
            if not self.isExist(file):
                return False, "file not found!"
            if locks4file[file] == 1:
                return False, "Fail to read " + file

            locks4file[file] = 2
            file = path + file
            print("file location", file)
            content = open(file).read()
            locks4file[file] = 0
            return True, content

        def exposed_write(self,file, str):
            conn = rpyc.connect("localhost", port=8000)
            master = conn.root.Master()
            sign = master.prepare(file,str)
            if sign:
                str = 'Modify Successfully!'
            else:
                str = 'Fail to modify'
            return sign, str

        def exposed_delete(self,file):
            if not (self.isExist(file)):
                return False
            conn = rpyc.connect("localhost", port=8000)
            master = conn.root.Master()
            master.delete(file)
            return True

        def exposed_do_delete(self,file):
            if(self.isExist(file)):
                while locks4file[file] != 0:
                    time.sleep(0.1)
                    print(locks4file[file])
                locks4file[file] = 1
                os.remove(path+file)
                del locks4file[file]
                return True, "delete successfully on " + path
            else:
                return False, "file not found on " + path


def print_():
    global  locks4file
    global timestamp4file
    global value4file
    global laststamp
    while True:
        time.sleep(2)
        print("locks4file", locks4file)
        print('timestamp4file', timestamp4file)
        print('value4file', value4file)
        print('laststamp', laststamp)



if __name__ == '__main__':
    ini_lock()
    # threading.Thread(target=print_,args=()).start()
    ThreadedServer(DataService, port=8001).start()
