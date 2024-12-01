import os
import requests
from bs4 import BeautifulSoup
import pdfkit
from urllib.parse import urljoin
import json
import pandas as pd
import csv

# 0 - Fonction pour créer un dossier
def creer_dossier(nom_dossier):
    if not os.path.exists(nom_dossier):
        os.makedirs(nom_dossier)

# 1 - Extraction du sommaire et conversion en PDF
def creer_pdf_sommaire(url, output_dir, pdf_file):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    sommaire = soup.find("div", {"class": "vector-toc"})

    if sommaire:
        contenu_html = f"""
        <html>
        <head><meta charset="UTF-8"><title>Sommaire - Indiana Jones</title></head>
        <body><h1>Sommaire - Indiana Jones</h1><ul>
        """
        contenu_html += "".join(f'<li>{a.get_text(strip=True)}</li>' for a in sommaire.find_all("a"))
        contenu_html += "</ul></body></html>"

        temp_html = os.path.join(output_dir, "Sommaire_Indiana_Jones.html")
        with open(temp_html, "w", encoding="utf-8") as file:
            file.write(contenu_html)

        pdf_path = os.path.join(output_dir, pdf_file)
        try:
            pdfkit.from_file(temp_html, pdf_path)
            os.remove(temp_html)
            print(f"PDF créé : {pdf_path}")
        except Exception as e:
            print(f"Erreur création PDF : {e}")
    else:
        print("Sommaire introuvable.")

# 2 - Enregistrement des images dans un dossier
def extraire_images(url, output_dir):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    images = soup.find_all("img")

    for i, img in enumerate(images):
        img_url = img.get("src")
        if img_url:
            img_url = urljoin(url, img_url)
            img_path = os.path.join(output_dir, f"image_{i+1}.jpg")
            try:
                with open(img_path, "wb") as f:
                    f.write(requests.get(img_url).content)
                print(f"Image enregistrée : {img_path}")
            except Exception as e:
                print(f"Erreur téléchargement image {i+1}: {e}")

# 3 - Extraction des jeux vidéos et création des fichiers JSON
def extraire_jeux_video(soup, output_json, output_excel):
    section = soup.find("h3", {"id": "Jeux_vidéo"})
    jeux = []

    if section:
        ul = section.find_next("ul")
        if ul:
            for li in ul.find_all("li"):
                titre_complet = li.get_text(strip=True)
                titre, sep, desc = titre_complet.partition("–")
                titre = titre.lstrip("1234567890 ").strip()
                date = li.find("a", {"title": True})
                jeux.append({
                    "Date": date["title"].split()[0] if date else "Date inconnue",
                    "Titre": titre,
                    "Description": desc.strip() if sep else "Description non fournie"
                })

            with open(output_json, "w", encoding="utf-8") as json_f:
                json.dump(jeux, json_f, ensure_ascii=False, indent=4)
            pd.DataFrame(jeux).to_excel(output_excel, index=False)

            print(f"JSON créé : {output_json}")
            print(f"Excel créé : {output_excel}")
        else:
            print("Aucune liste de jeux vidéo trouvée.")
    else:
        print("Section 'Jeux vidéo' introuvable.")

# 4 - Extraction des données et création d'un CSV (Sujet 1 suite)
url = 'https://www.worldometers.info/world-population/germany-population/'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find('table', {'class': 'table'})
rows = table.find_all('tr')

population_data = []

for row in rows[1:6]:
    cols = row.find_all('td')
    year = int(cols[0].text.strip())
    population = f"{cols[1].text.strip()} habitants"
    migrants = f"{cols[4].text.strip()} migrants"
    avg_age = f"{cols[5].text.strip()} ans"
    rank = int(cols[-1].text.strip())
    
    population_data.append([year, population, migrants, avg_age, rank])

output_dir = 'rendu CSV'
os.makedirs(output_dir, exist_ok=True)
csv_file_path = os.path.join(output_dir, 'Allemagne.csv')

with open(csv_file_path, mode='w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Année', 'Population totale', 'Nombre de migrants', 'Âge moyen', 'Rang'])
    writer.writerows(population_data)
print(f"Les données ont été enregistrées dans {csv_file_path}")

# Exécution des fonctions
creer_dossier("rendu PDF")
creer_pdf_sommaire("https://fr.wikipedia.org/wiki/Indiana_Jones", "rendu PDF", "Sommaire_Indiana_Jones.pdf")
creer_dossier("Images Indiana Jones")
extraire_images("https://fr.wikipedia.org/wiki/Indiana_Jones", "Images Indiana Jones")
response = requests.get("https://fr.wikipedia.org/wiki/Indiana_Jones")
soup = BeautifulSoup(response.text, "html.parser")
extraire_jeux_video(soup, "jeux_video_indiana_jones.json", "jeux_video_indiana_jones.xlsx")