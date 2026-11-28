import base64
import tempfile
from contextlib import closing
from pathlib import Path

from dash import Dash, Input, Output, State, ctx, dcc, html, no_update
from persistencia import conectar, cargar, TABLAS

app = Dash(__name__, title='MetroBahía', update_title='Procesando…')
server = app.server
app.index_string = '''<!DOCTYPE html><html lang="es"><head>{%metas%}<title>{%title%}</title>{%favicon%}{%css%}<style>
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 95% 0%,#30245b 0%,transparent 45%),radial-gradient(ellipse at 0% 80%,#103847 0%,transparent 45%),#101827;color:#e9eef8;font:14px 'Segoe UI',Arial,sans-serif;min-height:100vh} .shell{width:100%;padding:22px clamp(14px,2.5vw,40px);margin:auto}.brand{display:flex;align-items:center;gap:10px;font-weight:750;font-size:22px}.logo{display:grid;place-items:center;width:38px;height:38px;border-radius:11px;background:linear-gradient(135deg,#3478f6,#7955e8);color:white;font-weight:800}.header{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-bottom:20px;flex-wrap:wrap}h1{font-size:clamp(24px,2.5vw,34px);margin:0;font-weight:700;letter-spacing:-.7px}h2{font-size:19px;margin:0 0 5px;color:#f5f7fc}h3{font-size:15px;margin:16px 0 10px}p{margin:5px 0 12px;color:#aab7ce;line-height:1.5}.panel{background:#1a2538;border:1px solid #344158;border-radius:17px;padding:19px;min-width:0;box-shadow:0 8px 25px #0002}.workspace{display:grid;grid-template-columns:minmax(0, .85fr) minmax(0,1.65fr);gap:16px;margin-bottom:16px}.metrics{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:12px 0 16px}.metric{background:#202e44;border:1px solid #37465f;border-radius:12px;padding:14px;min-width:0;border-top:3px solid var(--accent)}.metric span{display:block;color:#b9c5d8;font-size:12px}.metric strong{display:block;font-size:clamp(21px,2.5vw,32px);color:var(--accent);margin-top:5px;font-variant-numeric:tabular-nums}.drop{border:1.5px dashed #7589dc;border-radius:12px;background:#202b46;text-align:center;padding:21px 10px;cursor:pointer;overflow-wrap:anywhere;width:100%}.drop:hover{background:#293858}.upload-icon{display:block;font-size:30px;color:#a7baff;margin-bottom:5px}.button{border:0;border-radius:9px;background:linear-gradient(110deg,#315edc,#7046d8);color:white;font:inherit;font-weight:700;padding:11px 18px;cursor:pointer;margin-top:12px}.button:disabled{opacity:.45;cursor:not-allowed}.selected{font-size:12px;color:#c6d3eb;margin:10px 0;overflow-wrap:anywhere}.notice{padding:10px 12px;border-radius:9px;background:#173b38;color:#91ebc7;font-size:13px;margin:10px 0}.notice.error{background:#4b2937;color:#ffc2ce}.table-wrap{overflow-x:auto;width:100%}table{width:100%;border-collapse:collapse;text-align:left;font-size:13px;white-space:nowrap}th{background:#233149;color:#b8c6dd;font-size:12px;font-weight:600}td,th{padding:10px 12px;border-bottom:1px solid #344158}td.num,th.num{text-align:right;font-variant-numeric:tabular-nums}tbody tr:hover{background:#233149}.reason{display:grid;grid-template-columns:minmax(0,1fr) 54px;gap:5px 12px;margin:8px 0;font-size:12px}.reason b{text-align:right}.track{grid-column:1/-1;height:5px;border-radius:5px;background:#344158;overflow:hidden}.bar{height:100%;background:linear-gradient(90deg,#e87987,#f3a06e);border-radius:5px}.muted{color:#aab7ce;font-size:12px}.report-select{margin:10px 0;color:#152238}.status{color:#8ceac2;font-weight:600}.status.bad{color:#ff9eaa}details{margin-top:12px}summary{cursor:pointer;color:#b9c8fc} .history-title{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap}button:focus-visible,summary:focus-visible{outline:2px solid #9ac2ff;outline-offset:3px}@media(max-width:850px){.workspace{grid-template-columns:1fr}.header{align-items:flex-start}.metrics{gap:8px}.metric{padding:10px}}.workspace .metrics{grid-template-columns:repeat(2,minmax(0,1fr))}@media(min-width:1400px){.workspace .metrics{grid-template-columns:repeat(4,minmax(0,1fr))}.workspace .metric strong{font-size:clamp(20px,1.65vw,30px)}}@media(max-width:950px){.metrics{grid-template-columns:repeat(2,minmax(0,1fr))}}@media(max-width:500px){.metrics,.workspace .metrics{grid-template-columns:1fr}}
</style></head><body>{%app_entry%}<footer>{%config%}{%scripts%}{%renderer%}</footer></body></html>'''


