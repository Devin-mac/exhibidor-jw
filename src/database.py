import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta

def conectar_db():
    """Establece la conexión con el Google Sheet PROGRAMADOR_EXHIBIDOR."""
    return st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=60)
# src/database.py

def leer_reservas():
    conn = conectar_db()
    try:
        data = conn.read(ttl=0)
        df = pd.DataFrame(data)
        
        # Si el DF está vacío, crear uno con las columnas correctas
        if df.empty:
            return pd.DataFrame(columns=['ID_Bloque', 'Dia', 'Hora', 'Lugar', 'Publicador1', 'Publicador2', 'Registro', 'Tipo'])

        # Limpieza de nombres de columnas (elimina espacios accidentales como "Hora ")
        df.columns = df.columns.str.strip()

        # Lógica de fechas (la que ya teníamos)
        hoy = datetime.now()
        lunes_actual = (hoy - timedelta(days=hoy.weekday())).replace(hour=0, minute=0, second=0)
        
        df['Registro_DT'] = pd.to_datetime(df['Registro'], format="%d/%m/%Y %H:%M", errors='coerce')
        
        # Filtro: Permanentes O Temporales de esta semana
        df_visible = df[(df['Tipo'] == 'Permanente') | 
                        ((df['Tipo'] == 'Temporal') & (df['Registro_DT'] >= lunes_actual))]
        
        return df_visible
    except Exception as e:
        st.error(f"Error en base de datos: {e}")
        return pd.DataFrame(columns=['ID_Bloque', 'Dia', 'Hora', 'Lugar', 'Publicador1', 'Publicador2', 'Registro', 'Tipo'])



def guardar_reserva(nueva_reserva):
    """
    Añade una nueva fila al Google Sheet.
    nueva_reserva: dict con llaves ['ID_Bloque', 'Dia', 'Hora', 'Lugar', 'Publicador1', 'Publicador2']
    """
    conn = conectar_db()
    df_actual = leer_reservas()
    
    # Concatenamos el nuevo registro
    nuevo_df = pd.concat([df_actual, pd.DataFrame([nueva_reserva])], ignore_index=True)
    
    conn.update(data=nuevo_df)
    st.cache_data.clear()

def borrar_reserva(id_bloque):
    """Elimina una reserva basada en su ID único (Dia-Hora-Lugar)."""
    conn = conectar_db()
    df_actual = leer_reservas()
    
    nuevo_df = df_actual[df_actual['ID_Bloque'] != id_bloque]
    
    conn.update(data=nuevo_df)
    st.cache_data.clear()

def reiniciar_calendario():
    conn = conectar_db()
    # Reiniciar con las 7 columnas
    df_vacio = pd.DataFrame(columns=['ID_Bloque', 'Dia', 'Hora', 'Lugar', 'Publicador1', 'Publicador2', 'Registro'])
    conn.update(data=df_vacio)
    st.cache_data.clear()
