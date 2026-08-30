# on importe nos deux autres fichiers 
import data_base
import operation


def afficher_menu():
    """afficher le menu interactif du logiciel"""
    print("\n============================================")
    print("     LOGICIEL DE CAISSE - KASHFLOW MANAGER ")
    print("\n============================================")
    print("1. Enregistere une nouvelle vente")
    print("2. consulter l'historique pour audit comptable")
    print("3. Quitter le logiciel")
    print("\n============================================")

def executer_logiciel():
    data_base.initialisation_systeme()

    while True: 
        afficher_menu()
        choix = input("selectionnez une option (1 , 2 ou 3) :")
        if choix == "1":
            print("\n ENREGISTREMENT D'UNE NOUVELLE VENTE")
            nom_client = input ("nom du client :")
            nom_article = input("nom de l'article :")
            prix_ht = input("prix unitaire hors taxe (FCFA) :")
            quantite = input("quantite vendue:")

            calculs = operation.calcule_des_elements_facture(prix_ht , quantite)
             # si le calcul est bon , on extrait les resultats du dictionaire pour les enregistrer dans la base de donnee
            if calculs is not None:
                mnt_ht = calculs["montant_ht"]
                v_tva = calculs["valeur_tva"]
                ttc = calculs["total_ttc"]

                succes = data_base.enregistrer_vente_sql(nom_client , nom_article , mnt_ht , v_tva , ttc)

                if succes :

                    # on appel notre generateur de pdf ,  et on lui passe toute les variables de la vente en parrametre
                    print("Generation du reçus officiel en cours...")
                    operation.generer_recu_pdf(nom_client , nom_article , quantite , mnt_ht , v_tva , ttc)
                    
                    # on affiche un re§us de caisse transparent pour le client 
                    print("\n ===== REçUS  DE CAISSE EMIS =====")
                    print(f"client : {nom_client}")
                    print(f"article : {nom_article} (x{quantite})")
                    print(f"montant total hors taxe :{mnt_ht} FCFA")
                    print(f"TVA calculée(19.25%):{v_tva} FCFA")
                    print(f" NET A PAYER (TTC) : {ttc} FCFA")
                    print("============================================")
                    print("transaction securisée et enregistrer en base ")

        
        elif choix =="2":
            print("\n ----- HISTORIQUE COMPLET DES VENTES (AUDIT) ----")
            # on va chercher toutes les ligne stoquer dans la base de donnée
            ventes = data_base.recuper_tout_les_ventes()

            if len(ventes) == 0 :
                print("Aucune vente enregistrer pour le moment ")
            else :
                chiffre_affaire_global = 0
                for v in ventes : 
                    #v[0] = id , v[1] = nom_client etc...
                    print(f"facture N°{v[0]} | nom du client : {v[1]} | article : {v[2]} | total TTC : {v[3]} FCFA")
                    chiffre_affaire_global += float(v[3])

                print("---------------------------------------------------")
                print(f" CHIFFRE D4AFFAIRES GLOBAL DE LA CAISSE : {chiffre_affaire_global} FCFA")

        elif choix == "3":
            print("\n Fermeture de la caisse. passez une exellente journee !!" )
            break

        else :
            print("[ATTENTION] option invalide.veuillez taper 1 , 2 ou 3.")

executer_logiciel()