from flask import Flask, render_template
import pandas as pd
import numpy as np
import os

app = Flask(__name__)
DATA_PATH = "Data"

# Archivos y pestañas
DATA_FILES = {
    'upcoming': ('Proximos a Correr.csv', 'Próximas Carreras'),
    'past_7_days': ('Corrieron en los ultimos 7 dias.csv', 'Resultados Últimos 7 Días'),
    'jockeys': ('WinShare_Jockeys.csv', 'Ranking de Jockeys'),
    'trainers': ('WinShare_Entrenadores.csv', 'Ranking de Entrenadores'),
    'sires': ('WinShare_Padrillos.csv', 'Ranking de Padrillos'),
    'graficos': (None, 'Rendimiento Visual')
}

# Columnas de Win Share a convertir a porcentaje
WIN_SHARE_COLUMNS = [
    'win_share_90', 'win_share_365',
    'win_share_hijos_90', 'win_share_hijos_365'
]

# Columnas a redondear a enteros
CARRERAS_COLUMNS = [
    'n_carreras_90', 'n_carreras_365',
    'n_carreras_hijos_90', 'n_carreras_hijos_365',
    'Carreras Corridas', 'Victorias'
]

# Renombres por archivo
COLUMN_RENAMES = {
    'Proximos a Correr.csv': {
        'eday': 'Fecha de la Carrera',
        'hora_carrera': 'Hora de la Carrera',
        'ejemplar': 'Ejemplar',
        'padrillo': 'Padrillo',
        'yegua': 'Yegua',
        'track': 'Hipódromo',
        'distance': 'Distancia',
        'surface': 'Pista',
        'condicion': 'Condición',
        'carreras_corridas': 'Carreras Corridas',
        'total_wins': 'Victorias',
        'pwin_bsn': 'BSN Estimado para Ganar',
        'avg_bsn_ejemplar': 'BSN Promedio'
    },
    'Corrieron en los ultimos 7 dias.csv': {
        'eday': 'Fecha',
        'ejemplar': 'Ejemplar',
        'padrillo': 'Padrillo',
        'yegua': 'Yegua',
        'track': 'Hipódromo',
        'distance': 'Distancia',
        'surface': 'Pista',
        'condicion': 'Condición',
        'p': 'Posición',
        'pwin_bsn': 'BSN Estimado para Ganar',
        'avg_bsn_ejemplar': 'BSN Promedio',
        'ecpos': 'EC Posición',
        'take_odds': 'Take Odds'
    },
    'WinShare_Jockeys.csv': {
        'jockey': 'Jockey',
        'track': 'Hipódromo',
        'surface': 'Pista',
        'dist_group_label': 'Distancia',
        'win_share_90': 'Win Share (90d)',
        'n_carreras_90': 'Carreras (90d)',
        'win_share_365': 'Win Share (365d)',
        'n_carreras_365': 'Carreras (365d)'
    },
    'WinShare_Entrenadores.csv': {
        'cuidador': 'Entrenador',
        'track': 'Hipódromo',
        'surface': 'Pista',
        'dist_group_label': 'Distancia',
        'win_share_90': 'Win Share (90d)',
        'n_carreras_90': 'Carreras (90d)',
        'win_share_365': 'Win Share (365d)',
        'n_carreras_365': 'Carreras (365d)'
    },
    'WinShare_Padrillos.csv': {
        'padrillo': 'Padrillo',
        'track': 'Hipódromo',
        'surface': 'Pista',
        'dist_group_label': 'Distancia',
        'win_share_90': 'Win Share (90d)',
        'n_carreras_hijos_90': 'Carreras Hijos (90d)',
        'win_share_365': 'Win Share (365d)',
        'n_carreras_hijos_365': 'Carreras Hijos (365d)'
    }
}


def format_dataframe(df, filename):
    if filename in COLUMN_RENAMES:
        df.rename(columns=COLUMN_RENAMES[filename], inplace=True)

    # 🕒 Formatear "Hora de la Carrera" a HH:MM
    if "Hora de la Carrera" in df.columns:
        df["Hora de la Carrera"] = df["Hora de la Carrera"].apply(lambda x: f"{int(x):04d}" if pd.notnull(x) else x)
        df["Hora de la Carrera"] = df["Hora de la Carrera"].str.slice(0, 2) + ":" + df["Hora de la Carrera"].str.slice(2, 4)

    # 🎯 Convertir Win Share a porcentaje
    for col in df.columns:
        if 'Win Share' in col or col in WIN_SHARE_COLUMNS:
            df[col] = df[col].apply(lambda x: f"{round(x * 100, 2)}%" if pd.notnull(x) else x)

    # 🔢 Redondear y convertir columnas numéricas
    for col in df.columns:
        if col in CARRERAS_COLUMNS or 'Carreras' in col or 'Posición' in col:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').round(0).astype('Int64')
            except Exception as e:
                print(f"❌ Error convirtiendo '{col}' a Int64: {e}")
        elif pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = df[col].round(2)
            except Exception as e:
                print(f"⚠️ Error redondeando '{col}': {e}")
    
    return df



def load_csv(file_name):
    if file_name is None:
        return ""
    try:
        path = os.path.join(DATA_PATH, file_name)
        if os.path.exists(path):
            df = pd.read_csv(path)
            df = format_dataframe(df, file_name)
            return df.to_html(classes='table table-striped table-sm', index=False)
        else:
            return f"<p class='text-danger'>Archivo <strong>{file_name}</strong> no encontrado.</p>"
    except Exception as e:
        return f"<p class='text-danger'>Error cargando <strong>{file_name}</strong>: {str(e)}</p>"


@app.route('/')
def index():
    tables = {}
    for key, (filename, title) in DATA_FILES.items():
        html_table = load_csv(filename)
        tables[key] = {
            'title': title,
            'table': html_table
        }
    return render_template('index.html', tables=tables)


if __name__ == '__main__':
    from waitress import serve
    serve(app, host='0.0.0.0', port=8080)


