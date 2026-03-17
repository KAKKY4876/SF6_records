import time
import get_battle_logs
import get_act_data
import get_battle_stats

class Task:
    def __init__(self, name, interval, func):
        self.name = name
        self.interval = interval
        self.func = func
        self.last_run = 0
        self.running = False

    def should_run(self, now):
        return now - self.last_run >= self.interval

    def run(self):
        if self.running:
            print(f"[{self.name}] スキップ（実行中）")
            return

        self.running = True
        start = time.time()

        try:
            print(f"[{self.name}] 開始")
            self.func()
            print(f"[{self.name}] 完了")

        except Exception as e:
            print(f"[{self.name}] エラー:", e)

        finally:
            # 実行終了時刻で更新（ズレ防止）
            self.last_run = time.time()
            self.running = False
            print(f"[{self.name}] 実行時間: {time.time() - start:.2f}秒")


# タスク定義
tasks = [
    Task("battle_logs", 3600, get_battle_logs.main),
    Task("act_data", 3700, get_act_data.main),
    Task("battle_stats", 86400, get_battle_stats.main),
]

print("=== Worker Start ===")

while True:
    now = time.time()

    for task in tasks:
        if task.should_run(now):
            task.run()

    time.sleep(5)