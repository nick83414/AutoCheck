import requests
import json
import os
from bs4 import BeautifulSoup

LINE_TOKEN = os.environ["LINE_TOKEN"]
USER_ID = "Ua7aa35fba69573bb0b679da49f6c293e"

URLS = {
    "2/7": "https://www.ms-aurora.com/abashiri/reserves/new_next.php?ynj=2026-2-7#reserves_from",
    "2/27": "https://www.ms-aurora.com/abashiri/reserves/new_next.php?ynj=2026-2-27#reserves_from",
    "2/28": "https://www.ms-aurora.com/abashiri/reserves/new_next.php?ynj=2026-2-28#reserves_from",
    "3/1":  "https://www.ms-aurora.com/abashiri/reserves/new_next.php?ynj=2026-3-1#reserves_from"
}

STATE_FILE = "notified.json"


def load_notified():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))


def save_notified(data):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(data)), f, ensure_ascii=False, indent=2)


def send_line(message):
    headers = {
        "Authorization": f"Bearer {LINE_TOKEN}",
        "Content-Type": "application/json"
    }

    data = {
        "to": USER_ID,
        "messages": [
            {"type": "text", "text": message}
        ]
    }

    r = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=data,
        timeout=10
    )

    print("LINE:", r.status_code, r.text)

def get_available_slots(label, url):
    res = requests.get(url, timeout=10)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.find("table", id="GridView1")
    if not table:
        return []

    result = []
    for row in table.find_all("tr")[1:]:
        tds = row.find_all("td")
        if len(tds) < 2:
            continue

        time_text = tds[0].get_text(strip=True)
        status = tds[1].get_text(strip=True)

        if status in ("○", "△"):
            text = f"{label} {time_text}（{status}）"
            result.append((text, url))

    return result

def main():
    notified = load_notified()
    new_items = []

    for label, url in URLS.items():
        for text, link in get_available_slots(label, url):
            if text not in notified:
                new_items.append((text, link))
                notified.add(text)

    if new_items:
        lines = ["🎉 發現新的可預約班次！\n"]
        for text, link in new_items:
            lines.append(text)
            lines.append(f"👉 {link}")
            lines.append("")

        message = "\n".join(lines)
        send_line(message)
        save_notified(notified)
    else:
        print("沒有新的空位")


if __name__ == "__main__":
    main()
