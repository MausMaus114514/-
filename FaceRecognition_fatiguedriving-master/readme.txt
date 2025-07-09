环境：
python3.8 及以上

依赖准备：命令行输入
    pip install --force-reinstall \
    huaweicloudsdkcore \
    huaweicloudsdkobs \
    -i https://repo.huaweicloud.com/repository/pypi/simple     
	
	问ai按照什么方法去检查目录安装是否齐全

	如果确实不齐全（尤其是obs子目录），尝试以下方法重新导入包（我试过了依然不行，也可以再试一下）
    # 卸载旧版本
    pip uninstall huaweicloudsdkcore huaweicloudsdkobs -y

    # 从 GitHub 下载源码安装
    git clone https://github.com/huaweicloud/huaweicloud-sdk-python-obs.git
    cd huaweicloud-sdk-python-obs
    python setup.py install --user


文件简要介绍：
    2obs.py：实现json消息发送给远端obs
	share_data.py: 实现疲劳检测系统输出的结果和monitor.py文件共享
	monitor.py：监听疲劳检测系统输出的信息，并将信息处理为json文本格式并将其保存到对应json文件中
	reference_main.py: 参考的主进程python程序，注意该程序中添加了部分信息，已经使用modify注释标注出，可以进行进一步调整（文件搜索方法，Ctrl+F，框中输入modify找到对应的注释部分，一共是三处，可以用这个文件替换原始main.py文件，别的部分没有做修改，但是名字一定要改回去）
	fatigue.py: 模拟测试脚本，正式部署不需要(可以去掉了，因为main.py已经添加了修改，脚本中也没有这个运行的相关配置)
    2upper.py: 传递json数据给上位机的脚本，注意配置信息可能需要修改（已经使用modify注明，主要就是上位机（要看上位机具体ip是什么，填写进去就可以了，整体的配置方式还是以华为云平台上位机来配置的）

云端达成技术路线
    本地py脚本->obs->DLI->DLV 实现看板功能（从obs往后的部分可以找代做）

obs配置相关信息（使用182手机号对应的账号）
        'ak': 'HPUAEO42TXTDVUNMLVKF',    
        'sk': 'jYNuSBCtlkryRcR58bidAVNd4y3vGgN8EER9anbs',
        'endpoint': 'https://obsmausmaus.obs.cn-east-3.myhuaweicloud.com',
        'bucket_name': 'obsmausmaus',
        'folder': 'fatigue_data/'

JSON消息格式示例：
    {
      "device_id": "driver_001",
      "timestamp": "2023-11-15 14:30:45",
      "status_code": 2,
      "status_text": "瞌睡",
      "is_alert": true
    }

运行方式：
    命令行输入 bash ./run.sh
    备注：
        在切换为向上位机发送信息时，请将脚本中 python3 2obs.py & 这一行使用 # 注释，同时解除注释 python3 2upper.py & 完成运行