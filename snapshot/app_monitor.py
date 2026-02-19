from pathlib import Path
from decouple import config
from datetime import datetime
import json

from AppKit import NSWorkspace
from Foundation import NSObject
from PyObjCTools import AppHelper
import objc


APP_USAGE_LOGS = Path(config('APP_USAGE_LOGS'))

def save_app_logs(data: dict):
    if APP_USAGE_LOGS.exists():
        with open(APP_USAGE_LOGS, 'r', encoding='utf-8') as app_log:
            app_data = json.load(app_log)
    else:
        app_data = []
    app_data.append(data)
    with open(APP_USAGE_LOGS, 'w', encoding='utf-8') as app_log:
        json.dump(app_data, app_log, ensure_ascii=False, indent=2)

class AppObserver(NSObject):
    def appLaunched_(self, notification):
        app = notification.userInfo()['NSWorkspaceApplicationKey']
        app_name = app.localizedName()
        pid = app.processIdentifier()

        print(f'LAUNCHED: {app_name}, :::::: {pid}')

        log_data = {
            'APPNAME' : app_name,
            'PID' : pid,
            'BEGIN' : datetime.now().strftime('%y-%m-%d %H:%M:%S')
        }
        save_app_logs(log_data)

if __name__ == "__main__":
    workspace = NSWorkspace.sharedWorkspace()
    notification_center = workspace.notificationCenter()

    observer = AppObserver.alloc().init()

    notification_center.addObserver_selector_name_object_(observer, b"appLaunched:", "NSWorkspaceDidLaunchApplicationNotification", None)

    print("App launch monitor started...")
    AppHelper.runConsoleEventLoop()