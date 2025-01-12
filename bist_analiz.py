import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import re

# Sayfa yapılandırması ve stil
st.set_page_config(
    page_title="BIST Hisse Analizi",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"  # Mobil görünüm için sidebar varsayılan olarak kapalı
)

# PWA için meta etiketleri
st.markdown("""
    <head>
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black">
        <meta name="apple-mobile-web-app-title" content="Stratejik Portföy">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <link rel="apple-touch-icon" href="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/apple/325/chart-increasing_1f4c8.png">
    </head>
""", unsafe_allow_html=True)

# Mobil CSS ayarları
st.markdown("""
<style>
    /* Mobil cihazlar için özel stiller */
    @media (max-width: 768px) {
        .main {
            padding: 5px !important;
        }
        .stApp {
            margin: 0 !important;
        }
        .element-container {
            padding: 5px !important;
        }
        /* Grafik boyutlarını mobil için ayarla */
        .js-plotly-plot {
            width: 100% !important;
            height: 400px !important;
        }
        /* Metrik kartlarını mobil için düzenle */
        .stMetric {
            padding: 5px !important;
            margin: 2px !important;
        }
        /* Brand name'i mobil için küçült */
        .brand-name {
            font-size: 24px !important;
            padding: 8px 20px !important;
        }
        /* Başlıkları mobil için küçült */
        h1 {
            font-size: 20px !important;
        }
        h2, h3 {
            font-size: 18px !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    .main {
        background-color: #4335A7;
    }
    .stApp {
        background-color: #4335A7;
    }
    .css-1d391kg {
        background-color: #001A6E;
    }
    h1, h2, h3, p {
        color: white !important;
    }
    .stMetricValue {
        color: white !important;
    }
    .stMetricLabel {
        color: #DA498D !important;
    }
    .stMetricDelta {
        color: #90EE90 !important;
    }
    .stMarkdown {
        color: white !important;
    }
    .streamlit-expanderHeader {
        color: white !important;
        background-color: #640D5F !important;
    }
    .css-1adrfps {
        background-color: #640D5F;
    }
    .css-1kyxreq {
        background-color: #640D5F;
        color: white !important;
    }
    .stAlert {
        background-color: #640D5F !important;
        color: white !important;
    }
    .stDataFrame {
        background-color: #640D5F !important;
    }
    [data-testid="stSidebar"] {
        background-color: #001A6E;
    }
    [data-testid="stSidebarNav"] {
        background-color: #001A6E;
    }
    .css-pkbazv {
        background-color: #001A6E;
    }
    .css-1oe5cao {
        background-color: #001A6E;
    }
    .stTextInput > div > div {
        background-color: #640D5F;
    }
    .stTextInput input {
        color: white !important;
    }
    .stSelectbox > div > div {
        background-color: #640D5F;
    }
    /* Expander stilleri */
    .streamlit-expanderHeader:hover {
        background-color: #DA498D !important;
    }
    /* Success mesajı stili */
    .stSuccess {
        background-color: #640D5F !important;
        color: white !important;
        border: 1px solid #DA498D !important;
    }
    /* Info mesajı stili */
    .stInfo {
        background-color: #4335A7 !important;
        color: white !important;
        border: 1px solid #DA498D !important;
    }
    /* Metrik kartları için özel stil */
    .stMetric {
        background-color: #640D5F !important;
        padding: 10px !important;
        border-radius: 5px !important;
        border: 1px solid #DA498D !important;
    }
    /* Grafik arka planı */
    .js-plotly-plot .plotly .main-svg {
        background-color: transparent !important;
    }
    /* Yasal uyarı stili */
    .legal-warning {
        background-color: #640D5F !important;
        border: 1px solid #DA498D !important;
        color: white !important;
    }
    /* Marka stili */
    .brand-name {
        color: white !important;
        font-size: 36px !important;
        font-weight: bold !important;
        text-align: center !important;
        margin-bottom: 0px !important;
        letter-spacing: 3px !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3) !important;
        background-color: #640D5F !important;
        padding: 10px 30px !important;
        border-radius: 50px !important;
        display: inline-block !important;
        border: 2px solid #DA498D !important;
    }
    /* Marka container stili */
    .brand-container {
        text-align: center !important;
        margin-bottom: 20px !important;
    }
    /* Grafik container stili */
    .element-container {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
    }

    .js-plotly-plot {
        margin: auto !important;
    }

    .plot-container {
        margin: auto !important;
    }
</style>
""", unsafe_allow_html=True)

