import pandas as pd
import streamlit as st
import os
from src.database import leer_reservas

def obtener_lista_publicadores():
    """Lee los nombres desde el archivo CSV en la carpeta data."""
    try:
        df = pd.read_csv("data/usuarios.csv")
        # Retorna la lista ordenada alfabéticamente
        return sorted(df['nombre'].tolist())
    except Exception:
        # Lista de respaldo por si el archivo no existe o falla
        return ["Invitado 1", "Invitado 2"]

def verificar_disponibilidad(dia, hora, lugar):
    """
    Busca si ya existe una reserva para ese bloque específico.
    Retorna la reserva (dict) si existe, o None si está libre.
    """
    df_reservas = leer_reservas()
    
    # El ID_Bloque es nuestra clave única: ej. "Lunes-08:00-Lugar 1"
    id_buscado = f"{dia}-{hora}-{lugar}"
    
    reserva = df_reservas[df_reservas['ID_Bloque'] == id_buscado]
    
    if not reserva.empty:
        return reserva.iloc[0].to_dict()
    return None

def es_mismo_publicador(p1, p2):
    """Evita que una persona se agende consigo misma."""
    if p1 == p2:
        return True
    return False

def obtener_lista_lugares():
    try:
        base_path = os.path.dirname(__file__)
        csv_path = os.path.join(base_path, "..", "data", "lugares.csv")
        df = pd.read_csv(csv_path)
        
        # .str.strip() elimina espacios en blanco accidentales
        return df['lugar'].str.strip().tolist()
    except Exception as e:
        # Si ves este error en la app, es que la ruta o el nombre de columna falló
        st.error(f"Error: {e}") 
        return [f"Lugar {i}" for i in range(1, 7)]
