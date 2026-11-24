"""Pontos de interesse e montagem do mapa de Florianopolis."""

from html import escape

import folium
from flask import url_for


LOCAIS = [
    {
        "nome": "Ponte Herc\u00edlio Luz",
        "latitude": -27.5928,
        "longitude": -48.5661,
        "descricao": "Um dos maiores cart\u00f5es-postais de Florian\u00f3polis. Inaugurada em 1926, a ponte suspensa liga a Ilha de Santa Catarina ao continente e pode ser apreciada de v\u00e1rios mirantes da regi\u00e3o central.",
        "endereco": "Centro, Florian\u00f3polis - SC",
    },
    {
        "nome": "Lagoa da Concei\u00e7\u00e3o",
        "latitude": -27.6054,
        "longitude": -48.4617,
        "descricao": "Regi\u00e3o conhecida pela lagoa, pelas dunas e por uma grande variedade de restaurantes, caf\u00e9s e atividades ao ar livre. \u00c9 um bom ponto de partida para explorar o leste da ilha.",
        "endereco": "Lagoa da Concei\u00e7\u00e3o, Florian\u00f3polis - SC",
    },
    {
        "nome": "Praia da Joaquina",
        "latitude": -27.6295,
        "longitude": -48.4445,
        "descricao": "Praia famosa pelas ondas e pelas dunas, onde visitantes podem caminhar e praticar sandboard. A faixa de areia \u00e9 extensa e conta com estrutura para receber visitantes.",
        "endereco": "Praia da Joaquina, Florian\u00f3polis - SC",
    },
    {
        "nome": "Ilha do Campeche",
        "latitude": -27.6969,
        "longitude": -48.4672,
        "descricao": "Ilha de \u00e1guas claras, trilhas e patrim\u00f4nio arqueol\u00f3gico. O acesso \u00e9 feito por embarca\u00e7\u00f5es autorizadas, com visita controlada para preservar o ambiente natural.",
        "endereco": "Ilha do Campeche, Florian\u00f3polis - SC",
    },
    {
        "nome": "Mercado P\u00fablico de Florian\u00f3polis",
        "latitude": -27.5978,
        "longitude": -48.5496,
        "descricao": "Edif\u00edcio hist\u00f3rico no centro da cidade, com bancas, restaurantes e bares. \u00c9 um lugar tradicional para conhecer a culin\u00e1ria e o cotidiano da capital catarinense.",
        "endereco": "R. Jer\u00f4nimo Coelho, 60 - Centro, Florian\u00f3polis - SC",
    },
    {
        "nome": "Santo Ant\u00f4nio de Lisboa",
        "latitude": -27.5088,
        "longitude": -48.5168,
        "descricao": "Bairro hist\u00f3rico de origem a\u00e7oriana, conhecido pelas casas antigas, pela igreja, pelos restaurantes de frutos do mar e pelo p\u00f4r do sol na beira-mar.",
        "endereco": "Santo Ant\u00f4nio de Lisboa, Florian\u00f3polis - SC",
    },
    {
        "nome": "Praia Mole",
        "latitude": -27.6006,
        "longitude": -48.4258,
        "descricao": "Praia de mar aberto cercada por morros e vegeta\u00e7\u00e3o nativa. Atrai surfistas e visitantes que procuram paisagens naturais no leste da ilha.",
        "endereco": "Rod. Jornalista Manoel de Menezes - Lagoa da Concei\u00e7\u00e3o, Florian\u00f3polis - SC",
    },
    {
        "nome": "Lagoinha do Leste",
        "latitude": -27.7770,
        "longitude": -48.4850,
        "descricao": "Praia preservada dentro de uma \u00e1rea natural protegida, com lagoa e trilhas de acesso. O percurso exige preparo e \u00e9 importante planejar a visita e levar \u00e1gua.",
        "endereco": "Parque Natural Municipal da Lagoinha do Leste, Florian\u00f3polis - SC",
    },
    {
        "nome": "Mirante do Morro da Cruz",
        "latitude": -27.5833,
        "longitude": -48.5350,
        "descricao": "Mirante com vista panor\u00e2mica da regi\u00e3o central, das pontes, da ba\u00eda e de partes da ilha. \u00c9 um dos pontos mais conhecidos para observar a cidade do alto.",
        "endereco": "Morro da Cruz, Florian\u00f3polis - SC",
    },
    {
        "nome": "Fortaleza de S\u00e3o Jos\u00e9 da Ponta Grossa",
        "latitude": -27.4328,
        "longitude": -48.5178,
        "descricao": "Fortifica\u00e7\u00e3o do s\u00e9culo XVIII que integrava o sistema de defesa da ilha. O conjunto hist\u00f3rico fica na regi\u00e3o da Praia do Forte e oferece vista para o mar.",
        "endereco": "Praia do Forte, Florian\u00f3polis - SC",
    },
]


def montar_mapa():
    """Gera o mapa interativo e as acoes de cada marcador."""
    mapa_folium = folium.Map(location=[-27.62, -48.52], zoom_start=11, control_scale=True, max_bounds=True)
    mapa_folium.fit_bounds([[-27.82, -48.60], [-27.40, -48.38]])
    mapa_folium.options["minZoom"] = 9
    mapa_folium.options["maxZoom"] = 17

    for indice, local in enumerate(LOCAIS, start=1):
        mais_info = url_for("detalhe_local", local_id=indice)
        rota = f'https://www.google.com/maps/dir/?api=1&destination={local["latitude"]},{local["longitude"]}'
        popup = folium.Popup(
            f'<strong>{escape(local["nome"])}</strong><br>'
            f'{escape(local["descricao"])}<br>'
            f'<span>Localizacao: {local["latitude"]}, {local["longitude"]}</span><br>'
            f'<a href="{escape(mais_info)}" target="_top" '
            'style="display:inline-block;margin:8px 6px 0 0;padding:7px 10px;background:#285260;color:white;border-radius:5px;text-decoration:none">'
            'Ver mais informa\u00e7\u00f5es</a>'
            f'<a href="{escape(rota)}" target="_blank" rel="noopener" '
            'style="display:inline-block;margin:8px 0 0;padding:7px 10px;background:#548C92;color:white;border-radius:5px;text-decoration:none">'
            'Abrir rota</a>',
            max_width=3400,
        )
        folium.Marker(
            [local["latitude"], local["longitude"]],
            tooltip=local["nome"],
            popup=popup,
        ).add_to(mapa_folium)

    return mapa_folium.get_root().render()
