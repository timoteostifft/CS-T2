from recomendacoes_api.domain.entities import Place


def test_create_place():
    place = Place.create(name="Praia do Rosa", city="Imbituba", category="beach")

    assert place.name == "Praia do Rosa"
    assert place.id is not None
