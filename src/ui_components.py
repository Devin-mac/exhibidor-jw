import streamlit as st
from src.logic import obtener_lista_publicadores, verificar_disponibilidad, es_mismo_publicador
from src.database import guardar_reserva, borrar_reserva
from src.logic import obtener_lista_lugares
from datetime import datetime
import pytz



def renderizar_cabecera_lugares():
    """Dibuja los encabezados de los 6 lugares."""
    cols = st.columns([1] + [2] * 6) # La primera columna es para la hora
    cols[0].write("**Hora**")
    for i in range(1, 7):
        cols[i].info(f"**Lugar {i}**")
    return cols

@st.dialog("Reservar Espacio")
def modal_reservar(dia, hora, lugar):
    st.write(f"🗓 **Día:** {dia} | ⏰ **Hora:** {hora} | 📍 {lugar}")
    nombres = obtener_lista_publicadores()
    
    p1 = st.selectbox("Selecciona Publicador 1", ["---"] + nombres, key=f"p1_{dia}_{hora}_{lugar}")
    p2 = st.selectbox("Selecciona Publicador 2", ["---"] + nombres, key=f"p2_{dia}_{hora}_{lugar}")
    
    # NUEVO: Opción de reserva fija
    es_fijo = st.checkbox("Hacer esta reserva permanente (todas las semanas)")
    
    # Dentro de modal_reservar en src/ui_components.py

    if st.button("Confirmar Reserva", use_container_width=True):
        if p1 == "---" or p2 == "---":
            st.error("Selecciona ambos nombres.")
        else:
            # 1. Obtener hora local
            zona_horaria = pytz.timezone('America/Bogota')
            registro_str = datetime.now(zona_horaria).strftime("%d/%m/%Y %H:%M")

            # 2. Crear el diccionario con las 7 columnas exactas
            nueva_reserva = {
                "ID_Bloque": f"{dia}-{hora}-{lugar}",
                "Dia": dia,
                "Hora": hora,
                "Lugar": lugar,
                "Publicador1": p1,
                "Publicador2": p2,
                "Registro": registro_str,
                "Tipo": "Permanente" if es_fijo else "Temporal"
            }
            
            # 3. Guardar
            from src.database import guardar_reserva
            guardar_reserva(nueva_reserva)
            st.success("¡Reserva guardada!")
            st.rerun()

@st.dialog("Cancelar Reserva")
def modal_cancelar(reserva):
    """Ventana emergente para eliminar una reserva."""
    st.warning(f"¿Deseas eliminar la reserva de {reserva['Publicador1']} y {reserva['Publicador2']}?")
    if st.button("Sí, eliminar y liberar espacio", use_container_width=True):
        borrar_reserva(reserva['ID_Bloque'])
        st.rerun()

def dibujar_matriz_dia(dia):
    # 1. Cargamos los lugares dinámicamente
    lugares = obtener_lista_lugares()
    #st.write(lugares)
    num_lugares = len(lugares)
    
    # 2. Definimos las horas
    horas = [f"{h}:00 - {h+1}:00" for h in range(6, 20)] 
    
    # 3. Dibujamos la cabecera dinámicamente
    # Ajustamos el ancho: 1.5 para la hora y 2 para cada lugar
    cols_header = st.columns([1.5] + [2] * num_lugares)
    cols_header[0].write("**Hora**")
    for i, nombre in enumerate(lugares):
        cols_header[i+1].info(f"**{nombre}**")
    
    # 4. Dibujamos las filas
    for hora in horas:
        cols = st.columns([1.5] + [2] * num_lugares)
        cols[0].write(f"**{hora}**")
        
        for i, lugar in enumerate(lugares):
            reserva = verificar_disponibilidad(dia, hora, lugar)
            key = f"btn_{dia}_{hora}_{lugar}".replace(" ", "_") # Evitar espacios en keys
            
            with cols[i+1]:
                if reserva:
                    label = f"👤 {reserva['Publicador1']}\n👤 {reserva['Publicador2']}\n\n\n🗑️"
                    if st.button(label, key=key, use_container_width=True, type="secondary"):
                        modal_cancelar(reserva)
                else:
                    if st.button("➕ Libre", key=key, use_container_width=True, type="primary"):
                        modal_reservar(dia, hora, lugar)
