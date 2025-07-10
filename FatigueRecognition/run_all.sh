#!/bin/bash
# 设置环境变量后运行
export OBS_AK=HPUAEO42TXTDVUNMLVKF
export OBS_SK=jYNuSBCtlkryRcR58bidAVNd4y3vGgN8EER9anbs

# 启动主进程（后台运行）
python3 main.py &

# 启动监控进程（后台运行）
python3 monitor.py &

# 启动OBS上传（可选项）
python3 2obs.py &

# 启动上位机数据传输（后台运行）
# python3 2upper.py &

wait
echo "所有进程已启动"