def fmt(n):
    return f'{n:,}'.replace(',', '.')


def pct(cargadas, leidas):
    if not leidas:
        return '—'
    return f'{100 * cargadas / leidas:.2f}'.replace('.', ',') + ' %'


def metric(label, value, color):
    texto = value if isinstance(value, str) else fmt(value)
    return html.Div([html.Span(label), html.Strong(texto)], className='metric', style={'--accent': color})


def metrics(l, c, r):
    return html.Div([
        metric('Filas leídas', l, '#91baff'),
        metric('Filas cargadas', c, '#62dfb5'),
        metric('Filas rechazadas', r, '#ff9b9f'),
        metric('Tasa de aceptación', pct(c, l), '#c4b5fd')
    ], className='metrics')


def aviso(text, error=False):
    return html.Div(text, className='notice error' if error else 'notice', role='status')


def historial():
    with closing(conectar()) as cn, cn.cursor() as cur:
        cur.execute("""SELECT id_carga, archivo,
            TO_CHAR(fecha_carga AT TIME ZONE 'America/Bogota','DD/MM/YYYY HH24:MI:SS'),
            filas_leidas, filas_cargadas, filas_rechazadas
            FROM cargas ORDER BY id_carga DESC""")
        return cur.fetchall()


def tabla(headers, rows, numeric=()):
    return html.Div(html.Table([
        html.Thead(html.Tr([html.Th(h, className='num' if i in numeric else '') for i,h in enumerate(headers)])),
        html.Tbody([html.Tr([html.Td(v, className='num' if i in numeric else '') for i,v in enumerate(row)]) for row in rows])
    ]), className='table-wrap')


def vista_historial(rows):
    if not rows:
        return html.P('Todavía no hay cargas registradas.')
    return tabla(['Archivo','Fecha de carga','Leídas','Cargadas','Rechazadas','Balance'], [
        [a, f, fmt(l), fmt(c), fmt(r), html.Span('Correcto' if l == c+r else 'Error', className='status' if l == c+r else 'status bad')]
        for _,a,f,l,c,r in rows], (2,3,4))


def reporte(cid):
    if cid is None:
        return html.P('Selecciona un archivo del historial para consultar su reporte.')
    with closing(conectar()) as cn, cn.cursor() as cur:
        cur.execute('SELECT archivo, filas_leidas, filas_cargadas, filas_rechazadas FROM cargas WHERE id_carga=%s',(cid,))
        row=cur.fetchone()
        if not row:
            return aviso('La carga seleccionada no existe.', True)
        cur.execute('SELECT motivo, COUNT(*) FROM rechazos WHERE id_carga=%s GROUP BY motivo ORDER BY COUNT(*) DESC, motivo',(cid,))
        motivos=cur.fetchall()
        cur.execute('SELECT fila_origen, motivo FROM rechazos WHERE id_carga=%s ORDER BY fila_origen LIMIT 25',(cid,))
        detalle=cur.fetchall()
    a,l,c,r=row
    correcto=l==c+r and sum(n for _,n in motivos)==r
    barras=[html.Div([html.Span(m),html.B(fmt(n)),html.Div(html.Div(className='bar',style={'width':f'{100*n/max(1,r):.2f}%'}),className='track')],className='reason') for m,n in motivos]
    return html.Div([html.H3(a),metrics(l,c,r),aviso('Conciliación correcta: leídas = cargadas + rechazadas.' if correcto else 'Revisar conciliación y motivos.',not correcto),html.H3('Motivos de rechazo'),html.Div(barras) if barras else html.P('Sin filas rechazadas.'),html.Details([html.Summary('Detalle de filas rechazadas (primeras 25)'),tabla(['Fila de origen','Motivo'],detalle,(0,))]) if detalle else None])


