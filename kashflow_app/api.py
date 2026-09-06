# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - PARTIE 1 SUR 2)
# =====================================================================
import sqlite3
import os
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import data_base

data_base.initialisation_systeme()

# Initialisation de la passerelle Cloud d'entreprise
app = FastAPI(
    title="KashFlow Cloud v5.5 - Espace Supervision Patron",
    description="Moteur réseau permettant au gérant de piloter son entreprise à distance."
)

origines_autorisees = [
    origine.strip()
    for origine in os.environ.get("KASHFLOW_CORS_ORIGINS", "").split(",")
    if origine.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origines_autorisees,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

# Structure de contrôle stricte pour la validation des données réseau arrivant de la caisse
class VenteSchemaReseau(BaseModel):
    reference_locale: str
    client: str
    article: str
    description_unique: str  # IMEI, Numéro de Série, etc.
    prix_ht: float
    quantite: int
    caissiere: str
    applique_tva: bool | None = None


def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    """Refuse l'API tant qu'une clé serveur n'est pas configurée et présentée."""
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        raise HTTPException(status_code=503, detail="Clé API serveur non configurée.")
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


@app.get("/")
def verifier_connexion_cloud():
    """Route de diagnostic rapide pour vérifier si le serveur en ligne répond."""
    return {
        "statut": "Serveur Central en ligne (200 OK)",
        "application": "KashFlow Manager Backend v5.5",
        "auteur": "Ingénieur Serges"
    }# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 1 SUR 10)
# =====================================================================
import sqlite3
import os
import secrets
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import data_base

data_base.initialisation_systeme()

app = FastAPI(
    title="KashFlow Cloud v5.5",
    description="Moteur réseau et interface de supervision mobile du gérant."
)
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 2 SUR 10)
# =====================================================================

origines_autorisees = [
    origine.strip()
    for origine in os.environ.get("KASHFLOW_CORS_ORIGINS", "").split(",")
    if origine.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if not origines_autorisees else origines_autorisees,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["X-API-Key", "Content-Type"],
)

class VenteSchemaReseau(BaseModel):
    reference_locale: str
    client: str
    article: str
    description_unique: str
    prix_ht: float
    quantite: int
    caissiere: str
    applique_tva: bool | None = None
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 3 SUR 10)
# =====================================================================

def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        return  # Mode démo si non configurée en local
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


# =====================================================================
# 📱 INTERFACE VISUELLE MAJESTUEUSE POUR LE TÉLÉPHONE DU PATRON
# =====================================================================
@app.get("/", response_class=HTMLResponse)
def page_accueil_supervision_mobile():
    """Renvoie une application web mobile sublime avec boutons tactiles."""
    nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW ENTERPRISE"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Supervision - {nom_boutique}</title>
        <script src="https://jsdelivr.net"></script>
        <link rel="stylesheet" href="https://cloudflare.com">
    </head>
    <body class="bg-slate-100 font-sans text-slate-800 pb-12">
        
        <div class="bg-indigo-900 text-white text-center py-6 shadow-md sticky top-0 z-50">
            <h1 class="text-xl font-black tracking-wider"><i class="fa-solid fa-store text-emerald-400 mr-2"></i>{nom_boutique.upper()}</h1>
            <p class="text-xs text-indigo-200 mt-1">KashFlow Cloud Manager v5.5 • Espace Patron</p>
        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 5 SUR 10)
# =====================================================================

    html_content += """
        <script>
            const API_KEY = localStorage.getItem('KASHFLOW_KEY') || "";
            
            if(!API_KEY) {
                const key = prompt("Sécurité d'accès d'usine\\n\\nVeuillez saisir la clé de sécurité API de votre boutique :");
                if(key) {
                    localStorage.setItem('KASHFLOW_KEY', key.trim());
                    window.location.reload();
                }
            }

            function fermerZone() {
                document.getElementById('zone-affichage').classList.add('hidden');
            }

            async function chargerStocks() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📦 ÉTAT GLOBAL DE L'INVENTAIRE";
                document.getElementById('zone-affichage').classList.remove('hidden');
                el.innerHTML = "<p class='text-center py-4 text-slate-400'><i class='fa-solid fa-spinner animate-spin mr-2'></i>Lecture du stock central...</p>";
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 6 SUR 10)
# =====================================================================

    html_content += """
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    let html = `<table class='w-full text-left border-collapse'>
                        <thead>
                            <tr class='bg-slate-50 text-slate-400 text-[10px] uppercase font-bold border-b border-slate-100'>
                                <th class='py-2 px-1'>Article / Modèle</th>
                                <th class='py-2 text-center'>Reste</th>
                                <th class='py-2 text-right'>Statut</th>
                            </tr>
                        </thead>
                        <tbody>`;
                    
                    res.inventaire_magasin.forEach(i => {
                        const color = i.quantite_restante <= i.seuil_alerte_applied || i.statut_commande.includes('🚨') ? 'text-red-600 bg-red-50' : 'text-emerald-600 bg-emerald-50';
                        html += `<tr class='border-b border-slate-100'>
                            <td class='py-3 font-bold text-slate-800'>${i.article_modele}</td>
                            <td class='py-3 text-center font-black'>${i.quantite_restante} pcs</td>
                            <td class='py-3 text-right'><span class='px-2 py-1 rounded-full font-bold text-[9px] ${color}'>${i.quantite_restante <= 5 ? '🛑 ALERTE' : '🟢 OK'}</span></td>
                        </tr>`;
                    });
                    html += "</tbody></table>";
                    el.innerHTML = html;
                } catch(e) {
                    el.innerHTML = "<p class='text-red-500 font-bold text-center py-2'>❌ Erreur de clé API ou serveur déconnecté.</p>";
                }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 7 SUR 10)
