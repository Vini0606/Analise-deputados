import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np
import os

def prepare_dataframe(df_json):
    """
    Prepara o dataframe calculando métricas, limpando dados e cruzando 
    com a base do Excel usando o username do Instagram como chave.
    """
    # ==========================================
    # 0. CALCULAR MÉDIAS DOS POSTS (Se necessário)
    # ==========================================
    if 'avg_engajamento' not in df_json.columns and 'latestPosts' in df_json.columns:
        likes_list, comments_list, views_list = [], [], []
        avg_likes, avg_comments, avg_views, avg_eng = [], [], [], []
        
        for index, row in df_json.iterrows():
            posts = row.get('latestPosts', [])
            if isinstance(posts, list) and len(posts) > 0:
                likes = sum(post.get('likesCount', 0) for post in posts)
                comments = sum(post.get('commentsCount', 0) for post in posts)
                views = sum(post.get('playCount', post.get('videoPlayCount', 0)) for post in posts) 
                
                qtd_posts = len(posts)
                
                avg_likes.append(likes / qtd_posts)
                avg_comments.append(comments / qtd_posts)
                avg_views.append(views / qtd_posts)
                avg_eng.append((likes + comments) / qtd_posts)

                likes_list.append(likes) 
                comments_list.append(comments) 
                views_list.append(views)

            else:
                
                avg_likes.append(0)
                avg_comments.append(0)
                avg_views.append(0)
                avg_eng.append(0)
                
                # ADICIONAR ESTAS TRÊS LINHAS:
                likes_list.append(0)
                comments_list.append(0)
                views_list.append(0)
                
        df_json['avg_likes'] = avg_likes
        df_json['avg_comments'] = avg_comments
        df_json['avg_video_views'] = avg_views
        df_json['avg_engajamento'] = avg_eng
        df_json['likes'] = likes_list
        df_json['comments'] = comments_list
        df_json['views'] = views_list
        


    # ==========================================
    # 1. CÁLCULO DE PORCENTAGENS E MÉTRICAS FINAIS
    # ==========================================
    followers = df_json['followersCount'].replace(0, 1) 
    df_json['% Engajamento'] = (df_json['avg_engajamento'] / followers) * 100
    df_json['% de Visualização'] = (df_json['avg_video_views'] / followers) * 100
    df_json['% Curtidas'] = (df_json['avg_likes'] / followers) * 100
    df_json['% Comentarios'] = (df_json['avg_comments'] / followers) * 100
    
    df_json.columns = df_json.columns.str.strip()
    
    if 'inputUrl' in df_json.columns:
        df_json['ig_join_key'] = (df_json['inputUrl']
                                  .astype(str).str.lower().str.strip()
                                  .str.replace('@', '', regex=False).str.split('?').str[0]
                                  .str.rstrip('/').str.split('/').str[-1])

    # ==========================================
    # 2. PREPARAÇÃO DO DATAFRAME DO EXCEL
    # ==========================================
    try:
        df_excel = pd.read_excel(settings.DEPUTADOS_INSTA_XLSX_OUT)
        df_excel.columns = df_excel.columns.str.strip()
        
        # GARANTE QUE A COLUNA DE NOME SE CHAMARÁ 'Nome_Deputado'
        if 'Nome Civil' in df_excel.columns:
            df_excel = df_excel.rename(columns={'Nome Civil': 'Nome_Deputado'})
        elif 'Nome' in df_excel.columns:
            df_excel = df_excel.rename(columns={'Nome': 'Nome_Deputado'})
        
        if 'Partido' in df_excel.columns and df_excel['Partido'].astype(str).str.contains('-').any():
            df_excel[['Partido', 'UF']] = df_excel['Partido'].astype(str).str.split('-', n=1, expand=True)
            df_excel['Partido'] = df_excel['Partido'].str.strip()
            df_excel['UF'] = df_excel['UF'].str.strip()
            
        if 'Instagram' in df_excel.columns:
            df_excel['ig_join_key'] = (df_excel['Instagram']
                                      .astype(str).str.lower().str.strip()
                                      .str.replace('@', '', regex=False).str.split('?').str[0]
                                      .str.rstrip('/').str.split('/').str[-1])
            
    except FileNotFoundError:
        print("\n[ALERTA JOIN] Arquivo CSV não encontrado. Retornando apenas JSON.")
        return df_json

    # ==========================================
    # 3. CRUZAMENTO (MERGE) DOS DADOS
    # ==========================================
    if 'ig_join_key' in df_excel.columns and 'ig_join_key' in df_json.columns:
        # REMOVE CHAVES VAZIAS PARA EVITAR EXPLOSÃO CARTESIANA
        chaves_invalidas = ['', 'nan', 'none', 'null']
        df_excel = df_excel[~df_excel['ig_join_key'].isin(chaves_invalidas)]
        df_json = df_json[~df_json['ig_join_key'].isin(chaves_invalidas)]
        
        df_merged = pd.merge(df_excel, df_json, on='ig_join_key', how='inner')
        df_merged = df_merged.drop(columns=['ig_join_key'])
        
        print(f"\n[SUCESSO JOIN] Merge limpo realizado! Linhas válidas: {len(df_merged)}")
        return df_merged
    else:
        return df_json

