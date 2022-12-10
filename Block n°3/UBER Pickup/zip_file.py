import zipfile
from zipfile import ZipFile
import os
from os.path import basename


# Compresse les fichiers du répertoire donné qui correspond au filtre
def zipFilesInDir(dir_name, zip_filename, filter):
   # Crée un objet ZipFile
    with ZipFile(zip_filename, 'w') as zip_object:
       # Itere sur tous les fichiers du repertoire
        for folderName, subfolders, filenames in os.walk(dir_name):
            for filename in filenames:
                if filter(filename):
                    # Créer le chemin complet du fichier dans le répertoire
                    filepath = os.path.join(folderName, filename)
                    # Ajouter le fichier au zip 
                    zip_object.write(filepath, basename(filepath))
                    
                    
def main():
    print('*** Créer un fichier zip à partir de plusieurs fichiers')
    # Crée un objet ZipFile
    zip_object = ZipFile('./src/datasets/merge_df.zip', 'w')
    # Ajoute plusieurs fichiers au zip
    zip_object.write('./src/datasets/merge_df.csv')
    # Ferme le fichier Zip 
    zip_object.close()
    print('*** Créer un fichier zip à partir de plusieurs fichiers en les utilisant')
    # Crée un objet ZipFile
    with ZipFile('./src/datasets/janjun15.zip', 'w', compression=zipfile.ZIP_DEFLATED) as zip_object2:
        # Ajoute plusieurs fichiers au zip
        zip_object2.write('./src/datasets/uber-raw-data-janjune-15.csv')
    # Nom du répertoire à compresser
    dirName = 'datasets'
    # Crée un objet ZipFile
    with ZipFile('datasets.zip', 'w') as zipObj:
       # Itere sur tous les fichiers du repertoire
        for folderName, subfolders, filenames in os.walk(dirName):
            for filename in filenames:
                # Créer le chemin complet du fichier dans le répertoire
                filePath = os.path.join(folderName, filename)
                # Ajouter le fichier au zip
                zipObj.write(filePath)
    print("*** Créer une archive zip de fichiers csv uniquement à partir d'un répertoire ***")
    zipFilesInDir('datasets', 'datasets2.zip', lambda name : 'csv' in name)
    
    
if __name__ == '__main__':
    main()