import requests
from bs4 import BeautifulSoup
from fpdf import FPDF
from django.http import FileResponse, HttpResponse
from django.shortcuts import render
from io import BytesIO

def home(request):
    return render(request, 'scrape/home.html')

def scrape_pdf(request):
    url = 'https://maxwellstampltd.com/services/'
    response = requests.get(url)

    if response.status_code != 200:
        return HttpResponse("Failed to fetch the webpage", status=500)

    soup = BeautifulSoup(response.content, 'html.parser')##

    items = []

    #---------------
    titles = soup.find_all('h4', class_='bt_bb_headline_tag')
    descriptions = soup.find_all('div', class_='bt_bb_headline_subheadline')

    for title_tag, desc_tag in zip(titles, descriptions):
        a_tag = title_tag.find('a')
        title = a_tag.get_text(strip=True) if a_tag else title_tag.get_text(strip=True)
        desc = desc_tag.get_text(strip=True)
        items.append((title, desc))

    if not items:
        for h in soup.find_all('h4'):
            title = h.get_text(strip=True)
            next_p = h.find_next_sibling('p')
            desc = next_p.get_text(strip=True) if next_p else ''
            items.append((title, desc))

    if not items:
        return HttpResponse("No service data found", status=404)

##pdf section
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Maxwell Stamp Ltd - Services", ln=True, align='C')
    pdf.ln(10)

    def clean_text(text):
        import unicodedata
        return unicodedata.normalize('NFKD', text).encode('latin-1', errors='ignore').decode('latin-1')

    for idx, (title, desc) in enumerate(items, 1):
        pdf.set_font("Arial", "B", 12)
        pdf.multi_cell(0, 10, f"{idx}. {clean_text(title)}")
        if desc:
            pdf.set_font("Arial", size=11)
            pdf.multi_cell(0, 10, f"   {clean_text(desc)}")
        pdf.ln(5)

    buffer = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    buffer.write(pdf_bytes)
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename='MSL_services.pdf')


