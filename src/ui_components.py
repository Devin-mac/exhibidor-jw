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

def dibujar_matriz_dia(dia, mostrar_resumen):
    lugares = obtener_lista_lugares()
    horas = [f"{h:02d}:00 - {h+1:02d}:00" for h in range(6, 22)]
    
    # Definir qué pestañas mostrar
    if mostrar_resumen:
        nombres_tabs = ["📊 Resumen General"] + lugares
    else:
        nombres_tabs = lugares

    tabs = st.tabs(nombres_tabs)
    
    # Índice inicial para los lugares
    # Si mostramos resumen, el primer lugar está en la pestaña 1. Si no, en la 0.
    offset = 1 if mostrar_resumen else 0

    # --- VISTA DE RESUMEN (Solo si el toggle está activo) ---
    if mostrar_resumen:
        with tabs[0]:
            st.subheader(f"Vista General - {dia}")
            # Dibujar la matriz que ya tenías (la compacta para PC)
            cols_header = st.columns([1.2] + [2] * len(lugares))
            cols_header[0].write("**Hora**")
            for i, nombre in enumerate(lugares):
                cols_header[i+1].info(f"**{nombre}**")

            for hora in horas:
                cols = st.columns([1.2] + [2] * len(lugares))
                cols[0].write(f"**{hora}**")
                for i, lugar in enumerate(lugares):
                    reserva = verificar_disponibilidad(dia, hora, lugar)
                    key_res = f"res_{dia}_{hora}_{lugar}".replace(" ", "_")
                    with cols[i+1]:
                        if reserva:
                            st.button(f"👤 {reserva['Publicador1']}\n👤 {reserva['Publicador2']}", 
                                      key=key_res, use_container_width=True, disabled=True)
                        else:
                            st.caption("Libre")

    # --- VISTA DE PESTAÑAS POR LUGAR (La vista cómoda para móvil) ---
    for i, lugar in enumerate(lugares):
        with tabs[i + offset]:
            st.subheader(f" 🏡 {lugar}")
            for hora in horas:
                reserva = verificar_disponibilidad(dia, hora, lugar)
                key_btn = f"tab_{dia}_{hora}_{lugar}".replace(" ", "_")
                
                # Layout de dos columnas: una para la hora y otra para el botón
                c1, c2 = st.columns([1, 3])
                c1.write(f"**{hora}**")
                
                with c2:
                    if reserva:
                        # Botón para eliminar (Formato vertical de nombres)
                        label = f"👤 {reserva['Publicador1']}\n👤 {reserva['Publicador2']}\n\n🗑️ ELIMINAR"
                        if st.button(label, key=key_btn, use_container_width=True, type="secondary"):
                            modal_cancelar(reserva)
                    else:
                        if st.button(f"➕ Reservar", key=key_btn, use_container_width=True, type="primary"):
                            modal_reservar(dia, hora, lugar)
                st.divider()
