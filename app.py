import streamlit as st
import pandas as pd
import math
import backend
import cv2
import os
from ultralytics import YOLO
import easyocr
import csv
import numpy as np
# Função para carregar dados do CSV de teste
def load_test_csv(file):
    data = pd.read_csv(file)
    return data

# Função para iterar pelos dados do CSV e adicionar à sessão
def iterar_pelo_csv(data):
    st.session_state.new_entries = []
    for index, row in data.iterrows():
        st.session_state.new_entries.append(row)

def tamanho_csv(file):
    df = pd.DataFrame(file)
    return df.shape[0]

def proxima_pagina(quant_multas, tamanho_pagina):
    if st.session_state.pagina_atual < math.ceil(quant_multas / tamanho_pagina):
        if (st.session_state.pagina_atual + 1) != math.ceil(quant_multas / tamanho_pagina):
            st.session_state.pagina_atual += 1

def pagina_anterior():
        if st.session_state.pagina_atual != 0:
            st.session_state.pagina_atual -= 1

def get_elementos_pagina_atual(pagina_atual, tamanho_pagina):
    inicio = pagina_atual * tamanho_pagina
    fim = inicio + tamanho_pagina
    return st.session_state.new_entries[inicio:fim]

# Função para filtrar dados com base nos inputs do usuário
def filtrar_dados(test_data):
    filtro_CNH = st.session_state.get("filtro_CNH", "")
    filtro_nome = st.session_state.get("filtro_nome", "")
    filtro_pontos = st.session_state.get("filtro_pontos", "")
    filtro_licenca = st.session_state.get("filtro_licenca", "")
    filtro_data = st.session_state.get("filtro_data", "")
    filtro_decisao = st.session_state.get("filtro decisao", "")
    #filtro_localizacao = st.session_state.get("filtro_localizacao", "Todos")

    filtered_data = test_data
    if filtro_CNH:
        filtered_data = filtered_data[filtered_data['Numero CNH'].astype(str).str.contains(filtro_CNH, case=False, na=False)]
    if filtro_pontos:
        filtered_data = filtered_data[filtered_data['Pontos na Carteira'].astype(str).str.contains(filtro_pontos, case=False, na=False)]
    if filtro_nome:
        filtered_data = filtered_data[filtered_data['Nome'].astype(str).str.contains(filtro_nome, case=False, na=False)]
    if filtro_data:
        filtered_data = filtered_data[filtered_data['Data/Hora'].astype(str).str.contains(filtro_data, case=False, na=False)]
    if filtro_decisao and filtro_decisao != "Todos":
        filtered_data = filtered_data[filtered_data['Decisao'] == filtro_decisao]
    if filtro_licenca and filtro_licenca != "Todos":
        filtered_data = filtered_data[filtered_data['Licença Ativa'] == filtro_licenca]
    
    return filtered_data


