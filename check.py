import requests
import time
from bs4 import BeautifulSoup

LINE_TOKEN = "KmUhMZQ+k0BaM4pIMkfTYGAR7lpn+hAIbMv2k0hAfl52+TxOpQwx/5GzrGZOn0VZONEaE4o8qkvCnO82IMi0k+RS7MSxngHMdomoEjqTPAHiY1otVWMSYkCFKGnVcJ1juJNHDuDu0xxjgPq1uFK4AQdB04t89/1O/w1cDnyilFU="
USER_ID = "Ua7aa35fba69573bb0b679da49f6c293e"

URLS = {
    "2/27": "https://www.ms-aurora.com/abashiri/reserves/new_next.php?ynj=2026-2-7#reserves_from",
    "2/28": "https://www.ms-aurora.com/abashiri/reserves/new_next.php?ynj=2026-2-28#reserves_from",
    "3/1": "https://www.ms-aurora.com/abashiri/reserves/new_next.php?ynj=2026-3-1#reserves_from"
}

def send_line(message):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}"
    }
    data = {
        "to":USER_ID,
        "messages":[
            {
                "type":"text",
                "text":message
            }
        ]
    }
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=data,
        timeout=10
    )

def get_available_slots(label, url):
    res = requests.get(url, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", id="GridView1")
    if not table:
        return []

    available = []
    rows = table.find_all("tr")[1:]

    for row in rows:
        tds = row.find_all("td")
        if len(tds) < 2:
            continue

        time_text = tds[0].get_text(strip=True)
        status = tds[1].get_text(strip=True)

        if status in ("○", "△"):
            available.append(f"{label} {time_text}（{status}）")

    return available

if __name__ == "__main__":
    notified = set()

    while True:
        try:
            all_new_slots = []

            for label, url in URLS.items():
                slots = get_available_slots(label, url)

                for s in slots:
                    if s not in notified:
                        all_new_slots.append(s)
                        notified.add(s)

            if all_new_slots:
                message = "🎉 發現可預約班次！\n" + "\n".join(all_new_slots)
                send_line(message)
                print("已通知：", all_new_slots)
            else:
                print("目前都沒有新空位")

        except Exception as e:
            print("錯誤：", e)

        time.sleep(600)  # 每 10 分鐘
