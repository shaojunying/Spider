import datetime
import logging
import os
import re

import math
import pandas as pd
import pdfplumber

pdf_dir_path = "todo"
done_dir_path = "done"

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
logger = logging.getLogger('my_module_name')
logger.setLevel(logging.INFO)

df = None

def get_pdf_text(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text


def load_word_from_file():
    words = []
    df = pd.read_excel("words.xlsx", header=0)
    for index, row in df.iterrows():
        for i in range(row.size):
            if type(row[i]) == float and math.isnan(row[i]):
                continue
            words.append(row[i])
    return words


def process(pdf_file_name, words, category_path, company):
    global df
    file_path = category_path + "/" + company + "/" + pdf_file_name
    logger.info("开始处理: " + file_path)
    # 打开pdf文件
    pdf_text = get_pdf_text(os.path.join(pdf_dir_path, file_path))

    company_code, company_name = parse_company(company)
    year = get_year(pdf_file_name)
    row = {"公司代码": company_code, "公司名称": company_name, "年份": year, "分类": category_path, "文件名": pdf_file_name}
    for i in range(len(words)):
        word = words[i]
        count = pdf_text.count(word)
        row[word] = count
    df = df.append(row, ignore_index=True)
    # df[company_name + "/" + pdf_file_name] = count_list
    df.to_excel("output.xlsx", index=False)
    # 将pdf_file移动到已处理文件夹
    if not os.path.exists(os.path.join(done_dir_path, category_path, company)):
        os.makedirs(os.path.join(done_dir_path, category_path, company))
    os.rename(os.path.join(pdf_dir_path, file_path),
              os.path.join(done_dir_path, file_path))
    logger.info(f"已完成文件{pdf_file_name}的统计")


def parse_company(company):
    index = company.find("--")
    if index == -1:
        return "", ""
    return company[:index], company[index + 2:]


def get_year(file_name):
    pattern = re.compile(r'\d{4}')
    match = pattern.search(file_name)
    if match:
        return match.group()
    return ""


def main():
    words = load_word_from_file()
    global df
    df = pd.DataFrame(columns=["公司代码", "公司名称", "年份", "分类", "文件名"] + words)
    if os.path.exists("output.xlsx"):
        df = pd.read_excel("output.xlsx", converters={'公司代码': str, '公司名称': str, '年份': str, '分类': str, '文件名': str})

    logger.info("开始时间: " + str(datetime.datetime.now()))

    # 遍历pdf_path下的所有pdf文件
    for category_path in os.listdir(pdf_dir_path):
        if category_path.startswith("."):
            continue
        for company_name in os.listdir(os.path.join(pdf_dir_path, category_path)):
            if company_name.startswith("."):
                continue
            for pdf_file_name in os.listdir(os.path.join(pdf_dir_path, category_path, company_name)):
                if pdf_file_name.startswith("."):
                    continue
                process(pdf_file_name, words, category_path, company_name)

    logger.info("结束时间: " + str(datetime.datetime.now()))


if __name__ == '__main__':
    main()
