# definition du taux officiel de la tva au cameroun dans une variable globale (19.25%)
taux_tva = 19.25 / 100

def calcule_des_elements_facture(prix_unitaire_ht , quantite):
     try:
        prix = float(prix_unitaire_ht)
        qt = int(quantite)

        if prix < 0 or qt < 0:
            print("[ERREUR] le prix unitaire et la quantite doivent etre superieur a zero")
            return None

        montant_ht = prix * qt
        valeur_tva = montant_ht * taux_tva
        montant_ttc = montant_ht + valeur_tva

        # on arrondit a 2 decimales pour eviter les chiffres infinie
        # on range tout dans un dictionnaire propre pour le renvoyer au programme principal
        return{
            "montant_ht" : round(montant_ht , 2) , 
            "valeur_tva" : round(valeur_tva , 2) ,
            "total_ttc":round(montant_ttc , 2)
        }
          
     except Exception as e:
         print (f"[ERREUR MOTEUR] echec du calcul financier. raison:{e}")
         return None
     