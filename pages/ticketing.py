import io
import uuid
import sqlite3
from pathlib import Path
from datetime import datetime

import qrcode
import streamlit as st


# ============================================================
# CONFIGURATION PAGE
# ============================================================

st.set_page_config(
    page_title="Billetterie | FanPulse360",
    page_icon="🎟️",
    layout="wide"
)


DB_PATH = Path.home() / "FanPulse360_Data" / "fanpulse.db"

DB_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# CONNEXION BASE DE DONNÉES
# ============================================================

def get_connection():

    conn = sqlite3.connect(DB_PATH)

    return conn


# ============================================================
# INITIALISATION BILLETTERIE
# ============================================================

def initialiser_billetterie():

    conn = get_connection()

    cursor = conn.cursor()


    # --------------------------------------------------------
    # MATCHS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billetterie_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domicile TEXT NOT NULL,
            exterieur TEXT NOT NULL,
            date_match TEXT NOT NULL,
            stade TEXT,
            capacite INTEGER,
            statut TEXT DEFAULT 'À venir'
        )
    """)


    # --------------------------------------------------------
    # BILLETS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS billets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            supporter_id TEXT,
            match_id INTEGER NOT NULL,
            tribune TEXT NOT NULL,
            bloc TEXT,
            rang TEXT,
            place TEXT,
            prix REAL NOT NULL,
            statut TEXT DEFAULT 'Valide',
            qr_token TEXT UNIQUE NOT NULL,
            date_achat TEXT NOT NULL,
            date_scan TEXT,
            FOREIGN KEY (match_id)
                REFERENCES billetterie_matches(id)
        )
    """)


    # --------------------------------------------------------
    # SCANS
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scans_billets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT NOT NULL,
            date_scan TEXT NOT NULL,
            porte TEXT,
            resultat TEXT NOT NULL
        )
    """)


    # --------------------------------------------------------
    # MATCHS DE DÉMONSTRATION
    # --------------------------------------------------------

    cursor.execute("""
        SELECT COUNT(*)
        FROM billetterie_matches
    """)

    nombre_matchs = cursor.fetchone()[0]


    if nombre_matchs == 0:

        matchs_demo = [

            (
                "Racing Strasbourg",
                "Lille",
                "2027-02-15 20:45",
                "Stade de la Meinau",
                30000,
                "À venir"
            ),

            (
                "Racing Strasbourg",
                "Lyon",
                "2027-03-01 17:00",
                "Stade de la Meinau",
                30000,
                "À venir"
            ),

            (
                "Racing Strasbourg",
                "Marseille",
                "2027-03-15 21:00",
                "Stade de la Meinau",
                30000,
                "À venir"
            )

        ]


        cursor.executemany("""
            INSERT INTO billetterie_matches (
                domicile,
                exterieur,
                date_match,
                stade,
                capacite,
                statut
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, matchs_demo)


    conn.commit()

    conn.close()


# ============================================================
# MATCHS DISPONIBLES
# ============================================================

def get_matches():

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT
            id,
            domicile,
            exterieur,
            date_match,
            stade,
            capacite
        FROM billetterie_matches
        WHERE statut = 'À venir'
        ORDER BY date_match
    """)


    matchs = cursor.fetchall()


    conn.close()


    return matchs


# ============================================================
# PRIX DES TRIBUNES
# ============================================================

PRIX_TRIBUNES = {

    "Tribune Ouest": 35,

    "Tribune Est": 30,

    "Tribune Nord": 25,

    "Tribune Sud": 25,

    "VIP": 120
}


# ============================================================
# VÉRIFIER SI PLACE DÉJÀ VENDUE
# ============================================================

def place_deja_vendue(
    match_id,
    tribune,
    bloc,
    rang,
    place
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        SELECT id

        FROM billets

        WHERE match_id = ?

        AND tribune = ?

        AND bloc = ?

        AND rang = ?

        AND place = ?

        AND statut != 'Annulé'
    """, (

        match_id,

        tribune,

        bloc,

        rang,

        place

    ))


    resultat = cursor.fetchone()


    conn.close()


    return resultat is not None


# ============================================================
# CRÉATION D'UN BILLET
# ============================================================