# Header bölümü
col1, col2, col3 = st.columns([1,3,1])
with col2:
    st.markdown('<div class="brand-container"><p class="brand-name">STRATEJİK PORTFÖY</p></div>', unsafe_allow_html=True)
    st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)  # Boşluk ekle
    st.title("🚀 BIST Hisse Analizi ve Değerleme Platformu")

st.markdown("---")

# BIST hisseleri için .IS ekini otomatik ekleyen fonksiyon
def get_bist_symbol(symbol):
    return f"{symbol}.IS"

def format_large_number(number):
    if number >= 1e9:
        return f"{number/1e9:.2f} Milyar"
    elif number >= 1e6:
        return f"{number/1e6:.2f} Milyon"
    else:
        return f"{number:,.0f}"

def analyze_stock(hisse_kodu):
    try:
        hisse = yf.Ticker(get_bist_symbol(hisse_kodu))
        # Genel metrikler için günlük veri
        daily_data = hisse.history(period="1y", interval="1d")
        info = hisse.info
        
        if not daily_data.empty:
            # Üst bilgi kartı
            st.success(f"📊 {hisse_kodu} - {info.get('longName', hisse_kodu)} Analiz Raporu")
            
            # Ana metrikler
            col1, col2, col3, col4 = st.columns(4)
            son_fiyat = daily_data['Close'][-1]
            önceki_fiyat = daily_data['Close'][-2]
            değişim = ((son_fiyat - önceki_fiyat) / önceki_fiyat) * 100
            
            with col1:
                st.metric("💰 Son Kapanış", f"{son_fiyat:.2f} TL", f"{değişim:.2f}%")
            with col2:
                if 'marketCap' in info:
                    st.metric("🏢 Piyasa Değeri", format_large_number(info['marketCap']) + " TL")
            with col3:
                if 'volume' in info:
                    st.metric("📊 Günlük İşlem Hacmi", format_large_number(daily_data['Volume'][-1]))
            with col4:
                if 'fiftyTwoWeekHigh' in info:
                    st.metric("📈 52 Hafta En Yüksek", f"{info['fiftyTwoWeekHigh']:.2f} TL")

            # Temel Analiz Metrikleri
            st.markdown("### 📊 Temel Analiz Metrikleri")
            metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
            
            with metrics_col1:
                if 'trailingPE' in info:
                    st.metric("F/K Oranı", f"{info['trailingPE']:.2f}")
                if 'priceToBook' in info:
                    st.metric("PD/DD", f"{info['priceToBook']:.2f}")
                if 'profitMargins' in info:
                    st.metric("Kar Marjı", f"{info['profitMargins']*100:.2f}%")
            
            with metrics_col2:
                if 'forwardPE' in info:
                    st.metric("İleriye Dönük F/K", f"{info['forwardPE']:.2f}")
                if 'enterpriseToRevenue' in info:
                    st.metric("FD/Satışlar", f"{info['enterpriseToRevenue']:.2f}")
                if 'returnOnEquity' in info:
                    st.metric("Özsermaye Karlılığı", f"{info['returnOnEquity']*100:.2f}%")
            
            with metrics_col3:
                if 'enterpriseToEbitda' in info:
                    st.metric("FD/FAVÖK", f"{info['enterpriseToEbitda']:.2f}")
                if 'debtToEquity' in info:
                    st.metric("Borç/Özsermaye", f"{info['debtToEquity']:.2f}")
                if 'returnOnAssets' in info:
                    st.metric("Aktif Karlılığı", f"{info['returnOnAssets']*100:.2f}%")
            
            with metrics_col4:
                if 'dividendYield' in info and info['dividendYield'] is not None:
                    st.metric("Temettü Verimi", f"{info['dividendYield']*100:.2f}%")
                if 'payoutRatio' in info and info['payoutRatio'] is not None:
                    st.metric("Temettü Dağıtım Oranı", f"{info['payoutRatio']*100:.2f}%")
                if 'beta' in info:
                    st.metric("Beta", f"{info['beta']:.2f}")

            # Teknik Göstergeler
            st.markdown("### 📈 Teknik Göstergeler")
            
            # Hareketli Ortalamalar
            daily_data['MA50'] = daily_data['Close'].rolling(window=50).mean()
            daily_data['MA200'] = daily_data['Close'].rolling(window=200).mean()
            daily_data['RSI'] = calculate_rsi(daily_data['Close'])
            
            tech_col1, tech_col2, tech_col3, tech_col4 = st.columns(4)
            
            with tech_col1:
                st.metric("50 Günlük Ortalama", f"{daily_data['MA50'][-1]:.2f} TL")
            with tech_col2:
                st.metric("200 Günlük Ortalama", f"{daily_data['MA200'][-1]:.2f} TL")
            with tech_col3:
                st.metric("RSI (14)", f"{daily_data['RSI'][-1]:.2f}")
            with tech_col4:
                volatility = daily_data['Close'].pct_change().std() * (252 ** 0.5) * 100
                st.metric("Yıllık Volatilite", f"{volatility:.2f}%")

            # Grafikler
            st.markdown("### 📊 Fiyat ve Hacim Grafikleri")
            
            # Zaman dilimi seçimi için dropdown
            time_periods = {
                "4 Saat": ("60d", "1h"),     # Son 60 gün, saatlik veriler (sonra 4 saatlik resampling yapılacak)
                "1 Gün": ("90d", "1d"),      # Son 90 gün, günlük mumlar
                "1 Hafta": ("180d", "1d"),   # Son 180 gün, günlük veriler (sonra haftalık resampling yapılacak)
                "1 Ay": ("730d", "1d"),      # Son 730 gün, günlük veriler (sonra aylık resampling yapılacak)
                "1 Yıl": ("max", "1d")       # Tüm veriler, günlük veriler (sonra yıllık resampling yapılacak)
            }
            selected_period = st.selectbox(
                "📊 Mum Periyodu",
                options=list(time_periods.keys()),
                index=1,  # Varsayılan olarak 1 Gün seçili
                key="chart_period"
            )
            
            # Sadece grafikler için veri çekme
            period, interval = time_periods[selected_period]
            try:
                chart_data = hisse.history(period=period, interval=interval)
                
                if not chart_data.empty:
                    # Veriyi seçilen periyoda göre yeniden örnekle
                    if selected_period == "4 Saat":
                        chart_data = chart_data.resample('4H').agg({
                            'Open': 'first',
                            'High': 'max',
                            'Low': 'min',
                            'Close': 'last',
                            'Volume': 'sum'
                        }).dropna()
                    elif selected_period == "1 Hafta":
                        chart_data = chart_data.resample('W').agg({
                            'Open': 'first',
                            'High': 'max',
                            'Low': 'min',
                            'Close': 'last',
                            'Volume': 'sum'
                        }).dropna()
                    elif selected_period == "1 Ay":
                        chart_data = chart_data.resample('M').agg({
                            'Open': 'first',
                            'High': 'max',
                            'Low': 'min',
                            'Close': 'last',
                            'Volume': 'sum'
                        }).dropna()
                    elif selected_period == "1 Yıl":
                        chart_data = chart_data.resample('Y').agg({
                            'Open': 'first',
                            'High': 'max',
                            'Low': 'min',
                            'Close': 'last',
                            'Volume': 'sum'
                        }).dropna()

                    # Hareketli ortalamalar
                    if len(chart_data) > 50:
                        chart_data['MA50'] = chart_data['Close'].rolling(window=50).mean()
                    if len(chart_data) > 200:
                        chart_data['MA200'] = chart_data['Close'].rolling(window=200).mean()
                    
                    # Mum grafiği
                    fig = create_candlestick_chart(chart_data, hisse_kodu, selected_period)
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Hacim grafiği
                    fig_volume = create_volume_chart(chart_data, hisse_kodu, selected_period)
                    st.plotly_chart(fig_volume, use_container_width=True)
                else:
                    st.warning(f"⚠️ {selected_period} için veri bulunamadı. Lütfen başka bir zaman dilimi seçin.")
            except Exception as e:
                st.warning(f"⚠️ {selected_period} için veri çekilemedi. Lütfen başka bir zaman dilimi seçin.")

            # Şirket Bilgileri
            if 'longBusinessSummary' in info:
                with st.expander("ℹ️ Şirket Hakkında"):
                    try:
                        st.write("Bu bilgi İngilizce kaynaktan alınmıştır.")
                        st.write("---")
                        st.write(info['longBusinessSummary'])
                    except:
                        st.write("Şirket bilgisi bulunamadı.")

            # Teknik Analiz Özeti
            with st.expander("📊 Teknik Analiz Özeti"):
                trend = "Yükselen Trend" if daily_data['MA50'][-1] > daily_data['MA200'][-1] else "Düşen Trend"
                st.write(f"{'✅' if daily_data['MA50'][-1] > daily_data['MA200'][-1] else '⚠️'} **Trend Durumu:** {trend}")
                
                if 'trailingPE' in info:
                    fk_durum = "Düşük (Cazip)" if info['trailingPE'] < 10 else "Yüksek (Pahalı)" if info['trailingPE'] > 20 else "Normal"
                    st.write(f"{'✅' if info['trailingPE'] < 10 else '⚠️' if info['trailingPE'] > 20 else 'ℹ️'} **F/K Durumu:** {fk_durum}")
                
                rsi = daily_data['RSI'][-1]
                rsi_durum = "Aşırı Satım (Alım Fırsatı)" if rsi < 30 else "Aşırı Alım (Satış Fırsatı)" if rsi > 70 else "Normal"
                st.write(f"{'✅' if 40 < rsi < 60 else '⚠️'} **RSI Durumu:** {rsi_durum}")
                
                hacim_değişimi = ((daily_data['Volume'][-5:].mean() - daily_data['Volume'][-10:-5].mean()) / daily_data['Volume'][-10:-5].mean()) * 100
                st.write(f"{'✅' if hacim_değişimi > 0 else 'ℹ️'} **Hacim Değişimi (5 günlük):** {hacim_değişimi:.2f}%")

            # Ham veri
            with st.expander("📋 Ham Veri"):
                st.dataframe(daily_data)
                
        else:
            st.error("❌ Veri bulunamadı. Lütfen geçerli bir hisse kodu giriniz.")
            
    except Exception as e:
        st.error(f"❌ Bir hata oluştu: {str(e)}")
        st.info("💡 Lütfen geçerli bir BIST hisse kodu giriniz (örn: THYAO, GARAN, AKBNK)")

    st.markdown("---")
    show_legal_warning()

