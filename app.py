# app.py
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from io import BytesIO

st.set_page_config(page_title="Generátor bodů na kružnici", layout="wide")

# --- Page routing (umožní otevřít info v novém okně přes ?page=info) ---
params = st.experimental_get_query_params()
page = params.get("page", ["main"])[0]

if page == "info":
    st.title("Informace o autorovi a použitých technologiích")
    st.markdown("""
    **Autor:** Tvoje jméno  
    **Kontakt:** tve@email.cz  
    **Použité technologie:** Streamlit, Python, NumPy, pandas, Matplotlib  
    **Popis:** Tato aplikace generuje body na kružnici podle zadaného středu, poloměru a počtu bodů. 
    """)
    st.markdown("### Jak aplikace funguje")
    st.markdown("- Zadej střed (X,Y), poloměr, počet bodů a barvu bodů.\n- Aplikace vykreslí body, tabulku souřadnic, umožní stažení CSV a generování PDF s grafem a parametry.")
    st.markdown("[Otevřít hlavní aplikaci](./)")

else:
    st.title("Generátor bodů na kružnici (Streamlit)")
    # --- vstupy v sidebar ---
    st.sidebar.header("Parametry kružnice")
    cx = st.sidebar.number_input("Střed X", value=0.0, format="%.3f")
    cy = st.sidebar.number_input("Střed Y", value=0.0, format="%.3f")
    radius = st.sidebar.number_input("Poloměr", min_value=0.0, value=5.0, format="%.3f")
    n = st.sidebar.number_input("Počet bodů (3–500)", min_value=3, max_value=500, value=36, step=1)
    color = st.sidebar.color_picker("Barva bodů", value="#1f77b4")
    show_line = st.sidebar.checkbox("Spojit body čarou", value=True)
    unit = st.sidebar.selectbox("Jednotka", options=["m", "cm", "mm", "km"], index=0)

    st.sidebar.markdown("---")
    st.sidebar.markdown("**Informace o autorovi / technologiích**")
    st.sidebar.markdown("Napiš své jméno a kontakt pro report:")
    name = st.sidebar.text_input("Tvé jméno", value="Tvoje Jméno")
    contact = st.sidebar.text_input("Kontakt (email)", value="tvoje@email.cz")

    # Odkaz otevřít info v novém okně
    st.markdown('[Otevřít informace o autorovi v novém okně](?page=info){:target="_blank"}', unsafe_allow_html=True)

    # --- generování bodů ---
    angles = np.linspace(0, 2*np.pi, int(n), endpoint=False)
    x = cx + radius * np.cos(angles)
    y = cy + radius * np.sin(angles)

    df = pd.DataFrame({
        f"X ({unit})": np.round(x, 6),
        f"Y ({unit})": np.round(y, 6),
        "angle_deg": np.round(np.degrees(angles), 3)
    })

    # --- vykreslení ---
    fig, ax = plt.subplots(figsize=(6,6))
    if show_line:
        ax.plot(x, y, marker='o', linestyle='-', markersize=6, color=color)
    else:
        ax.scatter(x, y, s=40, color=color)
    ax.plot([cx], [cy], marker='x', color='black') # střed
    ax.set_aspect('equal', adjustable='box')

    # rozsah os tak, aby byl kruh vidět pohodlně
    pad = radius * 0.3 if radius>0 else 1
    xmin, xmax = cx - radius - pad, cx + radius + pad
    ymin, ymax = cy - radius - pad, cy + radius + pad
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)

    # nastavit číselné hodnoty na osách (9 ticků)
    xticks = np.linspace(xmin, xmax, 9)
    yticks = np.linspace(ymin, ymax, 9)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.set_xlabel(f"X ({unit})")
    ax.set_ylabel(f"Y ({unit})")
    ax.grid(True, linestyle='--', alpha=0.6)

    st.pyplot(fig)

    # --- zobrazit tabulku souřadnic a možnost stažení CSV ---
    st.subheader("Souřadnice bodů")
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Stáhnout souřadnice (CSV)", data=csv, file_name="points.csv", mime="text/csv")

    # --- vygenerovat PDF obsahující parametry a graf ---
    def create_pdf(name, contact, params_text, fig_for_pdf):
        buf = BytesIO()
        with PdfPages(buf) as pdf:
            # cover page (A4)
            fig_cover = plt.figure(figsize=(8.27, 11.69)) # A4 inches
            plt.axis('off')
            cover_text = f"Report\n\nAutor: {name}\nKontakt: {contact}\n\nParametry úlohy:\n{params_text}"
            plt.text(0.05, 0.95, cover_text, fontsize=12, va='top')
            pdf.savefig(fig_cover, bbox_inches='tight')
            plt.close(fig_cover)

            # plot page (výstup grafu)
            pdf.savefig(fig_for_pdf, bbox_inches='tight')
        buf.seek(0)
        return buf

    params_text = f"Střed: ({cx}, {cy}) {unit}\nPoloměr: {radius} {unit}\nPočet bodů: {n}\nBarva: {color}\nSpojit čarou: {show_line}"
    pdf_buf = create_pdf(name, contact, params_text, fig)

    st.download_button("Stáhnout report (PDF)", data=pdf_buf.getvalue(),
                       file_name="report.pdf", mime="application/pdf")

    st.markdown("---")
    st.markdown("Tip: PDF si můžeš stáhnout a vytisknout pomocí prohlížeče.")