def save_graph_2a(df):
    
    if df.empty: return
    
    # Filtramos perfis menores que 1K para não jogar a escala logarítmica lá pro fundo
    df_valid = df[df['followersCount'] >= 1000]
    if df_valid.empty: 
        df_valid = df # Fallback de segurança
        
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.scatter(df_valid['followersCount'], df_valid['% Engajamento'], 
               alpha=0.6, color='#2c3e50', edgecolors='white', linewidth=0.5, s=60)
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    #ax.set_title('Correlação: Volume de Seguidores vs Taxa de Engajamento', fontsize=14, pad=15, fontweight='bold', color='#333333')
    ax.set_xlabel('Número de Seguidores', fontsize=11, labelpad=10, color='#555555')
    ax.set_ylabel('Taxa de Engajamento (%)', fontsize=11, labelpad=10, color='#555555')

    def human_format(num, _):
        magnitude = 0
        while abs(num) >= 1000 and magnitude < 3:
            magnitude += 1
            num /= 1000.0
        if num.is_integer():
            return f"{int(num)}{['', 'K', 'M', 'B'][magnitude]}"
        return f"{num:.1f}{['', 'K', 'M', 'B'][magnitude]}"
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(human_format))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y*100:g}%"))

    # --- A SOLUÇÃO DO ESPAÇO: LIMITES DINÂMICOS ---
    # Encontra o min e max real da sua base e aplica uma margem multiplicativa (escala log)
    min_x = df_valid['followersCount'].min() * 0.7   # 30% de respiro à esquerda
    max_x = df_valid['followersCount'].max() * 1.5   # 50% de respiro à direita
    
    # Filtra valores maiores que zero para evitar erro de log(0)
    engajamentos_validos = df_valid[df_valid['% Engajamento'] > 0]['% Engajamento']
    if not engajamentos_validos.empty:
        min_y = engajamentos_validos.min() * 0.6     # 40% de respiro embaixo
        max_y = engajamentos_validos.max() * 1.5     # 50% de respiro em cima
        ax.set_ylim(min_y, max_y)
        
    ax.set_xlim(min_x, max_x)

    # Design
    ax.grid(True, which="major", ls="--", alpha=0.4, color='#cccccc')
    ax.grid(False, which="minor") 
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#dddddd')
    ax.spines['bottom'].set_color('#dddddd')

    plt.tight_layout()
    os.makedirs('data/Graphics', exist_ok=True)
    
    plt.savefig('data/Graphics/graph_2a.png', dpi=300, bbox_inches='tight') 
    plt.close()

