# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Série C - ÉTAPE 1 SUR 3)
# =====================================================================
import sqlite3
import os
import secrets
import sys

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# 🔑 SÉCURITÉ CONSTRUCTEUR : Forcer Render à cibler le bon dossier physique
DOSSIER_DU_FICHIER = os.path.dirname(os.path.abspath(__file__))
if DOSSIER_DU_FICHIER not in sys.path:
    sys.path.insert(0, DOSSIER_DU_FICHIER)

import data_base

# On s'assure que l'API pointe sur la MEME chaîne de base de données que l'application
data_base.initialisation_systeme()

app = FastAPI(
    title="KashFlow Cloud v5.5",
    description="Moteur réseau et interface de supervision mobile du gérant."
)
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Série C - ÉTAPE 2 SUR 3)
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


def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        return  
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


@app.get("/", response_class=HTMLResponse)
def page_accueil_supervision_mobile():
    """Renvoie l'application web mobile du gérant avec cloche d'alerte et sélecteur tactile."""
    nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW ENTREPRISE"
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Supervision - {nom_boutique}</title>
        <!-- 🟢 CORRECTIF ABSOLU : Liens de production stables et sécurisés pour smartphone -->
        <script src="https://jsdelivr.net"></script>
        <link rel="stylesheet" href="https://cloudflare.com">
    </head>
    <body class="bg-slate-50 font-sans text-slate-800 pb-12">
        
        <!-- En-tête avec Cloche d'alerte en direct -->
        <div class="bg-indigo-950 text-white px-4 py-5 shadow-lg sticky top-0 z-50 flex justify-between items-center">
            <div>
                <h1 class="text-lg font-black tracking-wider text-emerald-400 uppercase"><i class="fa-solid fa-store mr-2"></i>{nom_boutique}</h1>
                
            </div>
            
            <!-- 🔔 LA CLOCHE DE NOTIFICATION CRITIQUE -->
            <div class="relative cursor-pointer" onclick="ouvrirAlerteStocks()">
                <div id="badge-cloche" class="hidden absolute -top-1.5 -right-1.5 bg-rose-600 text-white font-black text-4xs w-4 h-4 rounded-full flex items-center justify-center animate-ping"></div>
                <div id="badge-cloche-fixe" class="hidden absolute -top-1.5 -right-1.5 bg-rose-600 text-white font-black text-4xs w-4 h-4 rounded-full flex items-center justify-center text-center text-rose-100 z-10">!</div>
                <div id="icone-cloche" class="text-xl filter grayscale opacity-40 transition-all duration-300">🔔</div>
            </div>
        </div>

        <div class="max-w-md mx-auto px-4 mt-6 space-y-4">
            <!-- Grille de contrôle rapide -->
            <div class="grid grid-cols-2 gap-4">
                <button onclick="chargerStocks()" class="bg-white p-4 rounded-xl border border-slate-200 text-center shadow-sm active:scale-95 transition-transform cursor-pointer font-bold text-xs text-slate-700">
                    <div class="text-2xl mb-1">📦</div>
                    État des Stocks
                </button>

                <button onclick="chargerStatistiques()" class="bg-white p-4 rounded-xl border border-slate-200 text-center shadow-sm active:scale-95 transition-transform cursor-pointer font-bold text-xs text-slate-700">
                    <div class="text-2xl mb-1">📊</div>
                    Chiffre d'Affaires
                </button>
            </div>

            <!-- 📋 MODULE DU REGISTRE GÉNÉRAL AVEC DÉPLOIEMENT TACTILE DES EMPLOYÉS -->
            <div class="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
                <button onclick="basculerMenuEmployes()" class="w-full p-4 flex items-center justify-between active:bg-slate-50 cursor-pointer">
                    <div class="flex items-center gap-3">
                        <div class="text-xl">📋</div>
                        <div class="text-left">
                            <p class="text-sm font-bold text-slate-800">Registre Général</p>
                            <p class="text-2xs text-slate-400">Transactions de la boutique par caissière</p>
                        </div>
                    </div>
                    <span id="fleche-registre" class="text-slate-300 font-bold text-sm transition-transform duration-200">&gt;</span>
                </button>
                
                <!-- Zone masquée qui va afficher la liste des caissières en un clic -->
                <div id="menu-tactile-employes" class="hidden border-t border-slate-100 bg-slate-50/50 p-4">
                    <p class="text-4xs font-bold text-slate-400 tracking-wider uppercase mb-2">Sélectionnez une caissière à auditer :</p>
                    <div id="liste-boutons-caissieres" class="flex flex-wrap gap-2">
                        <!-- Les macarons des vendeuses s'injectent ici dynamiquement via le JavaScript -->
                    </div>
                </div>
            </div>

            <!-- ÉCRAN D'AFFICHAGE DYNAMIQUE DES RAPPORTS COMPTABLES -->
            <div id="zone-affichage" class="bg-white rounded-2xl p-4 shadow-md border border-slate-200 hidden">
                <div class="flex justify-between items-center border-b border-slate-100 pb-3 mb-4">
                    <h3 id="titre-section" class="text-xs font-extrabold text-slate-800 uppercase tracking-wide">SECTION</h3>
                    <span onclick="fermerZone()" class="bg-slate-100 text-slate-500 font-bold px-2.5 py-1 rounded-lg text-3xs cursor-pointer active:bg-slate-200 transition-colors">X</span>
                </div>
                <div id="contenu-section" class="overflow-x-auto text-xs"></div>
            </div>
        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Série C - ÉTAPE 3.1 SUR 3)
