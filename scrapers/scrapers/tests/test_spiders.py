import pytest
from scrapy.http import HtmlResponse
from scrapers.spiders.glass_spider import GlassSpider

def test_parse():
    spider = GlassSpider()
    url = "https://www.france-optique.com/gravures/fournisseur=2399"
    body = """
    <div class="row tr group">
        Catégorie 1
    </div>
    <div class="row tr">
        <div class="col s4 m4"><p>Verre 1</p></div>
        <div class="col s1 m1"><p class="gravure_txt"><b>Gravure 1</b></p></div>
        <div class="col s1 m1"></div>
        <div class="col s1 m1"><p>Indice 1</p></div>
        <div class="col s1 m1"><p>Matériau 1</p></div>
    </div>
    """
    def test_parse():
        spider = GlassSpider()
        url = "https://www.france-optique.com/gravures/fournisseur=2399"
        body = """
        <div class="row tr group">
            Catégorie 1
        </div>
        <div class="row tr">
            <div class="col s4 m4"><p>Verre 1</p></div>
            <div class="col s1 m1"><p class="gravure_txt"><b>Gravure 1</b></p></div>
            <div class="col s1 m1"></div>
            <div class="col s1 m1"><p>Indice 1</p></div>
            <div class="col s1 m1"><p>Matériau 1</p></div>
        </div>
        """
        response = HtmlResponse(url=url, body=body, encoding='utf-8')
        results = list(spider.parse(response))
        
        assert len(results) == 1
        item = results[0]
        assert item['category'] == 'Catégorie 1'
        assert item['glass_name'] == 'Verre 1'
        assert item['nasal_engraving'] == 'Gravure 1'
        assert item['glass_index'] == 'Indice 1'
        assert item['material'] == 'Matériau 1'
        assert item['glass_supplier_id'] == '2399'

    def test_parse_no_engraving():
        spider = GlassSpider()
        url = "https://www.france-optique.com/gravures/fournisseur=2399"
        body = """
        <div class="row tr group">
            Catégorie 2
        </div>
        <div class="row tr">
            <div class="col s4 m4"><p>Verre 2</p></div>
            <div class="col s1 m1"></div>
            <div class="col s1 m1"></div>
            <div class="col s1 m1"><p>Indice 2</p></div>
            <div class="col s1 m1"><p>Matériau 2</p></div>
        </div>
        """
        response = HtmlResponse(url=url, body=body, encoding='utf-8')
        results = list(spider.parse(response))
        
        assert len(results) == 1
        item = results[0]
        assert item['category'] == 'Catégorie 2'
        assert item['glass_name'] == 'Verre 2'
        assert item['nasal_engraving'] is None
        assert item['glass_index'] == 'Indice 2'
        assert item['material'] == 'Matériau 2'
        assert item['glass_supplier_id'] == '2399'

    def test_parse_multiple_items():
        spider = GlassSpider()
        url = "https://www.france-optique.com/gravures/fournisseur=2399"
        body = """
        <div class="row tr group">
            Catégorie 3
        </div>
        <div class="row tr">
            <div class="col s4 m4"><p>Verre 3</p></div>
            <div class="col s1 m1"><p class="gravure_txt"><b>Gravure 3</b></p></div>
            <div class="col s1 m1"></div>
            <div class="col s1 m1"><p>Indice 3</p></div>
            <div class="col s1 m1"><p>Matériau 3</p></div>
        </div>
        <div class="row tr">
            <div class="col s4 m4"><p>Verre 4</p></div>
            <div class="col s1 m1"><p class="gravure_txt"><b>Gravure 4</b></p></div>
            <div class="col s1 m1"></div>
            <div class="col s1 m1"><p>Indice 4</p></div>
            <div class="col s1 m1"><p>Matériau 4</p></div>
        </div>
        """
        response = HtmlResponse(url=url, body=body, encoding='utf-8')
        results = list(spider.parse(response))
        
        assert len(results) == 2
        
        item1 = results[0]
        assert item1['category'] == 'Catégorie 3'
        assert item1['glass_name'] == 'Verre 3'
        assert item1['nasal_engraving'] == 'Gravure 3'
        assert item1['glass_index'] == 'Indice 3'
        assert item1['material'] == 'Matériau 3'
        assert item1['glass_supplier_id'] == '2399'
        
        item2 = results[1]
        assert item2['category'] == 'Catégorie 3'
        assert item2['glass_name'] == 'Verre 4'
        assert item2['nasal_engraving'] == 'Gravure 4'
        assert item2['glass_index'] == 'Indice 4'
        assert item2['material'] == 'Matériau 4'
        assert item2['glass_supplier_id'] == '2399'