def save_graph_3(df, target_username=None):
    
    if df.empty: return
    
    # Filtramos perfis menores que 1K para não jogar a escala logarítmica lá pro fundo
    df_valid = df[df['followersCount'] >= 1000]
    if df_valid.empty: 
        df_valid = df # Fallback de segurança
        
    fig, ax = plt.subplots(figsize=(10, 6))
    
    ax.scatter(df_valid['followersCount'], df_valid['% Engajamento'], 
               alpha=0.6, color='#2c3e50', edgecolors='white', linewidth=0.5, s=60)
    
    ax.set_xscale('log')
    ax.set_yscale('log')
    
    #ax.set_title('Correlação: Volume de Seguidores vs Taxa de Engajamento', fontsize=14, pad=15, fontweight='bold', color='#333333')
    ax.set_xlabel('Número de Seguidores', fontsize=11, labelpad=10, color='#555555')
    ax.set_ylabel('Taxa de Engajamento (%)', fontsize=11, labelpad=10, color='#555555')

    def human_format(num, _):
        magnitude = 0
        while abs(num) >= 1000 and magnitude < 3:
            magnitude += 1
            num /= 1000.0
        if num.is_integer():
            return f"{int(num)}{['', 'K', 'M', 'B'][magnitude]}"
        return f"{num:.1f}{['', 'K', 'M', 'B'][magnitude]}"
    
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(human_format))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda y, _: f"{y*100:g}%"))

    # --- A SOLUÇÃO DO ESPAÇO: LIMITES DINÂMICOS ---
    # Encontra o min e max real da sua base e aplica uma margem multiplicativa (escala log)
    min_x = df_valid['followersCount'].min() * 0.7   # 30% de respiro à esquerda
    max_x = df_valid['followersCount'].max() * 1.5   # 50% de respiro à direita
    
    # Filtra valores maiores que zero para evitar erro de log(0)
    engajamentos_validos = df_valid[df_valid['% Engajamento'] > 0]['% Engajamento']
    if not engajamentos_validos.empty:
        min_y = engajamentos_validos.min() * 0.6     # 40% de respiro embaixo
        max_y = engajamentos_validos.max() * 1.5     # 50% de respiro em cima
        ax.set_ylim(min_y, max_y)
        
    ax.set_xlim(min_x, max_x)

    # Design
    ax.grid(True, which="major", ls="--", alpha=0.4, color='#cccccc')
    ax.grid(False, which="minor") 
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#dddddd')
    ax.spines['bottom'].set_color('#dddddd')

    plt.tight_layout()
    os.makedirs('data/Graphics', exist_ok=True)
    
    # Destacar um usuário específico se solicitado
    if target_username:
        user_row = df[df['username'] == target_username]
        if not user_row.empty:
            # Pegamos o valor exato de X e Y do deputado alvo
            target_x = user_row['followersCount'].values[0]
            target_y = user_row['% Engajamento'].values[0]
            
            # Desenha a linha vertical e horizontal cruzando no ponto exato
            # zorder=1 garante que as linhas fiquem atrás do ponto em destaque
            ax.axvline(x=target_x, color='gray', linestyle=':', alpha=0.7, zorder=1)
            ax.axhline(y=target_y, color='gray', linestyle=':', alpha=0.7, zorder=1)
            
            # Plota o ponto de destaque (zorder=5 garante que fique por cima das linhas)
            ax.scatter(target_x, target_y, color='gold', s=150, edgecolors='black', 
                       label=target_username, zorder=5)
            ax.legend()

    # Salva o gráfico 3 corretamente
    plt.savefig('data/Graphics/graph_3.png', dpi=300, bbox_inches='tight')
    plt.close()

