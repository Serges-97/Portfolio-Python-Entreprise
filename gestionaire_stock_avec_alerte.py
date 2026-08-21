# inventaire = [
#     {"nom":"samsung" , "quantite":20 , "prix_unitaire_ht": 60000 , "seuil_critique": 4},
#     {"nom":"itel" , "quantite":50 , "prix_unitaire_ht": 50000 , "seuil_critique": 7},
#     {"nom":"tecno" , "quantite":1 , "prix_unitaire_ht": 45000 , "seuil_critique": 10},
#     {"nom":"iphone" , "quantite":40 , "prix_unitaire_ht": 100000 , "seuil_critique": 3}
# ]

nom_article = input("entrer le nom du telephone :")
quantite_article = int(input("veuiller entrer la quantiter de telephone en stock :"))
prix_unitaire_article = float(input("veuiller entre le prix d'un telehone :"))
seuil_article = int(input("veuiller entrer le seuil du stoque :"))

inventaire = [
    {"nom":nom_article , "quantite":quantite_article , "prix_unitaire_ht":prix_unitaire_article , "seuil_critique":seuil_article}
]

def analyse_stock(inventaire):

    nbre_total_telephone = 0
    valeur_total_du_stock_ht = 0
    for produit in inventaire :
        try :
            qt = int (produit["quantite"])
            prix = float (produit["prix_unitaire_ht"])
            seuil = int(produit["seuil_critique"])
            valeur_total_ht = qt * prix
            valeur_total_du_stock_ht += valeur_total_ht
            nbre_total_telephone += qt
        except ValueError :
            print("veuiller entrer une valeur correct !!")
            return "donnée non valide"
            
        if qt <= seuil :
            print(f"[ALERTE] le produit {produit['nom']} est en rupture iminente ! stock :{produit['seuil_critique']}")
    return f" actuellement dans le magasin il ya :{nbre_total_telephone} telephones \n ce qui fait au total  :{valeur_total_du_stock_ht} fcfa"

magasin1 = analyse_stock(inventaire)
print(magasin1) 