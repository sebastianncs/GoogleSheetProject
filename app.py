import gspread
from google.oauth2.service_account import Credentials
import pandas as pd

# --- CONFIGURACIÓN DE IDENTIFICADORES ---
ID_SHEET = "1czgMQ-pjuG36c46k_PTL0TYoHRMz-RNHK9aZGAWi2uY"
HOJA_ATB = "StockAntibióticos"
HOJA_INSUMOS = "StockInsumos"

def obtener_datos_laboratorio():
    """Conecta con Google Sheets y extrae los dos inventarios."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    
    try:
        # Autenticación
        creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
        client = gspread.authorize(creds)
        spreadsheet = client.open_by_key(ID_SHEET)
        
        # Extracción de StockAntibióticos
        df_atb = pd.DataFrame(spreadsheet.worksheet(HOJA_ATB).get_all_records())
        
        # Extracción de StockInsumos
        df_insumos = pd.DataFrame(spreadsheet.worksheet(HOJA_INSUMOS).get_all_records())
        
        print("✅ Datos extraídos correctamente.")
        return df_atb, df_insumos

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        return None, None

def preprocesamiento_auditoria(df, nombre):
    """Limpia y valida que las fechas y columnas sean procesables."""
    if df.empty:
        print(f"⚠️ La hoja {nombre} está vacía.")
        return df

    # 1. Estandarizar nombres de columnas (quitar espacios y tildes internamente)
    df.columns = df.columns.str.strip().str.replace(' ', '_')
    
    # 2. Convertir fechas (Manejo de excepciones para datos nulos)
    columnas_fecha = ['Marca_temporal', 'Vencimiento', 'Fecha_Recep', 'Fecha_Apertura', 'Fecha_Cierre']
    for col in columnas_fecha:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce')
    
    print(f"📊 {nombre}: {len(df)} registros listos para análisis.")
    return df

# --- EJECUCIÓN DEL FLUJO ---
df_atb_raw, df_insumos_raw = obtener_datos_laboratorio()

if df_atb_raw is not None:
    # Aplicamos limpieza inicial
    df_atb = preprocesamiento_auditoria(df_atb_raw, "Antibióticos")
    df_insumos = preprocesamiento_auditoria(df_insumos_raw, "Insumos")

    # Mostrar vista previa de Antibióticos
    print("\n--- Vista Previa df_atb ---")
    print(df_atb[['Tipo_de_registro', 'Producto', 'Cantidad']].head())