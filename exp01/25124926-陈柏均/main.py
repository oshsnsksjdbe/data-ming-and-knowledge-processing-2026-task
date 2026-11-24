# 实验一：从 90 万条 Amazon 训练集抽取 5000 条，供课程 run_lab.py 训练 window=2/5 词向量
# 说明：训练与评估调用课程提供的 run_lab.py，未修改其内容
import csv, hashlib, random
from pathlib import Path

BASE = Path(__file__).resolve().parent          # main.py 所在目录
SRC  = BASE.parent / "data" / "amazon_train_local.csv"  # 手动下载的原始数据（标签 0/1）
DST  = BASE.parent / "data" / "train_sample_5000.csv"    # 输出：5000 条、标签 1/2

if not SRC.exists():
    raise SystemExit(f"找不到源数据：{SRC}（需自行下载 Amazon 训练集放到该路径）")

SIZE  = 5000 #抽取5000条
SEED  = 42 #随机种子

LABEL_MAP = {"0": 1, "1": 2}   #原来差评是0，好评是1，现在要更改为差评是1，好评是2

rng       = random.Random(SEED) #随机数生成器
reservoir = []      # 空列表，存被选中的行，最多存5000条数据
seen      = set()   # 存已被处理的内容的摘要
eligible  = 0       # 已处理的合格行数，计数器

with SRC.open(encoding="utf-8-sig", newline="") as f: #用此格式打开
    reader = csv.reader(f) 
    header = next(reader) 
    assert len(header) == 3 and header == ["label","title","content"], header #检查表头是不是这三个标签，如果不是直接报错
    for row in reader: #循环处理每一行的内容
        if len(row)!=3 or row[0] not in LABEL_MAP: #不等于三列的直接毙掉，当然下载下来的列数已经符合要求了
            continue
        key = hashlib.sha256((row[1] + "\x00" + row[2]).encode()).digest()
        if key in seen:
            continue #去重，跳过
        seen.add(key)
        eligible += 1  # 合格的条数加 1

        if len(reservoir) < SIZE: #还没到5000条
            reservoir.append(row)
        else: #已到达5000条，蓄水池已满
            j = rng.randrange(eligible)
            if j < SIZE:
                reservoir[j] = row

assert len(reservoir) == SIZE, f"只抽到 {len(reservoir)} 条，不足 {SIZE}"  # 抽不满直接失败，不留半拉数据

with DST.open("w", encoding="utf-8", newline="") as f: #写入文件
    writer = csv.writer(f)
    writer.writerow(["label", "title", "content"]) #写表头
    for row in reservoir: #蓄水池里留下的5000条
        writer.writerow([LABEL_MAP[row[0]], row[1], row[2]]) #把1改成2，把0改成1

print(f"eligible={eligible} saved={len(reservoir)} -> {DST}")
