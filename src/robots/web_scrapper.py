from ast import pattern
import re
from time import sleep
from typing import Callable, Self, TypedDict, override
from contextlib import AbstractContextManager
from urllib.parse import urlparse
from progress.bar import IncrementalBar

from selenium.webdriver import Chrome, ChromeService, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select

from src.robots.read_pdf import ReadPdf
from src.types import Data
from src.utils import get_chrome_resources
from src.constants import Constants, State


class Property(TypedDict):
    locale_property: str
    open_cmd: str
    bar: IncrementalBar


class WebScrapper(AbstractContextManager):

    @staticmethod
    def get_url(path: str):
        domain_path = urlparse(Constants.URL_CAIXA_PAGE)
        return f'{domain_path.scheme}://{domain_path.hostname}{path}'

    @staticmethod
    def __get_cmd(attr: str = 'onclick') -> Callable[[WebElement], str]:
        def lambda_(web_element: WebElement):
            attr_value = web_element.get_attribute(attr)
            return attr_value.replace('javascript:', '') \
                if attr_value \
                else ''
        return lambda_

    def __init__(self):
        self.chrome_resources = get_chrome_resources()
        self.options = ChromeOptions()
        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--proxy-server='direct://'")
        self.options.add_argument("--proxy-bypass-list=*")
        self.options.add_argument("--start-maximized")
        # self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--disable-logging')
        self.options.binary_location = self.chrome_resources['executable']

    def __enter__(self) -> Self:
        self.service = ChromeService(
            executable_path=self.chrome_resources['driver'],
        )
        self.driver = Chrome(
            service=self.service,
            options=self.options,
        )
        self.driver.minimize_window()
        self.wait = WebDriverWait(self.driver, timeout=20)
        return self

    @override
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.driver.quit()
        self.service.stop()

    def __wait_processing(self):
        try:
            div_processando = self.driver.find_element(
                By.XPATH, '//*[@id="div_processando"]')
            sleep(3)
            self.wait.until(lambda _: not div_processando.is_displayed())
        except: pass

    def access_page(self):
        self.driver.get(Constants.URL_CAIXA_PAGE)
        return self

    def select_state(self, state: State):
        self.state = state
        search_input = self.driver.find_element(
            By.XPATH, '//*[@id="cmb_estado"]')
        self.wait.until(lambda _: search_input.is_enabled())
        select = Select(search_input)
        select.select_by_value(self.state['uf'])
        btn_next = self.driver.find_element(By.XPATH, '//*[@id="btn_next1"]')
        btn_next.click()
        self.__wait_processing()
        return self

    def iterate_notices(self):
        links = self.driver.find_elements(
            By.XPATH, '//div[@id="listalicitacoes"]//p[@class="action"]//a[@title="Listar todos os imóveis deste edital"]')
        commands = list(map(WebScrapper.__get_cmd(), links))
        for open_notice_cmd in commands:
            class Notice(TypedDict):
                open_notice_cmd: str
            yield Notice(open_notice_cmd=open_notice_cmd)

    def iterate_all_properties(self, cmd: str, state: State | None = None):
        self.driver.execute_script(cmd)
        self.__wait_processing()
        results = self.driver.find_element(
            By.XPATH, '//div[@id="listalicitacoespaginacao"]')
        self.wait.until(lambda _: results.is_displayed())
        # obter total de propriedades
        all_properties_elem = self.driver.find_element(
            By.XPATH, '//div[@id="listalicitacoes"]/span[1]')
        pattern_all_properties = r'Foram encontrados (\d+) imóveis'
        match_all_properties = re.search(
            pattern_all_properties, all_properties_elem.text)
        self.all_properties = int(match_all_properties.group(
            1)) if match_all_properties else 0
        # obter a paginação
        pagination_anchors = self.driver.find_elements(
            By.XPATH, '//div[@id="paginacao"]//a')
        self.wait.until(lambda _: all([p.is_displayed()
                        for p in pagination_anchors]))
        pagination_anchors_cmds = list(
            map(WebScrapper.__get_cmd('href'), pagination_anchors))
        curr_edital = self.driver.find_element(
            By.XPATH, '//p[@class="hero-description"]')
        edital_pattern = r'(\d+)'
        match_edital = re.search(edital_pattern, curr_edital.text)
        edital_number = match_edital.group(1) if match_edital else 0
        with IncrementalBar(f'Processando edital: {edital_number}', max=self.all_properties) as bar:
            for anchor_cmd in pagination_anchors_cmds:
                yield from self.__iterate_properties(anchor_cmd, bar)
            else:
                st = state if state else self.state
                self.access_page()\
                    .select_state(st)

    def __iterate_properties(self, cmd: str, bar: IncrementalBar):
        self.driver.execute_script(cmd)
        self.__wait_processing()
        result_list = self.driver.find_element(
            By.XPATH, '//div[@id="listalicitacoespaginacao"]')
        self.wait.until(lambda _: result_list.is_displayed())
        properties = self.driver.find_elements(
            By.XPATH, '//div[@id="listalicitacoespaginacao"]//ul[@class="control-group no-bullets"]')

        properties_anchors_locale = list(map(lambda anc_loc: (
            anc_loc.find_element(
                By.XPATH, './/div[@class="control-item control-span-5_12"]//a'),
            anc_loc.find_element(
                By.XPATH, './/div[@class="dadosimovel-col2"]//div[@class="control-item control-span-12_12"]/span/font')
        ), properties))
        pattern_loc = r'([A-Z]+\s[A-Z]+.*[A-Z]+)'
        get_loc: Callable[[str], str] = lambda s: re.search(pattern_loc, s).group(  # type: ignore
            1) if re.search(pattern_loc, s) else ''
        properties_cmd_loc = list(
            map(lambda anc_loc: (
                WebScrapper.__get_cmd()(anc_loc[0]),
                get_loc(anc_loc[1].text)
            ), properties_anchors_locale))
        for cmd, loc in properties_cmd_loc:
            yield Property(locale_property=loc, open_cmd=cmd, bar=bar)

    def open_property(self, prop: Property, contains: Callable[[str], bool]) -> Data | None:
        try:
            data: Data = {
                'cpf': None,
                'nome': None,
                'item': None,
                'edital': None,
                'endereco': None,
                'valor': None,
            }
            self.driver.execute_script(prop['open_cmd'])
            self.__wait_processing()
            # obtendo elementos
            edital_elem = self.driver.find_element(
                By.XPATH, '//*[@id="dadosImovel"]//div[@class="related-box"]//span[1]')
            item_elem = self.driver.find_element(
                By.XPATH, '//*[@id="dadosImovel"]//div[@class="related-box"]//span[2]')
            valor: dict = self.driver.execute_script(
                'return document.evaluate(\'//*[@id="dadosImovel"]//div[@class="content"]/p[1]/text()[1]\', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;')
            endereco: dict = self.driver.execute_script(
                'return document.evaluate(\'//*[@id="dadosImovel"]//div[@class="related-box"]//p/strong[text()="Endereço:"]/following-sibling::text()\', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;')
            # padrões de expressões
            pattern_num_item = r'Número do item: ?(\d+)'
            pattern_edital = r'(Edital Único.*)'
            pattern_valor = r'Valor de avaliação:\s*R?\$?\s*([\d\.,]+)'
            # compilando padrões com valores
            item_match = re.search(pattern_num_item, item_elem.text)
            edital_match = re.search(pattern_edital, edital_elem.text)
            valor_match = re.search(pattern_valor, valor['data'])
            # atribuindo ao objeto de retorno
            data['item'] = item_match.group(1) if item_match else ''
            data['edital'] = edital_match.group(1) if edital_match else ''
            data['endereco'] = endereco['data']
            data['valor'] = float(valor_match.group(1).replace(
                '.', '').replace(',', '.')) if valor_match else None
            if contains(endereco['data']):
                return
            # link matricula
            link_matricula_elem = self.driver.find_element(
                By.XPATH, '//*[@id="dadosImovel"]//div[@class="related-box"]//a[text()="Baixar matrícula do imóvel"]')
            cmd_path = link_matricula_elem.get_attribute('onclick')
            cmd_path = cmd_path if cmd_path else ''
            pattern_path = r'javascript:ExibeDoc\(\'(.*)\'\)'
            path_match = re.search(pattern_path, cmd_path)
            path = path_match.group(1) if path_match else ''
            url = WebScrapper.get_url(path)
            # baixando pdf e lendo dados
            read_pdf = ReadPdf(url).get_name_and_cpf_ai()
            data['cpf'] = read_pdf['cpf']
            data['nome'] = read_pdf['nome']
            return data
        except Exception as e:
            raise e
        finally:
            btn_voltar = self.driver.find_element(
                By.XPATH, '//*[@id="dadosImovel"]//ul[@class="form-set no-bullets"]/span/a')
            btn_voltar.click()
            self.__wait_processing()


# if __name__ == '__main__':
#     with WebScrapper() as ws:
#         ws = ws.access_page()\
#             .select_state(Constants.STATES[0])
#         all_props = 0
#         for notice in ws.iterate_notices():
#             for prop in ws.iterate_all_properties(notice['open_notice_cmd']):
#                 data = ws.open_property(prop)
