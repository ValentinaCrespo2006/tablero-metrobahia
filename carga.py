import csv, datetime as dt, unicodedata, json, os, sys
from pathlib import Path
from collections import Counter
from decimal import Decimal, InvalidOperation
from openpyxl import load_workbook
class Rechazo(ValueError): pass
BASE=Path(__file__).parent
FRANJAS={'pico manana':'Pico mañana','valle':'Valle','pico tarde':'Pico tarde','noche':'Noche'}
TIPOS={'general':'General','estudiante':'Estudiante','adulto mayor':'Adulto mayor'}
ARCHIVOS=['rutas.xlsx','estaciones.csv','validaciones.xlsx','despachos.xlsx']
def texto(v):
    if v is None or not str(v).strip(): raise Rechazo('Campo obligatorio vacío')
    return str(v).strip()
def normal(v): return ''.join(c for c in unicodedata.normalize('NFD',texto(v).lower()) if not unicodedata.combining(c))
def categoria(v, opciones):
    k=normal(v)
    if k not in opciones: raise Rechazo('Categoría desconocida')
    return opciones[k]
def numero(v, nombre, entero=False):
    try:
        t=str(v).strip(); n=Decimal(t.replace('.','').replace(',','.') if ',' in t else t)
        if not n.is_finite(): raise InvalidOperation()
    except (InvalidOperation,ValueError): raise Rechazo(nombre+' no numérico')
    if n<0: raise Rechazo(nombre+' negativo')
    if entero and n!=int(n): raise Rechazo(nombre+' no entero')
    return int(n) if entero else n
def fecha(v):
    if v is None: raise Rechazo('Fecha vacía')
    if str(v).strip().upper()=='SUBTOTAL': raise Rechazo('Fila SUBTOTAL')
    conocida=isinstance(v,dt.datetime)
    try:
        f=v if conocida else dt.datetime.strptime(texto(v),'%d/%m/%Y')
    except ValueError: raise Rechazo('Fecha inválida')
    if not dt.date(2025,11,1)<=f.date()<=dt.date(2026,10,31): raise Rechazo('Fecha fuera del periodo')
    return f,conocida
def filas(path):
    if path.suffix=='.csv':
        with path.open(encoding='utf-8-sig',newline='') as f:
            for i,r in enumerate(csv.reader(f,delimiter=';'),1):
                if i>1: yield i,r
    else:
        w=load_workbook(path,read_only=True,data_only=True)
        try:
            for i,r in enumerate(w.active.values,1):
                if i>(5 if path.name=='validaciones.xlsx' else 1): yield i,r
        finally: w.close()
def revisar(nombre,r,rutas,estaciones):
    if nombre=='rutas.xlsx':
        c,n,km,b=r; return texto(c).upper(),texto(n),numero(km,'Kilómetros'),numero(b,'Buses',True)
    if nombre=='estaciones.csv':
        c,n,ruta,cajero=r; ruta=texto(ruta).upper()
        if ruta not in rutas: raise Rechazo('Ruta inexistente')
        return texto(c).upper(),texto(n),ruta,categoria(cajero,{'si':True,'no':False})
    if nombre=='validaciones.xlsx':
        f,e,t,tip,p=r; f,h=fecha(f); e=texto(e).upper()
        if e not in estaciones: raise Rechazo('Estación inexistente')
        return f,h,e,texto(t),categoria(tip,TIPOS),numero(p,'Pasaje')
    f,ruta,fr,p,real=r; f,_=fecha(f); ruta=texto(ruta).upper()
    if ruta not in rutas: raise Rechazo('Ruta inexistente')
    p=numero(p,'Programados',True); real=numero(real,'Realizados',True)
    if real>p: raise Rechazo('Realizados superiores a programados')
    return f.date(),ruta,categoria(fr,FRANJAS),p,real
def procesar(path,rutas,estaciones,existentes=()):
    buenos=[]; malos=[]; vistos=set(existentes)
    for i,r in filas(path):
        try:
            v=revisar(path.name,r,rutas,estaciones)
            k=v[:3] if path.name=='despachos.xlsx' else v[:1] if path.name in ARCHIVOS[:2] else v
            if k in vistos: raise Rechazo('Fila duplicada / llave repetida')
            vistos.add(k); buenos.append((i,v))
        except Rechazo as e: malos.append((i,str(e),json.dumps(r,default=str,ensure_ascii=False)))
    return buenos,malos
def resumen(path,b,m): return dict(archivo=path.name,leidas=len(b)+len(m),cargables=len(b),rechazadas=len(m),motivos=dict(Counter(x[1] for x in m)))
def simular():
    rutas=set(); estaciones=set(); resultado=[]
    for nombre in ARCHIVOS:
        p=BASE/'datos_cliente'/nombre; b,m=procesar(p,rutas,estaciones)
        if nombre==ARCHIVOS[0]: rutas.update(v[0] for _,v in b)
        if nombre==ARCHIVOS[1]: estaciones.update(v[0] for _,v in b)
        resultado.append(resumen(p,b,m))
    return resultado
if __name__=='__main__':
    print(json.dumps(simular(),ensure_ascii=False,indent=2))
