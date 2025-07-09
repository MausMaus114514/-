需要处理的数据为以下格式的json数据
    {
      "device_id": "driver_001",
      "timestamp": "2023-11-15 14:30:45",
      "status_code": 2,
      "status_text": "瞌睡",
      "is_alert": true
    }

提供了一个模拟生成的python脚本，同时也提供了一个监听开发板的python脚本，其中的config信息需要根据开发板的发送端口和ip进行一定的更改（目前是192.168.5.15：5000）

目前需要根据这个json文本，编写一个上位机的gui看板界面注意在文件中已经给出了一些示例（可以运行），可以运行脚本模拟一下

目前的项目结构：
    fatigue.py    模拟数据生成到json文档中
    gui.py    展示图形化界面看板
    listen.py    监听开发板
    store2csv.py    将每次更新的json数据保存到csv文档中
    info.json
    info.csv

运行方式：
    bash ./run_all.sh

    备注：实际运行时使用 # 注释掉 $PYTHON $FATIGUE_SCRIPT > $FATIGUE_LOG 2>&1 & 这一行，此处是模拟器