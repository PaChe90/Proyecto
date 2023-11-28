import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
from streamlit_folium import folium_static
import folium


class VisualizadorDatos:
    def __init__(self, archivo):
        self.data = pd.read_csv(archivo, delimiter=";")
        self.data_ubigeos = pd.read_csv('TB_UBIGEOS.csv')
        self.columnas_departamento = ['DEPARTAMENTO1']
        self.columnas_provincia = ['DEPARTAMENTO1', 'PROVINCIA1']
        self.columnas_distrito = ['DEPARTAMENTO1', 'PROVINCIA1', 'DISTRITO1']
        self.columnas_anp_cate = ['ANP_CATE']

    def filtrar_y_eliminar_nulos(self, data_frame):
        return data_frame.dropna()

    def convertir_a_str(self, data_frame):
        return data_frame.applymap(str)

    def concatenar_columnas(self, data_frame, columnas):
        data_frame['Location'] = data_frame.apply(lambda row: ', '.join(row), axis=1)
        return data_frame

    def contar_ocurrencias(self, data_frame):
        conteo = data_frame['Location'].value_counts().reset_index()
        conteo.columns = ['Ubicacion', 'Count']
        return conteo

    def generar_grafica(self, conteo, titulo):
        figura = px.bar(conteo, x='Ubicacion', y='Count', title=titulo)
        return figura

    def mostrar_grafica(self, figura):
        st.plotly_chart(figura)
    
    def generar_mapa_ubigeos(self, gdf):
        m = folium.Map(location=[-9.1900, -75.0152], zoom_start=5, control_scale=True)

        for idx, row in gdf.iterrows():
            folium.Marker(
                location=[row['latitud'], row['longitud']],
                popup=row['distrito'],
                icon=folium.Icon(color='blue')
            ).add_to(m)

        return m

def main():
    # Título de la aplicación Streamlit
    st.markdown("# GRAFICA DE DATOS ")

    # Crear una instancia de la clase VisualizadorDatos y cargar el archivo CSV
    visualizador = VisualizadorDatos("archivo.csv")

    # Filtrar y eliminar valores nulos para cada nivel geográfico (departamento, provincia, distrito)
    data_anp_cate = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_anp_cate])
    data_departamento = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_departamento])
    data_provincia = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_provincia])
    data_distrito = visualizador.filtrar_y_eliminar_nulos(visualizador.data[visualizador.columnas_distrito])

    # Convertir las columnas a tipo str si no lo son
    data_anp_cate = visualizador.convertir_a_str(data_anp_cate)
    data_departamento = visualizador.convertir_a_str(data_departamento)
    data_provincia = visualizador.convertir_a_str(data_provincia)
    data_distrito = visualizador.convertir_a_str(data_distrito)

    # Concatenar las columnas para formar la columna 'Location' para cada nivel geográfico
    data_anp_cate = visualizador.concatenar_columnas(data_anp_cate, visualizador.columnas_anp_cate)
    data_departamento = visualizador.concatenar_columnas(data_departamento, visualizador.columnas_departamento)
    data_provincia = visualizador.concatenar_columnas(data_provincia, visualizador.columnas_provincia)
    data_distrito = visualizador.concatenar_columnas(data_distrito, visualizador.columnas_distrito)

    # Contar las ocurrencias de cada ubicación para cada nivel geográfico
    conteo_anp_cate = visualizador.contar_ocurrencias(data_anp_cate)
    conteo_departamento = visualizador.contar_ocurrencias(data_departamento)
    conteo_provincia = visualizador.contar_ocurrencias(data_provincia)
    conteo_distrito = visualizador.contar_ocurrencias(data_distrito)

    # Generar gráficas de barras para cada nivel geográfico
    fig_anp_cate = visualizador.generar_grafica(conteo_anp_cate, "Conteo por ANP CATE")
    fig_departamento = visualizador.generar_grafica(conteo_departamento, "Conteo por Departamento")
    fig_provincia = visualizador.generar_grafica(conteo_provincia, "Conteo por Provincia")
    fig_distrito = visualizador.generar_grafica(conteo_distrito, "Conteo por Distrito")
    
    # Unir los datos de coordenadas con los datos de Ubigeos utilizando el código UBIGEO1
    merged_data = pd.merge(visualizador.data, visualizador.data_ubigeos, how="left", left_on="UBIGEO1", right_on="ubigeo_inei")

    # Filtrar solo las filas que tienen datos de Ubigeo y coordenadas
    filtered_data = merged_data.dropna(subset=['latitud', 'longitud'])
    
    # Crear un GeoDataFrame con la información de Ubigeos
    geometry = gpd.points_from_xy(filtered_data['longitud'], filtered_data['latitud'])
    gdf = gpd.GeoDataFrame(filtered_data, geometry=geometry)

    # Generar el mapa de Ubigeos
    mapa_ubigeos = visualizador.generar_mapa_ubigeos(gdf)
    
    # Mostrar el mapa de Ubigeos en la aplicación Streamlit
    st.markdown("## Mapa de Ubigeos")
    folium_static(mapa_ubigeos)

    # Mostrar las gráficas en la aplicación Streamlit
    visualizador.mostrar_grafica(fig_anp_cate)
    visualizador.mostrar_grafica(fig_departamento)
    visualizador.mostrar_grafica(fig_provincia)
    visualizador.mostrar_grafica(fig_distrito)

if __name__ == "__main__":
    main()
