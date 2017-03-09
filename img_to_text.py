import csv
from io import open, BytesIO
import pytesseract
import PyPDF2
from PIL import Image


def pdf_to_text(path):
    """given a path returns a string formed by picture,
    taken from the document
    :param path:
    :return: data
    """
    input1 = PyPDF2.PdfFileReader(open(path, "rb"))
    page0 = input1.getPage(0)
    x_object = page0['/Resources']['/XObject'].getObject()
    for obj in x_object:
        size = (x_object[obj]['/Width'], x_object[obj]['/Height'])
        data = x_object[obj].getData()
        if x_object[obj]['/ColorSpace'] == '/DeviceRGB':
            mode = "RGB"
        else:
            mode = "P"
        if x_object[obj]['/Filter'] == '/FlateDecode':
            img = Image.frombytes(mode, size, data)
            image = img.point(lambda x: 0 if x < 113 else 255)
            width, height = image.size
            frame1 = image.crop((width / 4, 50, width/2, height))
            frame2 = image.crop((width / 2, 50, width, height))
            if pytesseract.image_to_string(image) != 'ANALYTICS':
                return pytesseract.image_to_string(frame1), pytesseract.image_to_string(frame2)
            else:
                pass


def if_another_pdf(path):
    """if you can't fetch the image the first method, then use this function
    :param path:
    :return: data
    """
    pdf = open(path, "rb").read()
    startmark = b'\xff\xd8'
    startfix = 0
    endmark = b'\xff\xd9'
    endfix = 2
    i = 0

    for count in range(1):
        istream = pdf.find('stream'.encode(), i)
        if istream < 0:
            break
        istart = pdf.find(startmark, istream, istream + 20)
        if istart < 0:
            i = istream + 20
            continue
        iend = pdf.find('endstream'.encode(), istart)
        if iend < 0:
            raise Exception("Didn't find end of stream!")
        iend = pdf.find(endmark, iend - 20)
        if iend < 0:
            raise Exception("Didn't find end of JPG!")

        istart += startfix
        iend += endfix
        jpg = pdf[istart:iend]
        img = Image.open(BytesIO(jpg))
        image = img.point(lambda x: 0 if x < 113 else 255)
        width, height = image.size
        frame1 = image.crop((width / 4, 50, width / 2, height))
        frame2 = image.crop((width / 2, 50, width, height))

    return pytesseract.image_to_string(frame1), pytesseract.image_to_string(frame2)


def scrape():
    """extracted information and write it to the file
    :return: the data file
    """
    ticker = LEFT_LINE.split('\n\n')[0].replace(' ', '')
    recent_price = LEFT_LINE.split('\n\n')[1].replace(' ', '')
    market_cap = LEFT_LINE.split('\n\n')[2].replace(' ', '')
    forecast = RIGHT_LINE.replace('\n\n', ' ')
    with open('ready.csv', 'w', encoding='utf8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(('Ticker', 'Recent Price', 'Market Cap', 'Forecast'))
        writer.writerow((ticker, recent_price, market_cap, forecast))

if __name__ == '__main__':
    try:
        PATH_TO_FILE = input('Enter the path to the file: ')
        LEFT_LINE, RIGHT_LINE = pdf_to_text(PATH_TO_FILE)
        scrape()
    except KeyError:
        LEFT_LINE, RIGHT_LINE = if_another_pdf(PATH_TO_FILE)
        scrape()
    print('Ready!')
