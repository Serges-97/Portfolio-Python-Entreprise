# on demande a python d'importer notre FastApi. c'est l'outil qui va transformer notre code en serveur web
from fastapi import FastAPI

# pour manipuler les fichiers json
import json  

#on crée notre aplication web et on la stock dans une variable nommée "app".
# c'est le moteur principal de notre serveur  
app = FastAPI()

# ** l'accueil de notre serveur **

# le app.get("/") est un intepreteur,il dit a FastAPI que si un utisateur tape l'adresse de base ("/") dans son navigateur directement la fonction en dessou se declanche
@app.get("/")
def accueil():
    return {"statut" : "api de consolidation nationale operationnelle "}

# ** le calculateur de sites (BUSINESS LOGIC) **
 
@app.get("/api/bilan-national")
def obtenir_bilan_national():
    # securisation , si un fichier json est introuvable ou cassé , le seveur ne vas pas cracher
    try:
        total_douala = 0 
        total_yaounde = 0 

        with open ("douala.json" , "r", encoding="utf-8") as fichier_douala :
            f_d = json.load(fichier_douala)
            for item in f_d :
                total_douala += float(item["ventes"])
            
        with open ("yaounde.json", "r", encoding="utf-8") as fichier_yaounde :
            f_y = json.load(fichier_yaounde)
            for item in f_y :
                total_yaounde += float(item["ventes"])
        
        total_national = total_douala + total_yaounde

        # avec les api, le return renvoi directement les resultats sur internet sous forme de dictionaire 
        return {
               "entreprise " : "RAPPORT DES VENTES !!" , 
               "ventes_de_douala" : total_douala , 
               "ventes_de_yaounde" : total_yaounde ,
               "chiffre_d'affaire_total" : total_national
        }
            
    except Exception as e :
        return {"erreur" : f"impossible de lire les fichiers de données : {str(e)}"}