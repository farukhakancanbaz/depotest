import streamlit as st
import yfinance as yf
import pandas as pd
import random 

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="İsviçre Portföy Takip", layout="wide")

st.title("🇨🇭 İsviçre Borsası Akıllı Takip Paneli")
st.markdown("---")

# --- KULLANICI PORTFÖYÜ (KENDİ VERİNİZİ BURAYA GİRİN) ---
my_portfolio = {
    'NESN.SW': {'qty': 50, 'name': 'Nestle'},
    'ROG.SW':  {'qty': 30, 'name': 'Roche Holding'},
    'NOVN.SW': {'qty': 40, 'name': 'Novartis'},
    'UBSG.SW': {'qty': 100, 'name': 'UBS Group'},
    'ABBN.SW': {'qty': 60, 'name': 'ABB Ltd'}
}

# --- VERİ ÇEKME FONKSİYONU ---
@st.cache_data
def get_data(portfolio):
    tickers = list(portfolio.keys())
    data = yf.download(tickers, period="1d", group_by='ticker')
    
    portfolio_data = []
    
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker).info
            current_price = info.get('currentPrice', 0)
            prev_close = info.get('previousClose', 0)
            sector = info.get('sector', 'Bilinmiyor')
            # Temettü verimi: yfinance'da float gelir, % için 100 ile çarpılır
            dividend_yield = info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0
            
            qty = portfolio[ticker]['qty']
            total_val = current_price * qty
            daily_change_pct = ((current_price - prev_close) / prev_close) * 100
            
            portfolio_data.append({
                'Kod': ticker,
                'Şirket': portfolio[ticker]['name'],
                'Adet': qty,
                'Fiyat (CHF)': round(current_price, 2),
                'Günlük Değişim (%)': daily_change_pct,
                'Toplam Değer (CHF)': round(total_val, 2),
                'Sektör': sector,
                'Temettü Verimi (%)': round(dividend_yield, 2)
            })
        except:
            pass 
            
    return pd.DataFrame(portfolio_data)

# --- HABER SİMÜLASYONU VE DUYGU ANALİZİ ---
def get_news_sentiment(company_name):
    # Bu kısım, haber API'si yerine çalışan basit bir simülasyondur.
    possible_news = [
        ("Yeni bir satın alma gerçekleştirdi.", "pozitif"),
        ("Çeyrek sonuçları beklentilerin altında.", "negatif"),
        ("Yeni CEO ataması yapıldı.", "nötr"),
        ("Temettü artırma kararı aldı.", "pozitif"),
        ("Sektördeki daralma şirketi etkiliyor.", "negatif")
    ]
    
    news, sentiment = random.choice(possible_news)
    
    if sentiment == "pozitif":
        icon = "🟢 (Pozitif)"
        color = "green"
    elif sentiment == "negatif":
        icon = "🔴 (Negatif)"
        color = "red"
    else:
        icon = "⚪ (Nötr)"
        color = "grey"
        
    return f":{color}[{icon} **{company_name}:** {news}]"

# --- ARAYÜZÜ OLUŞTURMA ---
df = get_data(my_portfolio)

if not df.empty:
    # 2. Üst Özet Kartları
    total_portfolio_value = df['Toplam Değer (CHF)'].sum()
    daily_avg_change = df['Günlük Değişim (%)'].mean()
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Toplam Portföy Değeri", f"{total_portfolio_value:,.2f} CHF")
    col2.metric("Günlük Ortalama Değişim", f"%{daily_avg_change:.2f}", delta_color="normal")
    col3.metric("Toplam Şirket", len(df))
    
    st.markdown("---")

    # 3. Ana Tablo ve Grafikler
    col_main, col_chart = st.columns([2, 1])
    
    with col_main:
        st.subheader("📊 Hisse Senedi Detayları")
        st.dataframe(df.style.format({'Günlük Değişim (%)': '{:.2f}', 'Fiyat (CHF)': '{:.2f}'}), use_container_width=True)
        
    with col_chart:
        st.subheader("🍰 Sektörel Dağılım")
        sector_counts = df['Sektör'].value_counts()
        st.bar_chart(sector_counts)

    st.markdown("---")

    # 4. Akıllı Haber Akışı Bölümü
    st.subheader("📰 Akıllı Haber Takibi & Sinyaller")
    st.info("Yapay Zeka Destekli Özet: Pozitif haberler yeşil, riskli durumlar kırmızı ile işaretlenmiştir.")
    
    news_cols = st.columns(2)
    for index, row in df.iterrows():
        news_item = get_news_sentiment(row['Şirket'])
        if index % 2 == 0:
            news_cols[0].markdown(news_item)
        else:
            news_cols[1].markdown(news_item)

else:
    st.error("Veri çekilemedi. Lütfen hisse kodlarını kontrol edin.")
