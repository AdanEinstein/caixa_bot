import io
import re
import fitz
import pytesseract
import requests
from openai import OpenAI
from openai.types.chat.chat_completion import Choice
from PIL import Image
from typing import TypedDict

from src.constants import Constants


class NameCpf(TypedDict):
    nome: str | None
    cpf: str | None


class ReadPdf:

    def __init__(self, pdf_url: str):
        self.pdf_url = pdf_url

    def __get_pdf(self):
        response = requests.get(self.pdf_url, headers={
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36',
        }, stream=True)
        if response.status_code != 200:
            return
        return response.content

    def __open_pdf(self):
        pdf_bytes = self.__get_pdf()
        if pdf_bytes is None:
            raise requests.RequestException('pdf indisponível')
        return fitz.open(stream=io.BytesIO(pdf_bytes), filetype='pdf')
    
    def __to_text(self) -> str:
        full_text = ''
        with self.__open_pdf() as pdf:
            for page_num in range(len(pdf)):
                page = pdf.load_page(page_num)
                display = page.get_displaylist()
                pix = display.get_pixmap()
                with Image.frombytes("RGB", [pix.width, pix.height], pix.samples) as img:
                    full_text += pytesseract.image_to_string(img)
        return full_text

    # def get_name_and_cpf(self):
    #     try:
    #         with self.__open_pdf() as pdf:
    #             pattern_nome_cpf = r'([A-Z]+(?:\s[A-Z]+)+).{0,10}CPF.{0,10}(\d{3}\.\d{3}\.\d{3}\-\d{2})'
    #             for page_num in range(len(pdf)):
    #                 page = pdf.load_page(page_num)
    #                 display = page.get_displaylist()
    #                 pix = display.get_pixmap()
    #                 with Image.frombytes("RGB", [pix.width, pix.height], pix.samples) as img:
    #                     text = pytesseract.image_to_string(img)
    #                     nome_cpf_match = re.findall(pattern_nome_cpf, text, flags=re.MULTILINE)
    #                     if nome_cpf_match and len(nome_cpf_match[0]) >= 2:
    #                         nome = nome_cpf_match[0][0].replace('\n', ' ').replace('n', '').strip()
    #                         cpf = nome_cpf_match[0][1]
    #                         if not nome or not cpf: continue
    #                         return NameCpf(nome=nome, cpf=cpf)
    #             return NameCpf(cpf=None, nome=None)
    #     except requests.RequestException:
    #         return NameCpf(cpf=None, nome=None)

    def get_name_and_cpf_ai(self):
        try:
            pattern_nome_cpf = r'([A-Z]+(?:\s[A-Z]+)+).*(\d{3}\.\d{3}\.\d{3}\-\d{2})'
            content = self.__to_text()
            with OpenAI(api_key=Constants.OPENAI_API_KEY) as model:
                stream = model.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é um assistente útil."},
                        {"role": "user", "content": f"Contexto: {Constants.OPENAI_API_CONTEXT}"},
                        {"role": "user", "content": content}
                    ],
                    stream=True
                )
                content = ''
                for chunk in stream:
                    if chunk.choices[0].delta.content is not None:
                        content += chunk.choices[0].delta.content
                nome_match = re.search(pattern_nome_cpf, f'{content}')
                cpf_match = re.search(pattern_nome_cpf, f'{content}')
                if nome_match and cpf_match:
                    nome = nome_match.group(1).replace('\n', ' ').replace('n', '').replace('CPF', '').strip()
                    cpf = cpf_match.group(2)
                    return NameCpf(nome=nome, cpf=cpf)
            return NameCpf(cpf=None, nome=None)
        except requests.RequestException:
            return NameCpf(cpf=None, nome=None)