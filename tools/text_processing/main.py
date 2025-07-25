import csv

# 提取文件中 `-------------start------------` 和 `-------------end------------` 之间的内容
def extract_content(file_path):
    content = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        extracting = False
        buffer = []
        for line in lines:
            line = line.strip()
            if line == "-------------start------------":
                extracting = True
                buffer = []  # 清空缓冲区
            elif line == "-------------end------------":
                extracting = False
                content.append(' '.join(buffer))  # 将缓冲区内容作为一条记录
            elif extracting:
                buffer.append(line)
    return content

# 写入CSV文件
def write_csv(file0_content, file1_content, file2_content, output_file):
    with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['日期', '内容', '标签'])  # 添加表头
        for line0, line1, line2 in zip(file0_content, file1_content, file2_content):
            writer.writerow([line0, line1, line2])

# 文件路径
file0_path = 'date.txt'
file1_path = 'sentences.txt'
file2_path = 'result.txt'
output_csv = 'output.csv'

# 执行脚本
file0_content = extract_content(file0_path)
file1_content = extract_content(file1_path)
file2_content = extract_content(file2_path)
print(len(file1_content))
print(len(file2_content))
if len(file0_content) == len(file1_content) and len(file1_content) == len(file2_content):
    write_csv(file0_content, file1_content, file2_content, output_csv)
    print(f"文件已成功合并并保存到 {output_csv}")
else:
    print("文件1和文件2的行数不同，无法合并。")