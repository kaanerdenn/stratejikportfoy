# BIST Hisse Analiz Uygulaması

Bu uygulama, Borsa İstanbul (BIST) hisselerini interaktif grafiklerle analiz etmenizi sağlar.

## Özellikler

- Mum grafiği ile teknik analiz
- İşlem hacmi analizi
- Günlük değişim ve temel metrikler
- Farklı zaman aralıkları için analiz
- İnteraktif grafikler
- Ham veri görüntüleme

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
streamlit run bist_analiz.py
```

## Kullanım

1. Hisse kodunu girin (örn: THYAO, GARAN, AKBNK)
2. İstediğiniz zaman aralığını seçin
3. Grafikleri ve metrikleri inceleyin

## Veri Kaynağı

Veriler Yahoo Finance API'si üzerinden çekilmektedir. 