# Função principal do Streamlit
def main():
    csvDB = backend.CsvDB("assets/csv/cars.csv", "assets/csv/owners.csv")
    computerVision = backend.ComputerVision(YOLO("assets/plates.pt"), easyocr.Reader(['en']))
    manager = backend.Manager(csvDB, computerVision)

    quant_videos = len(os.listdir("assets/videos"))
    arquivo_video = "assets/videos/Video1.mp4"
    test_data = load_test_csv('assets/logs/log.csv')
    #test_data = load_test_csv("teste.csv")
    quant_total_multas = tamanho_csv(test_data)
    tamanho_pagina = 12

    if 'new_entries' not in st.session_state:
        st.session_state['new_entries'] = []

    if 'pagina_atual' not in st.session_state:
        st.session_state['pagina_atual'] = 0
    
    if 'primeira' not in st.session_state:
        st.session_state['primeira'] = False
    pagina_atual = st.session_state.pagina_atual

    if 'toggle_states' not in st.session_state:
        st.session_state["toggle_states"] = {}

    st.title('Aplicação de infrações automática')


    with st.sidebar:
        st.text_input("CNH", key="filtro_CNH")
        st.text_input("Nome", key="filtro_nome")
        st.text_input("Pontos", key="filtro_pontos")
        st.selectbox("Licença Ativa", ("Todos", "1", "0"), key="filtro_licenca")
        st.text_input("Data", key="filtro_data")
        st.selectbox("Desição", ("Todos", "Documento Irregular", "Linceça Cassada"), key="filtro_decisao")
        #st.selectbox("Localizacao", 
        #               ("Todos", "Bairro de Fátima", "Boa Viagem", "Cachoeiras", "Centro", "Charitas", 
        ##             "Ponta d'Areia", "Santa Rosa", "São Domingos", "São Francisco", "Viradouro",
            #            "Vital Brazil", "Baldeador", "Barreto", "Caramujo", "Cubango", "Engenhoca",
            #           "Fonseca", "Ilha da Conceição", "Santa Bárbara", "Santana", "São Lourenço",
            #          "Tenente Jardim", "Viçoso Jardim", "Cafubá", "Camboinhas", "Engenho do Mato",
            #         "Itacoatiara", "Itaipu", "Jacaré", "Jardim Imbuí", "Maravista", "Piratininga",
                #        "Santo Antônio", "Serra Grande", "Badu", "Cantagalo", "Ititioca",
                #       "Largo da Batalha", "Maceió", "Maria Paula", "Matapaca", "Sapê",
                #      "Vila Progresso", "Muriqui", "Rio do Ouro", "Várzea das Moças"), key="filtro_localizacao")
        if st.sidebar.button("Aplicar Filtros"):
            filtered_data = filtrar_dados(test_data)
            iterar_pelo_csv(filtered_data)

    confidence = float(st.sidebar.slider("Confiança", 25, 100, 40)) / 100
    source_img = st.sidebar.file_uploader("Escolha a imagem...", type=("jpg", "jpeg", "png", 'bmp', 'webp'))


    # st.write(st.session_state)

    
    colunas_videos = st.columns([9, 1])

    with colunas_videos[1]:
        for i in range(quant_videos):
            if st.button(label=f"{i+1}", key=f"video{i+1}"):
                arquivo_video = f"assets/videos/Video{i+1}.mp4"
                filtered_data = filtrar_dados(test_data)
                iterar_pelo_csv(filtered_data)

    with colunas_videos[0]:
        if source_img is None:
            st.video(arquivo_video)
        else:
            file_bytes = np.asarray(bytearray(source_img.read()))
            opencv_image = cv2.imdecode(file_bytes, 1)
            st.image(opencv_image, use_column_width=True)
            manager.run(opencv_image)
            iterar_pelo_csv(test_data)
    # Exibir novos dados conforme são processados
    colunas_multas = st.columns(3)
    contador = 0

#----------------------------------------------------------------------

    entradas_pagina_atual = get_elementos_pagina_atual(pagina_atual, tamanho_pagina)

    for index in range(len(entradas_pagina_atual)):
        coluna = colunas_multas[contador]
        entry = entradas_pagina_atual[index]
        with coluna:
            content_placeholder = st.empty()
            print("--------", entry)
            
            # Inicializar o estado de toggle para cada card
            if index not in st.session_state['toggle_states']:
                st.session_state['toggle_states'][index] = False

            # # Alternar entre exibir o card ou a imagem
            if st.session_state['toggle_states'][index]:
                content_placeholder.image(entry['imagem'])
            else:
                content_placeholder.write(entry.drop(labels=['imagem']))
            
            # Botão para alternar o estado de exibição
            if st.button(f"Imagem", key=f"toggle_button_{index}"):
                st.session_state['toggle_states'][index] = not st.session_state['toggle_states'][index]
                st.rerun()

        contador = (contador + 1) % 3

#----------------------------------------------------------------------



    colunas_botoes_paginas = st.columns(2)

    with colunas_botoes_paginas[0]:
        if st.button("Página Anterior", key="pagina_anterior"):
            pagina_anterior()
            st.rerun()


    with colunas_botoes_paginas[1]:
        if st.button("Proxima Página", key="proxima_pagina"):
            proxima_pagina(quant_total_multas, tamanho_pagina)
            st.rerun()
    


    if st.session_state.primeira == False:
        st.session_state.primeira = True
        iterar_pelo_csv(test_data)
        st.rerun()



if __name__ == '__main__':
    main()
