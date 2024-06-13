# тут будет обработчик, который будет читать файлы и вставлять их в контекст. 
# расширения с которыми планирую работать: .txt .pdf .sh .cpp .h .c .sql .json .xml .
# планирую сделать ограничение до 1мб ~= 1.000.000.000 символов, более чем достаточно 


# importing required modules 
from pypdf import PdfReader 
  
# creating a pdf reader object 
reader = PdfReader('example.pdf') 
  
# printing number of pages in pdf file 
print(len(reader.pages)) 
  
# getting a specific page from the pdf file 
page = reader.pages[0] 
  
# extracting text from page 
text = page.extract_text() 
print(text) 