
import time
import threading

from PTTLibrary import PTT
import Notification
import Menu
import Log


class Core(object):
    def __init__(
        self,
        SystemTray,
        ConfigObj,
        MenuObj,
        ID,
        PW
    ):
        self._SysTray = SystemTray
        self._Notification = Notification.Notification(
            SystemTray,
            ConfigObj
        )
        self._ConfigObj = ConfigObj
        self._MenuObj = MenuObj

        self._ID = ID
        self._PW = PW

        self._ThreadRun = True
        self._LoginStatus = False

    def start(self):
        Thread = threading.Thread(
            target=self.TrackThread,
            daemon=True
        )
        Thread.start()

    def stop(self):
        self._ThreadRun = False

    def isStop(self):
        return self._PTTBot is None

    def TrackThread(self):

        self._PTTBot = PTT.Library()

        Recover = False
        while self._ThreadRun:

            try:
                self._PTTBot.login(self._ID, self._PW)
            except PTT.Exceptions.LoginError:
                self._PTTBot.log('登入失敗')
                if Recover:
                    self._Notification.throw('uPTT', '重新登入失敗')
                else:
                    self._Notification.throw('uPTT', '登入失敗')
                self._PTTBot = None
                self._LoginStatus = False
                self._MenuObj.setMenu(Menu.Type.Login)
                return

            self._MenuObj.setMenu(Menu.Type.Logout)

            if Recover:
                self._PTTBot.log('重新登入成功')
                self._Notification.throw('uPTT', '重新登入成功')
            else:
                self._PTTBot.log('登入成功')
                self._Notification.throw('uPTT', '登入成功')

            Recover = False
            self._LoginStatus = True

            ShowNewMail = False
            try:
                while True:

                    # Log.log(
                    #     'uPTT Core',
                    #     Log.Level.INFO,
                    #     '進入等待區'
                    # )
                    StartTime = EndTime = time.time()
                    while EndTime - StartTime < self._ConfigObj.QueryCycle:
                        # 優先操作層
                        if not self._ThreadRun:
                            Log.log(
                                'uPTT Core',
                                Log.Level.INFO,
                                '登出'
                            )
                            self._MenuObj.setMenu(Menu.Type.Login)
                            self._PTTBot.logout()
                            self._PTTBot = None
                            break

                        # 未來實作
                        # 丟水球

                        time.sleep(0.1)
                        EndTime = time.time()

                    # Log.log(
                    #     'uPTT Core',
                    #     Log.Level.INFO,
                    #     '等待區結束'
                    # )
                    if self._PTTBot is None:
                        break

                    if self._PTTBot.hasNewMail():
                        if not ShowNewMail:
                            Log.log(
                                'uPTT Core',
                                Log.Level.INFO,
                                '你有新信件'
                            )
                            self._Notification.throw('uPTT', '你有新信件')
                            self._SysTray.setToolTip('uPTT - 你有新信件')
                        ShowNewMail = True
                    else:
                        self._SysTray.setToolTip('uPTT - 無新信件')
                        ShowNewMail = False
            except:
                Recover = True
                for s in range(5):
                    Log.showValue(
                        'uPTT Core',
                        Log.Level.INFO,
                        '啟動恢復機制',
                        5 - s
                    )
                    time.sleep(1)

            self._PTTBot = None
        self._Notification.throw('uPTT', '登出成功')
