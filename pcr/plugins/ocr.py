from PIL import Image
import pytesseract
import cv2
import re


def preprocess(img_path: str):
    img = Image.open(img_path).convert('RGB')
    width, height = img.size
    img = img.crop((width*0.7, height*0.25, width*0.9, height*0.9))  # 截取需要的部分

    datas = img.getdata()
    newData = []
    for item in datas:
        if (item[0] + item[1]) / (item[2] + 1) >= 3:  # 将图片黄色部分替换为纯黑
            newData.append((0, 0, 0))
        else:
            newData.append(item)  # 其余部分不变
    img.putdata(newData)
    img.save("intermediate.jpg", "JPEG")

    image = cv2.imread("intermediate.jpg")
    gray = image * 1.5 - 100  # 增加对比度

    filename = "output.png"  # 写至 output.png
    cv2.imwrite(filename, gray)


def recognize_text(img_path: str):
    pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract.exe'
    tessdata_dir_config = '--tessdata-dir "C:/Program Files (x86)/Tesseract-OCR/tessdata"'

    preprocess(img_path)

    img = Image.open('output.png')
    text: str = pytesseract.image_to_string(img, lang='chi_sim', config=tessdata_dir_config)
    print(text)
    record_list: list = process_text(text)

    print(record_list)


def process_text(text: str):
    text = text.replace(' ', '')
    split = re.split('\n\n+', text)  # 以空白行分割字符串
    filtered = list(filter(lambda t: '伤害' in t or '造成了' in t, split))  # 必须包含伤害 或 造成了
    record_list = list()
    for record in filtered:
        record_split = re.split('\n', record)
        if len(record_split) != 3:  # 必须是3行
            continue
        username = record_split[0].replace('对', '')
        target = record_split[1].replace('造成了', '')
        damage = re.findall(r'\d+', record_split[2])[0]
        record_list.append([username, target, damage])
    print(record_list)
    return record_list


if __name__ == '__main__':
    recognize_text('../../test/10.png')
