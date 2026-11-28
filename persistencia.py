import os
from pathlib import Path
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import execute_values
from carga import BASE,ARCHIVOS,procesar,resumen
load_dotenv()
TABLAS={
'rutas.xlsx':('rutas','cod_ruta,nombre,km_recorrido,buses_asignados','cod_ruta'),
'estaciones.csv':('estaciones','cod_estacion,estacion,ruta,tiene_cajero','cod_estacion'),
'validaciones.xlsx':('validaciones','fecha_hora,hora_conocida,cod_estacion,id_tarjeta,tipo_tarjeta,valor_pasaje','fecha_hora,hora_conocida,cod_estacion,id_tarjeta,tipo_tarjeta,valor_pasaje'),
'despachos.xlsx':('despachos','fecha,cod_ruta,franja,despachos_programados,despachos_realizados','fecha,cod_ruta,franja')}
def conectar(): return psycopg2.connect(os.environ['DATABASE_URL'])
def cargar(path):
    path=Path(path); tabla,cols,llave=TABLAS[path.name]
    with conectar() as cn, cn.cursor() as cur:
        cur.execute('LOCK TABLE rutas, estaciones, validaciones, despachos IN SHARE ROW EXCLUSIVE MODE')
        cur.execute('SELECT cod_ruta FROM rutas'); rutas={r[0] for r in cur.fetchall()}
        cur.execute('SELECT cod_estacion FROM estaciones'); estaciones={r[0] for r in cur.fetchall()}
        cur.execute(f'SELECT {llave} FROM {tabla}'); existentes=cur.fetchall()
        b,m=procesar(path,rutas,estaciones,existentes); r=resumen(path,b,m)
        cur.execute('INSERT INTO cargas(archivo,filas_leidas,filas_cargadas,filas_rechazadas) VALUES (%s,%s,%s,%s) RETURNING id_carga',(path.name,r['leidas'],r['cargables'],r['rechazadas'])); cid=cur.fetchone()[0]
        if b: execute_values(cur,f'INSERT INTO {tabla}({cols},id_carga) VALUES %s',[(*v,cid) for _,v in b])
        if m: execute_values(cur,'INSERT INTO rechazos(id_carga,fila_origen,motivo,contenido_fila) VALUES %s',[(cid,*v) for v in m])
        r['id_carga']=cid; return r
if __name__=='__main__':
    import json
    with conectar() as cn, cn.cursor() as c: c.execute((BASE/'esquema.sql').read_text())
    for n in ARCHIVOS: print(json.dumps(cargar(BASE/'datos_cliente'/n),ensure_ascii=False))
