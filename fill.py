import csv
import re

REG_1 = re.compile(r"Mission text message (\d+)")
REG_2 = re.compile(r"Accepted Quest Character Message (\d+)")
REG_3 = re.compile(r"カレンダーメッセージ(\d+)")

with open("bundle.csv", "r", encoding="utf-8") as f:
    with open("bundle_o.csv", "w", encoding="utf-8", newline="") as f2:
        reader = csv.reader(f)
        writer = csv.writer(f2)
        for row in reader:
            res1 = REG_1.match(row[2])
            res2 = REG_2.match(row[2])
            res3 = REG_3.match(row[2])

            if res1:
                print(res1.group(1))
                row[3] = row[2]
            if res2:
                print(res2.group(1))
                row[3] = row[2]
            if res3:
                print(res3.group(1))
                row[3] = row[2]
            writer.writerow(row)