def gerar_graficos_por_uf_(df, uf, metrica):
    """
    Filtra os deputados de uma UF, ranqueia por uma métrica e salva os gráficos de Top 10 e Bottom 10.
    """
    # Filtra pela UF solicitada (Assumindo que a coluna se chama 'UF' após aquele seu split anterior)
    df_uf = df[df['UF'] == uf].copy()
    
    if df_uf.empty:
        print(f"Nenhum dado encontrado para a UF: {uf}. Verifique a sigla.")
        return
        
    # Remove deputados que não tenham valor nessa métrica (NaN)
    df_uf = df_uf.dropna(subset=[metrica])
    
    # Ordena do maior para o menor
    df_sorted = df_uf.sort_values(by=metrica, ascending=False)
    
    # Separa os 10 melhores e os 10 piores
    top_10 = df_sorted.head(10)
    bottom_10 = df_sorted.tail(10)
    
    # Para o gráfico de barras horizontais ficar com o 1º lugar no topo, 
    # precisamos ordenar a amostra de trás pra frente
    top_10 = top_10.sort_values(by=metrica, ascending=True)
    bottom_10 = bottom_10.sort_values(by=metrica, ascending=True)
    
    # Cria a pasta da UF caso não exista
    pasta_destino = f'data/Graphics/ufs/{uf}'
    os.makedirs(pasta_destino, exist_ok=True)
    
    # --- PLOT: TOP 10 ---
    plt.figure(figsize=(10, 6))
    
    # 1. Altera a cor para amarelo/ouro
    plt.barh(top_10['Nome_Deputado'], top_10[metrica], color='gold', edgecolor='black')
    
    plt.title(f'Top 10 Deputados - {metrica} ({uf})', fontsize=14)
    plt.xlabel(metrica, fontsize=12)
    plt.ylabel('Nome do Deputado', fontsize=12)
    
    # 2. Força a remoção de qualquer grade (grid)
    plt.grid(False)
    
    # 3. Remove as bordas do topo e da direita para focar apenas nas barras
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    metrica_arquivo = metrica.replace(' ', '_').replace('%', 'pct')
    plt.savefig(f'{pasta_destino}/TOP10_{metrica_arquivo}_{uf}.png', dpi=300)
    plt.close()
    
    # --- PLOT: BOTTOM 10 ---
    plt.figure(figsize=(10, 6))
    
    # 1. Altera a cor para amarelo/ouro
    plt.barh(bottom_10['Nome_Deputado'], bottom_10[metrica], color='gold', edgecolor='black')
    
    plt.title(f'Bottom 10 Deputados - {metrica} ({uf})', fontsize=14)
    plt.xlabel(metrica, fontsize=12)
    plt.ylabel('Nome do Deputado', fontsize=12)
    
    # 2. Força a remoção de qualquer grade (grid)
    plt.grid(False)
    
    # 3. Remove as bordas do topo e da direita para focar apenas nas barras
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    
    plt.savefig(f'{pasta_destino}/BOTTOM10_{metrica_arquivo}_{uf}.png', dpi=300)
    plt.close()

def gerar_graficos_por_uf(df, uf, metrica):
    """
    Filtra os deputados de uma UF, ranqueia por uma métrica e salva os gráficos de Top 10 e Bottom 10.
    """
    # Filtra pela UF solicitada (Assumindo que a coluna se chama 'UF' após aquele seu split anterior)
    df_uf = df[df['UF'] == uf].copy()
    
    if df_uf.empty:
        print(f"Nenhum dado encontrado para a UF: {uf}. Verifique a sigla.")
        return
        
    # Remove deputados que não tenham valor nessa métrica (NaN)
    df_uf = df_uf.dropna(subset=[metrica])
    
    # Ordena do maior para o menor
    df_sorted = df_uf.sort_values(by=metrica, ascending=False)
    
    # Separa os 10 melhores e os 10 piores
    top_10 = df_sorted.head(10)
    bottom_10 = df_sorted.tail(10)
    
    # Para o gráfico de barras horizontais ficar com o 1º lugar no topo, 
    # precisamos ordenar a amostra de trás pra frente
    top_10 = top_10.sort_values(by=metrica, ascending=True)
    bottom_10 = bottom_10.sort_values(by=metrica, ascending=True)
    
    # Cria a pasta da UF caso não exista
    pasta_destino = f'data/Graphics/ufs/{uf}'
    os.makedirs(pasta_destino, exist_ok=True)
    
