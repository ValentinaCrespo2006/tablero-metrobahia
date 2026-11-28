import pytest
from carga import fecha,numero,Rechazo,simular

def test_fecha_vacia():
    with pytest.raises(Rechazo): fecha(None)
def test_numero_negativo():
    with pytest.raises(Rechazo): numero(-5,'Pasaje')
def test_coma_decimal(): assert numero('2.900,0','Pasaje')==2900
def test_balance():
    for r in simular(): assert r['leidas']==r['cargables']+r['rechazadas']
