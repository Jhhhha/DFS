import sys
import rpyc
from rpyc.utils.server import ThreadedServer

dataServers = [("localhost", 8001), ("localhost", 8002), ("localhost", 8003)]
fileList = []

agreeProcess = {}

class MasterService(rpyc.Service):
    class exposed_Master():
        def exposed_query(self):
            return dataServers

        def exposed_prepare(self, file, value):
            if file not in agreeProcess:
                agreeProcess[file] = 0
            agreeProcess[file] += 1
            cur_timestamp = agreeProcess[file]
            max_timestamp = cur_timestamp
            accepted_value = value
            for DS in dataServers:
                conn = rpyc.connect(DS[0], DS[1])
                replica = conn.root.Replica()
                sign, value, timestamp  = replica.confirm(file, value, cur_timestamp)
                print(sign, value, timestamp)
                if timestamp != None and timestamp > max_timestamp:
                    max_timestamp = timestamp
                    accepted_value = value

            total_ = True
            print(max_timestamp, accepted_value)
            for DS in dataServers:
                conn = rpyc.connect(DS[0], DS[1])
                replica = conn.root.Replica()
                sign, path, value, timestamp = replica.accept(file, accepted_value, cur_timestamp)
                print(sign, path, value, timestamp)
                if sign == True:
                    print(path + "is modified to '" + value)
                else:
                    total_ = False

            if total_ and file not in fileList: #total_是true说明操作成功
                fileList.append(file)

            if cur_timestamp == agreeProcess[file]:
                del agreeProcess[file]
                for DS in dataServers:
                    conn = rpyc.connect(DS[0], DS[1])
                    replica = conn.root.Replica()
                    replica.done(file)

            return total_

        def exposed_delete(self, file):
            for DS in dataServers:
                conn = rpyc.connect(DS[0], DS[1])
                replica = conn.root.Replica()
                sign = replica.do_delete(file)
                print(sign)


if __name__ == '__main__':
    ThreadedServer(MasterService, port = 8000).start()
