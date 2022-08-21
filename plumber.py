import pdfplumber, math
from PyPDF2 import PdfFileReader


def calculate_cost(file_path):
    with open(file_path, "rb") as pdf:
        no_of_pages = PdfFileReader(pdf).numPages

    with pdfplumber.open(file_path) as pdf:
        for i in range(no_of_pages):
            first_page = pdf.pages[i]
            imgData = first_page.images

    # with open(file_path, "rb") as pdf:
    #     pages = PdfFileReader(pdf).numPages

    page_area = 499897.84 
    area = 0

    for i in range(len(imgData)):
        area += (imgData[i]['x1']-imgData[i]['x0'])*(imgData[i]['y1']-imgData[i]['y0'])

    area = float(area)
    # setting the fully occupied image file will cost 10 rs, we can now calculate pdf cost

    cost = 9*(area/(page_area*no_of_pages)) + no_of_pages
    
    return math.floor(cost)


