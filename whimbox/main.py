import sys, os
from whimbox.common.logger import logger
from whimbox.common.path_lib import SCRIPT_PATH

def init():
    """
    如果更新后有什么初始化或者变更操作，就写在这里
    启动器会在更新后调用whimbox init命令
    """
    logger.info("正在初始化应用程序环境...")
    from whimbox.config.config import GlobalConfig
    GlobalConfig()
    if not os.path.exists(SCRIPT_PATH):
        os.makedirs(SCRIPT_PATH, exist_ok=True)
    logger.info("初始化完成")

def run_app():
    """运行主应用程序"""
    from whimbox.common.utils.utils import is_admin
    if not is_admin():
        logger.error("请用管理员权限运行")
        exit()

    from importlib.metadata import version, PackageNotFoundError
    try:
        logger.info(f"奇想盒版本号: {version("whimbox")}")
    except PackageNotFoundError:
        logger.info(f"奇想盒版本号: dev")

    if not os.path.exists(SCRIPT_PATH):
        os.makedirs(SCRIPT_PATH, exist_ok=True)

    from whimbox.mcp_server import start_mcp_server
    from whimbox.mcp_agent import mcp_agent
    import asyncio
    import threading

    mcp_thread = threading.Thread(target=start_mcp_server)
    mcp_thread.daemon = True
    mcp_thread.start()
    asyncio.run(mcp_agent.start())

    from whimbox.common.handle_lib import HANDLE_OBJ
    import time
    logger.info("WAIT_FOR_GAME_START")
    while not HANDLE_OBJ.get_handle():
        time.sleep(5)
        HANDLE_OBJ.refresh_handle()
    logger.info("GAME_STARTED")

    from whimbox.ingame_ui.ingame_ui import run_ingame_ui
    run_ingame_ui()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init()
    else:
        run_app()

if __name__ == "__main__":
    main()