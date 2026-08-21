import json
  
  #on charge les données de douala.json dans une variable
with open("douala.json" , "r" , encoding="utf-8") as fichier_douala:
    vente_douala = json.load(fichier_douala)

 #on charge les données de yaounde.json dans une  autre variable
with open("yaounde.json" , "r", encoding="utf-8") as fichier_yaounde :
    vente_yaounde = json.load(fichier_yaounde)

chiffre_affaire_total = 0
vente_total_douala = 0
vente_total_yaounde = 0

for vente1 in vente_douala :
    vente_total_douala += vente1["ventes"] 

for vente2 in vente_yaounde :
    vente_total_yaounde += vente2["ventes"]

chiffre_affaire_total = vente_total_douala + vente_total_yaounde

with open("bilan_national.txt", "w" , encoding="utf-8") as fichier_rapport:
    fichier_rapport.write(f"[RAPPORT DES VENTES !!] \n\n  ventes de douala : {vente_total_douala} \n ventes de yaounde : {vente_total_yaounde}\n TOTAL NATIONAL : {chiffre_affaire_total}")

print(f"le rapport a ete soumis , consulter le fichier bilan_national.txt")

