import streamlit as st
import pandas as pd
import math
import plotly_express as px
import plotly.graph_objects as go
from streamlit_option_menu import option_menu
from functions import *
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.stylable_container import stylable_container
from streamlit_extras.row import row
import plotly.io as pio
import io
import base64


#import files
participants=pd.read_excel("Excel files/Transformações.xlsx",sheet_name='participantes')
scores=pd.read_excel("Excel files/Transformações.xlsx",sheet_name='trans_campo_perg_pont')
scores['Pergunta']=scores['Pergunta'].str.strip()

trans_name=pd.read_excel("Excel files/Transformações.xlsx",sheet_name='transf_names')



# Retrieve the data from session state (that was received in upload page)
part_df,answ_df=st.session_state['dataframe']



# SIDEBAR
with st.sidebar:
    # Homepage button
    homepage=st.button(label=' Página Inicial ',on_click=reset,use_container_width=True,icon=':material/home:')

    st.write('')

    # Option Menu
    selected=option_menu(
        menu_title='',
        menu_icon='menu',
        options=['Dashboard','Respostas','Simulação','---','Participantes','Transformações'],
        icons=['speedometer2','journal-text','pencil','','person','columns-gap'],
        styles={
            'container':{'background-color':'white'}},
        default_index=0,
        orientation='vertical',
        key='option_menu_dashboard')
    
 
    # filtro do NOME DA EMPRESA
    company=collect_compay(part_df)

    # filtro dos PARTICIPANTES A CONSIDERAR
    participant=collect_participants(answ_df,company=company)







# with content:
titles,logo=st.columns((6,1),vertical_alignment='top')
with titles:
    title=st.empty() # lugar para o texto
    subtitle=st.empty() #lugar para o subtitulo
with logo:
    st.image(f'images/{company}.png',use_column_width=True)


