import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión Laboratorio Microbiología", layout="wide")

st.title("🧪 Sistema de Inventario de Antibióticos")
st.markdown("### Diplomado IA para Ciencias de la Salud - USM")

# --- 1. CARGA Y LIMPIEZA (Tu lógica validada) ---
@st.cache_data # Esto hace que la web sea rápida
def cargar_datos():
    df = pd.read_csv('stock_atb.csv')
    
    # Renombrar
    nuevos_nombres = {
        'Tipo de registro': 'tipo_registro',
        'Antibiótico': 'antibiotico',
        'Fecha de recepción': 'fecha_recepcion',
        'Cantidad (En caso de sensidiscos, indicar cantidad de tubos)': 'cantidad',
        'Fecha de apertura': 'fecha_apertura',
        'Fecha de cierre': 'fecha_cierre',
        'Motivo de cierre': 'motivo_cierre',
        'Fecha de vencimiento': 'fecha_vencimiento',
        'Cantidad eliminada': 'cantidad_eliminada'
    }
    df = df.rename(columns=nuevos_nombres)
    
    # Limpieza
    cols_drop = ['Marca temporal', 'Responsable (iniciales)', 'Comentario (opcional)']
    df = df.drop(columns=cols_drop, errors='ignore')
    
    # Formato Fechas
    cols_fechas = ['fecha_recepcion', 'fecha_apertura', 'fecha_cierre', 'fecha_vencimiento']
    for col in cols_fechas:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors='coerce')
        
    # Lógica de Números
    df['cantidad'] = pd.to_numeric(df['cantidad'], errors='coerce').fillna(0)
    df['cantidad_eliminada'] = pd.to_numeric(df['cantidad_eliminada'], errors='coerce').fillna(0)
    
    return df

df = cargar_datos()

# --- 2. CÁLCULO DE STOCK (Tu fórmula de éxito) ---
recepcionados = df[df['tipo_registro'] == 'Recepción'].groupby('antibiotico')['cantidad'].sum()
aperturas = df[df['tipo_registro'] == 'Apertura'].groupby('antibiotico').size()
eliminados = df.groupby('antibiotico')['cantidad_eliminada'].sum()

resumen_stock = pd.DataFrame({
    'Recepcionados': recepcionados,
    'Aperturas': aperturas,
    'Eliminados': eliminados
}).fillna(0)

resumen_stock['Stock_Actual'] = resumen_stock['Recepcionados'] - resumen_stock['Aperturas'] - resumen_stock['Eliminados']

# --- 3. INTERFAZ DE USUARIO (La "Mini Web") ---

# Métricas rápidas arriba
col1, col2, col3 = st.columns(3)
col1.metric("Antibióticos Registrados", len(resumen_stock))
col2.metric("Total Críticos (<=1)", len(resumen_stock[resumen_stock['Stock_Actual'] <= 1]))
col3.metric("Total Eliminados (Vencimiento/Falla)", int(resumen_stock['Eliminados'].sum()))

# Gráfico y Tabla lado a lado
col_izq, col_der = st.columns([2, 1])

with col_izq:
    st.subheader("📊 Visualización de Stock")
    fig, ax = plt.subplots()
    resumen_stock['Stock_Actual'].plot(kind='bar', ax=ax, color='teal')
    ax.axhline(y=1, color='red', linestyle='--', label='Umbral Crítico')
    ax.set_ylabel("Unidades")
    plt.xticks(rotation=45, ha='right')
    st.pyplot(fig)

with col_der:
    st.subheader("📋 Detalle por Producto")
    st.dataframe(resumen_stock[['Stock_Actual']].sort_values(by='Stock_Actual'))

# Botón para tus colegas
if st.button('🚀 Ejecutar Análisis de Vencimientos'):
    st.write("Análisis en desarrollo para el Módulo 3...")