def creer_billet(
    supporter_id,
    match_id,
    tribune,
    bloc,
    rang,
    place,
    prix
):

    maintenant = datetime.now()


    ticket_id = (
        "TICKET-"
        + maintenant.strftime("%Y")
        + "-"
        + uuid.uuid4().hex[:8].upper()
    )


    qr_token = uuid.uuid4().hex


    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute("""
        INSERT INTO billets (

            ticket_id,

            supporter_id,

            match_id,

            tribune,

            bloc,

            rang,

            place,

            prix,

            statut,

            qr_token,

            date_achat

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

    """, (

        ticket_id,

        supporter_id,

        match_id,

        tribune,

        bloc,

        rang,

        place,

        prix,

        "Valide",

        qr_token,

        maintenant.isoformat(timespec="seconds")

    ))


    conn.commit()

    conn.close()


    return ticket_id, qr_token


# ============================================================
# GÉNÉRATION QR CODE
# ============================================================

def generer_qr_code(qr_token):

    contenu_qr = f"FANPULSE360|{qr_token}"


    qr = qrcode.QRCode(

        version=1,

        error_correction=qrcode.constants.ERROR_CORRECT_M,

        box_size=10,

        border=4

    )


    qr.add_data(contenu_qr)

    qr.make(fit=True)


    image = qr.make_image(

        fill_color="black",

        back_color="white"

    )


    buffer = io.BytesIO()


    image.save(

        buffer,

        format="PNG"

    )


    buffer.seek(0)


    return buffer


# ============================================================
# INITIALISATION
# ============================================================

initialiser_billetterie()


