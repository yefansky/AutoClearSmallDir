import os
import shutil
import logging

DST_PATH = "\\\\192.168.XXX\\XXXXX"  # 请替换为你的SMB目标路径
USER_NAME = "username"  # 请替换为你的SMB用户名
PASSWD = "password"  # 请替换为你的SMB密码
# 设置最大允许的子目录总大小（4M）
max_directory_size = 4 * 1024 * 1024

logger = logging.getLogger("SMBLogger")

def Init(_DST_PATH, _USER_NAME, _PASSWD, loggerName):
    global DST_PATH, USER_NAME, PASSWD, logger
    DST_PATH, USER_NAME, PASSWD = _DST_PATH, _USER_NAME, _PASSWD
    logger = logging.getLogger(loggerName)

def Connect(bForceConnect):
    backup_storage_available = os.path.isdir(DST_PATH)

    if (backup_storage_available and not bForceConnect):
        logger.info("Backup storage already connected.")
    else:
        logger.info("Connecting to backup storage.")

        mount_command = "net use " + DST_PATH + " " + PASSWD + " /user:" + USER_NAME
        os.system(mount_command)
        backup_storage_available = os.path.isdir(DST_PATH)

        if backup_storage_available:
            logger.info("Connection success.")
        else:
            raise Exception("Failed to find storage directory.")

def Disconnect():
    unmount_command = "net use " + DST_PATH + " /delete"
    os.system(unmount_command)
    logger.info("Disconnection success.")

def get_directory_size(directory):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            total_size += os.path.getsize(filepath)
    return total_size

def delete_small_directories(base_directory, max_size):
    for dirpath, dirnames, filenames in os.walk(base_directory, topdown=False):
        for dirname in dirnames:
            current_dir = os.path.join(dirpath, dirname)
            dir_size = get_directory_size(current_dir)
            if dir_size < max_size:
                print(f"Deleting {current_dir} as total size is {dir_size} bytes.")
                shutil.rmtree(current_dir)

if __name__ == "__main__":
    # 初始化SMB连接
    Init(DST_PATH, USER_NAME, PASSWD, "SMBLogger")
    try:
        # 连接SMB
        Connect(bForceConnect=False)

        # 指定目录
        base_directory = DST_PATH

        # 调用函数进行删除操作
        delete_small_directories(base_directory, max_directory_size)
    finally:
        # 断开SMB连接
        Disconnect()