# =====================================================================

    html_content += """
        <script>
            const API_KEY = localStorage.getItem('KASHFLOW_KEY') || "";
            let listeStocksGlobaux = []; // Stockage temporaire pour la cloche
            
            if(!API_KEY) {
                const key = prompt("Sécurité d'accès d'usine\\n\\nVeuillez saisir la clé de sécurité API de votre boutique :");
                if(key) {
                    localStorage.setItem('KASHFLOW_KEY', key.trim());
                    window.location.reload();
                }
            }

            // --- ALLUMAGE DE SÉCURITÉ EN TÂCHE DE FOND ---
            if(API_KEY) {
                verifierAlertesStocksEnArrierePlan();
                chargerProfilsCaissieresTactiles();
                // La cloche interroge le serveur automatiquement toutes les 20 secondes
                setInterval(verifierAlertesStocksEnArrierePlan, 20000);
            }

            function fermerZone() {
                document.getElementById('zone-affichage').style.display = 'none';
            }

            // --- 🔔 RECHERCHE AUTOMATIQUE DES SEUILS CRITIQUES ---
            async function verifierAlertesStocksEnArrierePlan() {
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    listeStocksGlobaux = res.inventaire_magasin || [];
                    
                    // On filtre si au moins un article a déclenché l'alerte rupture proche
                    const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                    
                    const cloche = document.getElementById('icone-cloche');
                    const badge = document.getElementById('badge-cloche');
                    const badgeFixe = document.getElementById('badge-cloche-fixe');
                    
                    // 🟢 LE CODE CORRIGÉ À METTRE À LA PLACE :
                    if(articlesEnAlerte.length > 0) {
                        // Rupture détectée : on retire le filtre gris, on augmente l'opacité et on fait sauter la cloche !
                        cloche.className = "text-xl filter-none opacity-100 animate-bounce";
                        badge.classList.remove('hidden');
                        badgeFixe.classList.remove('hidden');
                    } else {
                        // Tout est OK : la cloche redevient grise et calme
                        cloche.className = "text-xl filter grayscale opacity-40";
                        badge.classList.add('hidden');
                        badgeFixe.classList.add('hidden');
                    }

                } catch(e) { console.error("Erreur check cloche:", e); }
            }

            // Déclenche l'affichage du rapport d'alerte quand le patron clique sur la cloche
            function ouvrirAlerteStocks() {
                const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "🚨 ALERTE STOCKS CRITIQUES EN DIRECT";
                document.getElementById('zone-affichage').style.display = 'block';
                
                if(articlesEnAlerte.length === 0) {
                    el.innerHTML = "<p class='text-center py-4 font-bold text-emerald-600 text-xs'>🟢 Aucun produit en seuil critique. Tous les stocks sont confortables !</p>";
                    return;
                }
                
                let html = "<div class='space-y-2'>";
                articlesEnAlerte.forEach(i => {
                    html += `<div class='bg-rose-50 border border-rose-200 text-rose-900 rounded-lg p-3 flex justify-between items-center font-bold'>
                        <div>⚠️ ${i.article_modele.toUpperCase()}</div>
                        <div class='text-right text-rose-700 text-xxs'>Reste : ${i.quantite_restante} pcs <br><span class='text-4xs text-slate-400 font-normal'>(Seuil max appliqué: ${i.seuil_alerte_applique})</span></div>
                    </div>`;
                });
                html += "</div>";
                el.innerHTML = html;
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Série C - ÉTAPE 3.2 SUR 3)
# =====================================================================

    html_content += """
            // --- 📋 STRUCTURE TACTILE DES EMPLOYÉS ---
            function basculerMenuEmployes() {
                const menu = document.getElementById('menu-tactile-employes');
                const fleche = document.getElementById('fleche-registre');
                if(menu.classList.contains('hidden')) {
                    menu.classList.remove('hidden');
                    fleche.style.transform = "rotate(90deg)";
                } else {
                    menu.classList.add('hidden');
                    fleche.style.transform = "rotate(0deg)";
                }
            }

            async function chargerProfilsCaissieresTactiles() {
                const conteneur = document.getElementById('liste-boutons-caissieres');
                try {
                    const r = await fetch('/employes/liste', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    conteneur.innerHTML = "";
                    res.employes.forEach(emp => {
                        const bouton = document.createElement('button');
                        bouton.className = "bg-white border border-slate-200 text-slate-800 text-xxs font-extrabold px-3 py-2 rounded-lg shadow-2xs active:bg-indigo-600 active:text-white cursor-pointer transition-colors uppercase tracking-wide";
                        bouton.innerText = emp;
                        bouton.onclick = () => chargerHistoriqueCaissiereDirect(emp);
                        conteneur.appendChild(bouton);
                    });
                } catch(e) { conteneur.innerHTML = "<span class='text-rose-500 font-bold'>Échec de liaison employés.</span>"; }
            }

            async function chargerHistoriqueCaissiereDirect(caissiere) {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = `📋 DOSSIER FACTURES : ${caissiere.toUpperCase()}`;
                document.getElementById('zone-affichage').style.display = 'block';
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Calcul des transactions...</p>";

                try {
                    const r = await fetch(`/ventes/caissiere/${encodeURIComponent(caissiere)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    if(res.total_ventes_effectuees === 0) {
                        el.innerHTML = `<p style='text-align:center; padding:1rem; color:#94a3b8;'>Aucune opération enregistrée pour ${caissiere.toUpperCase()}.</p>`;
                        return;
                    }

                    let html = `<p class='font-black text-indigo-900 mb-3 text-xs'>Tiroir-Caisse : ${res.total_ventes_effectuees} factures</p><div class='space-y-2'>`;
                    res.liste_ventes.forEach(v => {
                        html += `<div class='bg-slate-50 border border-slate-100 rounded-xl p-3 flex justify-between items-center'>
                            <div>
                                <div class='font-extrabold text-slate-800'>Facture #00${v.facture_no}</div>
                                <div class='text-4xs text-slate-400 font-medium'>Client : ${v.client.toUpperCase()}</div>
                                <div class='text-4xs text-slate-400 mt-0.5 font-normal'>🕒 ${v.date} à ${v.heure}</div>
                            </div>
                            <div class='text-right'>
                                <div class='font-black text-indigo-700 text-xxs'>${v.montant_ttc}</div>
                                <div class='text-4xs font-bold text-slate-500 uppercase tracking-tight'>${v.article}</div>
                            </div>
                        </div>`;
                    });
                    html += "</div>";
                    el.innerHTML = html;
                } catch(e) { el.innerHTML = "<p style='color:#ef4444; font-weight:bold;'>❌ Échec d'audit.</p>"; }
            }

            async function chargerStocks() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📦 ÉTAT GLOBAL DE L'INVENTAIRE";
                document.getElementById('zone-affichage').style.display = 'block';
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Lecture du stock central...</p>";
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    let html = "<table style='width:100%; text-align:left; border-collapse:collapse;'><thead><tr style='color:#94a3b8; font-size:0.75rem; border-bottom:1px solid #e2e8f0;'><th style='padding:0.5rem 0;'>Article</th><th style='text-align:center;'>Reste</th><th style='text-align:right;'>Statut</th></tr></thead><tbody>";
                    res.inventaire_magasin.forEach(i => {
                        const color = i.quantite_restante <= i.seuil_alerte_applique ? 'color:#b91c1c; background:#fee2e2;' : 'color:#047857; background:#dcfce7;';
                        html += `<tr style='border-bottom:1px solid #f1f5f9;'>
                            <td style='padding:0.75rem 0; font-weight:bold; color:#334155;'>${i.article_modele}</td>
                            <td style='text-align:center; font-weight:900;'>${i.quantite_restante} pcs</td>
                            <td style='text-align:right;'><span style='padding:0.25rem 0.5rem; border-radius:9999px; font-size:0.65rem; font-weight:bold; ${color}'>${i.statut_commande}</span></td>
                        </tr>`;
                    });
                    html += "</tbody></table>"; el.innerHTML = html;
                } catch(e) { el.innerHTML = "<p style='color:#ef4444;'>❌ Erreur réseau.</p>"; }
            }

            async function chargerStatistiques() {
                const el = document.getElementById('contenu-section');
                document.getElementById('titre-section').innerText = "📊 ANALYSE DU CHIFFRE D'AFFAIRES";
                document.getElementById('zone-affichage').style.display = 'block';
                let cible = prompt("Tapez la date au format J/M/AAAA (ex: 12/9/2026) :");
                if(!cible) return;
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Calcul...</p>";
                try {
                    const r = await fetch(`/ventes/statistiques?temporalite=JOUR&cible=${encodeURIComponent(cible)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    el.innerHTML = `
                        <div style='background:#dcfce7; border:1px solid #bbf7d0; border-radius:0.75rem; padding:1rem; text-align:center; color:#14532d;'>
                            <p style='margin:0; font-size:0.75rem; font-weight:bold;'>Chiffre d'Affaires du ${cible}</p>
                            <p style='margin:0.25rem 0 0 0; font-size:1.5rem; font-weight:900;'>${res.chiffre_affaires_ttc} FCFA</p>
                        </div>
                        <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:0.75rem; padding:0.75rem; font-size:0.75rem; margin-top:1rem;'>
                            <p>🔥 <b>Article Star :</b> ${res.article_le_plus_vendu}</p>
                            <p style='border-top:1px solid #e2e8f0; margin-top:0.5rem; pt-2; font-style:italic;'>📈 ${res.comparatif_performance_n_1}</p>
                        </div>`;
                } catch(e) { el.innerHTML = "<p style='color:#ef4444;'>❌ Erreur de calcul.</p>"; }
            }
        </script>
    </body>
    </html>
    """
    return html_content
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Série C - ÉTAPE 3.3 SUR 3)
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
                "montant_ttc": f"{v[3]} FCFA", "date": f"{v[4]}", "heure": v[5]
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
                "seuil_alerte_applique": seuil,
                "statut_commande": etat_alerte
            })
        return {"inventaire_magasin": rapport_stock}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/employes/liste", dependencies=[Depends(verifier_cle_api)])
def api_liste_des_employes():
    """Extrait la liste unique des caissières enregistrées pour alimenter le smartphone du patron."""
    try:
        liste_employes = data_base.recuperer_liste_tous_employes()
        if not liste_employes:
            return {"employes": ["caissiere1", "caissiere2"]}
        return {"employes": [str(emp).strip().lower() for emp in liste_employes]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
