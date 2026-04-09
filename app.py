import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Gestión Laboratorio Microbiología", layout="wide")

st.title("🧪 Sistema de Inventario de Antibióticos")

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

df_consumo['siguiente_evento'] = df_consumo.groupby('antibiotico')['tipo_registro'].shift(-1)
df_consumo['fecha_siguiente_apertura'] = df_consumo.groupby('antibiotico')['fecha_apertura'].shift(-1)

# 3. FILTRO CRÍTICO: 
# Solo calculamos la duración si:
# - El evento actual es 'Apertura'
# - El siguiente evento TAMBIÉN es 'Apertura' (esto garantiza que NO hubo un 'Cierre' entre medio)
mask_consumo_real = (df_consumo['tipo_registro'] == 'Apertura') & (df_consumo['siguiente_evento'] == 'Apertura')

# 4. Calculamos los días solo para esos casos
df_consumo.loc[mask_consumo_real, 'dias_duracion'] = (
    df_consumo['fecha_siguiente_apertura'] - df_consumo['fecha_apertura']
).dt.days

# 5. Resumen final de duración real
rendimiento_real = df_consumo.groupby('antibiotico')['dias_duracion'].mean().reset_index()
rendimiento_real.columns = ['Antibiótico', 'Duración Promedio (Días)']

st.subheader("⏳ Rendimiento Neto por Antibiótico")
st.markdown("_Cálculo basado exclusivamente en ciclos de consumo completo (Apertura a Apertura)_")

if not rendimiento_real.dropna().empty:
    st.dataframe(rendimiento_real.dropna().style.highlight_max(axis=0, color='#b7e4c7'))
else:
    st.info("Aún no hay suficientes ciclos Apertura-Apertura para calcular promedios.")
