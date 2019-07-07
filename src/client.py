import sys
import rpyc

server_port = 8000

def main(args):
    if args[0] == 'show':
        conn = rpyc.connect("localhost", server_port)
        Master = conn.root.Master()
        print('DataServers include:')
        count = 1
        for DS in Master.query():
            print('--' + str(count) + '-- ',DS)
            count += 1

    elif args[0] == 'list':
        addr = args[1].split(':')
        conn = rpyc.connect(addr[0], int(addr[1]))
        replica = conn.root.Replica()
        content = replica.list().strip('.DS_Store').lstrip()
        print('\n'+content)
        conn.close()

    elif args[0] == 'write':
        addr = args[1].split(':')
        conn = rpyc.connect(addr[0], int(addr[1]))
        replica = conn.root.Replica()
        try:
            sign, ret = replica.write(args[2], args[3].strip("'"))
        except:
            sign, ret = replica.write(args[2], '')
        conn.close()

    elif args[0] == 'new':
        addr = args[1].split(':')
        conn = rpyc.connect(addr[0], int(addr[1]))
        replica = conn.root.Replica()
        try:
            sign, ret = replica.create(args[2], args[3])
        except:
            sign, ret = replica.create(args[2], '')
        print(ret)
        conn.close()

    elif args[0] == 'get':
        addr = args[1].split(':')
        conn = rpyc.connect(addr[0], int(addr[1]))
        replica = conn.root.Replica()
        sign, ret = replica.get(args[2])
        with open('./local/' + args[2], 'w') as f:
            f.write(ret)
        conn.close()

    elif args[0] == 'del':
        addr = args[1].split(':')
        conn = rpyc.connect(addr[0], int(addr[1]))
        replica = conn.root.Replica()
        sign = replica.delete(args[2])
        if not sign:
            print('File not found')
        else:
            print('Delete Successfully!')
        conn.close()

    else:
        print('Illegal input!')


if __name__ == '__main__':
    main(sys.argv[1:])
