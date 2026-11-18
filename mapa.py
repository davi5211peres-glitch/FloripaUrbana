"""Dados dos pontos turísticos e criação do mapa de Florianópolis."""

from html import escape

import folium
from flask import url_for


PONTOS_TURISTICOS = [
    {"nome": "Ponte Hercílio Luz", "latitude": -27.5928, "longitude": -48.5661},
    {"nome": "Lagoa da Conceição", "latitude": -27.6054, "longitude": -48.4617},
    {"nome": "Praia da Joaquina", "latitude": -27.6295, "longitude": -48.4445},
    {"nome": "Ilha do Campeche", "latitude": -27.6969, "longitude": -48.4672},
    {"nome": "Mercado Público", "latitude": -27.5978, "longitude": -48.5496},
    {"nome": "Santo Antônio de Lisboa", "latitude": -27.5088, "longitude": -48.5168},
    {"nome": "Praia Mole", "latitude": -27.6006, "longitude": -48.4258},
    {"nome": "Lagoinha do Leste", "latitude": -27.7770, "longitude": -48.4850},
    {"nome": "Mirante do Morro da Cruz", "latitude": -27.5833, "longitude": -48.5350},
    {"nome": "Fortaleza de São José da Ponta Grossa", "latitude": -27.4328, "longitude": -48.5178},
]


def montar_mapa():
    """Gera o HTML do mapa com os dez pontos fornecidos."""
    mapa_folium = folium.Map(location=[-27.62, -48.52], zoom_start=11, control_scale=True, max_bounds=True)
    mapa_folium.fit_bounds([[-27.82, -48.60], [-27.40, -48.38]])
    mapa_folium.options["minZoom"] = 9
    mapa_folium.options["maxZoom"] = 17

    for ponto in PONTOS_TURISTICOS:
        detalhe_url = url_for("mapa")
        popup = folium.Popup(
            f'<strong>{escape(ponto["nome"])}</strong><br>'
            f'Latitude: {ponto["latitude"]}<br>Longitude: {ponto["longitude"]}<br>'
            f'<a href="{escape(detalhe_url)}">Ver mapa</a>',
            max_width=300,
        )
        folium.Marker(
            [ponto["latitude"], ponto["longitude"]],
            tooltip=ponto["nome"],
            popup=popup,
        ).add_to(mapa_folium)

    return mapa_folium.get_root().render()