def calculate_rsi(prices, period=14):
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Grafik stillerini güncelle
def create_figure_layout(title):
    return dict(
        title=title,
        template="plotly",
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        width=1000,  # Sabit genişlik
        height=600,  # Sabit yükseklik
        margin=dict(l=50, r=50, t=50, b=50)  # Kenar boşlukları
    )

# Mum grafiği oluşturma fonksiyonunu güncelle
def create_candlestick_chart(hist, hisse_kodu, period_text):
    fig = go.Figure()
    
    # Mum çubukları
    fig.add_trace(go.Candlestick(
        x=hist.index,
        open=hist['Open'],
        high=hist['High'],
        low=hist['Low'],
        close=hist['Close'],
        name="OHLC"
    ))
    
    # Hareketli ortalamalar (eğer varsa)
    if 'MA50' in hist.columns:
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['MA50'],
            name='50 Periyot Ort.',
            line=dict(width=2)
        ))
    
    if 'MA200' in hist.columns:
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['MA200'],
            name='200 Periyot Ort.',
            line=dict(width=2)
        ))
    
    layout = create_figure_layout(f"{hisse_kodu} {period_text}lik Fiyat Grafiği")
    layout.update(
        xaxis=dict(
            rangeslider=dict(visible=False),
            type='date',
            autorange=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1G", step="day", stepmode="backward"),
                    dict(count=7, label="1H", step="day", stepmode="backward"),
                    dict(count=1, label="1A", step="month", stepmode="backward"),
                    dict(count=3, label="3A", step="month", stepmode="backward"),
                    dict(count=6, label="6A", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="Tümü")
                ])
            )
        ),
        yaxis=dict(
            autorange=True,
            fixedrange=False,
            title=dict(
                text="Fiyat (TL)",
                standoff=10
            )
        ),
        dragmode='zoom',
        showlegend=True,
        hovermode='x unified'
    )
    fig.update_layout(layout)
    
    return fig