# --- PLOT: TOP 10 ---
    plt.figure(figsize=(10, 6))
    
    # 1. Salva as barras em uma variável chamada 'bars'
    bars = plt.barh(top_10['Nome_Deputado'], top_10[metrica], color='gold') 
    
    plt.title(f'Top 10 Deputados - {metrica} ({uf})', fontsize=14, pad=20)
    # plt.xlabel(metrica, fontsize=12, labelpad=10) <-- REMOVE ESTA LINHA (não precisamos mais)
    
    plt.grid(False)
    ax = plt.gca()
    
    # 2. Adiciona os valores na ponta de cada barra (com 1 casa decimal)
    ax.bar_label(bars, padding=5, fmt='%.1f', fontsize=10, color='black')
    
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    # 3. Esconde completamente os números da régua do Eixo X na base do gráfico
    ax.xaxis.set_visible(False)
    
    plt.tight_layout()
    
    metrica_arquivo = metrica.replace(' ', '_').replace('%', 'pct')
    plt.savefig(f'{pasta_destino}/TOP10_{metrica_arquivo}_{uf}.png', dpi=300)
    plt.close()
    
    # --- PLOT: BOTTOM 10 ---
    plt.figure(figsize=(10, 6))
    
    # 1. Salva as barras em uma variável
    bars = plt.barh(bottom_10['Nome_Deputado'], bottom_10[metrica], color='gold')
    
    plt.title(f'Bottom 10 Deputados - {metrica} ({uf})', fontsize=14, pad=20)
    # plt.xlabel(metrica, fontsize=12, labelpad=10) <-- REMOVE ESTA LINHA
    
    plt.grid(False)
    ax = plt.gca()
    
    # 2. Adiciona os valores na ponta de cada barra
    ax.bar_label(bars, padding=5, fmt='%.1f', fontsize=10, color='black')
    
    for spine in ax.spines.values():
        spine.set_visible(False)
        
    ax.tick_params(left=False, bottom=False)
    
    # 3. Esconde a régua do Eixo X
    ax.xaxis.set_visible(False)
    
    plt.tight_layout()
    
    plt.savefig(f'{pasta_destino}/BOTTOM10_{metrica_arquivo}_{uf}.png', dpi=300)
    plt.close()

if __name__ == "__main__":
    
    try:
        from config import settings
        import pandas as pd
        
        print(f"Carregando dados do arquivo: {settings.APIFY_JSON_OUT} ...")
        df_deputados = pd.read_json(settings.APIFY_JSON_OUT, orient='records')
        
        # --- RAIO-X 1: Verificando o carregamento inicial ---
        print(f"\n[DEBUG 1] Linhas carregadas do JSON: {len(df_deputados)}")
        print(f"[DEBUG 2] A coluna 'latestPosts' existe no JSON? {'latestPosts' in df_deputados.columns}")
        
        df_processado = prepare_dataframe(df_deputados)
        print(f"[DEBUG 3] Linhas após a função prepare_dataframe: {len(df_processado)}")
        
        colunas_plotagem = ['followersCount', '% Engajamento', 'likesCount', 'Frequencia (Posts/Dia)']
        colunas_existentes = [c for c in colunas_plotagem if c in df_processado.columns]
        
        # --- RAIO-X 2: Verificando as colunas e os nulos ---
        print(f"\n[DEBUG 4] Colunas calculadas prontas para o gráfico: {colunas_existentes}")
        print("[DEBUG 5] Contagem de valores nulos (NaN) por coluna:")
        
        for col in colunas_existentes:
            nulos = df_processado[col].isna().sum()
            total = len(df_processado)
            print(f"   -> Coluna '{col}': {nulos} nulos de {total} linhas. ({total - nulos} linhas válidas)")
            
        df_plot = df_processado.dropna(subset=colunas_existentes).copy()
        
        print(f"\n[DEBUG 6] Linhas que sobraram para o gráfico após remover nulos: {len(df_plot)}")
        
        if not df_plot.empty:
            print(f"\nGerando gráficos com {len(df_plot)} registros...")
            save_graph_2a(df_plot)
            save_graph_3(df_plot, target_username='viniciuscarvalhooficial')
            gerar_graficos_por_uf(df_plot, uf='SP', metrica='% Engajamento')
            gerar_graficos_por_uf(df_plot, uf='SP', metrica='followersCount')
            gerar_graficos_por_uf(df_plot, uf='SP', metrica='postsCount')
            gerar_graficos_por_uf(df_plot, uf='SP', metrica='likes')
            gerar_graficos_por_uf(df_plot, uf='SP', metrica='comments')
            gerar_graficos_por_uf(df_plot, uf='SP', metrica='views')
            

            print("Sucesso: Gráficos salvos em data/Graphics/")
        else:
            print("\nErro: DataFrame de plotagem está vazio.")
            print("Ação: Olhe o [DEBUG 5] acima. A coluna que tiver a mesma quantidade de nulos e de linhas totais é o problema!")
            
    except Exception as e:
        print(f"Erro na execução do script: {e}")