# ============================================================
# DESIGN
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 0px;
    }

    .subtitle {
        color: #888;
        font-size: 17px;
        margin-bottom: 25px;
    }

    .ticket-card {
        padding: 25px;
        border: 1px solid rgba(128,128,128,0.25);
        border-radius: 18px;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .price {
        font-size: 32px;
        font-weight: 800;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TITRE
# ============================================================

st.markdown(
    '<div class="main-title">🎟️ Billetterie digitale</div>',
    unsafe_allow_html=True
)


st.markdown(
    '<div class="subtitle">'
    'FanPulse360 — Achat, ticket digital et expérience supporter'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# MATCHS
# ============================================================

matchs = get_matches()


if not matchs:

    st.warning(
        "Aucun match disponible dans la billetterie."
    )

    st.stop()


match_dict = {}


for match in matchs:

    match_id = match[0]

    domicile = match[1]

    exterieur = match[2]

    date_match = match[3]


    label = (
        f"{domicile} vs {exterieur}"
        f" — {date_match}"
    )


    match_dict[label] = match


match_selectionne = st.selectbox(

    "⚽ Choisir un match",

    list(match_dict.keys())

)


match = match_dict[match_selectionne]


match_id = match[0]

domicile = match[1]

exterieur = match[2]

date_match = match[3]

stade = match[4]

capacite = match[5]


# ============================================================
# CARTE DU MATCH
# ============================================================

st.subheader(
    f"⚽ {domicile}  VS  {exterieur}"
)


col1, col2, col3 = st.columns(3)


with col1:

    st.info(
        f"""
        📅 **Date**

        {date_match}
        """
    )


with col2:

    st.info(
        f"""
        🏟️ **Stade**

        {stade}
        """
    )


with col3:

    st.info(
        f"""
        👥 **Capacité**

        {capacite:,} places
        """.replace(",", " ")
    )


st.divider()


# ============================================================
# SUPPORTER
# ============================================================

st.subheader(
    "👤 Supporter"
)


supporter_id = st.text_input(

    "Identifiant supporter",

    value="SUP0018",

    placeholder="Exemple : SUP0018"

)


st.caption(
    "Dans FanPulse360, cet identifiant permettra ensuite de relier "
    "l'achat au profil CRM du supporter."
)


# ============================================================
# CHOIX DE LA PLACE
# ============================================================

st.subheader(
    "🏟️ Choisir votre place"
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    tribune = st.selectbox(

        "Tribune",

        list(PRIX_TRIBUNES.keys())

    )


with col2:

    bloc = st.selectbox(

        "Bloc",

        [
            "A1",
            "A2",
            "B10",
            "B11",
            "B12",
            "C1",
            "C2"
        ]

    )


with col3:

    rang = st.selectbox(

        "Rang",

        [str(i) for i in range(1, 21)]

    )


with col4:

    place = st.selectbox(

        "Place",

        [str(i) for i in range(1, 51)]

    )


prix = PRIX_TRIBUNES[tribune]


# ============================================================
# DISPONIBILITÉ DE LA PLACE
# ============================================================

vendue = place_deja_vendue(

    match_id,

    tribune,

    bloc,

    rang,

    place

)


if vendue:

    st.error(
        "❌ Cette place est déjà vendue."
    )

else:

    st.success(
        "✅ Cette place est disponible."
    )


# ============================================================
# RÉCAPITULATIF
# ============================================================

st.divider()


st.subheader(
    "🛒 Votre commande"
)


col1, col2, col3, col4, col5 = st.columns(5)


col1.metric(

    "Tribune",

    tribune.replace(
        "Tribune ",
        ""
    )

)


col2.metric(

    "Bloc",

    bloc

)


col3.metric(

    "Rang",

    rang

)


col4.metric(

    "Place",

    place

)


col5.metric(

    "Prix",

    f"{prix} €"

)


# ============================================================
# ACHAT
# ============================================================

st.divider()


acheter = st.button(

    "🎫 Acheter mon billet",

    type="primary",

    width="stretch",

    disabled=vendue

)


if acheter:

    if not supporter_id.strip():

        st.error(
            "Veuillez renseigner un identifiant supporter."
        )


    elif place_deja_vendue(

        match_id,

        tribune,

        bloc,

        rang,

        place

    ):

        st.error(
            "❌ Cette place vient d'être vendue."
        )


    else:

        ticket_id, qr_token = creer_billet(

            supporter_id.strip(),

            match_id,

            tribune,

            bloc,

            rang,

            place,

            prix

        )


        st.session_state["dernier_billet"] = {

            "ticket_id": ticket_id,

            "qr_token": qr_token,

            "supporter_id": supporter_id.strip(),

            "domicile": domicile,

            "exterieur": exterieur,

            "date_match": date_match,

            "stade": stade,

            "tribune": tribune,

            "bloc": bloc,

            "rang": rang,

            "place": place,

            "prix": prix

        }


# ============================================================
# AFFICHAGE DU DERNIER BILLET
# ============================================================

if "dernier_billet" in st.session_state:

    billet = st.session_state["dernier_billet"]


    st.divider()


    st.success(
        "✅ Achat confirmé !"
    )


    st.subheader(
        "🎟️ Votre billet digital"
    )


    ticket_col, qr_col = st.columns(

        [2, 1]

    )


    with ticket_col:

        st.markdown(
            f"""
<div class="ticket-card">

<h2>
{billet["domicile"]}
vs
{billet["exterieur"]}
</h2>

<p>
📅 <b>{billet["date_match"]}</b>
</p>

<p>
🏟️ <b>{billet["stade"]}</b>
</p>

<hr>

<h3>
🎫 {billet["ticket_id"]}
</h3>

<p>
👤 Supporter :
<b>{billet["supporter_id"]}</b>
</p>

<p>
🏟️ Tribune :
<b>{billet["tribune"]}</b>
</p>

<p>
📍 Bloc :
<b>{billet["bloc"]}</b>
</p>

<p>
🔢 Rang :
<b>{billet["rang"]}</b>
</p>

<p>
💺 Place :
<b>{billet["place"]}</b>
</p>

<p class="price">
{billet["prix"]} €
</p>

<p>
✅ <b>BILLET VALIDE</b>
</p>

</div>
            """,
            unsafe_allow_html=True
        )


    with qr_col:

        qr_image = generer_qr_code(

            billet["qr_token"]

        )


        st.image(

            qr_image,

            caption="QR Code d'accès",

            width=280

        )


        qr_download = generer_qr_code(

            billet["qr_token"]

        )


        st.download_button(

            label="⬇️ Télécharger le QR Code",

            data=qr_download,

            file_name=(
                billet["ticket_id"]
                + ".png"
            ),

            mime="image/png",

            width="stretch"

        )


    st.info(
        "Présentez ce QR Code lors du contrôle d'accès au stade."
    )


# ============================================================
# INFORMATIONS MVP
# ============================================================

st.divider()


with st.expander(
    "ℹ️ Fonctionnement de la billetterie FanPulse360"
):

    st.markdown(
        """
Cette démonstration permet actuellement de :

- sélectionner un match ;
- choisir une tribune ;
- choisir un bloc, rang et une place ;
- calculer automatiquement le prix ;
- vérifier qu'une place n'a pas déjà été vendue ;
- créer un billet unique ;
- générer un QR Code unique ;
- enregistrer l'achat dans SQLite ;
- rattacher le billet à un identifiant supporter.

La prochaine étape sera le **contrôle d'accès au stade**.
        """
    )