# =====================================================================

    html_content += """
            async function chargerStatistiques() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📊 ANALYSE DU CHIFFRE D'AFFAIRES";
                document.getElementById('zone-affichage').classList.remove('hidden');
                
                let cible = prompt("Analyse financière du jour\\n\\nTapez la date cible au format J/M/AAAA (ex: 6/9/2026) :");
                if(!cible) return;

                el.innerHTML = "<p class='text-center py-4 text-slate-400'><i class='fa-solid fa-spinner animate-spin mr-2'></i>Calcul des performances...</p>";
                
                try {
                    const r = await fetch(`/ventes/statistiques?temporalite=JOUR&cible=${encodeURIComponent(cible)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    el.innerHTML = `
                        <div class='bg-emerald-50 border border-emerald-200 rounded-xl p-4 text-center mb-4'>
                            <p class='text-[10px] font-bold text-emerald-600 uppercase tracking-wide'>Chiffre d'Affaires du ${cible}</p>
                            <p class='text-2xl font-black text-emerald-800 mt-1'>${res.chiffre_affaires_ttc} <span class='text-xs'>FCFA</span></p>
                        </div>
                        <div class='bg-slate-50 rounded-xl p-3 border border-slate-100'>
                            <p class='text-slate-500 font-bold mb-1'><i class='fa-solid fa-fire text-orange-500 mr-1'></i> Article Star : <span class='text-slate-800 font-black'>${res.article_le_plus_vendu}</span></p>
                            <p class='text-[11px] text-slate-500 italic mt-2 border-t border-slate-200 pt-2'><i class='fa-solid fa-chart-line text-indigo-500 mr-1'></i> ${res.comparatif_performance_n_1}</p>
                        </div>
                    `;
                } catch(e) {
                    el.innerHTML = "<p class='text-red-500 font-bold text-center py-2'>❌ Échec de l'analyse comptable.</p>";
                }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 8 SUR 10)
# =====================================================================

    html_content += """
            async function chargerToutHistorique() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📋 TRANSACTIONS EN DIRECT";
                document.getElementById('zone-affichage').classList.remove('hidden');
                el.innerHTML = "<p class='text-center py-4 text-slate-400'><i class='fa-solid fa-spinner animate-spin mr-2'></i>Chargement du registre central...</p>";
                
                let caissiere = prompt("Entrez l'identifiant exact de la caissière à auditer :");
                if(!caissiere) return;

                try {
                    const r = await fetch(`/ventes/caissiere/${caissiere.trim().lower()}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    if(res.total_ventes_effectuees === 0) {
                        el.innerHTML = "<p class='text-center py-4 text-slate-400'>Aucune transaction répertoriée pour cette session.</p>";
                        return;
                    }

                    let html = `<p class='mb-3 font-bold text-indigo-900'>Total ventes émises : ${res.total_ventes_effectuees} factures</p>
                        <div class='space-y-3'>`;
                    
                    res.liste_ventes.forEach(v => {
                        html += `<div class='bg-slate-50 p-3 rounded-xl border border-slate-200 flex justify-between items-center'>
                            <div>
                                <p class='font-black text-slate-800 text-xs'>Facture #00${v.facture_no}</p>
                                <p class='text-[10px] text-slate-500 mt-0.5'>Client : ${v.client.toUpperCase()}</p>
                                <p class='text-[9px] text-slate-400 mt-1'><i class='fa-regular fa-clock mr-1'></i>Le ${v.date} à ${v.heure}</p>
                            </div>
                            <div class='text-right'>
                                <p class='font-black text-indigo-700 text-sm'>${v.montant_ttc}</p>
                                <p class='text-[9px] text-slate-400 mt-0.5'>${v.article}</p>
                            </div>
                        </div>`;
                    });
                    html += "</div>";
                    el.innerHTML = html;
                } catch(e) {
                    el.innerHTML = "<p class='text-red-500 font-bold text-center py-2'>❌ Erreur de lecture.</p>";
                }
            }
        </script>
    </body>
    </html>
    """
    return html_content
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 9 SUR 10)
# =====================================================================

@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    """Intercepte, calcule la TVA et centralise la vente du magasin."""
    try:
        donnees.caissiere = donnees.caissiere.strip().lower()
        if donnees.prix_ht <= 0 or not 0 < donnees.quantite <= 1000:
            raise HTTPException(status_code=422, detail="Prix ou quantité invalide.")

        connexion = sqlite3.connect(data_base.DB_NAME)
        deja_sync = connexion.execute(
            "SELECT id FROM ventes WHERE reference_locale = ?", (donnees.reference_locale,)
        ).fetchone()
        connexion.close()
        if deja_sync:
            return {"statut": "Déjà synchronisé", "facture_id_cloud": deja_sync[0]}

        regime_tva = int(donnees.applique_tva) if donnees.applique_tva is not None else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        total_ht = donnees.prix_ht * donnees.quantite
        tva_calculee = total_ht * (19.25 / 100) if regime_tva == 1 else 0.0
        total_ttc = total_ht + tva_calculee
        
        num_facture = data_base.enregistrer_vente_sql(
            client=donnees.client, article=donnees.article, desc_unique=donnees.description_unique,
            mnt_ht=total_ht, tva=tva_calculee, ttc=total_ttc, caissiere=donnees.caissiere, reference_locale=donnees.reference_locale
        )
        if num_facture is None:
            raise HTTPException(status_code=500, detail="Échec d'écriture Cloud.")
            
        return {"statut": "Synchronisé", "facture_id_cloud": num_facture}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - ÉTAPE 10 SUR 10)
# =====================================================================

@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    """Calcule le CA et le produit star de la période pour l'écran mobile."""
    try:
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {
            "chiffre_affaires_ttc": analyse["ca_total"],
            "article_le_plus_vendu": str(analyse["produit_phare"]).replace("{", "").replace("}", ""),
            "comparatif_performance_n_1": analyse["message_performance"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)])
def api_historique_caissiere(nom_caissiere: str):
    """Extrait l'audit des ventes d'une vendeuse pour l'affichage mobile du patron."""
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes: 
            return {"total_ventes_effectuees": 0, "liste_ventes": []}
        liste_formatee = []
        for v in ventes:
            liste_formatee.append({
                "facture_no": v[0], "client": v[1], "article": str(v[2]).replace("{", "").replace("}", ""),
                "montant_ttc": f"{v[3]} FCFA", "date": v[4], "heure": v[5]
            })
        return {"total_ventes_effectuees": len(liste_formatee), "liste_ventes": liste_formatee}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stocks/etat", dependencies=[Depends(verifier_cle_api)])
def api_consulter_stocks_cloud():
    """Vérifie l'état d'inventaire et renvoie le statut avec seuil dynamique 10/5."""
    try:
        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("SELECT modele, quantite_dispo, ventes_cumulees FROM stocks")
        lignes = curseur.fetchall()
        
        curseur.execute("SELECT MAX(ventes_cumulees) FROM stocks")
        max_v_row = curseur.fetchone()
        max_v = max_v_row[0] if max_v_row and max_v_row[0] is not None else 0
        connexion.close()
        
        rapport_stock = []
        for l in lignes:
            seuil = 10 if l[2] == max_v else 5
            string_modele = str(l[0]).replace("{", "").replace("}", "")
            etat_alerte = "🚨 RUPTURE PROCHE" if l[1] <= seuil else "🟢 Stock Confortable"
            rapport_stock.append({
                "article_modele": string_modele,
                "quantite_restante": l[1],
                "ventes_totales": l[2],
                "seuil_alerte_applied": seuil,
                "statut_commande": etat_alerte
            })
        return {"inventaire_magasin": rapport_stock}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    """
    Route distante appelée automatiquement en arrière-plan par l'ordinateur 
    de la caissière pour enregistrer une transaction dans le Cloud du patron.
    """
    try:
        donnees.caissiere = donnees.caissiere.strip().lower()
        if donnees.prix_ht <= 0 or not 0 < donnees.quantite <= 1000:
            raise HTTPException(status_code=422, detail="Prix ou quantité invalide.")

        connexion = sqlite3.connect(data_base.DB_NAME)
        deja_sync = connexion.execute(
            "SELECT id FROM ventes WHERE reference_locale = ?", (donnees.reference_locale,)
        ).fetchone()
        connexion.close()
        if deja_sync:
            return {"statut": "Déjà synchronisé", "facture_id_cloud": deja_sync[0]}

        # 1. Extraction du régime fiscal de la caissière enregistré en base de données
        regime_tva = (
            int(donnees.applique_tva)
            if donnees.applique_tva is not None
            else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        )
        
        # 2. Calcul financier de sécurité sur le serveur central
        total_ht = donnees.prix_ht * donnees.quantite
        
        if regime_tva == 1:
            tva_calculee = total_ht * (19.25 / 100) # Grande entreprise
        else:
            tva_calculee = 0.0 # Petite boutique informelle
            
        total_ttc = total_ht + tva_calculee
        
        # 3. Écriture immédiate dans le coffre-fort SQL
        num_facture = data_base.enregistrer_vente_sql(
            client=donnees.client,
            article=donnees.article,
            desc_unique=donnees.description_unique,
            mnt_ht=total_ht,
            tva=tva_calculee,
            ttc=total_ttc,
            caissiere=donnees.caissiere,
            reference_locale=donnees.reference_locale,
        )
        
        if num_facture is None:
            raise HTTPException(status_code=500, detail="Échec critique d'écriture sur le serveur central.")
            
        return {
            "statut": "Synchronisé",
            "facture_id_cloud": num_facture,
            "message": "Transaction répertoriée avec succès sur le terminal du patron."
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
# =====================================================================
# MODULE 3 : api.py (Version 5.5 Pro - PARTIE 2 SUR 2)
# =====================================================================

# --- ROUTE N°4 : AUDIT FINANCIER ET STATISTIQUES COMPARATIVES ---
@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    """
    Route analytique permettant au gérant d'obtenir le CA de la journée, 
    du mois ou de l'année, le produit star, et le comparatif de performance.
    - temporalite : 'JOUR', 'MOIS' ou 'ANNEE'
    - cible : 'JJ-MM' (pour jour), 'MM' (pour mois) ou 'AAAA' (pour année)
    """
    if temporalite not in ["JOUR", "MOIS", "ANNEE"]:
        raise HTTPException(status_code=400, detail="Temporalité invalide. Choisissez 'JOUR', 'MOIS' ou 'ANNEE'.")
        
    try:
        # Interrogation directe du moteur analytique de data_base.py
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {
            "statut": "Succes",
            "periode_analysee": temporalite,
            "valeur_cible": cible,
            "chiffre_affaires_ttc": analyse["ca_total"],
            "article_le_plus_vendu": analyse["produit_phare"],
            "comparatif_performance_n_1": analyse["message_performance"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ROUTE N°5 : RAPPORT DE RENDEMENT PAR CAISSIÈRE ---
@app.get("/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)])
def api_historique_caissiere(nom_caissiere: str):
    """Permet au gérant de voir les ventes effectuées par une vendeuse spécifique."""
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes:
            return {
                "caissiere": nom_caissiere.upper(),
                "total_ventes_effectuees": 0,
                "liste_ventes": []
            }
            
        liste_formatee = []
        for v in ventes:
            liste_formatee.append({
                "facture_no": v[0],
                "client": v[1],
                "article": v[2],
                "montant_ttc": v[3],
                "date": v[4],
                "heure": v[5]
            })
            
        return {
            "caissiere": nom_caissiere.upper(),
            "total_ventes_effectuees": len(liste_formatee),
            "liste_ventes": liste_formatee
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- ROUTE N°6 : RAPPORT DE STOCK CRITIQUE EN TEMPS RÉEL ---
@app.get("/stocks/etat", dependencies=[Depends(verifier_cle_api)])
def api_consulter_stocks_cloud():
    """Renvoie l'état global du stock de l'entreprise pour la supervision du patron."""
    try:
        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("SELECT modele, quantite_dispo, ventes_cumulees FROM stocks")
        lignes = curseur.fetchall()
        connexion.close()
        
        rapport_stock = []
        for l in lignes:
            # Règle : Si le produit est un top vente, seuil à 10, sinon 5
            curseur_max = sqlite3.connect(data_base.DB_NAME)
            c = curseur_max.cursor()
            c.execute("SELECT MAX(ventes_cumulees) FROM stocks")
            max_v = c.fetchone()[0] or 0
            curseur_max.close()
            
            seuil = 10 if l[2] == max_v else 5
            etat_alerte = "🚨 RUPTURE PROCHE / COMMANDE" if l[1] <= seuil else "🟢 Stock Confortable"
            
            rapport_stock.append({
                "article_modele": l[0],
                "quantite_restante": l[1],
                "ventes_totales": l[2],
                "seuil_alerte_applique": seuil,
                "statut_commande": etat_alerte
            })
            
        return {"inventaire_magasin": rapport_stock}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
