import json

def auditer_entreprise() :
    # on charge les données du fichier json externe
    with open ("ventes.json", "r" , encoding="utf-8") as fichier_source:
        equipe_comercial = json.load(fichier_source)
    
    # on ouvre le fichier rapport TXT dans le quel on vas ecrire le rapport
    with open("ropport.txt", "w" , encoding="utf-8") as fichier_rapport :
        fichier_rapport.write("=== RAPPORT DES VENTES === \n\n" )

        for commercial in equipe_comercial :
            nom = commercial["vendeur"]
            ca = float(commercial["chiffre_affaire"])
            obj = float(commercial["objectif"])

            taux_reussite = (ca/obj) * 100
            if taux_reussite >= 100 :
                fichier_rapport.write(f"{nom} : Obejectif Atteint ({taux_reussite:.2f}%) \n")
                
            elif taux_reussite < 70 :
                fichier_rapport.write(f"[ALERTE DIRECTION] convocation requise pour :{nom} \n")
            pass

auditer_entreprise()
print(f"audit terminé !! consulter le fichier rapport.txt")