app.layout=html.Main([
    html.Header([html.Div([html.Span('M',className='logo'),html.Span('MetroBahía')],className='brand'),html.H1('Sistema de carga de datos')],className='header'),
    html.Div(id='resumen'),
    html.Div([
        html.Section([html.H2('Carga de archivos'),html.P('Selecciona un archivo original del cliente.'),dcc.Upload(id='archivo',children=html.Div([html.Span('↑',className='upload-icon'),html.Strong('Arrastra o selecciona un archivo'),html.P('Excel (.xlsx) · CSV (.csv)')]),className='drop',multiple=False,accept='.xlsx,.csv'),html.Div(id='seleccion',className='selected'),html.Button('Cargar archivo',id='cargar',n_clicks=0,className='button',disabled=False),html.Div(id='mensaje')],className='panel'),
        html.Section([html.H2('Reporte de carga'),dcc.Dropdown(id='carga_id',options=[],placeholder='Selecciona una carga',clearable=False,className='report-select'),dcc.Loading(html.Div(id='reporte'),type='circle')],className='panel')
    ],className='workspace'),
    html.Section([html.Div([html.H2('Historial de archivos aplicados'),html.Span(id='cantidad',className='muted')],className='history-title'),html.Div(id='historial')],className='panel')
],className='shell')


@app.callback(Output('seleccion','children'),Input('archivo','filename'))
def seleccionar(nombre):
    if not nombre:
        return 'Ningún archivo seleccionado.'
    if nombre not in TABLAS:
        return 'Archivo no admitido: '+nombre
    return 'Seleccionado: '+nombre


@app.callback(Output('resumen','children'),Output('historial','children'),Output('cantidad','children'),Output('carga_id','options'),Output('carga_id','value'),Output('mensaje','children'),Output('archivo','contents'),Output('archivo','filename'),Input('cargar','n_clicks'),State('archivo','contents'),State('archivo','filename'),running=[(Output('cargar','disabled'),True,False),(Output('cargar','children'),'Procesando…','Cargar archivo'),(Output('archivo','disabled'),True,False)])
def actualizar(n,contenido,nombre):
    mensaje=None
    elegido=None
    limpiar=False
    try:
        if ctx.triggered_id=='cargar' and n:
            limpiar=True
            if not contenido or nombre not in TABLAS:
                mensaje=aviso('Selecciona un archivo válido.',True)
            else:
                with tempfile.TemporaryDirectory() as carpeta:
                    ruta=Path(carpeta)/nombre
                    ruta.write_bytes(base64.b64decode(contenido.split(',',1)[1],validate=True))
                    resultado=cargar(ruta)
                elegido=resultado['id_carga']
                mensaje=aviso('Archivo procesado correctamente.')
        rows=historial()
        opciones=[{'label':f'{a} · {f}', 'value':i} for i,a,f,*_ in rows]
        if elegido is None and rows:
            elegido=next((r[0] for r in rows if r[1]=='validaciones.xlsx' and r[4]>0),rows[0][0])
        totales=[sum(r[i] for r in rows) for i in (3,4,5)]
        return metrics(*totales),vista_historial(rows),f'{len(rows)} cargas registradas',opciones,elegido,mensaje,None if limpiar else no_update,None if limpiar else no_update
    except Exception:
        app.logger.exception('Error de carga o consulta')
        return no_update,no_update,no_update,no_update,no_update,aviso('No se pudo completar la operación. Revisa la terminal y el historial antes de reintentar.',True),None if limpiar else no_update,None if limpiar else no_update


@app.callback(Output('reporte','children'),Input('carga_id','value'))
def ver_reporte(cid):
    try:
        return reporte(cid)
    except Exception:
        app.logger.exception('Error consultando reporte')
        return aviso('No se pudo consultar el reporte.',True)


if __name__=='__main__':
    app.run(host='127.0.0.1',port=8050,debug=False)
