#!/bin/bash

# 设置Python解释器路径（如果需要的话）
# PYTHON=/usr/bin/python3
PYTHON=python3

# 定义各个脚本的路径
FATIGUE_SCRIPT=./fatigue.py
LISTEN_SCRIPT=./listen.py
STORE_CSV_SCRIPT=./store2csv.py
GUI_SCRIPT=./gui.py

# 定义日志文件路径（可选）
LOG_DIR=./logs
mkdir -p $LOG_DIR

FATIGUE_LOG=$LOG_DIR/fatigue.log
LISTEN_LOG=$LOG_DIR/listen.log
STORE_CSV_LOG=$LOG_DIR/store_csv.log
GUI_LOG=$LOG_DIR/gui.log

echo "==============================="
echo "启动疲劳数据模拟器..."
echo "==============================="
$PYTHON $FATIGUE_SCRIPT > $FATIGUE_LOG 2>&1 &

echo "==============================="
echo "启动监听开发板..."
echo "==============================="
$PYTHON $LISTEN_SCRIPT > $LISTEN_LOG 2>&1 &

echo "==============================="
echo "启动数据存储到CSV..."
echo "==============================="
$PYTHON $STORE_CSV_SCRIPT > $STORE_CSV_LOG 2>&1 &

echo "==============================="
echo "启动图形化界面看板..."
echo "==============================="
$PYTHON $GUI_SCRIPT > $GUI_LOG 2>&1 &

echo "所有组件已启动。日志文件位于 $LOG_DIR 目录下。"