# Hacim grafiği oluşturma fonksiyonunu güncelle
def create_volume_chart(hist, hisse_kodu, period_text):
    fig_volume = go.Figure()
    
    # Hacim çubukları (lacivert renk)
    fig_volume.add_trace(go.Bar(
        x=hist.index,
        y=hist['Volume'],
        name="Hacim",
        marker_color='#001A6E'  # Lacivert renk
    ))
    
    layout = create_figure_layout(f"{hisse_kodu} {period_text}lik İşlem Hacmi")
    layout.update(
        xaxis=dict(
            type='date',
            autorange=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1G", step="day", stepmode="backward"),
                    dict(count=7, label="1H", step="day", stepmode="backward"),
                    dict(count=1, label="1A", step="month", stepmode="backward"),
                    dict(count=3, label="3A", step="month", stepmode="backward"),
                    dict(count=6, label="6A", step="month", stepmode="backward"),
                    dict(count=1, label="1Y", step="year", stepmode="backward"),
                    dict(step="all", label="Tümü")
                ]),
                x=0.7,  # Butonların x pozisyonu
                y=1.1   # Butonların y pozisyonu
            )
        ),
        yaxis=dict(
            autorange=True,
            fixedrange=False,
            title=dict(
                text="İşlem Hacmi",
                standoff=10  # Y ekseni başlığı ile eksen arasındaki mesafe
            )
        ),
        dragmode='zoom',
        showlegend=True
    )
    fig_volume.update_layout(layout)
    
    return fig_volume

