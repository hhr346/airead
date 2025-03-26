from PyPDF2 import PdfReader, PdfWriter
import pikepdf

# 打开原PDF文件
input_pdf = "D:\\看论文\\2404.07073v2.pdf"
output_pdf = "D:\\看论文\\extracted.pdf"

reader = PdfReader(input_pdf)
writer = PdfWriter()

# 提取前23页
for page_num in range(23):  # 提取第1到23页（页码从0开始）
    writer.add_page(reader.pages[page_num])

# 保存新PDF文件
with open(output_pdf, "wb") as output_file:
    writer.write(output_file)
print("新文件保存成功！")


input_pdf = "前23页.pdf"
output_pdf = "压缩后的文件.pdf"

# 打开PDF文件
with pikepdf.open(input_pdf) as pdf:
    # 压缩PDF，设置压缩级别
    pdf.save(output_pdf, compress_streams=True)

print("PDF文件已成功压缩并保存！")
