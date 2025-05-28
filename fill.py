import csv
import re

REGS = [
    re.compile(r"Mission text message (\d+)"),
    re.compile(r"Accepted Quest Character Message (\d+)"),
    re.compile(r"カレンダーメッセージ(\d+)"),
    re.compile(r"tTemporarymessage"),
    re.compile(r"\[9999\]NULL#00＠DummyVoice"),
]

with open("dlc.csv", "r", encoding="utf-8") as f:
    with open("dlc_o.csv", "w", encoding="utf-8", newline="") as f2:
        reader = csv.reader(f)
        writer = csv.writer(f2)
        for row in reader:
            for reg in REGS:
                res = reg.match(row[2])
                if res:
                    print(res)
                    row[3] = row[2]
            writer.writerow(row)
