import streamlit as st
from src.ui_components import dibujar_matriz_dia
from src.database import reiniciar_calendario
from datetime import datetime, timedelta

# 1. Configuración de la página
st.set_page_config(
    page_title="Programador Exhibidor",
    page_icon="📅",
    layout="wide" # Importante para que los 6 lugares quepan bien
)

# 2. CSS para mejorar la visibilidad de los botones en las pestañas
st.markdown("""
    <style>
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 18px; /* Pestañas más grandes y legibles */
        font-weight: bold;
    }
    .stButton button {
        white-space: pre-wrap; /* Permite que los nombres se rompan en dos líneas */
    }
    </style>
""", unsafe_allow_html=True)

# Estilo CSS personalizado para mejorar la estética de los botones
# 3. Bloque de Estilo CSS Unificado
st.markdown("""
    <style>
    /* --- Pestañas (Tabs) más grandes --- */
    button[data-baseweb="tab"] {
        font-size: 22px !important;
        font-weight: bold !important;
        padding: 15px 30px !important;
        height: auto !important;
    }
    
    button[data-baseweb="tab"] p {
        font-size: 22px !important;
    }

    /* --- Botón OCUPADO (Verde Pastel) --- */
    /* Usamos 'secondary' para los ocupados */
    div.stButton > button[kind="secondary"] {
        background-color: #77DD77 !important; /* Verde pastel suave */
        color: #004d00 !important;           /* Texto verde oscuro para contraste */
        border: 2px solid #5cb85c !important;
        height: 110px !important;
        font-weight: 600;
        border-radius: 10px;
        transition: transform 0.1s;
    }
    
    div.stButton > button[kind="secondary"]:hover {
        background-color: #66cc66 !important; /* Un tono un poco más oscuro al pasar el mouse */
        transform: scale(1.02);
    }

    /* --- Botón LIBRE (Blanco / Gris muy claro) --- */
    /* Usamos 'primary' para los libres */
    div.stButton > button[kind="primary"] {
        background-color: #FFFFFF !important;
        color: #555555 !important;
        border: 1px dashed #D3D3D3 !important;
        height: 110px !important;
        border-radius: 10px;
    }
    
    div.stButton > button[kind="primary"]:hover {
        border: 1px solid #28a745 !important;
        color: #28a745 !important;
    }

    /* Ajuste para que el texto dentro del botón se vea bien */
    div.stButton > button p {
        white-space: pre-wrap;
        line-height: 1.2;
    }
    </style>
    """, unsafe_allow_html=True)

def main():

    # Lógica para calcular la semana
    hoy = datetime.now()
    # weekday() devuelve 0 para lunes, 5 para sábado
    lunes = hoy - timedelta(days=hoy.weekday())
    domingo = lunes + timedelta(days=6)
    
    # Meses en español
    meses = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto", 
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    
    # Lógica de formato dinámico
    if lunes.month == domingo.month:
        # Ejemplo: Semana del 2 al 8 de Febrero
        semana_msg = f"Semana del {lunes.day} al {domingo.day} de {meses[lunes.month]}"
    else:
        # Ejemplo: Semana del 30 de Marzo al 5 de Abril
        semana_msg = f"Semana del {lunes.day} de {meses[lunes.month]} al {domingo.day} de {meses[domingo.month]}"

    st.title("📅 Programación semanal de exhibidores")
    st.subheader(f"✨ {semana_msg}")
    st.write("Selecciona un día y haz clic en un espacio libre para agendarte con tu pareja de servicio.")

    

    # 2. Creación de pestañas por día
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    tabs = st.tabs(dias)

    for i, dia in enumerate(dias):
        with tabs[i]:
            st.subheader(f"Horarios para el {dia}")
            dibujar_matriz_dia(dia)

    # 3. Sección de administración (al final de la página)
    st.divider()
    with st.expander("⚙️ Administración del Sistema"):
        st.warning("El reinicio borrará todos los registros del calendario.")
        
        # Campo para el PIN
        pin_ingresado = st.text_input("Introduce el PIN de administrador", type="password")
        
        if st.button("Reiniciar Semana Completa"):
            # Aquí defines tu PIN (por ejemplo: 1234)
            if pin_ingresado == "1234":
                reiniciar_calendario()
                st.success("¡Calendario reiniciado con éxito!")
                st.rerun()
            else:
                st.error("PIN incorrecto. No tienes permisos para esta acción.")

if __name__ == "__main__":
    main()