# DASHBOARD
if selected == 'Dashboard':
    
    title.header(company)
    subtitle.subheader('')

    # --------------------- Métricas ------------------------------------------
    num_participants,mean,category=st.columns(3,gap='small',vertical_alignment='top')
    with mean:
        st.metric(label='Média das pontuações',value=calculate_mean(dataframe=answ_df,company=company,participants=participant))
    with category:
        st.metric(label='Nível de Maturidade Digital',value=maturity_level(calculate_mean(answ_df,company,participants=participant)))
    with num_participants:
        df_selection= answ_df.query("Empresa == @company and Colaborador==@participant")
        st.metric(label='Número total de respostas',value=len(df_selection['Colaborador'].unique()))

    style_metric_cards()
    
    # -------------------------- Radar Chart | Tabela ------------------------------------
    with stylable_container(
        key='container_with_border',
        css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px)
        }
        """):            
        
        st.subheader('Média das pontuações por transformação')

        table, radar_chart=st.columns((3,5),gap='medium',vertical_alignment='top')
        with radar_chart:

            def create_polar_chart(toggle_values):
                avg_per_transf=average_per_transformation(answ_df,company,participant)
                
                # 1. create figure where we're going to add our chart
                fig=go.Figure()

                # 2. set the text size and shape of chart
                fig.update_layout({'font_size':14})
                fig.update_polars(gridshape='linear')

                # 3. adapt our data so that both lines can close; we have to add the first element back into our list 
                r=avg_per_transf['Média'].to_list()
                r.append(r[0])

                l=avg_per_transf['Nome Transformação'].to_list()
                l.append(l[0])

                    # 3.1 formatar o texto para não ficar muito comprido
                l[3]='T4 -Engenharia Focada no <br> Cliente de Ponta a Ponta'
                l[4]='T5 - Organização Centrada <br> no Ser Humano'
                l[6]='T7 - Indústria aberta e orientada <br> para a cadeia de valor'
                l[0]=l[-1]= 'T1 - Tecnologias de <br> Manufatura Avançada'


                # 4. define a web chart for the results and for the industry of the future
                company_results = go.Scatterpolar(
                    r=r,  
                    theta=l,
                    mode='lines+markers+text',                
                    name=f'{company}',

                    # text=r,
                    # textposition='middle center',
                    # textfont=dict(
                    #     family='Trebuchet MS Black',
                    #     size=13,        # Change text size
                    #     color='black'),   # Change text color

                    line=dict(color='#FD6C6A',width=2),
                    fill='toself',
                    fillcolor="rgba(255, 0, 0, 0.2)")   


                future_industry = go.Scatterpolar(
                    r=[4]*(len(avg_per_transf['Média'])+1),  
                    theta=l,
                    mode='lines+markers',                
                    name='Indústria do Futuro',
                    hoverinfo='r',
                    line=dict(color='#2AC8C5',width=3)
                    )            

                # 5. add both charts to figure previously defined
                fig.add_traces([company_results,future_industry])

                if toggle_values:
                    # Add annotations for each label with background color
                    annotations = []

                    for i, category in enumerate(avg_per_transf['Média']):
                        angle = (i * 2 * math.pi / len(avg_per_transf['Média']))- (math.pi / 2) # Angle in radians for each category
                        annotations.append(
                            dict(
                                text=category,  # Text label
                                xref='paper', yref='paper',  # Positioning reference
                                x=0.5 + 0.10 * math.cos(angle),  # X position based on angle
                                y=0.5-((0.5 + 0.37 * math.sin(angle))-0.5),  # Y position based on angle
                                showarrow=False,
                                font=dict(family='Trebuchet MS',color="white", size=13),  # Font color
                                bgcolor="#FD6C6A",  # Background color
                                bordercolor="white",  # Border color
                                borderwidth=1,  # Border thickness
                                borderpad=3  # Padding around text
                            )
                        )

                    # 6. update layout with desired changes             
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 5],  # Adjust range based on your data
                                showticklabels=False,
                                ticks=''),

                            angularaxis=dict(
                                showticklabels=True,
                                rotation=90,
                                direction='clockwise',
                                tickfont=dict( size=15, color="black"))),

                            legend=dict(
                                orientation="h",  # Horizontal legend
                                yanchor="bottom",  # Align to the bottom of the legend
                                y=-0.4,            # Move legend above the plot area
                                xanchor="center", # Align to the center
                                x=0.5,
                                font={'size':15}),  # Center the legend
                                
                        showlegend=True,
                        annotations=annotations)
                else:
                    # 6. update layout with desired changes             
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 5],  # Adjust range based on your data
                                showticklabels=False,
                                ticks=''),

                            angularaxis=dict(
                                showticklabels=True,
                                rotation=90,
                                direction='clockwise',
                                tickfont=dict(size=15, color="black"))),

                            legend=dict(
                                orientation="h",  # Horizontal legend
                                yanchor="bottom",  # Align to the bottom of the legend
                                y=-0.4,            # Move legend above the plot area
                                xanchor="center", # Align to the center
                                x=0.5,
                                font={'size':15}),  # Center the legend
                                
                        showlegend=True)
                
                return fig

            
            
            # 7. construct the chart with streamlit
            toggle_values=st.toggle(label=f'Dispor valores no gráfico')

            polar_chart=create_polar_chart(toggle_values)
            st.plotly_chart(polar_chart)


    
        with table:
            st.success(f'''**Melhor Performance**   
            {best_transformations(answ_df,company,participant)}''',icon=':material/check_circle:')
            st.error(f'''**Pior Performance**   
            {worst_transformations(answ_df,company,participant)}''',icon=':material/cancel:')


            df_average=average_per_transformation(answ_df,company,participant)
            
            st.dataframe(df_average,
                         column_order=('Nome Transformação','Média','Diferença para indústria do futuro'),
                         column_config={
                             "Nome Transformação":st.column_config.TextColumn(
                                 'Transformação'),
                            "Diferença para indústria do futuro": st.column_config.NumberColumn(
                                'Diferença p/ Ind.Futuro')
                         },
                         hide_index=True,
                         use_container_width=True)

# RESPOSTAS
if selected == 'Respostas':

    title.header(f'Respostas')
    subtitle.subheader('')

    #title.subheader(f'Respostas | {company}')
    #filtro par escolher transformação
    transf=st.selectbox(label='Selecione a transformação',options=scores['Transformação'].unique())

    tab1, tab2, tab3 = st.tabs(["Por Campo","Por Questão",'Respostas variáveis'])

    with tab1:
        # média da pontuação por campo 
             
        df_selection=answ_df.query("Transformação == @transf and Empresa==@company and Colaborador==@participant")
        st.subheader(f'Média da pontuação por campo')
        col1,col2,col3=st.columns((1,6,1))  
        fig=px.bar(average_per_field(df_selection),
                y='Campo', x='Média pontuação',
                orientation='h',                   
                color_discrete_sequence=['#37a7a8'],height=350)
        
        fig.add_vline(x=4,annotation_text='Indústria do Futuro',line_dash='dot')
        fig.update_layout(xaxis_title=None,font=dict(size=14))
        
        fig.update_xaxes(tickfont_size=14)
        col2.plotly_chart(figure_or_data=fig)



        # variância das respostas por questão, por campo
        st.subheader('Variância das respostas por questão')

        campo=st.selectbox(label='Selecione o campo',options=(answ_df.loc[answ_df['Transformação']==transf,'Campo']).unique(),key='filter1')
        df_selection=answ_df.query("Transformação == @transf and Empresa==@company and Campo==@campo and Colaborador==@participant")
        
    
        event=st.dataframe(calculate_variation(df_selection),
                        column_order=('Pergunta','Variancia'),
                        column_config={
                            'Variancia':st.column_config.ProgressColumn(
                            "Variância",
                            min_value=0,
                            max_value=5,
                            format='%.2f'),
                            'Pergunta':st.column_config.TextColumn(
                                "Pergunta"
                            )

                },
                hide_index=True,use_container_width=True,selection_mode='single-row')
        
        





        # fig=px.bar(calculate_variation(df_selection),
        #         x='Variancia',y='Pergunta',
        #         color_discrete_sequence=['#37a7a8'],
        #         orientation='h',
        #         height=600,
        #         )
        
        # st.plotly_chart(figure_or_data=fig)

    with tab2:
        # FILTROS
        filter1,filter2=st.columns([1,3],gap='small',vertical_alignment='top')
        with filter1:
            campo=st.selectbox(label='Selecione o campo',options=(answ_df.loc[answ_df['Transformação']==transf,'Campo']).unique(),key='filter_field')
        with filter2:
            pergunta=st.selectbox(label='Selecione a questão',
                                options=(answ_df.loc[((answ_df['Transformação']==transf) & (answ_df['Campo']==campo)),'Pergunta']).unique())
            
            df_selection=answ_df.query("Transformação == @transf and Campo ==@campo and Empresa==@company and Colaborador==@participant")


        # filter the data to that question only
        df_selection_question=df_selection.query('Pergunta == @pergunta')
        # sort the employees name alphabetically
        df_selection_question=df_selection_question.sort_values('Colaborador')

        col1,col2=st.columns((4,3),gap='medium')
        with col1:
            st.dataframe(scores.query("Transformação ==@transf and Campo==@campo and Categoria==@pergunta.split(':')[0]"),
                            hide_index=True,
                            column_order=('Pontuação','Resposta'),
                            column_config={
                                'Pontuação':st.column_config.NumberColumn(
                                    'Pontuação',
                                    width='small'),
                                    'Resposta':st.column_config.TextColumn(
                                        'Resposta',
                                        width='large')
                                    },
                            use_container_width=True)
        with col2:
            fig=px.bar(df_selection_question,
                    x='Colaborador', y='Pontuação',
                    title='Pontuação por colaborador',
                    color_discrete_sequence=['#37a7a8'],
                    )

            st.plotly_chart(figure_or_data=fig,)         
    
    with tab3:
        st.info('''Neste separador estão descritas as questões onde se verificou **maior disparidade nas respostas** dos colaboradores.  
                Esta variância pode ser explicada pelo facto de os participantes ocuparem diferentes
                cargos na empresa (separador Participantes) que lhes oferecem perspetivas díspares do funcionamento da mesma.''')
        st.markdown('')

        df=answ_df.query('Empresa==@company and Colaborador==@participant')

        df=calculate_variation(df)

        df_top_best=df.nlargest(4,['Variancia']).reset_index()


        
        # by columns
        for i,q in df_top_best.iterrows():
            col1,col2,col3=st.columns((1,5,5),vertical_alignment='center')

            question=df_top_best['Pergunta'][i]

            col1.metric(label='Variancia',value=df_top_best['Variancia'][i])
            col2.markdown(f'**{question}**')

            df_filter_question=answ_df.query('Empresa==@company and Pergunta==@question and Colaborador==@participant')
            fig=px.bar(df_filter_question,
                    x='Colaborador', y='Pontuação',
                    title='Pontuação por colaborador',
                    color_discrete_sequence=['#37a7a8'],
                    )

            with col3.expander(label='Ver respostas',icon=':material/equalizer:'):
                st.plotly_chart(figure_or_data=fig)  
            
            st.divider()
        
# SIMULAÇÃO
if selected == 'Simulação':
    title.header(f'Simulação')
    subtitle.subheader('')

    st.info('''Neste separador estão representadas a média e variância obtida em cada questão.
            Deslizando a barra é possível **simular a alteração da respetiva média** verificando de que forma afetará a média geral obtida pela empresa
            e, consequentemente, o seu nível de Maturidade Digital.  
            Ao clicar no botão 'Sugestão de Melhoria' a App devolve uma **medida
            que a empresa pode implementar** de modo a alcançar a média simulada. ''')
    st.write('')

    # filtros
    col1, col2, col3= st.columns((2,2,3),gap='small')
    transf=col1.selectbox(label='Transformação',options=scores['Transformação'].unique())
    transf_name=trans_name.loc[trans_name['Transformação']==transf,'Transformação_nome'].item()
    campo=col2.selectbox(label='Campo',options=(scores.loc[scores['Transformação']==transf,'Campo']).unique())
    st.write('')

    
    # criar df com média por questão
    df_avg_per_question=average_per_question(answ_df,participants=participant)
    selection_df=df_avg_per_question.query("Empresa==@company and Transformação==@transf and Campo==@campo ")
    
    if 'slider_version' not in st.session_state:
        st.session_state['slider_version']=0
    

    with st.container(border=True):
        data,results=st.columns((4,3),gap='medium')
        # SLIDERS
        with data:
            st.subheader('Questões')
            for i,d in selection_df.iterrows():
                question_container=st.container(border=False)
                with question_container:
                    st.markdown(f"**{selection_df['Pergunta'][i]}**")
                    

                    col1,col2,col3,col4=st.columns((2,2,6,1),gap='small')
                    col1.metric(label='Média obtida',value=selection_df['Média pontuação'][i])
                    col2.metric(label='Variância',value=selection_df['Variância'][i])
                    col3.slider('Simulação',
                                min_value=1.00,
                                max_value=5.00,
                                value=selection_df['Média pontuação'][i],
                                # key=f'simulation{i}',
                                key=f'simulation{i+st.session_state['slider_version']}',
                                label_visibility='visible',
                                help='Deslize a barra para ver como a média total varia consoante a média da questão!')
                    simulated_value=st.session_state[f'simulation{i+st.session_state['slider_version']}']
                    with col4.popover(label='',icon=':material/lightbulb:',help='Sugestão de melhoria'):
                        answer_suggestion=st.markdown(suggest_answer(df_avg_per_question['Pergunta'][i].split(':')[0],simulated_value))

                    with col4.popover(label='',icon=':material/bar_chart:',help='Ver respostas'):
                        cat=df_avg_per_question['Pergunta'][i].split(':')[0]
                        df_filter_question=answ_df.query('Empresa==@company and Categoria==@cat and Colaborador==@participant')

                        fig=px.bar(df_filter_question,
                                x='Colaborador', y='Pontuação',
                                title='Pontuação por colaborador',
                                color_discrete_sequence=['#37a7a8']
                                )

                        st.plotly_chart(figure_or_data=fig,key=f'plot{i}')  
                    
                    st.divider()


                    # with st.expander(label='Ver respostas',icon=':material/format_list_bulleted:',expanded=False):
                    #     st.dataframe(pop_up(df_avg_per_question['Pergunta'][i].split(':')[0]),hide_index=True)
                    
                    


                
            for index in selection_df.index:
                # fetch the simulated value
                simulated_value=st.session_state[f'simulation{index+st.session_state['slider_version']}']
                # replace in the simulation column
                df_avg_per_question.loc[index,'Simulação']=simulated_value

            selection_df=df_avg_per_question.query("Empresa==@company and Transformação==@transf and Campo==@campo")


        # AVERAGE
        with results:
            st.write('')

            # Melhor e Pior performance
            results_contain=st.container(border=True)

            with results_contain:
                performance,col2=st.columns(2,gap='medium')
                performance.success(f'''**Melhor performance**  
                                {best_transformations(answ_df,company,participant)}''',icon=':material/check_circle:')
                performance.error(f'''**Pior performance**  
                                {worst_transformations(answ_df,company,participant)}''',icon=':material/cancel:')
                
                before_mean=calculate_mean_using_question_avg(df=df_avg_per_question,company=company)
                col2.subheader('Resultados')
                col2.metric(label='Média total original',value=before_mean)
                col2.metric(label='Nível de Maturidade Digital',value=maturity_level(before_mean))



            sim_container=st.container(border=True)
            with sim_container:
                mean_before=calculate_mean_using_question_avg(df=df_avg_per_question,company=company)
                mean_after=calculate_mean_simulation(df=df_avg_per_question,company=company)

                st.subheader('Simulação')
                col1,col2,col3=st.columns((3,3,2),gap='small')
                col1.metric(label='Média das pontuações',value=mean_after,
                        delta=round(mean_after-mean_before,2))
                col2.metric(label='Nível de Maturidade Digital',value=maturity_level(mean_after))
                
            # Reset Button
            reset_btn=st.button(label='REPOR VALORES',
                                icon=':material/refresh:',
                                type='primary',
                                on_click=reset_sliders,
                                use_container_width=True)

# PARTICIPANTES
if selected == 'Participantes':
    title.header(f'Participantes')
    subtitle.subheader('')


    df_participants=part_df.merge(participants, left_on='Email', right_on='email', how='left')

    df_selection= df_participants.query(
    "Empresa == @company")
    df_selection=df_selection.sort_values('Colaborador')


    st.info('''Sublinhados a vermelho estão os tempos de resposta considerados **demasiado curtos para entrar para a análise**, podendo
               representar um valor atípico no conjunto das respostas.  
               O colaborador sinalizado deve ser excluído da análise dos resultados. Para isso, elimine o nome do mesmo na barra lateral da aplicação''')

    df=st.dataframe(df_selection.style.map(highlight,subset='Tempo de resposta'),
                column_order=('Colaborador','Função',
                              'Email','Hora de início',
                              'Hora de conclusão','Tempo de resposta'),
                hide_index=True,
                use_container_width=True)

# TRANSFORMAÇÕES
if selected == 'Transformações':
    info=st.empty()
    with stylable_container(
        key='container_with_border',
        css_styles="""
        {
            border: 1px solid rgba(49, 51, 63, 0.2);
            border-radius: 0.5rem;
            padding: calc(1em - 1px)
        }
        """):

        filter,dataframe=st.columns([1,4],gap='medium',vertical_alignment='top')
        with filter:
            transf=st.selectbox(label='Transformação',options=scores['Transformação'].unique())
            transf_name=trans_name.loc[trans_name['Transformação']==transf,'Transformação_nome'].item()
            campo=st.selectbox(label='Campo',options=(scores.loc[scores['Transformação']==transf,'Campo']).unique())

            title.header(f'{transf} | {transf_name}')
            pergunta=st.selectbox(label='Questão',
                                options=(scores.loc[((scores['Transformação']==transf) & (scores['Campo']==campo)),'Pergunta']).unique())
            # subtitle.markdown(f'**{pergunta}**')

            description=trans_name.query('Transformação==@transf')['Descrição']
            info.info(f'''{description.values[0]}''')

        with dataframe:
            df_filtered=scores.query("Transformação ==@transf and Campo==@campo and Pergunta==@pergunta")
            st.markdown(f'**{pergunta}**')
            st.dataframe(df_filtered,
                        column_order=('Pontuação','Resposta'),
                        hide_index=True,use_container_width=True)

    st.write('')


