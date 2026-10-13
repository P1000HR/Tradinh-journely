import streamlit as st
import pandas as pd
import datetime
from datetime import date
import json
import os

st.set_page_config(page_title='TRADING JOURNAL V2 DUAL', layout='wide')
st.title('📊 TRADING JOURNAL V2 - Binárias + Futures')
st.caption('Anote tudo aqui - Calendario + Banca + Metas')

FILE = 'trades.json'
if os.path.exists(FILE):
    with open(FILE,'r') as f:
        dados = json.load(f)
else:
    dados = []

# SIDEBAR - BANCA
with st.sidebar:
    st.header('💰 Minhas Bancas')
    banca_bin = st.number_input('Banca Binárias R$', value=500.0)
    banca_fut = st.number_input('Banca Futures USDT', value=100.0)
    meta_dia = st.number_input('Meta Lucro Dia R$', value=50.0)
    stop_dia = st.number_input('Stop Loss Dia R$', value=50.0)
    st.divider()
    st.write(f'Total: R$ {banca_bin} + ${banca_fut}')

tab1, tab2, tab3 = st.tabs(['➕ LANÇAR TRADE','📅 CALENDARIO','📈 DASHBOARD'])

with tab1:
    st.subheader('Novo Trade')
    conta = st.selectbox('Conta', ['Binárias','Futures Binance'])
    col1, col2, col3 = st.columns(3)
    with col1:
        dt = st.date_input('Data', date.today())
        par = st.text_input('Par', 'EURUSD' if conta=='Binárias' else 'BTCUSDT')
    with col2:
        if conta=='Binárias':
            direcao = st.selectbox('Direção', ['CALL','PUT'])
            timeframe = st.selectbox('Time', ['1M','5M','15M'])
            stake = st.number_input('Stake R$', value=10.0)
            payout = st.number_input('Payout %', value=85.0)
            resultado = st.selectbox('Resultado', ['WIN','LOSS'])
            pnl = stake * (payout/100) if resultado=='WIN' else -stake
        else:
            direcao = st.selectbox('Direção', ['LONG','SHORT'])
            alav = st.selectbox('Alavanca', ['5x','10x','20x'])
            entrada = st.number_input('Entrada', value=83000.0)
            saida = st.number_input('Saída', value=83100.0)
            pnl = st.number_input('PnL USDT', value=2.5)
            timeframe = alav
            
    with col3:
        nota = st.text_input('Nota/Setup', 'Scalp 5M')
    
    if st.button('Salvar Trade'):
        novo = {
            'data': str(dt),
            'conta': conta,
            'par': par,
            'dir': direcao,
            'time': str(timeframe),
            'pnl': float(pnl),
            'nota': nota
        }
        dados.append(novo)
        with open(FILE,'w') as f:
            json.dump(dados,f)
        st.success(f'Trade salvo! PnL: {pnl}')

with tab2:
    st.subheader('Calendario de Resultados')
    if dados:
        df = pd.DataFrame(dados)
        df['data'] = pd.to_datetime(df['data'])
        df['dia'] = df['data'].dt.date
        
        # Agrupa por dia
        diario = df.groupby('dia')['pnl'].sum().reset_index()
        diario['cor'] = diario['pnl'].apply(lambda x: '🟢' if x>0 else '🔴' if x<0 else '⚪')
        
        st.dataframe(diario.sort_values('dia', ascending=False), use_container_width=True)
        
        # Heatmap simples
        st.write('### Ultimos 7 dias')
        cols = st.columns(7)
        for i, row in diario.tail(7).iterrows():
            with cols[i % 7]:
                st.metric(str(row['dia']), f"{row['pnl']:.2f}", row['cor'])
        
        # Stop/Meta do dia
        hoje = date.today()
        pnl_hoje = df[df['dia']==hoje]['pnl'].sum() if hoje in df['dia'].values else 0
        st.metric('PnL HOJE', f'R$ {pnl_hoje:.2f}')
        if pnl_hoje >= meta_dia:
            st.success('✅ Meta batida - PARA HOJE!')
        if pnl_hoje <= -stop_dia:
            st.error('🛑 STOP LOSS BATIDO - Fecha tudo!')
    else:
        st.info('Nenhum trade ainda')

with tab3:
    st.subheader('Dashboard Geral')
    if dados:
        df = pd.DataFrame(dados)
        total = df['pnl'].sum()
        wins = len(df[df['pnl']>0])
        total_trades = len(df)
        winrate = wins/total_trades*100 if total_trades>0 else 0
        
        c1,c2,c3,c4 = st.columns(4)
        c1.metric('Total Trades', total_trades)
        c2.metric('Winrate', f'{winrate:.1f}%')
        c3.metric('PnL Total', f'{total:.2f}')
        c4.metric('Média/Trade', f'{df["pnl"].mean():.2f}')
        
        # Por conta
        st.bar_chart(df.groupby('conta')['pnl'].sum())
        st.line_chart(df.groupby('data')['pnl'].sum().cumsum())
        
        st.dataframe(df.sort_values('data', ascending=False), use_container_width=True)
        
        if st.button('Exportar Excel'):
            df.to_csv('meus_trades.csv', index=False)
            st.success('CSV gerado!')
    else:
        st.info('Lance seu primeiro trade na aba 1')

st.divider()
st.caption('Dica: Lance TODO trade, ate loss. Quem nao anota, quebra.')
