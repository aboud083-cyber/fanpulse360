import sqlite3
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOCAL_DATA_DIR = Path.home() / "FanPulse360_Data"
LOCAL_DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = LOCAL_DATA_DIR / "fanpulse.db"

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def _table_columns(conn, table):
    try:
        return {r[1] for r in conn.execute(f"PRAGMA table_info({table})").fetchall()}
    except Exception:
        return set()

def _add_column_if_missing(conn, table, definition):
    name = definition.split()[0]
    if name not in _table_columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")

def create_tables():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS supporters(
        supporter_id TEXT PRIMARY KEY,
        prenom TEXT,
        nom TEXT,
        age INTEGER,
        ville TEXT,
        code_postal TEXT,
        email TEXT,
        date_inscription TEXT,
        consentement_marketing INTEGER,
        abonne INTEGER,
        canal_prefere TEXT,
        nb_matchs INTEGER DEFAULT 0,
        nb_achats INTEGER DEFAULT 0,
        total_depense REAL DEFAULT 0,
        nb_places INTEGER DEFAULT 0,
        taux_presence REAL DEFAULT 0,
        derniere_activite TEXT,
        satisfaction_moyenne REAL DEFAULT 0,
        nps_moyen REAL DEFAULT 0,
        nb_avis INTEGER DEFAULT 0,
        score_engagement REAL DEFAULT 0,
        segment_crm TEXT,
        note_crm TEXT DEFAULT ''
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS crm_actions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supporter_id TEXT,
        type_action TEXT,
        description TEXT,
        statut TEXT DEFAULT 'À faire',
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS campaigns(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom TEXT NOT NULL,
        segment TEXT,
        canal TEXT,
        objectif TEXT,
        message TEXT,
        statut TEXT DEFAULT 'Brouillon',
        nb_cibles INTEGER DEFAULT 0,
        conversions INTEGER DEFAULT 0,
        ca_genere REAL DEFAULT 0,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS campaign_targets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        campaign_id INTEGER,
        supporter_id TEXT,
        statut TEXT DEFAULT 'Ciblé',
        conversion REAL DEFAULT 0
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS matches(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        adversaire TEXT,
        date_match TEXT,
        competition TEXT,
        capacite INTEGER DEFAULT 30000,
        spectateurs INTEGER DEFAULT 0,
        statut TEXT DEFAULT 'À venir'
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS ticket_sales(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supporter_id TEXT,
        match_id INTEGER,
        quantite INTEGER DEFAULT 1,
        montant REAL DEFAULT 0,
        type_billet TEXT,
        statut TEXT DEFAULT 'Payé',
        date_achat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS experiences(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        supporter_id TEXT,
        match_id INTEGER,
        satisfaction REAL,
        nps INTEGER,
        commentaire TEXT,
        date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    _add_column_if_missing(conn, "supporters", "note_crm TEXT DEFAULT ''")
    conn.commit()
    conn.close()

def import_supporters_if_empty():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM supporters").fetchone()[0]

    if count == 0:
        csv_path = DATA_DIR / "supporters_scored.csv"
        if csv_path.exists():
            df = pd.read_csv(csv_path, encoding="utf-8-sig")
            allowed = _table_columns(conn, "supporters")
            cols = [c for c in df.columns if c in allowed]
            df[cols].to_sql("supporters", conn, if_exists="append", index=False)

    conn.commit()
    conn.close()

def initialize_database():
    create_tables()
    import_supporters_if_empty()

def query_df(sql, params=()):
    conn = get_connection()
    try:
        return pd.read_sql_query(sql, conn, params=params)
    finally:
        conn.close()

def execute(sql, params=()):
    conn = get_connection()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()

def get_supporters():
    return query_df("SELECT * FROM supporters ORDER BY score_engagement DESC, nom, prenom")

def get_supporter(supporter_id):
    df = query_df("SELECT * FROM supporters WHERE supporter_id=?", (supporter_id,))
    return None if df.empty else df.iloc[0].to_dict()

def update_supporter(supporter_id, segment, canal, note):
    execute(
        """UPDATE supporters
           SET segment_crm=?, canal_prefere=?, note_crm=?
           WHERE supporter_id=?""",
        (segment, canal, note, supporter_id),
    )

def get_actions(supporter_id=None):
    base = """
    SELECT a.*, s.prenom, s.nom
    FROM crm_actions a
    LEFT JOIN supporters s ON s.supporter_id = a.supporter_id
    """
    if supporter_id:
        return query_df(base + " WHERE a.supporter_id=? ORDER BY a.id DESC", (supporter_id,))
    return query_df(base + " ORDER BY a.id DESC")

def create_action(supporter_id, action_type, description):
    return execute(
        """INSERT INTO crm_actions(supporter_id,type_action,description)
           VALUES(?,?,?)""",
        (supporter_id, action_type, description),
    )

def update_action_status(action_id, status):
    execute("UPDATE crm_actions SET statut=? WHERE id=?", (status, action_id))

def create_campaign(nom, segment, canal, objectif, message):
    targets = query_df(
        """SELECT supporter_id FROM supporters
           WHERE segment_crm=? AND COALESCE(consentement_marketing,1)=1""",
        (segment,),
    )
    campaign_id = execute(
        """INSERT INTO campaigns(nom,segment,canal,objectif,message,nb_cibles)
           VALUES(?,?,?,?,?,?)""",
        (nom, segment, canal, objectif, message, len(targets)),
    )

    if not targets.empty:
        conn = get_connection()
        conn.executemany(
            "INSERT INTO campaign_targets(campaign_id,supporter_id) VALUES(?,?)",
            [(campaign_id, sid) for sid in targets["supporter_id"].tolist()],
        )
        conn.commit()
        conn.close()

    return campaign_id

def get_campaigns():
    return query_df("SELECT * FROM campaigns ORDER BY id DESC")

def get_campaign_targets(campaign_id):
    return query_df(
        """SELECT ct.*, s.prenom, s.nom, s.email, s.segment_crm, s.score_engagement
           FROM campaign_targets ct
           JOIN supporters s ON s.supporter_id=ct.supporter_id
           WHERE ct.campaign_id=?
           ORDER BY s.score_engagement DESC""",
        (campaign_id,),
    )

def update_campaign_status(campaign_id, status):
    execute("UPDATE campaigns SET statut=? WHERE id=?", (status, campaign_id))

def add_match(adversaire, date_match, competition, capacite):
    return execute(
        """INSERT INTO matches(adversaire,date_match,competition,capacite)
           VALUES(?,?,?,?)""",
        (adversaire, date_match, competition, capacite),
    )

def get_matches():
    return query_df("SELECT * FROM matches ORDER BY date_match DESC, id DESC")

def update_match_status(match_id, status):
    execute("UPDATE matches SET statut=? WHERE id=?", (status, match_id))

def add_ticket(supporter_id, match_id, qty, amount, ticket_type):
    sale_id = execute(
        """INSERT INTO ticket_sales(supporter_id,match_id,quantite,montant,type_billet)
           VALUES(?,?,?,?,?)""",
        (supporter_id, match_id, qty, amount, ticket_type),
    )

    execute(
        """UPDATE supporters
           SET nb_achats=COALESCE(nb_achats,0)+1,
               nb_places=COALESCE(nb_places,0)+?,
               nb_matchs=COALESCE(nb_matchs,0)+1,
               total_depense=COALESCE(total_depense,0)+?,
               derniere_activite=date('now')
           WHERE supporter_id=?""",
        (qty, amount, supporter_id),
    )

    execute(
        """UPDATE matches
           SET spectateurs=COALESCE(spectateurs,0)+?
           WHERE id=?""",
        (qty, match_id),
    )
    return sale_id

def get_tickets():
    return query_df(
        """SELECT t.*, s.prenom, s.nom, m.adversaire, m.date_match
           FROM ticket_sales t
           LEFT JOIN supporters s ON s.supporter_id=t.supporter_id
           LEFT JOIN matches m ON m.id=t.match_id
           ORDER BY t.id DESC"""
    )

def add_experience(supporter_id, match_id, satisfaction, nps, commentaire):
    experience_id = execute(
        """INSERT INTO experiences(supporter_id,match_id,satisfaction,nps,commentaire)
           VALUES(?,?,?,?,?)""",
        (supporter_id, match_id, satisfaction, nps, commentaire),
    )

    stats = query_df(
        """SELECT AVG(satisfaction) AS sat, AVG(nps) AS nps, COUNT(*) AS n
           FROM experiences WHERE supporter_id=?""",
        (supporter_id,),
    ).iloc[0]

    execute(
        """UPDATE supporters
           SET satisfaction_moyenne=?, nps_moyen=?, nb_avis=?, derniere_activite=date('now')
           WHERE supporter_id=?""",
        (
            float(stats["sat"] or 0),
            float(stats["nps"] or 0),
            int(stats["n"] or 0),
            supporter_id,
        ),
    )
    return experience_id

def get_experiences():
    return query_df(
        """SELECT e.*, s.prenom, s.nom, m.adversaire, m.date_match
           FROM experiences e
           LEFT JOIN supporters s ON s.supporter_id=e.supporter_id
           LEFT JOIN matches m ON m.id=e.match_id
           ORDER BY e.id DESC"""
    )

def dashboard_stats():
    fans = get_supporters()
    campaigns = get_campaigns()
    actions = get_actions()
    tickets = get_tickets()
    experiences = get_experiences()
    matches = get_matches()
    return fans, campaigns, actions, tickets, experiences, matches
