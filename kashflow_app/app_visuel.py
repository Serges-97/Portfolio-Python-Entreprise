# =====================================================================
# MODULE 4 : app_visuel.py (Version 5.5 Pro - PARTIE 1 SUR 5)
# =====================================================================
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, ttk
import sqlite3
import logging
import os
import threading
import uuid
from datetime import datetime
import requests
import data_base
import operation

# Lancement des configurations SQLite d'usine au démarrage du logiciel
data_base.initialisation_systeme()

# Variables globales de contrôle des privilèges et sécurité constructeur
SESSION_UTILISATEUR = "caissier"
NOM_CAISSIERE_ACTIVE = "Anonyme"
NOM_BOUTIQUE_FIXE = "KASHFLOW_MANAGER"
CLE_MASTER_SERGE = "KASHFLOW-RECOVERY-2026"
# FENETRE_PRINCIPALE_LOGIN = None  # Référence à la fenêtre de login principale
# URL_API_KASHFLOW = os.environ.get("KASHFLOW_API_URL", "").strip().rstrip("/")
# CLE_API_KASHFLOW = os.environ.get("KASHFLOW_API_KEY", "").strip()

# =====================================================================
# 🔑 CHARGEMENT DYNAMIQUE DE LA CONFIGURATION RÉSEAU (SANS RECOMPILER)
# =====================================================================
URL_API_KASHFLOW = "http://127.0.0.1:8000" # Adresse locale par défaut de secours
CLE_API_KASHFLOW = "KASHFLOW_KEY_DEFAUT"

