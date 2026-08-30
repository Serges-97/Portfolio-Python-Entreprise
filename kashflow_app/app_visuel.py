# =====================================================================
# INTERFACE GRAPHIQUE INDUSTRIELLE : app_visuel.py v5.0 (VERSION FINALE)
# =====================================================================
import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, ttk
import sqlite3
import requests
import data_base
import operation

data_base.initialisation_systeme()
SESSION_UTILISATEUR = "gerant"

# --- FONCTION 1 : PANNEAU INVENTAIRE / STOCKS ---
def ouvrir_panneau_stock():
    if SESSION_UTILISATEUR != "gerant":
        messagebox.showerror("Accès Interdit", "Seul le gérant peut modifier l'inventaire.")
        return

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
            messagebox.showinfo("Succès", f"Stock de '{modele}' mis à jour !")
            admin_stock.destroy()
            ouvrir_panneau_stock()
        except ValueError:
            messagebox.showerror("Erreur", "La quantité doit être un nombre entier supérieur à 0.")

    admin_stock = Toplevel()
    admin_stock.title("📦 Gestion des Stocks - Panel Gérant")
    admin_stock.geometry("500x480")
    admin_stock.configure(bg="#f8fafc")
    admin_stock.grab_set()

    tk.Label(admin_stock, text="INVENTAIRE DES SMARTPHONES EN STOCK", font=("Helvetica", 11, "bold"), bg="#0f766e", fg="white", pady=8).pack(fill=tk.X)
    cadre_tableau = tk.Frame(admin_stock, bg="#f8fafc")
    cadre_tableau.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    tableau = ttk.Treeview(cadre_tableau, columns=("Modèle", "Quantité Dispo"), show="headings", height=8)
    tableau.heading("Modèle", text="MODÈLE")
    tableau.heading("Quantité Dispo", text="EN STOCK")
    tableau.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

    connexion = sqlite3.connect(data_base.DB_NAME)
    curseur = connexion.cursor()
    curseur.execute("SELECT modele, quantite_dispo FROM stocks")
    lignes = curseur.fetchall()
    connexion.close()

    for l in lignes:
        tableau.insert("", tk.END, values=(l[0], f"{l[1]} pcs"))

    cadre_ajout = tk.LabelFrame(admin_stock, text="Ajouter un Smartphone", bg="#f8fafc", padx=10, pady=10)
    cadre_ajout.pack(fill=tk.X, padx=15, pady=15)
    tk.Label(cadre_ajout, text="Nom du Modèle :", bg="#f8fafc").pack(anchor=tk.W)
    entree_modele = tk.Entry(cadre_ajout, font=("Helvetica", 10))
    entree_modele.pack(fill=tk.X, pady=4)
    tk.Label(cadre_ajout, text="Quantité reçue :", bg="#f8fafc").pack(anchor=tk.W)
    entree_qte_stock = tk.Entry(cadre_ajout, font=("Helvetica", 10))
    entree_qte_stock.pack(fill=tk.X, pady=4)
    tk.Button(cadre_ajout, text="📥 ENREGISTRER L'ARRIVAGE", bg="#0f766e", fg="white", command=action_ajouter_modele).pack(fill=tk.X, pady=8)

# --- FONCTION 2 : AUDIT COMPTABLE ---
def ouvrir_panneau_historique():
    if SESSION_UTILISATEUR != "gerant":
        messagebox.showerror("Accès Interdit", "Seul le gérant consulte l'audit.")
        return

    audit = Toplevel()
    audit.title("📊 Rapport d'Audit Financier")
    audit.geometry("650x450")
    audit.configure(bg="#f8fafc")
    audit.grab_set()

    tk.Label(audit, text="HISTORIQUE COMPLET DES VENTES", font=("Helvetica", 11, "bold"), bg="#1e293b", fg="white", pady=8).pack(fill=tk.X)
    zone_affichage = tk.Text(audit, font=("Courier", 10), bg="white", bd=2)
    zone_affichage.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    ventes_sql = data_base.recuper_tout_les_ventes()
    if not ventes_sql:
        zone_affichage.insert(tk.END, "Aucune transaction.\n")
        ca_total = 0.0
    else:
        ca_total = 0.0
        for v in ventes_sql:
            ca_total += float(v[3])
            zone_affichage.insert(tk.END, f"N°{str(v[0]).zfill(3)} | {v[1]:<12} | {v[2]:<15} | {v[3]:>9} FCFA\n")

    zone_affichage.config(state=tk.DISABLED)
    tk.Label(audit, text=f"CHIFFRE D'AFFAIRES GLOBAL : {round(ca_total, 2)} FCFA", font=("Helvetica", 12, "bold"), bg="#10b981", fg="white", pady=10).pack(fill=tk.X)

