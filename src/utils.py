import os
import platform
from typing import TypedDict

class ChromeResources(TypedDict):
    executable: str
    driver: str

def get_chrome_resources() -> ChromeResources:
    cwd = os.path.dirname(os.path.abspath(__file__))
    os_name = platform.system()
    if os_name == 'Linux':
        return {
            'executable': os.path.join(cwd, os.path.pardir, 'resources', 'linux', 'chrome', 'chrome' ),
            'driver': os.path.join(cwd, os.path.pardir, 'resources', 'linux', 'chromedriver' )
        }
    if os_name == 'Windows':
        return {
            'executable': os.path.join(cwd, os.path.pardir, 'resources', 'win64', 'chrome', 'chrome.exe' ),
            'driver': os.path.join(cwd, os.path.pardir, 'resources', 'win64', 'chromedriver.exe' )
        }
    raise OSError('SO not supported')