## Projet Bloc n°6 : Recommendation system based on sentiments analysis

Francais : 

Ce projet est né d'une idée selon laquelle les recommandations actuelles de contenu n'étaient pas assez personnalisé et ciblé sur le ressenti d'un utilisateur. Au lieu d'etablir une recommandation sur les notes seulement, nous avons choisi de construire un système qui permettrait à l'utilisateur d'avoir le choix sur du contenu similaire aux émotions que lui à procurer le contenu qu'il a aimé. Nous avons ciblé les livres comme type de contenu car notre étude se base sur les commentaires des utilisateurs et ils sont riches en émotions et en vocabulaire. Nous avons décomposer notre travail en plusieurs taches :

1. Recupération de la donnée par du Data Mining 
2. Création d'un dictionnaire de synonymes et du vecteurs de sentiments (8 sentiments : joie, colère, peur, tristesse, confiance, surprise, honte, dégout)
3. EDA sur les notes, comportements des utilisateurs et des editeurs
4. Traitement de la donnée et formatage pour créer des vecteurs similarités entre émotions (similarité cosinus et distance de Jaccard)
5. Utilisation de Transformers pour créer un reseau de neurones pour classifier les sentiments
6. Création du système de recommandation graçe aux calculs de similarité
7. Mise en application

Chaque étape sera documenter par son propre fichier README.md 

Voici le rendu de l'application : http://mldatago.com:8080/

email : davidtiffeneau@live.fr</br>
name : David TIFFENEAU-GAUTIER</br>
link to the video () : 


English : 

This project was born from an idea that current content recommendations were not personalized and targeted enough to a user's feelings. Instead of establishing a recommendation on the ratings only, we chose to build a system that would allow the user to have the choice of content similar to the emotions that provide him with the content he liked. We focus books as the type of content because our research is based on user feedback and they are rich in emotion and vocabulary. We have create multiple parts of our work:

1. Data Mining to etablish database
2. Creation of a dictionary of synonyms and vectors of feelings (8 feelings: joy, anger, fear, sadness, confidence, surprise, shame, disgust)
3. EDA on Ratings, User and Editor Behaviors
4. Data processing and formatting to create similarity vectors between emotions (cosine similarity and Jaccard distance)
5. Using Transformers to create a neural network to classify feelings
6. Creation of the recommender system thanks to similarity calculations
7. Web App

Each step will be explain by his own README.md file

link to app : http://mldatago.com:8080/