# Yasal uyarı stilini güncelle
def show_legal_warning():
    st.markdown("""
    <div style='text-align: center; color: white; font-size: 14px; padding: 10px; 
    background-color: #640D5F; border: 1px solid #DA498D; border-radius: 5px;'>
    ⚠️ Bu platformda yer alan tüm bilgi, yorum ve analizler yatırım danışmanlığı 
    kapsamında değildir. Yatırım tavsiyesi değildir.
    </div>
    """, unsafe_allow_html=True)

# Kullanıcı girişi
col1, col2, col3 = st.columns([1,2,1])
with col2:
    hisse_kodu = st.text_input("🔍 Hisse Kodu Girin (örn: THYAO)", "").upper()

if hisse_kodu:
    analyze_stock(hisse_kodu)

# Sidebar
with st.sidebar:
    st.markdown("### 📈 Borsa İstanbul")
    st.markdown("""
    Bu platform, BIST hisselerinin detaylı analizini sunar:
    
    **Temel Analiz:**
    - Piyasa Değeri
    - F/K ve PD/DD Oranları
    - Karlılık Oranları
    - Temettü Verileri
    
    **Teknik Analiz:**
    - Fiyat Grafikleri
    - Hareketli Ortalamalar
    - RSI Göstergesi
    - Hacim Analizi
    """)
    
    st.markdown("### 💡 Popüler Hisseler")
    st.markdown("""
    - THYAO (Türk Hava Yolları)
    - GARAN (Garanti Bankası)
    - AKBNK (Akbank)
    - EREGL (Ereğli Demir Çelik)
    - SISE (Şişe Cam)
    - ASELS (Aselsan)
    - KCHOL (Koç Holding)
    - BIMAS (BİM)
    """)
    
    st.markdown("### ℹ️ Hakkında")
    st.markdown("""
    Bu platform, yatırımcılara BIST hisselerinin kapsamlı analizini sunmak için tasarlanmıştır.
    
    **Veri Kaynağı:** Yahoo Finance
    **Güncelleme:** Gerçek Zamanlı
    """)
    
    st.markdown("### 📚 Yatırım Terimleri")
    
    with st.expander("1️⃣ F/K Oranı Nedir?"):
        st.write("Fiyat/Kazanç oranı, hisse senedi fiyatının hisse başına düşen kara bölünmesiyle elde edilir. Düşük F/K genellikle hissenin ucuz olduğunu gösterir. Yatırım tavsiyesi değildir.")
    
    with st.expander("2️⃣ PD/DD Nedir?"):
        st.write("Piyasa Değeri/Defter Değeri oranı, şirketin piyasa değerinin özkaynaklarına bölünmesiyle bulunur. 1'in altındaki değerler hissenin defter değerinin altında işlem gördüğünü gösterir. Yatırım tavsiyesi değildir.")
    
    with st.expander("3️⃣ RSI Nedir?"):
        st.write("Göreceli Güç Endeksi (RSI), bir hisse senedinin aşırı alım veya aşırı satım bölgesinde olup olmadığını gösteren momentum göstergesidir. 70 üzeri aşırı alım, 30 altı aşırı satım bölgesidir. Yatırım tavsiyesi değildir.")
    
    with st.expander("4️⃣ FAVÖK Nedir?"):
        st.write("Faiz, Amortisman ve Vergi Öncesi Kâr, bir şirketin esas faaliyetlerinden elde ettiği kârı gösterir. Şirketin operasyonel performansını değerlendirmek için kullanılır. Yatırım tavsiyesi değildir.")
    
    with st.expander("5️⃣ Beta Katsayısı Nedir?"):
        st.write("Beta, bir hisse senedinin piyasaya göre ne kadar duyarlı olduğunu gösterir. 1'den büyük beta daha riskli, 1'den küçük beta daha az riskli olduğunu gösterir. Yatırım tavsiyesi değildir.")
    
    with st.expander("6️⃣ Temettü Verimi Nedir?"):
        st.write("Yıllık temettü miktarının hisse fiyatına bölünmesiyle elde edilir. Yüksek temettü verimi, düzenli gelir arayan yatırımcılar için önemli bir göstergedir. Yatırım tavsiyesi değildir.")
    
    with st.expander("7️⃣ Hareketli Ortalama Nedir?"):
        st.write("Belirli bir dönemdeki fiyatların ortalamasını gösteren teknik analiz göstergesidir. Trend yönünü ve destek/direnç seviyelerini belirlemekte kullanılır. Yatırım tavsiyesi değildir.")
    
    with st.expander("8️⃣ Piyasa Değeri Nedir?"):
        st.write("Şirketin toplam hisse sayısının hisse fiyatıyla çarpılmasıyla bulunan değerdir. Şirketin büyüklüğünü ve piyasa değerini gösterir. Yatırım tavsiyesi değildir.")
    
    with st.expander("9️⃣ Özsermaye Karlılığı Nedir?"):
        st.write("Net kârın özsermayeye bölünmesiyle elde edilir. Şirketin özsermayesini ne kadar verimli kullandığını gösterir. Yatırım tavsiyesi değildir.")
    
    with st.expander("🔟 Volatilite Nedir?"):
        st.write("Bir hisse senedinin fiyat değişkenliğini gösteren risk ölçütüdür. Yüksek volatilite yüksek risk ve potansiyel getiri anlamına gelir. Yatırım tavsiyesi değildir.")

    st.markdown("---")
    show_legal_warning()