# --- FONCTION 3 : COMPTOIR DE FACTURATION PRINCIPAL ---
def ouvrir_comptoir_facturation():
    nom_boutique_fixe = data_base.recuperer_nom_boutique_sql()
    
    if nom_boutique_fixe is None:
        nom_saisi = simpledialog.askstring("Configuration Initiale", "Entrez le nom de la boutique :")
        if nom_saisi and nom_saisi.strip():
            data_base.enregistrer_nom_boutique_sql(nom_saisi.strip())
            nom_boutique_fixe = nom_saisi.strip()
        else:
            messagebox.showerror("Erreur", "Le nom de l'entreprise est obligatoire.")
            return

    def action_bouton_enregistrer():
        client = entree_client.get().strip()
        article = liste_smartphones.get().strip()
        imei = entree_imei.get().strip()
        prix_ht = entree_prix.get().strip()
        quantite = entree_quantite.get().strip()

        if not client or not article or not imei or not prix_ht or not quantite:
            messagebox.showwarning("Champs vides", "Veuillez remplir tout le formulaire.")
            return

        try:
            qte_int = int(quantite)
            prix_float = float(prix_ht)
        except ValueError:
            messagebox.showerror("Erreur", "Le prix et la quantité doivent être des chiffres.")
            return

        test_stock = data_base.verifier_et_reduire_stock(article, qte_int)
        if not test_stock["autorise"]:
            messagebox.showerror("BLOCAGE STOCK", test_stock["raison"])
            return

        calculs = operation.calcule_des_elements_facture(prix_ht, quantite)
        ht, tva, ttc = calculs["montant_ht"], calculs["valeur_tva"], calculs["total_ttc"]

        num_facture = data_base.enregistrer_vente_sql(client, article, imei, ht, tva, ttc)
        if num_facture is not None:
            operation.generer_recu_pdf(nom_boutique_fixe, num_facture, client, article, imei, quantite, ht, tva, ttc)
            try:
                url_serveur_patron = "http://192.168.137"
                donnees_reseau = {"client": client, "article": article, "imei": imei, "prix_ht": prix_float, "quantite": qte_int}
                reponse = requests.post(url_serveur_patron, json=donnees_reseau, timeout=2)
                status_synchro = "☁️ Synchronisation Cloud : Réussie !" if reponse.status_code == 200 else "⚠️ Sauvegardé uniquement en local."
            except Exception:
                status_synchro = "🔌 Mode Hors-Ligne : Vente sécurisée en local."

            messagebox.showinfo("Vente Validée", f"Facture N°{str(num_facture).zfill(4)} émise !\n\n{status_synchro}")
            entree_client.delete(0, tk.END)
            entree_imei.delete(0, tk.END)
            entree_prix.delete(0, tk.END)
            entree_quantite.delete(0, tk.END)
            entree_client.focus()
        else:
            messagebox.showerror("Erreur", "Échec d'écriture SQL.")

    comptoir = tk.Tk()
    comptoir.title(f"KashFlow Manager v5.0 - {nom_boutique_fixe}")
    comptoir.geometry("480x640")
    comptoir.configure(bg="#f3f4f6")

    # FIX DU CRASH ICI : Nettoyage de la syntaxe
    tk.Label(comptoir, text=str(nom_boutique_fixe).upper(), font=("Helvetica", 14, "bold"), bg="#1e3a8a", fg="white", pady=12).pack(fill=tk.X)
    
    if SESSION_UTILISATEUR == "gerant":
        cadre_admin_btn = tk.Frame(comptoir, bg="#475569")
        cadre_admin_btn.pack(fill=tk.X)
        tk.Button(cadre_admin_btn, text="📦 INVENTAIRE & STOCKS", font=("Helvetica", 9, "bold"), bg="#0f766e", fg="white", bd=0, pady=6, command=ouvrir_panneau_stock).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(cadre_admin_btn, text="📊 RAPPORT COMPTABLE", font=("Helvetica", 9, "bold"), bg="#334155", fg="white", bd=0, pady=6, command=ouvrir_panneau_historique).pack(side=tk.RIGHT, fill=tk.X, expand=True)

    cadre = tk.Frame(comptoir, bg="#f3f4f6", padx=25, pady=15)
    cadre.pack(fill=tk.BOTH, expand=True)

    tk.Label(cadre, text="Nom complet du Client :", font=("Helvetica", 10, "bold"), bg="#f3f4f6").pack(anchor=tk.W, pady=2)
    entree_client = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_client.pack(fill=tk.X, pady=4)
    entree_client.focus()

    tk.Label(cadre, text="Sélectionner le Modèle :", font=("Helvetica", 10, "bold"), bg="#f3f4f6").pack(anchor=tk.W, pady=2)
    connexion = sqlite3.connect(data_base.DB_NAME)
    curseur = connexion.cursor()
    curseur.execute("SELECT modele FROM stocks WHERE quantite_dispo > 0")
    liste_modeles = [ligne[0] for ligne in curseur.fetchall()]
    connexion.close()
    
    liste_smartphones = ttk.Combobox(cadre, values=liste_modeles, font=("Helvetica", 11), state="readonly")
    liste_smartphones.pack(fill=tk.X, pady=4)
    if liste_modeles: liste_smartphones.current(0)

    tk.Label(cadre, text="Numéro IMEI (Garantie SAV) :", font=("Helvetica", 10, "bold"), bg="#f3f4f6").pack(anchor=tk.W, pady=2)
    entree_imei = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_imei.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Prix unitaire HT (FCFA) :", font=("Helvetica", 10, "bold"), bg="#f3f4f6").pack(anchor=tk.W, pady=2) 
    entree_prix = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_prix.pack(fill=tk.X, pady=4)

    tk.Label(cadre, text="Quantité vendue :", font=("Helvetica", 10, "bold"), bg="#f3f4f6").pack(anchor=tk.W, pady=2) 
    entree_quantite = tk.Entry(cadre, font=("Helvetica", 11), bd=2)
    entree_quantite.pack(fill=tk.X, pady=4)

    # 🚀 CONFIGURATION DE LA NAVIGATION CLAVIER (Touche Entrée)
    entree_client.bind("<Return>", lambda event: liste_smartphones.focus())
    liste_smartphones.bind("<Return>", lambda event: entree_imei.focus())
    entree_imei.bind("<Return>", lambda event: entree_prix.focus())
    entree_prix.bind("<Return>", lambda event: entree_quantite.focus())
    entree_quantite.bind("<Return>", lambda event: action_bouton_enregistrer())

    # Gros bouton Encaisser vert
    tk.Button(cadre, text="🛒 VALIDER LA VENTE & ÉMETTRE LE PDF", font=("Helvetica", 11, "bold"), bg="#10b981", fg="white", command=action_bouton_enregistrer, pady=10).pack(fill=tk.X, pady=20)
    comptoir.mainloop()

# =====================================================================
# ÉCRAN DE VERROUILLAGE INITIAL (LOGIN BLEU NUIT)
# =====================================================================
def verifier_acces():
    global SESSION_UTILISATEUR
    user = entree_user.get().strip()
    pwd = entree_password.get().strip()
    if data_base.verifier_identifiants_sql(user, pwd):
        SESSION_UTILISATEUR = user.lower()
        messagebox.showinfo("Accès Autorisé", "Bienvenue, session ouverte !")
        login.destroy() # On détruit le verrou
        ouvrir_comptoir_facturation() # On ouvre le comptoir v5.0
    else:
        messagebox.showerror("Accès Refusé", "Identifiant ou mot de passe incorrect.")

login = tk.Tk()
login.title("Sécurité d'Accès")
login.geometry("350x380")
login.configure(bg="#1e293b")

tk.Label(login, text="CONNEXION SÉCURISÉE", font=("Helvetica", 12, "bold"), bg="#1e293b", fg="white").pack(pady=25)
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

tk.Button(login, text="🔓 ACCÉDER AU COMPTOIR", font=("Helvetica", 11, "bold"), bg="#3b82f6", fg="white", command=verifier_acces, pady=8).pack(fill=tk.X, padx=30, pady=35)
login.mainloop()
