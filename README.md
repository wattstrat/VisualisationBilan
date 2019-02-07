# WattStrat

L'outil de visualisation de simulation énergétique territoriale de Wattstrat a
été construit avec amour et [Python][0], en s'appuyant sur le [Framework Django][1].
Les données de bilan, ainsi que les données de référence par code géographique
sont stockées dans [MongoDB][2], alors que les données géométriques, par exemple
les contours des territoires, sont stockées dans [PostgreSQL][3] et que les calculs
géométriques sont effectués grâce à [PostGIS][4].

La front-end s'appuie sur [AngularJs][5], [amCharts][6], [Leaflet][7] et [OpenLayers][8].

Le versionnage de code est réalisé via [GitHub][9].

## Installation

### Démarrage rapide

Commencer par installer Python 3.6. Nous recommandons d'utiliser [pyenv][19].
Nous recommandons également d'utiliser [Pipenv][20] ou [Poetry][21] pour la gestion
des dépendances et des environnements virtuels, en chargeant notre fichier
requirements.txt

Exécuter les migrations:

    python manage.py migrate

### Installation détaillée

1. Télécharger les données nécessaires :
  * [geocodes.bson.xz][10] et [metadatas][11]: données compressées et les
  metadonnées associées permettant de reconstruire une collection MongoDB nécessaire
  * [bilan2015.bson.xz][12] et [metadatas][13] : données compressées et les
  métadonnées associées permettant de reconstruire la collection contenant
  l'intégralité des résultats de la reconstruction du bilan énergétique français
  de l'année 2015, commune par commune et heure par heure.
  * [world][14] : dump de la base PostgreSQL contenant les contours nécessaires à
  l'affichage des différentes cartographies

2. Décompresser les données avec xz :
  * Linux :
    * installer xz si besoin : `$ sudo apt-get install xz`
    * décompresser : `$ xz --decompress file.xz`
  * MacOS :
    * installer un logiciel de décompression, par exemple [TheUnarchiver][15]
    * décompresser en ouvrant le fichier avec ce logiciel
  * Windows :
    * installer un logiciel de décompression, par exemple [WinZip][16]
    * décompresser en ouvrant le fichier avec ce logiciel (voici un [tutoriel][17])

3. Installer MongoDB en suivant les indications de cette [page][18]

4. Lancer le serveur MongoDB via un terminal: `$ mongod`

5. Charger les données dans MongoDB via un second terminal :
  * geocodes :
  ```console
  $ mongorestore --collection geocodes --db simulations --batchSize=100 geocodes.bson
  ```
  * bilan :
  ```console
  $ mongorestore --collection bilan2015 --db simulations --batchSize=100 bilan2015.bson
  ```

6. Charger les données dans PostgreSQL
  * installer postgresql >= 9.6, postgis >= 2.3, les extension HSTORE et postgist
    sous debian, ce sont les packages
       postgresql-9.6-postgis-2.3 postgresql-9.6 postgresql-client-9.6
       postgresql-9.6-postgis-2.3-scripts postgresql-contrib-9.6
    
  * charger les données
  ```console
  $ sudo -u postgres createuser --no-createdb --no-createrole --no-superuser --no-replication worlduser
  $ echo -e "ALTER USER worlduser WITH PASSWORD 'worldpassword';\nCREATE DATABASE world OWNER worlduser;" | sudo -u postgres psql
  $ sudo -u postgres psql world -f world.sql
  $ echo "host   world            worlduser         127.0.0.1/32      md5" >> /etc/postgresql/9.6/main/pg_hba.conf

  ```
  * redemmarer postgreSQL
  
7. Cloner le dépôt Git :
```console
$ git clone https://github.com/wattstrat/VisualisationBilan.git
$ cd VisualisationBilan
$ git submodule init
$ git submodule update
```
8. Definir l'environnement local en editant le fichier wattstrat/settings/local.env
9. Intaller les requirements

### GeoData

Un écran de l'application utilise encore [Leaflet][7] et pas [OpenLayers][8],
et pour cela il est nécessaire de construire des geojson :
1. Vérifier que vous avez une locale UTF8
2. Création des geojson
```python
python scripts/transform_geo_data.py
```

### Serveur de dev
1. Effectuer les migration
```console
$ python manage.py migrate
```
2. Créer un superadmin
```console
$ python manage.py createsuperuser
```
3. Démarrer le serveur
```console
$ python manage.py runserver
```
4. Activer le compte admin en vous rendant sur http://172.17.0.2:8000/admin/ avec le username/password précédemment créé
  * http://127.0.0.1:8000/admin/accounts/user/1/change/
  * cocher "Email verified"
  * Enregistrer
  
### I18N

Le standard d'[internationalisation de django][22] estutilisé. Il s'appuie lui même
sur l'utilitaire gettext.
```console
$ python manage.py makemessages -l fr
```

Ensuite, la traduction peut être modifiée dans `BASE_DIR/locale/fr/LC_MESSAGES/django.po`
via un éditeur de texte ou un logiciel dédié, comme [Poedit][23]. Une fois le travail
de traduction effectué, executez la commande suivante :
```console
python manage.py compilemessages
```
Les fichiers *.mo sont ignorés par git, il faut donc les compiler sur le serveur de prod
également.

# TODO
* update duplicate mega link for geocodes et metadatas
* update link for postgresql dump on mega
* update instructions on load data in PostgreSQL

[0]: https://www.python.org/
[1]: https://www.djangoproject.com/
[2]: https://www.mongodb.org/
[3]: https://www.postgresql.org/
[4]: https://postgis.net/
[5]: https://angularjs.org/
[6]: http://www.amcharts.com
[7]: http://leafletjs.com/
[8]: https://openlayers.org/
[9]: https://github.com
[10]: https://mega.nz/#!lccy2SBa!lwqBLAngS6HA4IL5SHwkBBwoggwqyx6ftb6MMLawElM
[11]: https://mega.nz/#!xEcQFSDB!nqFWzV4q3aIEzQ_MzpuiswzZfI5Q_ILzyl4qUWD5wMU
[12]: https://mega.nz/#!JRcgUIYD!obp-9QLvaDCVXPJ7Kp8QUPvkZdQd6W9_y2duNduwGfI
[13]: https://mega.nz/#!IRF2ka4R!49Tk7U9p1ud8ziDAL8oDxHhGFw7fkFS2L4xhm9P0HyA
[14]: https://mega.nz/#!1FsRgaiK!9DP0kNF2sRsVflqPHwWUvP_E9BYc92G1Y0EsiZfHkeY
[15]: https://theunarchiver.com/
[16]: https://www.winzip.com/win/en/xz-file.html
[17]: https://www.winzip.com/win/en/xz-file.html
[18]: https://docs.mongodb.com/manual/installation/
[19]: https://github.com/pyenv/pyenv
[20]: https://pipenv.readthedocs.io/en/latest/
[21]: https://poetry.eustace.io/docs/
[22]: https://docs.djangoproject.com/en/1.8/topics/i18n/
[23]: https://poedit.net/