def charger_configuration_externe():
    """Lit le fichier config.txt sur le bureau pour adapter le logiciel au client."""
    global URL_API_KASHFLOW, CLE_API_KASHFLOW
    dossier_prog = os.path.dirname(os.path.abspath(__file__))
    fichier_config = os.path.join(dossier_prog, "config.txt")
    
    # Si le fichier n'existe pas (premier démarrage chez le client), on le crée proprement
    if not os.path.exists(fichier_config):
        with open(fichier_config, "w", encoding="utf-8") as f:
            f.write("# CONFIGURATION RESEAU KASHFLOW MANAGER\n")
            f.write("URL_API=http://127.0.0.1:8000\n")
            f.write("CLE_API=MON_CODE_SECRET_CLIENT\n")
        return

    # Si le fichier existe, on lit l'adresse IP ou le lien Render gravé dedans
    try:
        with open(fichier_config, "r", encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip().startswith("#") or "=" not in ligne:
                    continue
                cle, valeur = ligne.strip().split("=", 1)
                if cle.strip() == "URL_API":
                    URL_API_KASHFLOW = valeur.strip().rstrip("/")
                elif cle.strip() == "CLE_API":
                    CLE_API_KASHFLOW = valeur.strip()
    except Exception as e:
        print(f"[ERREUR CONFIG CONFIG.TXT] : {e}")

# Exécution immédiate du chargeur au démarrage de la caisse
charger_configuration_externe()


def normaliser_nom_caissiere(valeur):
    """Normalise un identifiant de caissière pour éviter les erreurs de typage ou d'espaces."""
    if valeur is None:
        return "anonyme"
    return str(valeur).strip().lower()


def synchroniser_vente_cloud(reference_locale, donnees):
    """Envoie une vente au Cloud ou la conserve dans la file locale."""
    data_base.mettre_en_attente_synchronisation(reference_locale, donnees)
    synchroniser_file_cloud()


def synchroniser_file_cloud():
    """Réessaie les ventes en attente sans bloquer l'interface Tkinter."""
    if not URL_API_KASHFLOW or not CLE_API_KASHFLOW:
        return

    for id_synchronisation, reference_locale, donnees in data_base.recuperer_synchronisations_en_attente():
        try:
            reponse = requests.post(
                f"{URL_API_KASHFLOW}/ventes/synchroniser",
                json=donnees,
                headers={"X-API-Key": CLE_API_KASHFLOW},
                timeout=8,
            )
            reponse.raise_for_status()
            data_base.marquer_synchronisation_reussie(id_synchronisation, reference_locale)
            logging.info("Vente synchronisée dans le Cloud: %s", reference_locale)
        except requests.RequestException as erreur:
            data_base.enregistrer_erreur_synchronisation(id_synchronisation, erreur)
            logging.warning("Synchronisation différée: %s", erreur)
            break
# =====================================================================
# MODULE 4 : app_visuel.py (Version 5.5 Pro - PARTIE 2 SUR 5)
# =====================================================================

# =====================================================================
# 📦 PANNEAU GESTION DE L'INVENTAIRE / STOCKS (EXCLUSIVITÉ GÉRANT)
# =====================================================================
def ouvrir_panneau_stock():
    """Permet au gérant d'ajouter de nouveaux modèles et de suivre le stock dispo."""
    if SESSION_UTILISATEUR != "gerant":
        messagebox.showerror("Accès Interdit", "Seul le gérant peut modifier l'inventaire.")
        return

    def action_ajouter_quantite(modele):
        """Ajoute une livraison à un article déjà présent dans l'inventaire."""
        qte = simpledialog.askinteger(
            "Réapprovisionnement",
            f"Quantité à ajouter pour « {modele} » :",
            parent=admin_stock,
            minvalue=1,
        )
        if qte is None:
            return

        connexion = sqlite3.connect(data_base.DB_NAME)
        connexion.execute(
            "UPDATE stocks SET quantite_dispo = quantite_dispo + ? WHERE modele = ?",
            (qte, modele),
        )
        connexion.commit()
        connexion.close()
        rafraichir_tableau()
        messagebox.showinfo("Inventaire mis à jour", f"{qte} unité(s) ajoutée(s) à « {modele} ».")

    def rafraichir_tableau():
        """Rafraîchit l'affichage du tableau des stocks."""
        for widget in cadre_produits.winfo_children():
            widget.destroy()
        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("SELECT modele, quantite_dispo FROM stocks")
        lignes = curseur.fetchall()
        connexion.close()

        for modele, quantite in lignes:
            ligne = tk.Frame(cadre_produits, bg="white", bd=1, relief=tk.SOLID)
            ligne.pack(fill=tk.X, pady=2)
            tk.Label(ligne, text=str(modele), bg="white", anchor=tk.W, width=32).pack(side=tk.LEFT, padx=8, pady=6)
            tk.Label(ligne, text=f"{quantite} pcs", bg="white", width=12).pack(side=tk.LEFT, padx=4)
            tk.Button(
                ligne,
                text="➕ Ajouter quantité",
                bg="#0f766e",
                fg="white",
                font=("Helvetica", 8, "bold"),
                command=lambda article=modele: action_ajouter_quantite(article),
            ).pack(side=tk.RIGHT, padx=8, pady=3)

    def action_ajouter_modele():
        modele = entree_modele.get().strip()
        qte_texte = entree_qte_stock.get().strip()
        
        if not modele or not qte_texte:
            messagebox.showwarning("Champs vides", "Veuillez remplir le modèle et la quantité.")
            return
            
        try:
            qte = int(qte_texte)
            if qte <= 0: raise ValueError
            
            connexion = sqlite3.connect(data_base.DB_NAME)
            curseur = connexion.cursor()
            curseur.execute("""
            INSERT INTO stocks (modele, quantite_dispo) VALUES (?, ?)
            ON CONFLICT(modele) DO UPDATE SET quantite_dispo = quantite_dispo + ?
            """, (modele, qte, qte))
            connexion.commit()
            connexion.close()
            
            messagebox.showinfo("Inventaire Mis à jour", f"Stock de '{modele}' augmenté de +{qte} unités !")
            entree_modele.delete(0, tk.END)
            entree_qte_stock.delete(0, tk.END)
            
            rafraichir_tableau()
            entree_modele.focus()
            
        except ValueError:
            messagebox.showerror("Erreur de type", "La quantité doit être un nombre entier supérieur à 0.")

    def action_supprimer_modele():
        modele = entree_modele.get().strip()
        if not modele:
            messagebox.showwarning("Article manquant", "Saisissez le nom de l'article à supprimer.")
            return

        confirmation = messagebox.askyesno(
            "Confirmer la suppression",
            f"Voulez-vous vraiment retirer « {modele} » de l'inventaire ?\n\n"
            "L'article ne sera plus proposé lors des ventes. Les ventes historiques seront conservées.",
            parent=admin_stock,
        )
        if not confirmation:
            return

        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("DELETE FROM stocks WHERE modele = ?", (modele,))
        article_supprime = curseur.rowcount > 0
        connexion.commit()
        connexion.close()

        if article_supprime:
            messagebox.showinfo("Article supprimé", f"« {modele} » a été retiré de l'inventaire.", parent=admin_stock)
            entree_modele.delete(0, tk.END)
            entree_qte_stock.delete(0, tk.END)
            rafraichir_tableau()
            entree_modele.focus()
        else:
            messagebox.showwarning("Article introuvable", f"Aucun article nommé « {modele} » n'a été trouvé.", parent=admin_stock)

    admin_stock = Toplevel(FENETRE_PRINCIPALE_LOGIN)
    admin_stock.title("📦 Gestion des Stocks - Panel Gérant")
    admin_stock.geometry("500x480")
    admin_stock.configure(bg="#f8fafc")
    admin_stock.grab_set()

    tk.Label(admin_stock, text="INVENTAIRE DES PRODUITS EN STOCK", font=("Helvetica", 11, "bold"), bg="#0f766e", fg="white", pady=8).pack(fill=tk.X)

    cadre_tableau = tk.Frame(admin_stock, bg="#f8fafc")
    cadre_tableau.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    cadre_entetes = tk.Frame(cadre_tableau, bg="#e2e8f0")
    cadre_entetes.pack(fill=tk.X)
    tk.Label(cadre_entetes, text="ARTICLE", bg="#e2e8f0", font=("Helvetica", 9, "bold"), width=32, anchor=tk.W).pack(side=tk.LEFT, padx=8, pady=5)
    tk.Label(cadre_entetes, text="QUANTITÉ", bg="#e2e8f0", font=("Helvetica", 9, "bold"), width=12).pack(side=tk.LEFT, padx=4, pady=5)
    tk.Label(cadre_entetes, text="ACTION", bg="#e2e8f0", font=("Helvetica", 9, "bold")).pack(side=tk.RIGHT, padx=45, pady=5)

    cadre_produits = tk.Frame(cadre_tableau, bg="#f8fafc")
    cadre_produits.pack(fill=tk.BOTH, expand=True)

    rafraichir_tableau()

    cadre_ajout = tk.LabelFrame(admin_stock, text="Approvisionner / Ajouter un Nouvel Article", font=("Helvetica", 9, "bold"), bg="#f8fafc", padx=10, pady=10)
    cadre_ajout.pack(fill=tk.X, padx=15, pady=15)

    tk.Label(cadre_ajout, text="Nom de l'article (ex: Écran Plasma LG, Frigo) :", bg="#f8fafc").pack(anchor=tk.W)
    entree_modele = tk.Entry(cadre_ajout, font=("Helvetica", 10))
    entree_modele.pack(fill=tk.X, pady=4)

    tk.Label(cadre_ajout, text="Quantité reçue du fournisseur :", bg="#f8fafc").pack(anchor=tk.W)
    entree_qte_stock = tk.Entry(cadre_ajout, font=("Helvetica", 10))
    entree_qte_stock.pack(fill=tk.X, pady=4)

    # 🚀 NAVIGATION CLAVIER DEMANDÉE : Entrée passe au champ suivant, puis valide
    entree_modele.bind("<Return>", lambda event: entree_qte_stock.focus())
    entree_qte_stock.bind("<Return>", lambda event: action_ajouter_modele())

    cadre_actions = tk.Frame(cadre_ajout, bg="#f8fafc")
    cadre_actions.pack(fill=tk.X, pady=8)
    tk.Button(
        cadre_actions,
        text="📥 CONFIRMER L'AJOUT",
        bg="#0f766e",
        fg="white",
        font=("Helvetica", 9, "bold"),
        command=action_ajouter_modele,
    ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
    tk.Button(
        cadre_actions,
        text="🗑 SUPPRIMER L'ARTICLE",
        bg="#dc2626",
        fg="white",
        font=("Helvetica", 9, "bold"),
        command=action_supprimer_modele,
    ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 0))
# =====================================================================
# MODULE 4 : app_visuel.py (Version 5.5 Pro - PARTIE 3 SUR 5)
# =====================================================================

# --- 3. PANNEAU D'AUDIT COMPTABLE TEMPOREL ET FILTRAGE VISIBLE ---
def ouvrir_panneau_historique():
    """Ouvre l'espace analytique et force l'affichage complet de la grille des ventes."""
    if SESSION_UTILISATEUR != "gerant":
        messagebox.showerror("Accès Interdit", "Seul le gérant a accès aux rapports financiers.")
        return

    def action_charger_statistiques():
        tempo = select_tempo.get()
        cible = entree_cible.get().strip()
        
        if not cible:
            messagebox.showwarning("Critère manquant", "Veuillez entrer une valeur cible (ex: 31-08, 08, 2026).")
            return
            
        statistiques = data_base.extraire_statistiques_avancees(tempo, cible)
        label_ca.config(text=f"CHIFFRE D'AFFAIRES TTC : {statistiques['ca_total']} FCFA", bg="#10b981", fg="white")
        label_top.config(text=f"🔥 Produit Phare sur la période : {statistiques['produit_phare']}")
        label_perf.config(text=statistiques['message_performance'])

    def action_filtrer_par_vendeuse():
        nom_vendeuse = normaliser_nom_caissiere(select_vendeuse.get())
        if not nom_vendeuse or nom_vendeuse == "anonyme":
            messagebox.showwarning("Champ vide", "Veuillez sélectionner une caissière.")
            return
            
        for i in grille_audit.get_children():
            grille_audit.delete(i)
            
        ventes_filtrees = data_base.recuperer_ventes_par_caissiere(nom_vendeuse)
        if not ventes_filtrees:
            messagebox.showinfo("Rapport", f"Aucune vente pour : {nom_vendeuse}")
            return
            
        for v in ventes_filtrees:
            art_propre = str(v[2]).strip()
            grille_audit.insert("", tk.END, values=(v[0], v[1], art_propre, f"{v[3]} FCFA", f"{v[4]} à {v[5]}", nom_vendeuse.upper()))

    def action_afficher_tout_historique():
        for i in grille_audit.get_children():
            grille_audit.delete(i)
        toutes_les_ventes = data_base.recuper_tout_les_ventes()
        for v in toutes_les_ventes:
            art_propre = str(v[2]).strip()
            grille_audit.insert("", tk.END, values=(v[0], v[1], art_propre, f"{v[3]} FCFA", v[4], str(v[5]).upper()))

    audit = Toplevel(FENETRE_PRINCIPALE_LOGIN)
    audit.title("📊 Tableau de Bord Économique")
    audit.geometry("750x650")
    audit.configure(bg="#f8fafc")
    audit.grab_set()

    tk.Label(audit, text="RAPPORT D'AUDIT COMPTABLE ANALYTIQUE", font=("Helvetica", 11, "bold"), bg="#1e293b", fg="white", pady=8).pack(fill=tk.X)

    # Zone du haut : Comparatifs et CA
    cadre_stat = tk.LabelFrame(audit, text="Analyse Temporelle Comparative (N vs N-1)", bg="#f8fafc", padx=10, pady=8)
    cadre_stat.pack(fill=tk.X, padx=15, pady=10)

    tk.Label(cadre_stat, text="Période :", bg="#f8fafc").grid(row=0, column=0, padx=5, sticky=tk.W)
    select_tempo = ttk.Combobox(cadre_stat, values=["JOUR", "MOIS", "ANNEE"], width=10, state="readonly")
    select_tempo.grid(row=0, column=1, padx=5)
    select_tempo.current(0)

    tk.Label(cadre_stat, text="Cible :", bg="#f8fafc").grid(row=0, column=2, padx=5, sticky=tk.W)
    entree_cible = tk.Entry(cadre_stat, width=12, font=("Helvetica", 10), bd=2)
    entree_cible.grid(row=0, column=3, padx=5)

    tk.Button(cadre_stat, text="🔍 ANALYSER", font=("Helvetica", 9, "bold"), bg="#1e293b", fg="white", command=action_charger_statistiques).grid(row=0, column=4, padx=10)

    label_ca = tk.Label(cadre_stat, text="CHIFFRE D'AFFAIRES TTC : 0.00 FCFA", font=("Helvetica", 11, "bold"), bg="#e2e8f0", fg="#1e293b", pady=6)
    label_ca.grid(row=1, column=0, columnspan=5, sticky=tk.EW, pady=6)
    
    label_top = tk.Label(cadre_stat, text="🔥 Produit Phare : Aucun", font=("Helvetica", 10), bg="#f8fafc", fg="#0f766e", anchor=tk.W)
    label_top.grid(row=2, column=0, columnspan=5, sticky=tk.EW, pady=2)
    
    label_perf = tk.Label(cadre_stat, text="📈 En attente d'analyse...", font=("Helvetica", 10, "italic"), bg="#f8fafc", fg="#475569", anchor=tk.W)
    label_perf.grid(row=3, column=0, columnspan=5, sticky=tk.EW, pady=2)

    # Zone du bas : Le registre de la grille enfin visible
    cadre_grille = tk.LabelFrame(audit, text="Registre des transactions et ventes", bg="#f8fafc", padx=10, pady=8)
    cadre_grille.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    cadre_filtre_nom = tk.Frame(cadre_grille, bg="#f8fafc")
    cadre_filtre_nom.pack(fill=tk.X, pady=4)
    
    tk.Label(cadre_filtre_nom, text="Caissière :", bg="#f8fafc").pack(side=tk.LEFT, padx=2)
    
    # 🔑 LISTE DÉROULANTE DES CAISSIÈRES DEMANDÉE : Extraction automatique
    liste_caissieres = data_base.recuperer_liste_tous_employes()
    select_vendeuse = ttk.Combobox(cadre_filtre_nom, values=liste_caissieres, width=18, state="readonly")
    if liste_caissieres:
        select_vendeuse.current(0)
    select_vendeuse.pack(side=tk.LEFT, padx=4)
    
    tk.Button(cadre_filtre_nom, text="🎯 Filtrer", bg="#475569", fg="white", font=("Helvetica", 8, "bold"), command=action_filtrer_par_vendeuse).pack(side=tk.LEFT, padx=4)
    tk.Button(cadre_filtre_nom, text="📋 Afficher Tout", bg="#0284c7", fg="white", font=("Helvetica", 8, "bold"), command=action_afficher_tout_historique).pack(side=tk.RIGHT, padx=4)

    grille_audit = ttk.Treeview(cadre_grille, columns=("ID", "Client", "Article", "Total TTC", "Date/Heure", "Émetteur"), show="headings", height=8)
    grille_audit.heading("ID", text="N°"); grille_audit.heading("Client", text="CLIENT"); grille_audit.heading("Article", text="ARTICLE"); grille_audit.heading("Total TTC", text="NET TTC"); grille_audit.heading("Date/Heure", text="TEMPOREL"); grille_audit.heading("Émetteur", text="CAISSIÈRE")
    
    grille_audit.column("ID", width=40, anchor=tk.CENTER); grille_audit.column("Client", width=110, anchor=tk.W); grille_audit.column("Article", width=140, anchor=tk.W); grille_audit.column("Total TTC", width=110, anchor=tk.CENTER); grille_audit.column("Date/Heure", width=120, anchor=tk.CENTER); grille_audit.column("Émetteur", width=80, anchor=tk.CENTER)
    grille_audit.pack(fill=tk.BOTH, expand=True, pady=5)

    action_afficher_tout_historique()
# =====================================================================
# INTERFACE GRAPHIQUE MULTI-SESSIONS : app_visuel.py v5.5 (PARTIE 4 DE 5)
# =====================================================================

# --- 4. CONFIGURATION ET RAJOUT DU PERSONNEL (EXCLUSIVITÉ GÉRANT) ---
def ouvrir_panneau_administration():
    if SESSION_UTILISATEUR != "gerant":
        messagebox.showerror("Accès Interdit", "Seul le gérant configure le personnel.")
        return

    def action_ajouter_caissier():
        nom = entree_nouveau_nom.get().strip()
        code = entree_nouveau_code.get().strip()
        tva_choix = select_tva_personnel.get()
        applique_tva = 1 if tva_choix == "Oui (Grande Entreprise)" else 0
        
        if not nom or not code:
            messagebox.showwarning("Champs vides", "Remplissez toutes les cases.")
            return
        if data_base.ajouter_nouvel_employe_sql(nom, code, applique_tva):
            messagebox.showinfo("Succès", f"Compte de la caissière '{nom.upper()}' créé !")
            entree_nouveau_nom.delete(0, tk.END)
            entree_nouveau_code.delete(0, tk.END)
        else:
            messagebox.showerror("Erreur", "Identifiant déjà pris.")

    admin = Toplevel(FENETRE_PRINCIPALE_LOGIN)
    admin.title("⚙️ Gestion Personnel")
    admin.geometry("400x380")
    admin.configure(bg="#f8fafc")
    admin.grab_set()

    tk.Label(admin, text="AJOUTER UNE NOUVELLE CAISSIÈRE", font=("Helvetica", 11, "bold"), bg="#475569", fg="white", pady=6).pack(fill=tk.X)
    cadre = tk.Frame(admin, bg="#f8fafc", padx=15, pady=15)
    cadre.pack(fill=tk.BOTH, expand=True)

    tk.Label(cadre, text="Identifiant de la caissière :", bg="#f8fafc").pack(anchor=tk.W)
    entree_nouveau_nom = tk.Entry(cadre, font=("Helvetica", 10))
    entree_nouveau_nom.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Mot de passe caissière :", bg="#f8fafc").pack(anchor=tk.W)
    entree_nouveau_code = tk.Entry(cadre, font=("Helvetica", 10), show="*")
    entree_nouveau_code.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Appliquer la TVA sur ses ventes ?", bg="#f8fafc").pack(anchor=tk.W, pady=2)
    select_tva_personnel = ttk.Combobox(cadre, values=["Oui (Grande Entreprise)", "Non (Petite Boutique)"], state="readonly")
    select_tva_personnel.pack(fill=tk.X, pady=4)
    select_tva_personnel.current(0)

    tk.Button(cadre, text="➕ CRÉER LE COMPTE SÉCURISÉ", bg="#3b82f6", fg="white", font=("Helvetica", 9, "bold"), command=action_ajouter_caissier, pady=6).pack(fill=tk.X, pady=15)
# =====================================================================
# INTERFACE GRAPHIQUE MULTI-SESSIONS : app_visuel.py v5.5 (BLOC 5A)
# =====================================================================

# --- 5. INTERFACE PRINCIPALE DE FACTURATION / COMPTOIR ---
def ouvrir_comptoir_facturation():
    """Interface de vente principale pour les caissières et le gérant."""
    global SESSION_UTILISATEUR, NOM_CAISSIERE_ACTIVE, NOM_BOUTIQUE_FIXE

    nom_boutique_fixe = (data_base.recuperer_nom_boutique_sql() or NOM_BOUTIQUE_FIXE).upper()
    NOM_BOUTIQUE_FIXE = nom_boutique_fixe

    comptoir = Toplevel(FENETRE_PRINCIPALE_LOGIN)
    comptoir.title(f"💳 KASHFLOW Comptoir - Session {NOM_CAISSIERE_ACTIVE.upper()}")
    comptoir.geometry("480x690")
    comptoir.configure(bg="#f8fafc")
    threading.Thread(target=synchroniser_file_cloud, daemon=True).start()

    def planifier_synchronisation_cloud():
        if comptoir.winfo_exists():
            threading.Thread(target=synchroniser_file_cloud, daemon=True).start()
            comptoir.after(30000, planifier_synchronisation_cloud)

    comptoir.after(30000, planifier_synchronisation_cloud)

    tk.Label(comptoir, text=f"{nom_boutique_fixe} - COMPTOIR DE FACTURATION", font=("Helvetica", 12, "bold"), bg="#0f766e", fg="white", pady=8).pack(fill=tk.X)

    def action_bouton_enregistrer():
        """Enregistre une vente et génère le PDF avec une sécurité totale."""
        caissiere_nom = str(NOM_CAISSIERE_ACTIVE).strip().lower()
        nom_client = entree_client.get().strip()
        smartphone = liste_smartphones.get().strip()
        desc = entree_desc.get().strip()
        prix_txt = entree_prix.get().strip()
        qte_txt = entree_quantite.get().strip()

        if not all([nom_client, smartphone, desc, prix_txt, qte_txt]):
            messagebox.showwarning("Champs incomplets", "Remplissez tous les champs obligatoires.")
            return

        try:
            prix = float(prix_txt)
            qte = int(qte_txt)
            if prix <= 0 or qte <= 0: raise ValueError
        except ValueError:
            messagebox.showerror("Erreur", "Prix et quantité invalides.")
            return

        try:
            verif_stock = data_base.verifier_et_reduire_stock(smartphone, qte)
            if not verif_stock["autorise"]:
                messagebox.showerror("Stock Insuffisant", verif_stock["reason"])
                return

            # 🔑 DIRECTIVE TVA : Le gérant applique à la volée via la case à cocher, la caissière suit son profil
            if SESSION_UTILISATEUR == "gerant":
                applique_tva = 1 if var_tva_directe.get() else 0
            else:
                applique_tva = data_base.obtenir_regime_tva_employe(caissiere_nom)
            
            calcul = operation.calculer_facture_dynamique(prix, qte, applique_tva)
            nom_boutique = data_base.recuperer_nom_boutique_sql() or "KASHFLOW_MANAGER"
            reference_locale = str(uuid.uuid4())
            
            num_facture = data_base.enregistrer_vente_sql(
                nom_client, smartphone, desc,
                calcul["montant_ht"], calcul["valeur_tva"], calcul["total_ttc"],
                caissiere_nom
            )

            if num_facture:
                donnees_cloud = {
                    "client": nom_client,
                    "article": smartphone,
                    "description_unique": desc,
                    "prix_ht": prix,
                    "quantite": qte,
                    "caissiere": caissiere_nom,
                    "applique_tva_vente": applique_tva
                }
                threading.Thread(target=synchroniser_vente_cloud, args=(reference_locale, donnees_cloud), daemon=True).start()

                succes_pdf = operation.generer_recu_pdf_industriel(
                    nom_boutique, num_facture, nom_client, smartphone, desc, qte,
                    calcul["montant_ht"], calcul["valeur_tva"], calcul["total_ttc"],
                    caissiere_nom
                )

                if succes_pdf:
                    if verif_stock["alerte_patron"]:
                        messagebox.showwarning("Alerte Stock", f"⚠️ Stock critique pour '{smartphone}' ! Reste: {verif_stock['restant']} pcs (Seuil: {verif_stock['seuil']})")
                    messagebox.showinfo("Succès", f"✅ Vente #{num_facture} émise avec succès !\nNom caissière : {caissiere_nom.upper()}")
                else:
                    messagebox.showerror("Erreur PDF", "Vente enregistrée mais erreur de génération du PDF.")

                entree_client.delete(0, tk.END)
                entree_desc.delete(0, tk.END)
                entree_prix.delete(0, tk.END)
                entree_quantite.delete(0, tk.END)
                entree_client.focus()
        except Exception as e:
            messagebox.showerror("Erreur Système", f"Une erreur s'est produite : {str(e)}")

    cadre = tk.Frame(comptoir, bg="#f8fafc", padx=15, pady=10)
    cadre.pack(fill=tk.BOTH, expand=True)

    tk.Label(cadre, text="Client :", bg="#f8fafc", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
    entree_client = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_client.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Sélectionner l'Article :", bg="#f8fafc", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
    liste_smartphones = ttk.Combobox(cadre, state="readonly", font=("Helvetica", 10))
    
    connexion = sqlite3.connect(data_base.DB_NAME)
    curseur = connexion.cursor()
    curseur.execute("SELECT modele FROM stocks WHERE quantite_dispo > 0")
    modeles = [str(row[0]).strip() for row in curseur.fetchall()]
    connexion.close()
    
    liste_smartphones["values"] = modeles
    if modeles: liste_smartphones.current(0)
    liste_smartphones.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Description unique (N° IMEI, Série, SAV) :", bg="#f8fafc", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
    entree_desc = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_desc.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Prix Unitaire HT (FCFA) :", bg="#f8fafc", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
    entree_prix = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_prix.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Quantité :", bg="#f8fafc", font=("Helvetica", 10, "bold")).pack(anchor=tk.W)
# =====================================================================
# INTERFACE GRAPHIQUE MULTI-SESSIONS : app_visuel.py v5.5 (BLOC 5B - 1/2)
# =====================================================================

    entree_quantite = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_quantite.pack(fill=tk.X, pady=4)

    # 🔑 CASE À COCHER TVA EN DIRECT AU COMPTOIR POUR LE GÉRANT
    var_tva_directe = tk.BooleanVar(value=True)
    if SESSION_UTILISATEUR == "gerant":
        case_tva = tk.Checkbutton(cadre, text="Facturer la TVA (19.25%) sur cette vente", variable=var_tva_directe, bg="#f8fafc", font=("Helvetica", 10, "bold"), fg="#1e3a8a")
        case_tva.pack(anchor=tk.W, pady=6)

    # 🚀 CONFIGURATION DE LA NAVIGATION RAPIDE (Touche Entrée)
    entree_client.bind("<Return>", lambda event: liste_smartphones.focus())
    liste_smartphones.bind("<Return>", lambda event: entree_desc.focus())
    entree_desc.bind("<Return>", lambda event: entree_prix.focus())
    entree_prix.bind("<Return>", lambda event: entree_quantite.focus())
    entree_quantite.bind("<Return>", lambda event: action_bouton_enregistrer())

    tk.Button(cadre, text="🛒 VALIDER LA VENTE & ÉMETTRE LE PDF", font=("Helvetica", 11, "bold"), bg="#10b981", fg="white", command=action_bouton_enregistrer, pady=10).pack(fill=tk.X, pady=15)

    # Menu de bas de page adaptatif selon la session
    tk.Label(comptoir, text="PANNEAU DE CONTROLE SÉCURISÉ", font=("Helvetica", 10, "bold"), bg="#e2e8f0", fg="#1e293b", pady=4).pack(fill=tk.X)
    cadre_menu = tk.Frame(comptoir, bg="#e2e8f0", padx=10, pady=8)
    cadre_menu.pack(fill=tk.X)

    if SESSION_UTILISATEUR == "gerant":
        tk.Button(cadre_menu, text="📦 Stocks", bg="#0284c7", fg="white", font=("Helvetica", 9, "bold"), command=ouvrir_panneau_stock).pack(side=tk.LEFT, padx=3)
        tk.Button(cadre_menu, text="📊 Audits", bg="#7c3aed", fg="white", font=("Helvetica", 9, "bold"), command=ouvrir_panneau_historique).pack(side=tk.LEFT, padx=3)
        tk.Button(cadre_menu, text="⚙️ Profils", bg="#ea580c", fg="white", font=("Helvetica", 9, "bold"), command=ouvrir_panneau_administration).pack(side=tk.LEFT, padx=3)
    else:
        # 🔑 ONGLÈT HISTORIQUE TEMPOREL PERSONNEL POUR CHAQUE CAISSIÈRE
        tk.Button(cadre_menu, text="📊 MON HISTORIQUE TEMPOREL DE VENTES", bg="#f59e0b", fg="white", font=("Helvetica", 9, "bold"), command=ouvrir_historique_caissiere).pack(side=tk.LEFT, padx=5)
    
    def deconnecter():
        comptoir.destroy()
        FENETRE_PRINCIPALE_LOGIN.deiconify()
        entree_user.delete(0, tk.END)
        entree_password.delete(0, tk.END)
        entree_user.insert(0, "gerant")
        entree_user.focus()
    
    tk.Button(cadre_menu, text="🚪 Quitter", bg="#64748b", fg="white", font=("Helvetica", 9, "bold"), command=deconnecter).pack(side=tk.RIGHT, padx=3)


def ouvrir_historique_caissiere():
    """Fenêtre d'historique personnelle des ventes de la caissière active avec filtrage temporel complet."""
    caissiere_nom = str(NOM_CAISSIERE_ACTIVE).strip().lower()

    historique = Toplevel(FENETRE_PRINCIPALE_LOGIN)
    historique.title(f"📊 Historique de {caissiere_nom.upper()}")
    historique.geometry("750x620")
    historique.configure(bg="#f8fafc")
    historique.grab_set()

    tk.Label(historique, text=f"HISTORIQUE DES VENTES PERSONNEL - {caissiere_nom.upper()}", font=("Helvetica", 11, "bold"), bg="#1e293b", fg="white", pady=8).pack(fill=tk.X)

    cadre_stat = tk.LabelFrame(historique, text="Suivi Temporel de mon Tiroir-Caisse", bg="#f8fafc", padx=10, pady=8)
    cadre_stat.pack(fill=tk.X, padx=15, pady=10)

    tk.Label(cadre_stat, text="Période :", bg="#f8fafc").grid(row=0, column=0, padx=5, sticky=tk.W)
    select_tempo = ttk.Combobox(cadre_stat, values=["JOUR", "MOIS", "ANNEE"], width=10, state="readonly")
    select_tempo.grid(row=0, column=1, padx=5); select_tempo.current(0)

    tk.Label(cadre_stat, text="Cible (ex: 4/9/2026 / 9 / 2026) :", bg="#f8fafc").grid(row=0, column=2, padx=5, sticky=tk.W)
    entree_cible_historique = tk.Entry(cadre_stat, width=15, font=("Helvetica", 10), bd=2)
    entree_cible_historique.grid(row=0, column=3, padx=5)

    def rafraichir_historique_caissiere():
        valeur = entree_cible_historique.get().strip()
        if not valeur:
            messagebox.showwarning("Critère manquant", "Saisissez un critère cible.")
            return

        for item in arbre_historique.get_children(): arbre_historique.delete(item)
        ventes = data_base.recuperer_ventes_par_caissiere(caissiere_nom)
        total_ttc = 0.0

        for v in ventes:
            date_brute = str(v[4]).strip()
            garder = False
            
            if select_tempo.get() == "JOUR":
                if date_brute == valeur: garder = True
            elif select_tempo.get() == "MOIS":
                try:
                    m_db = date_brute.split("/")
                    if int(m_db[1]) == int(valeur): garder = True
                except Exception: pass
            elif select_tempo.get() == "ANNEE":
                if date_brute.endswith(valeur): garder = True

            if garder:
                total_ttc += float(v[3])
                arbre_historique.insert("", tk.END, values=(v[0], v[1], str(v[2]).strip(), f"{v[3]} FCFA", f"{v[4]} à {v[5]}", caissiere_nom.upper()))

        label_total.config(text=f"MON TOTAL COMPTABLE CUMULÉ : {round(total_ttc, 2)} FCFA")

    tk.Button(cadre_stat, text="🔍 FILTRER", bg="#1e293b", fg="white", font=("Helvetica", 9, "bold"), command=rafraichir_historique_caissiere).grid(row=0, column=4, padx=10)

    label_total = tk.Label(cadre_stat, text="MON TOTAL COMPTABLE CUMULÉ : 0.00 FCFA", font=("Helvetica", 11, "bold"), bg="#d1fae5", fg="#065f46", pady=6)
    label_total.grid(row=1, column=0, columnspan=5, sticky=tk.EW, pady=6)

    arbre_historique = ttk.Treeview(historique, columns=("ID", "Client", "Article", "Total TTC", "Date/Heure", "Caissière"), show="headings", height=12)
    arbre_historique.heading("ID", text="N°"); arbre_historique.heading("Client", text="CLIENT"); arbre_historique.heading("Article", text="ARTICLE"); arbre_historique.heading("Total TTC", text="NET TTC"); arbre_historique.heading("Date/Heure", text="TEMPOREL"); arbre_historique.heading("Caissière", text="EMETTEUR")
    arbre_historique.column("ID", width=40, anchor=tk.CENTER); arbre_historique.column("Client", width=120, anchor=tk.W); arbre_historique.column("Article", width=180, anchor=tk.W); arbre_historique.column("Total TTC", width=110, anchor=tk.CENTER); arbre_historique.column("Date/Heure", width=140, anchor=tk.CENTER); arbre_historique.column("Caissière", width=100, anchor=tk.CENTER)
    arbre_historique.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
# =====================================================================
# ÉCRAN DE VERROUILLAGE SÉCURISÉ ET LOGIQUE DE DÉMARRAGE (BLOC 5B - 2/2)
# =====================================================================

def verifier_acces():
    """Valide la session employé et lance l'assistant d'installation en 2 étapes au premier démarrage."""
    global SESSION_UTILISATEUR, NOM_CAISSIERE_ACTIVE
    user = entree_user.get().strip()
    pwd = entree_password.get().strip()

    if not user or not pwd:
        messagebox.showwarning("Champs vides", "Saisissez l'identifiant et le mot de passe.")
        return

    try:
        connexion = sqlite3.connect(data_base.DB_NAME)
        curseur = connexion.cursor()
        curseur.execute("SELECT * FROM employes WHERE identifiant = 'gerant'")
        compte_existe = curseur.fetchone()
        connexion.close()

        # 🔑 L'ASSISTANT D'INSTALLATION D'USINE EN 2 ÉTAPES (NOM BOUTIQUE + CODE PATRON)
        if compte_existe is None:
            nom_magasin = simpledialog.askstring("Installation d'Usine - Étape 1/2", "Bienvenue chez KashFlow Manager !\n\nVeuillez entrer le NOM OFFICIEL de votre entreprise :")
            if not nom_magasin or not nom_magasin.strip():
                messagebox.showwarning("Incomplet", "Le nom de l'entreprise est exigé.")
                return

            creer_code = simpledialog.askstring("Installation d'Usine - Étape 2/2", "Veuillez définir votre MOT DE PASSE secret Administrateur :")
            if not creer_code or len(creer_code.strip()) < 6:
                messagebox.showerror("Erreur", "Le mot de passe exige un minimum de 6 caractères.")
                return

            data_base.enregistrer_nom_boutique_sql(nom_magasin.strip())
            data_base.configurer_compte_gerant_sql(creer_code.strip())
            messagebox.showinfo("Succès", f"Félicitations !\nL'entreprise '{nom_magasin.strip().upper()}' est activée.")
            return

        if data_base.verifier_identifiants_sql(user, pwd):
            SESSION_UTILISATEUR = str(user).strip().lower()
            NOM_CAISSIERE_ACTIVE = str(user).strip().lower()
            messagebox.showinfo("Accès Autorisé", f"Bienvenue {SESSION_UTILISATEUR.upper()} !")
            FENETRE_PRINCIPALE_LOGIN.withdraw() # Masquage de la racine unique
            ouvrir_comptoir_facturation()
        else:
            messagebox.showerror("Accès Refusé", "Identifiant ou mot de passe incorrect.")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur système : {str(e)}")


def recuperer_mot_de_passe_oublie():
    cle_saisie = simpledialog.askstring("Sécurité Constructeur", "Veuillez entrer la clé de secours fournie par l'ingénieur Serge :")
    if cle_saisie == CLE_MASTER_SERGE:
        nouveau_code = simpledialog.askstring("Réinitialisation", "Clé correcte !\nTapez votre nouveau mot de passe gérant :")
        if nouveau_code and nouveau_code.strip():
            data_base.configurer_compte_gerant_sql(nouveau_code.strip())
            messagebox.showinfo("Succès", "Mot de passe réinitialisé ! Connectez-vous.")
    elif cle_saisie is not None:
        messagebox.showerror("Accès Refusé", "Clé de secours invalide.")


# --- POINT DE DÉMARRAGE DE LA RACINE UNIQUE ---
login = tk.Tk()
FENETRE_PRINCIPALE_LOGIN = login

login.title("Sécurité d'Accès")
login.geometry("350x420")
login.configure(bg="#1e293b")

tk.Label(login, text="CONNEXION SÉCURISÉE", font=("Helvetica", 12, "bold"), bg="#1e293b", fg="white").pack(pady=20)
boite = tk.Frame(login, bg="#1e293b", padx=30)
boite.pack(fill=tk.X)

tk.Label(boite, text="Identifiant Employé :", bg="#1e293b", fg="#cbd5e1").pack(anchor=tk.W)
entree_user = tk.Entry(boite, font=("Helvetica", 11), bd=2)
entree_user.pack(fill=tk.X, pady=5)
entree_user.insert(0, "gerant")

tk.Label(boite, text="Mot de passe secret :", bg="#1e293b", fg="#cbd5e1").pack(anchor=tk.W)
entree_password = tk.Entry(boite, font=("Helvetica", 11), show="*", bd=2)
entree_password.pack(fill=tk.X, pady=5)

entree_user.bind("<Return>", lambda event: entree_password.focus())
entree_password.bind("<Return>", lambda event: verifier_acces())

tk.Button(login, text="🔓 ACCÉDER AU COMPTOIR", font=("Helvetica", 11, "bold"), bg="#3b82f6", fg="white", command=verifier_acces).pack(fill=tk.X, padx=30, pady=15)
tk.Button(login, text="❓ Mot de passe oublié / Réinitialiser", font=("Helvetica", 9, "underline"), bg="#1e293b", fg="#94a3b8", bd=0, command=recuperer_mot_de_passe_oublie, cursor="hand2").pack(pady=10)

login.mainloop()
