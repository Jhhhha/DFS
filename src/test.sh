#!/bin/bash

python client.py show & #显示DFS中包含哪些数据节点
#显示内容如下
#DataServers include:
#--1--  ('localhost', 8001)
#--2--  ('localhost', 8002)
#--3--  ('localhost', 8003)
sleep 1

python client.py new localhost:8001 test.txt &#在8001端口上的服务器上创建文件
python client.py new localhost:8002 test_1.txt &#在8002端口上的服务器上创建文件
sleep 1

python client.py list localhost:8003 &#在8003端口上的服务器要求显示文件列表
sleep 1

python client.py write localhost:8001 test.txt 'Sad' &
python client.py write localhost:8001 test.txt 'Happy' &#尽可能保证同时写入

sleep 1
python client.py get localhost:8003 test.txt &#从8003端口上的服务器拉取文件到本地，并保存在磁盘中

#sleep 1
#python client.py del localhost:8001 test.txt #从8001端口上的服务器删除文件 'text.txt'
