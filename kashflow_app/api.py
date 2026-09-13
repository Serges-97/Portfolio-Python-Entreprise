# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 1 SUR 7)
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
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 2 SUR 7)
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
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 3 SUR 7)
# =====================================================================

def verifier_cle_api(x_api_key: str | None = Header(default=None)):
    cle_attendue = os.environ.get("KASHFLOW_API_KEY", "").strip()
    if not cle_attendue:
        return  
    if not x_api_key or not secrets.compare_digest(x_api_key, cle_attendue):
        raise HTTPException(status_code=401, detail="Clé API invalide.")


@app.get("/", response_class=HTMLResponse)
def page_accueil_supervision_mobile():
    """Renvoie l'application web mobile du gérant calquée à 100% sur les maquettes de Serge."""
    nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW ENTREPRISE"
    
    # 🎨 REPRODUCTION INTÉGRALE ET CORRIGÉE DU VISUEL DE TES MAQUETTES
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{nom_boutique}</title>
        <!-- 🟢 SÉCURISATION DES LIENS DE STYLE POUR GOOGLE PIXEL & TOUS SMARTPHONES -->
        <script src="https://jsdelivr.net"></script>
        <link rel="stylesheet" href="https://cloudflare.com">
    </head>
    <body class="bg-slate-100 min-h-screen flex flex-col items-center p-4 text-slate-800 antialiased">

        <!-- Container Smartphone -->
        <div class="relative w-full max-w-[400px] bg-white rounded-[30px] shadow-xl px-5 py-7 min-h-[820px] overflow-hidden flex flex-col">
            
            <!-- HEADER AVEC CLOCHE ET BADGE DYNAMIQUE -->
            <header class="flex justify-between items-center mb-6">
                <h1 class="text-2xl font-extrabold text-slate-700 tracking-wide uppercase">{nom_boutique.lower()}</h1>
                <div class="relative cursor-pointer bg-amber-50 text-amber-600 p-2.5 rounded-full text-base active:scale-95 transition-transform" onclick="ouvrirAlerteStocks()">
                    <!-- Badge numérique avec clignotement doux (animate-pulse) et compteur de ruptures réelles -->
                    <div id="badge-cloche" class="hidden absolute -top-1.5 -right-1.5 bg-red-600 text-white font-black text-[9px] w-5 h-5 rounded-full flex items-center justify-center shadow-md z-10 animate-pulse">0</div>
                    <i id="icone-cloche" class="fa-solid fa-bell"></i>
                </div>
            </header>
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 4 SUR 7)
# =====================================================================

    html_content += """
            <!-- GRILLE DES ACTIONS DE LA MAQUETTE 1 -->
            <main class="grid grid-cols-2 gap-4 mb-6">
                <div onclick="chargerStocks()" class="bg-slate-50 border border-slate-200 rounded-2xl p-5 flex flex-col items-center gap-3 cursor-pointer active:scale-98 active:bg-slate-100 transition-all shadow-2xs">
                    <i class="text-2xl text-indigo-900 fa-solid fa-box"></i>
                    <span class="text-xs font-black text-slate-600 text-center tracking-tight">État des Stocks</span>
                </div>
                <div onclick="chargerStatistiques()" class="bg-slate-50 border border-slate-200 rounded-2xl p-5 flex flex-col items-center gap-3 cursor-pointer active:scale-98 active:bg-slate-100 transition-all shadow-2xs">
                    <i class="text-2xl text-indigo-900 fa-solid fa-chart-bar"></i>
                    <span class="text-xs font-black text-slate-600 text-center tracking-tight">Chiffre d'Affaires</span>
                </div>
            </main>

            <!-- REGISTRE GÉNÉRAL DE LA MAQUETTE 1 -->
            <div class="bg-white border border-slate-200 rounded-2xl p-5 text-center mb-6 shadow-xs flex flex-col items-center">
                <i class="text-3xl text-slate-500 fa-solid fa-clipboard-check mb-2"></i>
                <h2 class="text-base font-black text-slate-800 mb-1">Registre Général</h2>
                <p class="text-2xs text-slate-400 mb-3 font-medium">Transactions de la boutique par caissière</p>
                <i class="text-xs text-slate-300 fa-solid fa-chevron-right animate-pulse"></i>
            </div>

            <!-- SECTION SÉLECTION CAISSIÈRE AVEC LES MACARONS TACTILES -->
            <section class="flex-grow">
                <h3 class="text-2xs font-extrabold text-slate-400 uppercase tracking-wider mb-3">Sélectionnez une caissière à auditer :</h3>
                <div id="liste-boutons-caissieres" class="flex flex-wrap gap-2.5">
                    <!-- Les macarons élégants des vendeuses s'injectent ici automatiquement en JS -->
                </div>
            </section>

            <!-- 📱 FENÊTRE MODALE DES FACTURES (MAQUETTE 2 - CACHÉE AU DÉPART) -->
            <div id="modal-facturation" class="hidden absolute inset-0 bg-white/98 px-5 py-6 rounded-[30px] z-50 flex-col overflow-y-auto transition-all duration-200">
                <!-- Header Dossier Bleu Nuit de ton dessin -->
                <div class="bg-[#1c355e] text-white rounded-2xl p-4 flex items-center gap-4 mb-4 shadow-md">
                    <i class="text-2xl fa-solid fa-folder-open"></i>
                    <div class="text-left font-black tracking-wider text-xs uppercase leading-tight">
                        DOSSIER FACTURES :<br><span id="nom-caissiere-titre" class="text-emerald-400 font-black text-sm">--</span>
                    </div>
                </div>

                <!-- Tiroir Caisse et Bouton de Fermeture -->
                <div class="bg-[#e4effb] border border-[#cbdff4] text-[#1c355e] rounded-xl p-3 flex justify-between items-center text-xs font-bold shadow-3xs mb-4">
                    <span id="compteur-factures-tiroir">Tiroir-Caisse : 0 facture(s)</span>
                    <button onclick="fermerModal()" class="text-rose-600 text-xl px-2 py-0.5 font-black cursor-pointer active:scale-90 transition-transform"><i class="fa-solid fa-xmark"></i></button>
                </div>

                <!-- Conteneur Dynamique pour empiler tes fiches de factures beiges -->
                <div id="contenu-factures-modale" class="space-y-4 pb-6"></div>
            </div>

        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 5 SUR 7)
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

            function fermerModal() {
                document.getElementById('modal-facturation').classList.replace('flex', 'hidden');
            }

            // --- 🔔 CLOCHE DE LA MAQUETTE 1 DYNAMIQUE ---
            async function verifierAlertesStocksEnArrierePlan() {
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    listeStocksGlobaux = res.inventaire_magasin || [];
                    
                    const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                    const nombreAlertes = articlesEnAlerte.length;
                    
                    const cloche = document.getElementById('icone-cloche');
                    const badge = document.getElementById('badge-cloche');
                    
                    if(nombreAlertes > 0) {
                        cloche.className = "fa-solid fa-bell text-rose-500 text-lg";
                        badge.innerText = nombreAlertes;
                        badge.classList.remove('hidden');
                    } else {
                        cloche.className = "fa-solid fa-bell text-slate-400";
                        badge.classList.add('hidden');
                    }
                } catch(e) { console.error("Erreur check cloche:", e); }
            }

            function ouvrirAlerteStocks() {
                const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = "STOCKS CRITIQUES";
                document.getElementById('compteur-factures-tiroir').innerText = `Alerte : ${articlesEnAlerte.length} produit(s)`;
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "";
                
                if(articlesEnAlerte.length === 0) {
                    contenu.innerHTML = "<div class='bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-2xl p-5 text-center font-bold text-xs shadow-3xs'>🟢 Aucun produit en seuil critique. Tous les stocks sont confortables !</div>";
                    return;
                }
                
                let html = "";
                articlesEnAlerte.forEach(i => {
                    html += `
                    <div class='bg-rose-50 border border-rose-100 text-rose-900 rounded-2xl p-4 flex justify-between items-center font-bold text-xs shadow-3xs'>
                        <div>⚠️ ${i.article_modele.toUpperCase()}</div>
                        <div class='text-right text-rose-700 bg-white px-3 py-1 rounded-xl border border-rose-200 shadow-4xs'>Reste : ${i.quantite_restante} pcs</div>
                    </div>`;
                });
                contenu.innerHTML = html;
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 6.1 SUR 7)
# =====================================================================

    html_content += """
            // --- 📋 ENTRÉE DES EMPLOYÉS ET CRÉATION DES MACARONS TACTILES ---
            async function chargerProfilsCaissieresTactiles() {
                const conteneur = document.getElementById('liste-boutons-caissieres');
                try {
                    const r = await fetch('/employes/liste', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    conteneur.innerHTML = "";
                    res.employes.forEach(emp => {
                        const bouton = document.createElement('button');
                        // Style de tes macarons : bleu clair avec petite icône utilisateur
                        bouton.className = "bg-blue-50 text-blue-700 border border-blue-200 rounded-full px-5 py-2 text-sm font-semibold flex items-center gap-2 capitalize cursor-pointer active:bg-blue-700 active:text-white transition-all shadow-4xs";
                        bouton.innerHTML = `<i class="fa-solid fa-user text-blue-400"></i> ${emp}`;
                        bouton.onclick = () => chargerHistoriqueCaissiereDirect(emp);
                        conteneur.appendChild(bouton);
                    });
                } catch(e) { conteneur.innerHTML = "<span class='text-rose-500 font-bold text-xs'>❌ Liaison employés coupée.</span>"; }
            }

            // --- 📱 ALLUMAGE CHIRURGICAL DE TON DEUXIÈME DESIGN ---
            async function chargerHistoriqueCaissiereDirect(caissiere) {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = caissiere.toUpperCase();
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-4'>Ouverture du dossier comptable...</p>";

                try {
                    const r = await fetch(`/ventes/caissiere/${encodeURIComponent(caissiere)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    document.getElementById('compteur-factures-tiroir').innerText = `Tiroir-Caisse : ${res.total_ventes_effectuees} facture(s)`;
                    
                    if(!res.liste_ventes || res.liste_ventes.length === 0) {
                        contenu.innerHTML = `<div class='bg-slate-50 border border-slate-200 rounded-2xl p-5 text-center text-slate-400 font-bold text-xs shadow-3xs'>Tiroir-Caisse vide. Aucune opération enregistrée pour ${caissiere.toUpperCase()}.</div>`;
                        return;
                    }

                    let html = "";
                    // 3. Dessin rigoureux des cartes de factures beiges de ta maquette 2
                    res.liste_ventes.forEach(v => {
                        html += `
                        <div class="bg-white border border-slate-200 rounded-2xl shadow-xs overflow-hidden text-left">
                            <div class="bg-slate-50 p-4 border-b border-slate-200 flex justify-between items-center">
                                <h3 class="text-base font-bold text-slate-800">Facture #00${v.facture_no}</h3>
                                <i class="text-slate-400 fa-solid fa-gear animate-spin-slow"></i>
                            </div>
                            
                            <div class="p-5">
                                <div class="mb-4">
                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-1">Détails du Client</div>
                                    <div class="text-sm font-semibold text-slate-600 flex items-center gap-2"><i class="text-slate-400 fa-solid fa-user"></i> Client : ${v.client.toUpperCase()}</div>
                                </div>

                                <div class="mb-4">
                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-1">Détails de la Transaction</div>
                                    <div class="text-sm font-semibold text-slate-600 flex items-center gap-2"><i class="text-slate-400 fa-solid fa-clock"></i> ${v.date} à ${v.heure}</div>
                                </div>

                                <div class="mb-4">
                                    <!-- Le montant en gros bleu/vert centré de ton dessin -->
                                    <div class="bg-green-50 border border-dashed border-green-200 rounded-xl p-3 text-center text-xl font-black text-green-700 tracking-wide shadow-4xs">
                                        ${v.montant_ttc}
                                    </div>
                                </div>

                                <div class="mt-2">
                                    <div class="text-[10px] text-slate-400 uppercase font-bold tracking-wider mb-1">Produit</div>
                                    <div class="text-sm font-bold text-slate-800 uppercase tracking-tight">${v.article}</div>
                                </div>
                            </div>
                        </div>`;
                    });
                    contenu.innerHTML = html;
                } catch(e) { contenu.innerHTML = "<p class='text-rose-500 font-bold text-xs text-center py-4'>❌ Erreur de décodage du dossier.</p>"; }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Rectifiée Premium - ÉTAPE 6.2 SUR 7)
# =====================================================================

    html_content += """
            async function chargerStocks() {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                
                document.getElementById('nom-caissiere-titre').innerText = "INVENTAIRE DES STOCKS";
                document.getElementById('compteur-factures-tiroir').innerText = "État Centralisé";
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-4'>Lecture du stock central...</p>";
                
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    let html = "<div class='bg-white border border-slate-200 rounded-2xl p-4 shadow-3xs overflow-x-auto'><table class='w-full text-left text-xs border-collapse'><thead><tr class='text-slate-400 border-b border-slate-100 font-bold'><th class='pb-2'>Article</th><th class='text-center pb-2'>Reste</th><th class='text-right pb-2'>Statut</th></tr></thead><tbody>";
                    res.inventaire_magasin.forEach(i => {
                        const color = i.quantite_restante <= i.seuil_alerte_applique ? 'bg-red-50 text-red-700 border-red-100' : 'bg-green-50 text-green-700 border-green-100';
                        html += `<tr class='border-b border-slate-50/60'>
                            <td class='py-3 font-bold text-slate-700 uppercase tracking-tight'>${i.article_modele}</td>
                            <td class='text-center font-black text-slate-800'>${i.quantite_restante} pcs</td>
                            <td class='text-right'><span class='px-2 py-0.5 rounded-full border text-[10px] font-black ${color}'>${i.statut_commande}</span></td>
                        </tr>`;
                    });
                    html += "</tbody></table></div>";
                    contenu.innerHTML = html;
                } catch(e) { contenu.innerHTML = "<p class='text-rose-500 font-bold text-xs text-center py-4'>❌ Erreur de lecture d'inventaire.</p>"; }
            }

            async function chargerStatistiques() {
                const modal = document.getElementById('modal-facturation');
                const contenu = document.getElementById('contenu-factures-modale');
                let cible = prompt("Tapez la date au format J/M/AAAA (ex: 12/9/2026) :");
                if(!cible) return; // 🟢 CORRECTIF CRITIQUE : Syntaxe nettoyée et débloquée
                
                document.getElementById('nom-caissiere-titre').innerText = "RAPPORTS COMPTABLES";
                document.getElementById('compteur-factures-tiroir').innerText = `Date : ${cible}`;
                modal.classList.replace('hidden', 'flex');
                contenu.innerHTML = "<p class='text-center text-slate-400 text-xs py-4'>Analyse des performances financières...</p>";
                
                try {
                    const r = await fetch(`/ventes/statistiques?temporalite=JOUR&cible=${encodeURIComponent(cible)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    contenu.innerHTML = `
                        <div class='space-y-4'>
                            <div class='bg-emerald-50 border border-emerald-200 rounded-2xl p-5 text-center text-emerald-900 shadow-3xs'>
                                <p class='text-[10px] font-black text-emerald-600 uppercase tracking-wider mb-1'>Chiffre d'Affaires du ${cible}</p>
                                <p class='text-2xl font-black tracking-wide'>${res.chiffre_affaires_ttc} FCFA</p>
                            </div>
                            <div class='bg-slate-50 border border-slate-200 rounded-2xl p-4 text-xs font-medium space-y-2 shadow-4xs text-left'>
                                <p class='text-slate-600'>🔥 <b>Article Star :</b> <span class='text-slate-800 font-black uppercase tracking-tight'>${res.article_le_plus_vendu}</span></p>
                                <p class='text-slate-400 border-t border-slate-200/60 pt-2 font-normal italic'>📈 ${res.comparatif_performance_n_1}</p>
                            </div>
                        </div>`;
                } catch(e) { contenu.innerHTML = "<p class='text-rose-500 font-bold text-xs text-center py-4'>❌ Échec de calcul financier.</p>"; }
            }
        </script>
    </body>
    </html>
    """
    return html_content
# =====================================================================
# MODULE 3 : api.py (Version Spéciale Google Pixel - ÉTAPE 7 SUR 7)
# =====================================================================

@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    """Intercepte, calcule la TVA et centralise la vente du magasin."""
    try:
        donnees.caissiere = donnees.caissiere.strip().lower()
        if donnees.prix_ht <= 0 or not 0 < donnees.quantite <= 1000:
            raise HTTPException(status_code=422, detail="Prix ou quantité invalide.")
        connexion = sqlite3.connect(data_base.DB_NAME)
        deja_sync = connexion.execute("SELECT id FROM ventes WHERE reference_locale = ?", (donnees.reference_locale,)).fetchone()
        connexion.close()
        if deja_sync:
            return {"statut": "Déjà synchronisé", "facture_id_cloud": deja_sync[0]}
        regime_tva = int(donnees.applique_tva) if donnees.applique_tva is not None else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        total_ht = donnees.prix_ht * donnees.quantite
        tva_calculee = total_ht * (19.25 / 100) if regime_tva == 1 else 0.0
        total_ttc = total_ht + tva_calculee
        num_facture = data_base.enregistrer_vente_sql(client=donnees.client, article=donnees.article, desc_unique=donnees.description_unique, mnt_ht=total_ht, tva=tva_calculee, ttc=total_ttc, caissiere=donnees.caissiere, reference_locale=donnees.reference_locale)
        return {"statut": "Synchronisé", "facture_id_cloud": num_facture}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    """Calcule le CA et le produit star de la période pour l'écran mobile."""
    try:
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {"chiffre_affaires_ttc": analyse["ca_total"], "article_le_plus_vendu": str(analyse["produit_phare"]).replace("{", "").replace("}", ""), "comparatif_performance_n_1": analyse["message_performance"]}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)])
def api_historique_caissiere(nom_caissiere: str):
    """Extrait l'audit des ventes d'une vendeuse pour l'affichage mobile du patron."""
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes: return {"total_ventes_effectuees": 0, "liste_ventes": []}
        liste_formatee = []
        for v in ventes:
            # 🟢 SÉCURITÉ UNIONS : Extraction propre du tuple SQLite d'origine
            liste_formatee.append({"facture_no": v[0], "client": v[1], "article": str(v[2]).replace("{", "").replace("}", ""), "montant_ttc": f"{v[3]} FCFA", "date": v[4], "heure": v[5]})
        return {"total_ventes_effectuees": len(liste_formatee), "liste_ventes": liste_formatee}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

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
            rapport_stock.append({"article_modele": string_modele, "quantite_restante": l[1], "ventes_totales": l[2], "seuil_alerte_applique": seuil, "statut_commande": etat_alerte})
        return {"inventaire_magasin": rapport_stock}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/employes/liste", dependencies=[Depends(verifier_cle_api)])
def api_liste_des_employes():
    """Extrait la liste unique des caissières enregistrées pour alimenter le smartphone du patron."""
    try:
        liste_employes = data_base.recuperer_liste_tous_employes()
        if not liste_employes: return {"employes": ["caissiere1", "caissiere2"]}
        return {"employes": [str(emp).strip().lower() for emp in liste_employes]}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
