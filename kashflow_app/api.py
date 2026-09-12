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


# =====================================================================
# MODULE 3 : api.py (Version Premium Maquette Serge - ÉTAPE 1 SUR 3)
# =====================================================================

@app.get("/", response_class=HTMLResponse)
def page_accueil_supervision_mobile():
    """Renvoie l'application web mobile du gérant calquée à 100% sur les maquettes de Serge."""
    nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW ENTREPRISE"
    
    # 🎨 REPRODUCTION FIDÈLE DE LA MAQUETTE 1 : Fond gris-bleu clair (#f3f7fa)
    html_content = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Supervision - {nom_boutique}</title>
        <!-- Chargement sécurisé de Tailwind et FontAwesome pour les icônes de tes maquettes -->
        <script src="https://jsdelivr.net"></script>
        <link rel="stylesheet" href="https://cloudflare.com">
    </head>
    <body class="bg-[#f4f7fa] font-sans text-slate-800 pb-12 antialiased">
        
        <!-- En-tête de la Maquette 1 : Titre en minuscules et cloche d'alerte à droite -->
        <div class="max-w-md mx-auto px-6 py-6 flex justify-between items-center bg-transparent mt-2">
            <h1 class="text-2xl font-black tracking-tight text-slate-800 flex items-center gap-1" style="font-family: 'Helvetica', sans-serif;">
                {nom_boutique.lower()}
            </h1>
            
            <!-- 🔔 LA CLOCHE MINIATURISÉE DE LA MAQUETTE 1 -->
            <div class="relative cursor-pointer bg-white p-2.5 rounded-xl border border-slate-100 shadow-xs active:scale-95 transition-transform" onclick="ouvrirAlerteStocks()">
                <!-- Badge numérique avec clignotement doux (animate-pulse) -->
                <div id="badge-cloche" class="hidden absolute -top-1.5 -right-1.5 bg-rose-600 text-white font-black text-4xs w-4.5 h-4.5 rounded-full flex items-center justify-center shadow-md z-10 animate-pulse">0</div>
                <div id="icone-cloche" class="text-lg filter grayscale opacity-30 transition-all duration-300">🔔</div>
            </div>
        </div>

        <div class="max-w-md mx-auto px-5 space-y-5">
            <!-- Grille des Boutons : État des Stocks et Chiffre d'Affaires de la Maquette 1 -->
            <div class="grid grid-cols-2 gap-4">
                <button onclick="chargerStocks()" class="bg-white p-4 rounded-2xl border border-slate-100 text-center shadow-xs active:scale-95 transition-transform cursor-pointer">
                    <div class="text-2xl mb-1 text-slate-700">📦</div>
                    <span class="text-xs font-bold text-slate-700 tracking-tight">État des Stocks</span>
                </button>

                <button onclick="chargerStatistiques()" class="bg-white p-4 rounded-2xl border border-slate-100 text-center shadow-xs active:scale-95 transition-transform cursor-pointer">
                    <div class="text-2xl mb-1 text-slate-700">📊</div>
                    <span class="text-xs font-bold text-slate-700 tracking-tight">Chiffre d'Affaires</span>
                </button>
            </div>

            <!-- 📋 LE GRAND PANNEAU DU REGISTRE GÉNÉRAL DE LA MAQUETTE 1 -->
            <div class="bg-white rounded-3xl border border-slate-100 shadow-sm overflow-hidden p-5 text-center">
                <div class="flex flex-col items-center py-2">
                    <div class="text-3xl mb-3 text-slate-700">📋</div>
                    <h3 class="text-base font-black text-slate-800 tracking-tight">Registre Général</h3>
                    <p class="text-xxs text-slate-400 mt-1 max-w-xs leading-relaxed">Transactions de la boutique par caissière</p>
                    <div class="text-slate-800 font-black text-sm mt-4 select-none animate-bounce">&gt;</div>
                </div>
                
                <!-- Zone de sélection tactile immédiate : junior, nathan... -->
                <div class="border-t border-slate-50 mt-4 pt-4 text-left">
                    <p class="text-4xs font-bold text-slate-400 tracking-wider uppercase mb-3">Sélectionnez une caissière à auditer :</p>
                    <div id="liste-boutons-caissieres" class="flex flex-wrap gap-2.5">
                        <!-- Les macarons élégants s'injectent ici automatiquement en JS -->
                    </div>
                </div>
            </div>

            <!-- ZONE D'AFFICHAGE ET CONTENEUR DE LA DEUXIÈME MAQUETTE (CACHÉ AU DÉPART) -->
            <div id="zone-affichage" class="hidden transition-all duration-300">
                <div class="flex justify-end mb-2 px-2">
                    <span onclick="fermerZone()" class="bg-white text-slate-400 border border-slate-100 font-bold px-3 py-1 rounded-xl text-xs cursor-pointer shadow-xs active:bg-slate-50 transition-colors">Fermer ×</span>
                </div>
                <div id="contenu-section" class="w-full"></div>
            </div>
        </div>
    """
# =====================================================================
# MODULE 3 : api.py (Version Premium Maquette Serge - ÉTAPE 2 SUR 3)
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
                        cloche.className = "text-lg filter-none opacity-100";
                        badge.innerText = nombreAlertes;
                        badge.classList.remove('hidden');
                    } else {
                        cloche.className = "text-lg filter grayscale opacity-30";
                        badge.classList.add('hidden');
                    }
                } catch(e) { console.error("Erreur check cloche:", e); }
            }

            function ouvrirAlerteStocks() {
                const articlesEnAlerte = listeStocksGlobaux.filter(i => i.quantite_restante <= i.seuil_alerte_applique);
                const el = document.getElementById('contenu-section');
                
                // On prépare le conteneur visuel épuré
                document.getElementById('zone-affichage').style.display = 'block';
                el.innerHTML = "";
                
                if(articlesEnAlerte.length === 0) {
                    el.innerHTML = "<div class='bg-white rounded-3xl p-5 border border-slate-100 shadow-sm text-center font-bold text-emerald-600 text-xs'>🟢 Aucun produit en seuil critique. Tous les stocks sont confortables !</div>";
                    return;
                }
                
                let html = "<div class='bg-white rounded-3xl p-5 border border-slate-100 shadow-sm space-y-3'><h3 class='text-xs font-black text-slate-800 uppercase tracking-wide mb-2'>🚨 STOCKS CRITIQUES</h3>";
                articlesEnAlerte.forEach(i => {
                    html += `<div class='bg-rose-50 border border-rose-100 text-rose-900 rounded-xl p-3 flex justify-between items-center font-bold text-xxs'>
                        <div>⚠️ ${i.article_modele.toUpperCase()}</div>
                        <div class='text-right text-rose-700'>Reste : ${i.quantite_restante} pcs</div>
                    </div>`;
                });
                html += "</div>";
                el.innerHTML = html;
            }

            // --- 📋 MACARONS TACTILES DE LA MAQUETTE 1 ---
            async function chargerProfilsCaissieresTactiles() {
                const conteneur = document.getElementById('liste-boutons-caissieres');
                try {
                    const r = await fetch('/employes/liste', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    conteneur.innerHTML = "";
                    res.employes.forEach(emp => {
                        const bouton = document.createElement('button');
                        // Stylisation grise et blanche très propre des macarons
                        bouton.className = "bg-[#f8fafc] border border-slate-200/80 text-slate-700 text-xxs font-extrabold px-3.5 py-2 rounded-xl shadow-3xs active:bg-indigo-950 active:text-white cursor-pointer transition-all uppercase tracking-wide";
                        bouton.innerText = emp;
                        bouton.onclick = () => chargerHistoriqueCaissiereDirect(emp);
                        conteneur.appendChild(bouton);
                    });
                } catch(e) { conteneur.innerHTML = "<span class='text-rose-500 font-bold text-4xs'>Échec de liaison employés.</span>"; }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Premium Maquette Serge - ÉTAPE 3.1 SUR 2)
# =====================================================================

    html_content += """
            // --- 📱 REPRODUCTION INTELLIGENTE ET INTERACTIVE DE TA DEUXIÈME MAQUETTE ---
            async function chargerHistoriqueCaissiereDirect(caissiere) {
                const el = document.getElementById('contenu-section');
                document.getElementById('zone-affichage').style.display = 'block';
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Calcul des transactions...</p>";

                try {
                    const r = await fetch(`/ventes/caissiere/${encodeURIComponent(caissiere)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    
                    if(res.total_ventes_effectuees === 0) {
                        el.innerHTML = `
                            <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-md">
                                <div class="w-full bg-[#1e3a8a] text-white rounded-xl p-3.5 flex items-center gap-3 shadow-md mb-2">
                                    <span class="text-xl">📋</span>
                                    <div class="text-left font-black tracking-wider text-sm uppercase">DOSSIER FACTURES :<br><span class="text-emerald-400 font-extrabold text-base">${caissiere}</span></div>
                                </div>
                                <div class="bg-[#f0f4f8] border border-slate-200 text-slate-700 rounded-lg p-2.5 text-center font-bold text-xxs">
                                    Tiroir-Caisse : 0 facture(s)
                                </div>
                            </div>`;
                        return;
                    }

                    // 1. Calcul du Chiffre d'Affaires de cette vendeuse actualisé au centime près
                    let cumulCA = 0.0;
                    res.liste_ventes.forEach(v => {
                        const mnt = parseFloat(String(v.montant_ttc).replace(/[^0-9.]/g, ''));
                        if(!isNaN(mnt)) cumulCA += mnt;
                    });

                    // 2. Dessin du haut de ton dossier de factures de ton dessin
                    let html = `
                    <div class="bg-white rounded-3xl p-5 border border-slate-100 shadow-md space-y-4">
                        
                        <!-- Le bandeau bleu nuit de ta maquette 2 -->
                        <div class="w-full bg-[#1c355e] text-white rounded-xl p-3.5 flex items-center gap-3 shadow-md">
                            <span class="text-xl">📋</span>
                            <div class="text-left font-black tracking-wider text-sm uppercase leading-tight">DOSSIER FACTURES :<br><span class="text-white font-extrabold text-base">${caissiere.toUpperCase()}</span></div>
                        </div>
                        
                        <!-- La barre Tiroir-Caisse avec mise à jour du CA en direct -->
                        <div class="bg-[#e4effb] border border-[#cbdff4] text-[#1c355e] rounded-lg p-2.5 text-left font-bold text-xs flex justify-between items-center shadow-3xs">
                            <span>Tiroir-Caisse : ${res.total_ventes_effectuees} facture(s)</span>
                        </div>
                        
                        <div class="space-y-4">`;
                    
                    // 3. Dessin des cartes de factures (Ton encadré beige avec la roue dentée)
                    res.liste_ventes.forEach(v => {
                        html += `
                        <div class="bg-[#faf6f0] border border-[#ebdccf] rounded-2xl p-4 shadow-3xs relative">
                            <!-- La petite roue dentée d'ingénierie de ton dessin -->
                            <div class="absolute top-4 right-4 text-slate-400 text-base"><i class="fa-solid fa-gear opacity-60"></i></div>
                            
                            <h4 class="text-base font-black text-slate-800 tracking-tight">Facture #00${v.facture_no}</h4>
                            
                            <div class="border-t border-dashed border-slate-300/60 my-2 pt-2">
                                <p class="text-4xs font-bold text-slate-400 uppercase tracking-wider">Détails du Client</p>
                                <p class="text-xxs font-extrabold text-slate-700 flex items-center gap-1.5 mt-0.5"><i class="fa-solid fa-user text-slate-400/80"></i> Client : ${v.client.toUpperCase()}</p>
                            </div>
                            
                            <div class="border-t border-dashed border-slate-300/60 my-2 pt-2">
                                <p class="text-4xs font-bold text-slate-400 uppercase tracking-wider">Détails de la Transaction</p>
                                <p class="text-xxs font-extrabold text-slate-700 flex items-center gap-1.5 mt-0.5"><i class="fa-solid fa-clock-rotate-left text-slate-400/80"></i> ${v.date} à ${v.heure}</p>
                            </div>
                            
                            <!-- Le montant en gros bleu centré de ta maquette -->
                            <div class="bg-white border border-[#e2e8f0] rounded-xl p-3 my-2 text-center shadow-3xs">
                                <span class="text-lg font-black text-[#1c355e] tracking-tight">${v.montant_ttc}</span>
                            </div>
                            
                            <div class="mt-2">
                                <p class="text-4xs font-bold text-slate-400 uppercase tracking-wider">Produit</p>
                                <p class="text-xxs font-medium text-slate-600 mt-0.5">${v.article}</p>
                            </div>
                        </div>`;
                    });
                    
                    html += "</div></div>";
                    el.innerHTML = html;
                } catch(e) { el.innerHTML = "<div class='bg-white rounded-3xl p-5 border border-slate-100 shadow-sm text-center text-rose-500 font-bold'>❌ Échec de chargement du dossier caissière.</div>"; }
            }
    """
# =====================================================================
# MODULE 3 : api.py (Version Premium Maquette Serge - ÉTAPE 3.2 SUR 2)
# =====================================================================

    html_content += """
            async function chargerStocks() {
                const el = document.getElementById('contenu-section');
                document.getElementById('zone-affichage').style.display = 'block';
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Lecture du stock central...</p>";
                try {
                    const r = await fetch('/stocks/etat', { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    let html = "<div class='bg-white rounded-3xl p-5 border border-slate-100 shadow-sm'><h3 class='text-xs font-black text-slate-800 uppercase tracking-wide mb-3'>📦 INVENTAIRE</h3><table style='width:100%; text-align:left; border-collapse:collapse;'><thead><tr style='color:#94a3b8; font-size:0.75rem; border-bottom:1px solid #e2e8f0;'><th style='padding:0.5rem 0;'>Article</th><th style='text-align:center;'>Reste</th><th style='text-align:right;'>Statut</th></tr></thead><tbody>";
                    res.inventaire_magasin.forEach(i => {
                        const color = i.quantite_restante <= i.seuil_alerte_applique ? 'color:#b91c1c; background:#fee2e2;' : 'color:#047857; background:#dcfce7;';
                        html += `<tr style='border-bottom:1px solid #f1f5f9;'>
                            <td style='padding:0.75rem 0; font-weight:bold; color:#334155;'>${i.article_modele}</td>
                            <td style='text-align:center; font-weight:900;'>${i.quantite_restante} pcs</td>
                            <td style='text-align:right;'><span style='padding:0.25rem 0.5rem; border-radius:9999px; font-size:0.65rem; font-weight:bold; ${color}'>${i.statut_commande}</span></td>
                        </tr>`;
                    });
                    html += "</tbody></table></div>"; el.innerHTML = html;
                } catch(e) { el.innerHTML = "<p style='color:#ef4444;'>❌ Erreur réseau.</p>"; }
            }

            async function chargerStatistiques() {
                const el = document.getElementById('contenu-section');
                document.getElementById('zone-affichage').style.display = 'block';
                let cible = prompt("Tapez la date au format J/M/AAAA (ex: 12/9/2026) :");
                if(!cible) return;
                el.innerHTML = "<p style='text-align:center; color:#94a3b8; padding:1rem;'>Calcul...</p>";
                try {
                    const r = await fetch(`/ventes/statistiques?temporalite=JOUR&cible=${encodeURIComponent(cible)}`, { headers: { 'X-API-Key': API_KEY } });
                    const res = await r.json();
                    el.innerHTML = `
                        <div class='bg-white rounded-3xl p-5 border border-slate-100 shadow-sm'>
                            <div style='background:#dcfce7; border:1px solid #bbf7d0; border-radius:0.75rem; padding:1rem; text-align:center; color:#14532d;'>
                                <p style='margin:0; font-size:0.75rem; font-weight:bold;'>Chiffre d'Affaires du ${cible}</p>
                                <p style='margin:0.25rem 0 0 0; font-size:1.5rem; font-weight:900;'>${res.chiffre_affaires_ttc} FCFA</p>
                            </div>
                            <div style='background:#f8fafc; border:1px solid #e2e8f0; border-radius:0.75rem; padding:0.75rem; font-size:0.75rem; margin-top:1rem;'>
                                <p>🔥 <b>Article Star :</b> ${res.article_le_plus_vendu}</p>
                                <p style='border-top:1px solid #e2e8f0; margin-top:0.5rem; pt-2; font-style:italic;'>📈 ${res.comparatif_performance_n_1}</p>
                            </div>
                        </div>`;
                } catch(e) { el.innerHTML = "<p style='color:#ef4444;'>❌ Erreur de calcul.</p>"; }
            }
        </script>
    </body>
    </html>
    """
    return html_content

# =====================================================================
# LES ROUTES EN PYTHON CI-DESSOUS RESTENT IDENTIQUES À TON CODE D'ORIGINE
# =====================================================================
@app.post("/ventes/synchroniser", dependencies=[Depends(verifier_cle_api)])
def api_centraliser_vente(donnees: VenteSchemaReseau):
    try:
        donnees.caissiere = donnees.caissiere.strip().lower()
        if donnees.prix_ht <= 0 or not 0 < donnees.quantite <= 1000:
            raise HTTPException(status_code=422, detail="Prix ou quantité invalide.")
        connexion = sqlite3.connect(data_base.DB_NAME)
        deja_sync = connexion.execute("SELECT id FROM ventes WHERE reference_locale = ?", (donnees.reference_locale,)).fetchone()
        connexion.close()
        if deja_sync:
            return {"statut": "Déjà synchronisé", "facture_id_cloud": deja_sync}
        regime_tva = int(donnees.applique_tva) if donnees.applique_tva is not None else data_base.obtenir_regime_tva_employe(donnees.caissiere)
        total_ht = donnees.prix_ht * donnees.quantite
        tva_calculee = total_ht * (19.25 / 100) if regime_tva == 1 else 0.0
        total_ttc = total_ht + tva_calculee
        num_facture = data_base.enregistrer_vente_sql(client=donnees.client, article=donnees.article, desc_unique=donnees.description_unique, mnt_ht=total_ht, tva=tva_calculee, ttc=total_ttc, caissiere=donnees.caissiere, reference_locale=donnees.reference_locale)
        return {"statut": "Synchronisé", "facture_id_cloud": num_facture}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ventes/statistiques", dependencies=[Depends(verifier_cle_api)])
def api_obtenir_statistiques(temporalite: str, cible: str):
    try:
        analyse = data_base.extraire_statistiques_avancees(temporalite, cible)
        return {"chiffre_affaires_ttc": analyse["ca_total"], "article_le_plus_vendu": str(analyse["produit_phare"]).replace("{", "").replace("}", ""), "comparatif_performance_n_1": analyse["message_performance"]}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/ventes/caissiere/{nom_caissiere}", dependencies=[Depends(verifier_cle_api)])
def api_historique_caissiere(nom_caissiere: str):
    try:
        ventes = data_base.recuperer_ventes_par_caissiere(nom_caissiere)
        if not ventes: return {"total_ventes_effectuees": 0, "liste_ventes": []}
        liste_formatee = []
        for v in ventes:
            liste_formatee.append({"facture_no": v[0], "client": v[1], "article": str(v[2]).replace("{", "").replace("}", ""), "montant_ttc": f"{v[3]} FCFA", "date": v[4], "heure": v[5]})
        return {"total_ventes_effectuees": len(liste_formatee), "liste_ventes": liste_formatee}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/etat", dependencies=[Depends(verifier_cle_api)])
def api_consulter_stocks_cloud():
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
    try:
        liste_employes = data_base.recuperer_liste_tous_employes()
        if not liste_employes: return {"employes": ["caissiere1", "caissiere2"]}
        return {"employes": [str(emp).strip().lower() for emp in liste_employes]}
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))
