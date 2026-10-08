import json
from pathlib import Path

# Official PCGE Plan de Comptes - Modèle Normal (Classes 1 à 8)
# Extracted directly from:
# PDF pages 9 to 67 (printed pages 31 to 91),
# verified against the detailed functional specifications ("Contenu et modalités de fonctionnement des comptes", printed pages 119 to 266).

OFFICIAL_PLAN = [
    # =========================================================================
    # CLASSE 1 : COMPTES DE FINANCEMENT PERMANENT (pages 9-14, printed 31-36)
    # =========================================================================
    # 11. CAPITAUX PROPRES
    # 111. CAPITAL SOCIAL OU PERSONNEL (printed p. 31)
    {"code": "1111", "label": "Capital social", "printed_page": 31, "classe": 1},
    {"code": "1112", "label": "Fonds de dotation", "printed_page": 31, "classe": 1},
    {"code": "1117", "label": "Capital personnel", "printed_page": 31, "classe": 1},
    {"code": "11171", "label": "Capital individuel", "printed_page": 31, "classe": 1},
    {"code": "11175", "label": "Compte de l'exploitant", "printed_page": 31, "classe": 1},
    {"code": "1119", "label": "Actionnaires, capital souscrit-non appelé", "printed_page": 31, "classe": 1},
    # 112. PRIMES D'EMISSION, DE FUSION ET D'APPORT (printed p. 31)
    {"code": "1121", "label": "Primes d'émission", "printed_page": 31, "classe": 1},
    {"code": "1122", "label": "Primes de fusion", "printed_page": 31, "classe": 1},
    {"code": "1123", "label": "Primes d'apport", "printed_page": 31, "classe": 1},
    # 113. ECARTS DE REEVALUATION (printed p. 32)
    {"code": "1130", "label": "Ecarts de réévaluation", "printed_page": 32, "classe": 1},
    # 114. RESERVE LEGALE (printed p. 32)
    {"code": "1140", "label": "Réserve légale", "printed_page": 32, "classe": 1},
    # 115. AUTRES RESERVES (printed p. 32)
    {"code": "1151", "label": "Réserves statutaires ou contractuelles", "printed_page": 32, "classe": 1},
    {"code": "1152", "label": "Réserves facultatives", "printed_page": 32, "classe": 1},
    {"code": "1155", "label": "Réserves réglementées", "printed_page": 32, "classe": 1},
    # 116. REPORT A NOUVEAU (printed p. 32)
    {"code": "1161", "label": "Report à nouveau (solde créditeur)", "printed_page": 32, "classe": 1},
    {"code": "1169", "label": "Report à nouveau (solde débiteur)", "printed_page": 32, "classe": 1},
    # 118. RESULTATS NETS EN INSTANCE D'AFFECTATION (printed p. 32)
    {"code": "1181", "label": "Résultats nets en instance d'affectation (solde créditeur)", "printed_page": 32, "classe": 1},
    {"code": "1189", "label": "Résultats nets en instance d'affectation (solde débiteur)", "printed_page": 32, "classe": 1},
    # 119. RESULTAT NET DE L'EXERCICE (printed p. 32)
    {"code": "1191", "label": "Résultat net de l'exercice (créditeur)", "printed_page": 32, "classe": 1},
    {"code": "1199", "label": "Résultat net de l'exercice (débiteur)", "printed_page": 32, "classe": 1},

    # 13. CAPITAUX PROPRES ASSIMILES
    # 131. SUBVENTIONS D'INVESTISSEMENT (printed p. 33)
    {"code": "1311", "label": "Subventions d'investissement reçues", "printed_page": 33, "classe": 1},
    {"code": "1319", "label": "Subventions d'investissement inscrites au compte de produits et charges", "printed_page": 33, "classe": 1},
    # 135. PROVISIONS REGLEMENTEES (printed p. 33)
    {"code": "1351", "label": "Provisions pour amortissements dérogatoires", "printed_page": 33, "classe": 1},
    {"code": "1352", "label": "Provisions pour plus-values en instance d'imposition", "printed_page": 33, "classe": 1},
    {"code": "1354", "label": "Provisions pour investissements", "printed_page": 33, "classe": 1},
    {"code": "1355", "label": "Provisions pour reconstitution des gisements", "printed_page": 33, "classe": 1},
    {"code": "1356", "label": "Provisions pour acquisition et construction de logements", "printed_page": 33, "classe": 1},
    {"code": "1358", "label": "Autres provisions réglementées", "printed_page": 33, "classe": 1},

    # 14. DETTES DE FINANCEMENT
    # 141. EMPRUNTS OBLIGATAIRES (printed p. 34)
    {"code": "1410", "label": "Emprunts obligataires", "printed_page": 34, "classe": 1},
    # 148. AUTRES DETTES DE FINANCEMENT (printed p. 34)
    {"code": "1481", "label": "Emprunts auprès des établissements de crédit", "printed_page": 34, "classe": 1},
    {"code": "1482", "label": "Avances de l'Etat", "printed_page": 34, "classe": 1},
    {"code": "1483", "label": "Dettes rattachées à des participations", "printed_page": 34, "classe": 1},
    {"code": "1484", "label": "Billets de fonds", "printed_page": 34, "classe": 1},
    {"code": "1485", "label": "Avances reçues et comptes courants bloqués", "printed_page": 34, "classe": 1},
    {"code": "1486", "label": "Fournisseurs d'immobilisations", "printed_page": 34, "classe": 1},
    {"code": "1487", "label": "Dépôts et cautionnements reçus", "printed_page": 34, "classe": 1},
    {"code": "1488", "label": "Dettes de financement diverses", "printed_page": 34, "classe": 1},

    # 15. PROVISIONS DURABLES POUR RISQUES ET CHARGES
    # 151. PROVISIONS POUR RISQUES (printed p. 35)
    {"code": "1511", "label": "Provisions pour litiges", "printed_page": 35, "classe": 1},
    {"code": "1512", "label": "Provisions pour garanties données aux clients", "printed_page": 35, "classe": 1},
    {"code": "1513", "label": "Provisions pour propre assureur", "printed_page": 35, "classe": 1},
    {"code": "1514", "label": "Provisions pour pertes sur marchés à terme", "printed_page": 35, "classe": 1},
    {"code": "1515", "label": "Provisions pour amendes, doubles droits, pénalités", "printed_page": 35, "classe": 1},
    {"code": "1516", "label": "Provisions pour pertes de change", "printed_page": 35, "classe": 1},
    {"code": "1518", "label": "Autres provisions pour risques", "printed_page": 35, "classe": 1},
    # 155. PROVISIONS POUR CHARGES (printed p. 35)
    {"code": "1551", "label": "Provisions pour impôts", "printed_page": 35, "classe": 1},
    {"code": "1552", "label": "Provisions pour pensions de retraite et obligations similaires", "printed_page": 35, "classe": 1},
    {"code": "1555", "label": "Provisions pour charges à répartir sur plusieurs exercices", "printed_page": 35, "classe": 1},
    {"code": "1558", "label": "Autres provisions pour charges", "printed_page": 35, "classe": 1},

    # 16. COMPTES DE LIAISON DES ETABLISSEMENTS ET SUCCURSALES
    # 160. COMPTES DE LIAISON DES ETABLISSEMENTS ET SUCCURSALES (printed p. 35)
    {"code": "1601", "label": "Comptes de liaison du siège", "printed_page": 35, "classe": 1},
    {"code": "1605", "label": "Comptes de liaison des établissements", "printed_page": 35, "classe": 1},

    # 17. ECARTS DE CONVERSION - PASSIF
    # 171. AUGMENTATION DES CREANCES IMMOBILISEES (printed p. 36)
    {"code": "1710", "label": "Augmentation des créances immobilisées", "printed_page": 36, "classe": 1},
    # 172. DIMINUTION DES DETTES DE FINANCEMENT (printed p. 36)
    {"code": "1720", "label": "Diminution des dettes de financement", "printed_page": 36, "classe": 1},

    # =========================================================================
    # CLASSE 2 : COMPTES D'ACTIF IMMOBILISE (pages 15-25, printed 37-47)
    # =========================================================================
    # 21. IMMOBILISATION EN NON-VALEURS
    # 211. FRAIS PRELIMINAIRES (printed p. 37)
    {"code": "2111", "label": "Frais de constitution", "printed_page": 37, "classe": 2},
    {"code": "2112", "label": "Frais préalables au démarrage", "printed_page": 37, "classe": 2},
    {"code": "2113", "label": "Frais d'augmentation du capital", "printed_page": 37, "classe": 2},
    {"code": "2114", "label": "Frais sur opérations de fusions, scissions et transformations", "printed_page": 37, "classe": 2},
    {"code": "2116", "label": "Frais de prospection", "printed_page": 37, "classe": 2},
    {"code": "2117", "label": "Frais de publicité", "printed_page": 37, "classe": 2},
    {"code": "2118", "label": "Autres frais préliminaires", "printed_page": 37, "classe": 2},
    # 212. CHARGES A REPARTIR SUR PLUSIEURS EXERCICES (printed p. 37)
    {"code": "2121", "label": "Frais d'acquisition des immobilisations", "printed_page": 37, "classe": 2},
    {"code": "2125", "label": "Frais d'émission des emprunts", "printed_page": 37, "classe": 2},
    {"code": "2128", "label": "Autres charges à répartir", "printed_page": 37, "classe": 2},
    # 213. PRIMES DE REMBOURSEMENT DES OBLIGATIONS (printed p. 37)
    {"code": "2130", "label": "Primes de remboursement des obligations", "printed_page": 37, "classe": 2},

    # 22. IMMOBILISATIONS INCORPORELLES
    # 221. IMMOBILISATION EN RECHERCHE ET DEVELOPPEMENT (printed p. 38)
    {"code": "2210", "label": "Immobilisation en recherche et développement", "printed_page": 38, "classe": 2},
    # 222. BREVETS, MARQUES, DROITS ET VALEURS SIMILAIRES (printed p. 38)
    {"code": "2220", "label": "Brevets, marques, droits et valeurs similaires", "printed_page": 38, "classe": 2},
    # 223. FONDS COMMERCIAL (printed p. 38)
    {"code": "2230", "label": "Fonds commercial", "printed_page": 38, "classe": 2},
    # 228. AUTRES IMMOBILISATIONS INCORPORELLES (printed p. 38)
    {"code": "2285", "label": "Immobilisations incorporelles en cours", "printed_page": 38, "classe": 2},

    # 23. IMMOBILISATIONS CORPORELLES
    # 231. TERRAINS (printed p. 39)
    {"code": "2311", "label": "Terrains nus", "printed_page": 39, "classe": 2},
    {"code": "2312", "label": "Terrains aménagés", "printed_page": 39, "classe": 2},
    {"code": "2313", "label": "Terrains bâtis", "printed_page": 39, "classe": 2},
    {"code": "2314", "label": "Terrains de gisement", "printed_page": 39, "classe": 2},
    {"code": "2316", "label": "Agencements et aménagements de terrains", "printed_page": 39, "classe": 2},
    {"code": "2318", "label": "Autres terrains", "printed_page": 39, "classe": 2},
    # 232. CONSTRUCTIONS (printed p. 39)
    {"code": "2321", "label": "Bâtiments", "printed_page": 39, "classe": 2},
    {"code": "23211", "label": "Bâtiments industriels (A, B...)", "printed_page": 39, "classe": 2},
    {"code": "23214", "label": "Bâtiments administratifs et commerciaux (A, B...)", "printed_page": 39, "classe": 2},
    {"code": "23218", "label": "Autres bâtiments", "printed_page": 39, "classe": 2},
    {"code": "2323", "label": "Constructions sur terrains d'autrui", "printed_page": 39, "classe": 2},
    {"code": "2325", "label": "Ouvrages d'infrastructure", "printed_page": 39, "classe": 2},
    {"code": "2327", "label": "Agencements et aménagements des constructions", "printed_page": 39, "classe": 2},
    {"code": "2328", "label": "Autres constructions", "printed_page": 39, "classe": 2},
    # 233. INSTALLATIONS TECHNIQUES, MATERIEL ET OUTILLAGE (printed p. 40)
    {"code": "2331", "label": "Installations techniques", "printed_page": 40, "classe": 2},
    {"code": "2332", "label": "Matériel et outillage", "printed_page": 40, "classe": 2},
    {"code": "23321", "label": "Matériel", "printed_page": 40, "classe": 2},
    {"code": "23324", "label": "Outillage", "printed_page": 40, "classe": 2},
    {"code": "2333", "label": "Emballages récupérables identifiables", "printed_page": 40, "classe": 2},
    {"code": "2338", "label": "Autres installations techniques, matériel et outillage", "printed_page": 40, "classe": 2},
    # 234. MATERIEL DE TRANSPORT (printed p. 40)
    {"code": "2340", "label": "Matériel de transport", "printed_page": 40, "classe": 2},
    # 235. MOBILIER, MATERIEL DE BUREAU ET AMENAGEMENTS DIVERS (printed p. 40)
    {"code": "2351", "label": "Mobilier de bureau", "printed_page": 40, "classe": 2},
    {"code": "2352", "label": "Matériel de bureau", "printed_page": 40, "classe": 2},
    {"code": "2355", "label": "Matériel informatique", "printed_page": 40, "classe": 2},
    {"code": "2356", "label": "Agencements, installations et aménagements divers (biens n'appartenant pas à l'entreprise)", "printed_page": 40, "classe": 2},
    {"code": "2358", "label": "Autres mobilier, matériel de bureau et aménagements divers", "printed_page": 40, "classe": 2},
    # 238. AUTRES IMMOBILISATIONS CORPORELLES (printed p. 40)
    {"code": "2380", "label": "Autres immobilisations corporelles", "printed_page": 40, "classe": 2},
    # 239. IMMOBILISATIONS CORPORELLES EN COURS (printed p. 41)
    {"code": "2392", "label": "Immobilisations corporelles en cours de terrains et constructions", "printed_page": 41, "classe": 2},
    {"code": "2393", "label": "Immobilisations corporelles en cours des installations techniques, matériel et outillage", "printed_page": 41, "classe": 2},
    {"code": "2394", "label": "Immobilisations corporelles en cours de matériel de transport", "printed_page": 41, "classe": 2},
    {"code": "2395", "label": "Immobilisations corporelles en cours de mobilier, matériel de bureau et aménagements divers", "printed_page": 41, "classe": 2},
    {"code": "2397", "label": "Avances et acomptes versés sur commandes d'immobilisations corporelles", "printed_page": 41, "classe": 2},
    {"code": "2398", "label": "Autres immobilisations corporelles en cours", "printed_page": 41, "classe": 2},

    # 24/25. IMMOBILISATIONS FINANCIERES
    # 241. PRETS IMMOBILISES (printed p. 42)
    {"code": "2411", "label": "Prêts au personnel", "printed_page": 42, "classe": 2},
    {"code": "2415", "label": "Prêts aux associés", "printed_page": 42, "classe": 2},
    {"code": "2416", "label": "Billets de fonds", "printed_page": 42, "classe": 2},
    {"code": "2418", "label": "Autres prêts", "printed_page": 42, "classe": 2},
    # 248. AUTRES CREANCES FINANCIERES (printed p. 42)
    {"code": "2481", "label": "Titres immobilisés (droits de créance)", "printed_page": 42, "classe": 2},
    {"code": "24811", "label": "Obligations", "printed_page": 42, "classe": 2},
    {"code": "24813", "label": "Bons d'équipement", "printed_page": 42, "classe": 2},
    {"code": "24818", "label": "Bons divers", "printed_page": 42, "classe": 2},
    {"code": "2483", "label": "Créances rattachées à des participations", "printed_page": 42, "classe": 2},
    {"code": "2486", "label": "Dépôts et cautionnements versés", "printed_page": 42, "classe": 2},
    {"code": "24861", "label": "Dépôts", "printed_page": 42, "classe": 2},
    {"code": "24864", "label": "Cautionnements", "printed_page": 42, "classe": 2},
    {"code": "2487", "label": "Créances immobilisées", "printed_page": 42, "classe": 2},
    {"code": "2488", "label": "Créances financières diverses", "printed_page": 42, "classe": 2},
    # 251. TITRES DE PARTICIPATION (printed p. 42)
    {"code": "2510", "label": "Titres de participation", "printed_page": 42, "classe": 2},
    # 258. AUTRES TITRES IMMOBILISES (DROITS DE PROPRIETE) (printed p. 42)
    {"code": "2581", "label": "Actions", "printed_page": 42, "classe": 2},
    {"code": "2588", "label": "Titres divers", "printed_page": 42, "classe": 2},

    # 27. ECARTS DE CONVERSION - ACTIF
    # 271. DIMINUTION DES CREANCES IMMOBILISEES (printed p. 43)
    {"code": "2710", "label": "Diminution des créances immobilisées", "printed_page": 43, "classe": 2},
    # 272. AUGMENTATION DES DETTES DE FINANCEMENT (printed p. 43)
    {"code": "2720", "label": "Augmentation des dettes de financement", "printed_page": 43, "classe": 2},

    # 28. AMORTISSEMENTS DES IMMOBILISATIONS
    # 281. AMORTISSEMENTS DES NON-VALEURS (printed p. 44)
    {"code": "2811", "label": "Amortissements des Frais préliminaires", "printed_page": 44, "classe": 2},
    {"code": "28111", "label": "Amortissements des Frais de constitution", "printed_page": 44, "classe": 2},
    {"code": "28112", "label": "Amortissements des Frais préliminaires au démarrage", "printed_page": 44, "classe": 2},
    {"code": "28113", "label": "Amortissements des Frais d'augmentation du capital", "printed_page": 44, "classe": 2},
    {"code": "28114", "label": "Amortissements des Frais sur opérations de fusions, scissions et transformations", "printed_page": 44, "classe": 2},
    {"code": "28116", "label": "Amortissements des Frais de prospection", "printed_page": 44, "classe": 2},
    {"code": "28117", "label": "Amortissements des Frais de publicité", "printed_page": 44, "classe": 2},
    {"code": "28118", "label": "Amortissements des Autres frais préliminaires", "printed_page": 44, "classe": 2},
    {"code": "2812", "label": "Amortissements des charges à répartir", "printed_page": 44, "classe": 2},
    {"code": "28121", "label": "Amortissements des Frais d'acquisition des immobilisations", "printed_page": 44, "classe": 2},
    {"code": "28125", "label": "Amortissements des frais d'émission des emprunts", "printed_page": 44, "classe": 2},
    {"code": "28128", "label": "Amortissements des Autres charges à répartir", "printed_page": 44, "classe": 2},
    {"code": "2813", "label": "Amortissements des primes de remboursement des obligations", "printed_page": 44, "classe": 2},
    # 282. AMORTISSEMENTS DES IMMOBILISATIONS INCORPORELLES (printed p. 44-45)
    {"code": "2821", "label": "Amortissements de l'immobilisation en recherche et développement", "printed_page": 44, "classe": 2},
    {"code": "2822", "label": "Amortissements des brevets, marques, droits et valeurs similaires", "printed_page": 44, "classe": 2},
    {"code": "2823", "label": "Amortissements du Fonds commercial", "printed_page": 45, "classe": 2},
    {"code": "2828", "label": "Amortissements des autres immobilisations incorporelles", "printed_page": 45, "classe": 2},
    # 283. AMORTISSEMENTS DES IMMOBILISATIONS CORPORELLES (printed p. 45-46)
    {"code": "2831", "label": "Amortissements des Terrains", "printed_page": 45, "classe": 2},
    {"code": "28311", "label": "Amortissements des terrains nus", "printed_page": 45, "classe": 2},
    {"code": "28312", "label": "Amortissements des terrains aménagés", "printed_page": 45, "classe": 2},
    {"code": "28313", "label": "Amortissements des terrains bâtis", "printed_page": 45, "classe": 2},
    {"code": "28314", "label": "Amortissements des Terrains de gisement", "printed_page": 45, "classe": 2},
    {"code": "28316", "label": "Amortissements des agencements et aménagements de terrains", "printed_page": 45, "classe": 2},
    {"code": "28318", "label": "Amortissements des autres terrains", "printed_page": 45, "classe": 2},
    {"code": "2832", "label": "Amortissements des constructions", "printed_page": 45, "classe": 2},
    {"code": "28321", "label": "Amortissements des bâtiments", "printed_page": 45, "classe": 2},
    {"code": "28323", "label": "Amortissements des Constructions sur terrains d'autrui", "printed_page": 45, "classe": 2},
    {"code": "28325", "label": "Amortissements des ouvrages d'infrastructure", "printed_page": 45, "classe": 2},
    {"code": "28327", "label": "Amortissements des installations, agencements et aménagements des constructions", "printed_page": 45, "classe": 2},
    {"code": "28328", "label": "Amortissements des Autres constructions", "printed_page": 45, "classe": 2},
    {"code": "2833", "label": "Amortissements des installations techniques, matériel et outillage", "printed_page": 45, "classe": 2},
    {"code": "28331", "label": "Amortissements des installations techniques", "printed_page": 45, "classe": 2},
    {"code": "28332", "label": "Amortissements du matériel et outillage", "printed_page": 45, "classe": 2},
    {"code": "28333", "label": "Amortissements des emballages récupérables identifiables", "printed_page": 45, "classe": 2},
    {"code": "28338", "label": "Amortissements des autres installations techniques, matériel et outillage", "printed_page": 46, "classe": 2},
    {"code": "2834", "label": "Amortissements du matériel de transport", "printed_page": 46, "classe": 2},
    {"code": "2835", "label": "Amortissements du mobilier, matériel de bureau et aménagements divers", "printed_page": 46, "classe": 2},
    {"code": "28351", "label": "Amortissements du mobilier de bureau", "printed_page": 46, "classe": 2},
    {"code": "28352", "label": "Amortissements du matériel de bureau", "printed_page": 46, "classe": 2},
    {"code": "28355", "label": "Amortissements du matériel informatique", "printed_page": 46, "classe": 2},
    {"code": "28356", "label": "Amortissements des agencements, installations et aménagements divers", "printed_page": 46, "classe": 2},
    {"code": "28358", "label": "Amortissements des autres mobilier, matériel de bureau et aménagements divers", "printed_page": 46, "classe": 2},
    {"code": "2838", "label": "Amortissements des autres immobilisations corporelles", "printed_page": 46, "classe": 2},

    # 29. PROVISIONS POUR DEPRECIATION DES IMMOBILISATIONS
    # 292. PROVISIONS POUR DEPRECIATION DES IMMOBILISATIONS INCORPORELLES (printed p. 47)
    {"code": "2920", "label": "Provisions pour dépréciation des immobilisations incorporelles", "printed_page": 47, "classe": 2},
    # 293. PROVISIONS POUR DEPRECIATION DES IMMOBILISATIONS CORPORELLES (printed p. 47)
    {"code": "2930", "label": "Provisions pour dépréciation des immobilisations corporelles", "printed_page": 47, "classe": 2},
    # 294/295. PROVISIONS POUR DEPRECIATION DES IMMOBILISATIONS FINANCIERES (printed p. 47)
    {"code": "2941", "label": "Provisions pour dépréciation des prêts immobilisés", "printed_page": 47, "classe": 2},
    {"code": "2948", "label": "Provisions pour dépréciation des autres créances financières", "printed_page": 47, "classe": 2},
    {"code": "2951", "label": "Provisions pour dépréciation des titres de participation", "printed_page": 47, "classe": 2},
    {"code": "2958", "label": "Provisions pour dépréciation des autres titres immobilisés", "printed_page": 47, "classe": 2},

    # =========================================================================
    # CLASSE 3 : COMPTES D'ACTIF CIRCULANT (HORS TRESORERIE) (pages 27-33, printed 49-55)
    # =========================================================================
    # 31. STOCKS
    # 311. MARCHANDISES (printed p. 49)
    {"code": "3111", "label": "Marchandises (groupe A)", "printed_page": 49, "classe": 3},
    {"code": "3112", "label": "Marchandises (groupe B)", "printed_page": 49, "classe": 3},
    {"code": "3116", "label": "Marchandises en cours de route", "printed_page": 49, "classe": 3},
    {"code": "3118", "label": "Autres marchandises", "printed_page": 49, "classe": 3},
    # 312. MATIERES ET FOURNITURES CONSOMMABLES (printed p. 49-50)
    {"code": "3121", "label": "Matières premières", "printed_page": 49, "classe": 3},
    {"code": "31211", "label": "Matières premières (groupe A)", "printed_page": 49, "classe": 3},
    {"code": "31212", "label": "Matières premières (groupe B)", "printed_page": 49, "classe": 3},
    {"code": "3122", "label": "Matières et fournitures consommables", "printed_page": 49, "classe": 3},
    {"code": "31221", "label": "Matières consommables (groupe A)", "printed_page": 49, "classe": 3},
    {"code": "31222", "label": "Matières consommables (groupe B)", "printed_page": 49, "classe": 3},
    {"code": "31223", "label": "Combustibles", "printed_page": 49, "classe": 3},
    {"code": "31224", "label": "Produits d'entretien", "printed_page": 49, "classe": 3},
    {"code": "31225", "label": "Fournitures d'atelier et d'usine", "printed_page": 49, "classe": 3},
    {"code": "31226", "label": "Fournitures de magasin", "printed_page": 49, "classe": 3},
    {"code": "31227", "label": "Fournitures de bureau", "printed_page": 49, "classe": 3},
    {"code": "3123", "label": "Emballages", "printed_page": 50, "classe": 3},
    {"code": "31231", "label": "Emballages perdus", "printed_page": 50, "classe": 3},
    {"code": "31232", "label": "Emballages récupérables non identifiables", "printed_page": 50, "classe": 3},
    {"code": "31233", "label": "Emballages à usage mixte", "printed_page": 50, "classe": 3},
    {"code": "3126", "label": "Matières et fournitures consommables en cours de route", "printed_page": 50, "classe": 3},
    {"code": "3128", "label": "Autres matières et fournitures consommables", "printed_page": 50, "classe": 3},
    # 313. PRODUITS EN COURS (printed p. 50)
    {"code": "3131", "label": "Biens en cours", "printed_page": 50, "classe": 3},
    {"code": "31311", "label": "Biens produits en cours", "printed_page": 50, "classe": 3},
    {"code": "31312", "label": "Biens intermédiaires en cours", "printed_page": 50, "classe": 3},
    {"code": "31317", "label": "Biens résiduels en cours", "printed_page": 50, "classe": 3},
    {"code": "3134", "label": "Services en cours", "printed_page": 50, "classe": 3},
    {"code": "31341", "label": "Travaux en cours", "printed_page": 50, "classe": 3},
    {"code": "31342", "label": "Etudes en cours", "printed_page": 50, "classe": 3},
    {"code": "31343", "label": "Prestations en cours", "printed_page": 50, "classe": 3},
    {"code": "3138", "label": "Autres produits en cours", "printed_page": 50, "classe": 3},
    # 314. PRODUITS INTERMEDIAIRES ET PRODUITS RESIDUELS (printed p. 50)
    {"code": "3141", "label": "Produits intermédiaires", "printed_page": 50, "classe": 3},
    {"code": "31411", "label": "Produits intermédiaires (groupe A)", "printed_page": 50, "classe": 3},
    {"code": "31412", "label": "Produits intermédiaires (groupe B)", "printed_page": 50, "classe": 3},
    {"code": "3145", "label": "Produits résiduels (ou matières de récupération)", "printed_page": 50, "classe": 3},
    {"code": "31451", "label": "Déchets", "printed_page": 50, "classe": 3},
    {"code": "31452", "label": "Rebuts", "printed_page": 50, "classe": 3},
    {"code": "31453", "label": "Matières de récupération", "printed_page": 50, "classe": 3},
    {"code": "3148", "label": "Autres produits intermédiaires et produits résiduels", "printed_page": 50, "classe": 3},
    # 315. PRODUITS FINIS (printed p. 51)
    {"code": "3151", "label": "Produits finis (groupe A)", "printed_page": 51, "classe": 3},
    {"code": "3152", "label": "Produits finis (groupe B)", "printed_page": 51, "classe": 3},
    {"code": "3156", "label": "Produits finis en cours de route", "printed_page": 51, "classe": 3},
    {"code": "3158", "label": "Autres produits finis", "printed_page": 51, "classe": 3},

    # 34. CREANCES DE L'ACTIF CIRCULANT
    # 341. FOURNISSEURS DEBITEURS, AVANCES ET ACOMPTES (printed p. 52)
    {"code": "3411", "label": "Fournisseurs - avances et acomptes versés sur commandes d'exploitation", "printed_page": 52, "classe": 3},
    {"code": "3413", "label": "Fournisseurs - créances pour emballages et matériel à rendre", "printed_page": 52, "classe": 3},
    {"code": "3417", "label": "Rabais, remises et ristournes à obtenir-avoirs non encore reçus", "printed_page": 52, "classe": 3},
    {"code": "3418", "label": "Autres fournisseurs débiteurs", "printed_page": 52, "classe": 3},
    # 342. CLIENTS ET COMPTES RATTACHES (printed p. 52)
    {"code": "3421", "label": "Clients", "printed_page": 52, "classe": 3},
    {"code": "34211", "label": "Clients - catégorie A", "printed_page": 52, "classe": 3},
    {"code": "34212", "label": "Clients - catégorie B", "printed_page": 52, "classe": 3},
    {"code": "3423", "label": "Clients - retenues de garantie", "printed_page": 52, "classe": 3},
    {"code": "3424", "label": "Clients douteux ou litigieux", "printed_page": 52, "classe": 3},
    {"code": "3425", "label": "Clients - effets à recevoir", "printed_page": 52, "classe": 3},
    {"code": "3427", "label": "Clients - factures à établir et créances sur travaux non encore facturables", "printed_page": 52, "classe": 3},
    {"code": "34271", "label": "Clients - factures à établir", "printed_page": 52, "classe": 3},
    {"code": "34272", "label": "Créances sur travaux non encore facturables", "printed_page": 52, "classe": 3},
    {"code": "3428", "label": "Autres clients et comptes rattachés", "printed_page": 52, "classe": 3},
    # 343. PERSONNEL - DEBITEUR (printed p. 52)
    {"code": "3431", "label": "Avances et acomptes au personnel", "printed_page": 52, "classe": 3},
    {"code": "3438", "label": "Personnel - autres débiteurs", "printed_page": 52, "classe": 3},
    # 345. ETAT - DEBITEUR (printed p. 53)
    {"code": "3451", "label": "Subventions à recevoir", "printed_page": 53, "classe": 3},
    {"code": "34511", "label": "Subventions d'investissement à recevoir", "printed_page": 53, "classe": 3},
    {"code": "34512", "label": "Subventions d'exploitation à recevoir", "printed_page": 53, "classe": 3},
    {"code": "34513", "label": "Subventions d'équilibre à recevoir", "printed_page": 53, "classe": 3},
    {"code": "3453", "label": "Acomptes sur impôts sur les résultats", "printed_page": 53, "classe": 3},
    {"code": "3455", "label": "Etat - T.V.A. Récupérable", "printed_page": 53, "classe": 3},
    {"code": "34551", "label": "Etat - T.V.A. récupérable sur immobilisations", "printed_page": 53, "classe": 3},
    {"code": "34552", "label": "Etat - T.V.A. récupérable sur les charges", "printed_page": 53, "classe": 3},
    {"code": "3456", "label": "Etat - Crédit de T.V.A. (suivant déclarations)", "printed_page": 53, "classe": 3},
    {"code": "3458", "label": "Etat - Autres comptes débiteurs", "printed_page": 53, "classe": 3},
    # 346. COMPTES D'ASSOCIES - DEBITEURS (printed p. 53)
    {"code": "3461", "label": "Associés - comptes d'apport en société", "printed_page": 53, "classe": 3},
    {"code": "3462", "label": "Actionnaires - capital souscrit et appelé non versé", "printed_page": 53, "classe": 3},
    {"code": "3463", "label": "Comptes courants des associés débiteurs", "printed_page": 53, "classe": 3},
    {"code": "3464", "label": "Associés - opérations faites en commun", "printed_page": 53, "classe": 3},
    {"code": "3467", "label": "Créances rattachées aux comptes d'associés", "printed_page": 53, "classe": 3},
    {"code": "3468", "label": "Autres comptes d'associés débiteurs", "printed_page": 53, "classe": 3},
    # 348. AUTRES DEBITEURS (printed p. 54)
    {"code": "3481", "label": "Créances sur cessions d'immobilisations", "printed_page": 54, "classe": 3},
    {"code": "3482", "label": "Créances sur cessions d'éléments d'actif circulant", "printed_page": 54, "classe": 3},
    {"code": "3487", "label": "Créances rattachées aux autres débiteurs", "printed_page": 54, "classe": 3},
    {"code": "3488", "label": "Divers débiteurs", "printed_page": 54, "classe": 3},
    # 349. COMPTES DE REGULARISATION - ACTIF (printed p. 54)
    {"code": "3491", "label": "Charges constatées d'avance", "printed_page": 54, "classe": 3},
    {"code": "3493", "label": "Intérêts courus et non échus à percevoir", "printed_page": 54, "classe": 3},
    {"code": "3495", "label": "Comptes de répartition périodique des charges", "printed_page": 54, "classe": 3},
    {"code": "3497", "label": "Comptes transitoires ou d'attente - débiteurs", "printed_page": 54, "classe": 3},

    # 35. TITRES ET VALEURS DE PLACEMENT
    # 350. TITRES ET VALEURS DE PLACEMENT (printed p. 54)
    {"code": "3501", "label": "Actions, partie libérée", "printed_page": 54, "classe": 3},
    {"code": "3502", "label": "Actions, partie non libérée", "printed_page": 54, "classe": 3},
    {"code": "3504", "label": "Obligations", "printed_page": 54, "classe": 3},
    {"code": "3506", "label": "Bons de caisse et bons du Trésor", "printed_page": 54, "classe": 3},
    {"code": "35061", "label": "Bons de caisse", "printed_page": 54, "classe": 3},
    {"code": "35062", "label": "Bons du Trésor", "printed_page": 54, "classe": 3},
    {"code": "3508", "label": "Autres titres et valeurs de placement similaires", "printed_page": 54, "classe": 3},

    # 37. ECARTS DE CONVERSION - ACTIF (ELEMENTS CIRCULANTS)
    # 370. ECARTS DE CONVERSION - ACTIF (ELEMENTS CIRCULANTS) (printed p. 54)
    {"code": "3701", "label": "Diminution des créances circulantes", "printed_page": 54, "classe": 3},
    {"code": "3702", "label": "Augmentation des dettes circulantes", "printed_page": 54, "classe": 3},

    # 39. PROVISIONS POUR DEPRECIATION DES COMPTES DE L'ACTIF CIRCULANT
    # 391. PROVISIONS POUR DEPRECIATION DES STOCKS (printed p. 55)
    {"code": "3911", "label": "Provisions pour dépréciation des marchandises", "printed_page": 55, "classe": 3},
    {"code": "3912", "label": "Provisions pour dépréciation des matières et fournitures", "printed_page": 55, "classe": 3},
    {"code": "3913", "label": "Provisions pour dépréciation des produits en cours", "printed_page": 55, "classe": 3},
    {"code": "3914", "label": "Provisions pour dépréciation des produits intermédiaires", "printed_page": 55, "classe": 3},
    {"code": "3915", "label": "Provisions pour dépréciation des produits finis", "printed_page": 55, "classe": 3},
    # 394. PROVISIONS POUR DEPRECIATION DES CREANCES DE L'ACTIF CIRCULANT (printed p. 55)
    {"code": "3941", "label": "Provisions pour dépréciation-fournisseurs débiteurs, avances et acomptes", "printed_page": 55, "classe": 3},
    {"code": "3942", "label": "Provisions pour dépréciation des clients et comptes rattachés", "printed_page": 55, "classe": 3},
    {"code": "3943", "label": "Provisions pour dépréciation du personnel - débiteur", "printed_page": 55, "classe": 3},
    {"code": "3946", "label": "Provisions pour dépréciation des comptes d'associés débiteurs", "printed_page": 55, "classe": 3},
    {"code": "3948", "label": "Provisions pour dépréciation des autres débiteurs", "printed_page": 55, "classe": 3},
    # 395. PROVISIONS POUR DEPRECIATION DES TITRES ET VALEURS DE PLACEMENT (printed p. 55)
    {"code": "3950", "label": "Provisions pour dépréciation des titres et valeurs de placement", "printed_page": 55, "classe": 3},

    # =========================================================================
    # CLASSE 4 : COMPTES DE PASSIF CIRCULANT (HORS TRESORERIE) (pages 34-37, printed 57-60)
    # =========================================================================
    # 44. DETTES DU PASSIF CIRCULANT
    # 441. FOURNISSEURS ET COMPTES RATTACHES (printed p. 57)
    {"code": "4411", "label": "Fournisseurs", "printed_page": 57, "classe": 4},
    {"code": "44111", "label": "Fournisseurs - catégorie A", "printed_page": 57, "classe": 4},
    {"code": "44112", "label": "Fournisseurs - catégorie B", "printed_page": 57, "classe": 4},
    {"code": "4413", "label": "Fournisseurs - retenues de garantie", "printed_page": 57, "classe": 4},
    {"code": "4415", "label": "Fournisseurs - effets à payer", "printed_page": 57, "classe": 4},
    {"code": "4417", "label": "Fournisseurs - factures non parvenues", "printed_page": 57, "classe": 4},
    {"code": "4418", "label": "Autres fournisseurs et comptes rattachés", "printed_page": 57, "classe": 4},
    # 442. CLIENTS CREDITEURS, AVANCES ET ACOMPTES (printed p. 58)
    {"code": "4421", "label": "Clients - avances et acomptes reçus sur commandes en cours", "printed_page": 58, "classe": 4},
    {"code": "4425", "label": "Clients - Dettes pour emballages et matériel consignés", "printed_page": 58, "classe": 4},
    {"code": "4427", "label": "Rabais, remises et ristournes à accorder - avoirs à établir", "printed_page": 58, "classe": 4},
    {"code": "4428", "label": "Autres clients créditeurs", "printed_page": 58, "classe": 4},
    # 443. PERSONNEL - CREDITEUR (printed p. 58)
    {"code": "4432", "label": "Rémunérations dues au personnel", "printed_page": 58, "classe": 4},
    {"code": "4433", "label": "Dépôts du personnel créditeurs", "printed_page": 58, "classe": 4},
    {"code": "4434", "label": "Oppositions sur salaires", "printed_page": 58, "classe": 4},
    {"code": "4437", "label": "Charges du personnel à payer", "printed_page": 58, "classe": 4},
    {"code": "4438", "label": "Personnel - autres créditeurs", "printed_page": 58, "classe": 4},
    # 444. ORGANISMES SOCIAUX (printed p. 58)
    {"code": "4441", "label": "Caisse Nationale de la Sécurité Sociale", "printed_page": 58, "classe": 4},
    {"code": "4443", "label": "Caisses de retraite", "printed_page": 58, "classe": 4},
    {"code": "4445", "label": "Mutuelles", "printed_page": 58, "classe": 4},
    {"code": "4447", "label": "Charges sociales à payer", "printed_page": 58, "classe": 4},
    {"code": "4448", "label": "Autres organismes sociaux", "printed_page": 58, "classe": 4},
    # 445. ETAT - CREDITEUR (printed p. 58-59)
    {"code": "4452", "label": "Etat Impôts, taxes et assimilés", "printed_page": 58, "classe": 4},
    {"code": "44521", "label": "Etat, taxe urbaine et taxe d'édilité", "printed_page": 58, "classe": 4},
    {"code": "44522", "label": "Etat, patente", "printed_page": 58, "classe": 4},
    {"code": "44525", "label": "Etat, PTS et PSN", "printed_page": 58, "classe": 4},
    {"code": "4453", "label": "Etat, impôts sur les résultats", "printed_page": 58, "classe": 4},
    {"code": "4455", "label": "Etat, T V A facturée", "printed_page": 58, "classe": 4},
    {"code": "4456", "label": "Etat, T V A due (suivant déclarations)", "printed_page": 58, "classe": 4},
    {"code": "4457", "label": "Etat, impôts et taxes à payer", "printed_page": 59, "classe": 4},
    {"code": "4458", "label": "Etat - Autres comptes créditeurs", "printed_page": 59, "classe": 4},
    # 446. COMPTES D'ASSOCIES - CREDITEURS (printed p. 59)
    {"code": "4461", "label": "Associés - capital à rembourser", "printed_page": 59, "classe": 4},
    {"code": "4462", "label": "Associés - versements reçus sur augmentation de capital", "printed_page": 59, "classe": 4},
    {"code": "4463", "label": "Comptes courants des associés créditeurs", "printed_page": 59, "classe": 4},
    {"code": "4464", "label": "Associés - opérations faites en commun", "printed_page": 59, "classe": 4},
    {"code": "4465", "label": "Associés Dividendes à payer", "printed_page": 59, "classe": 4},
    {"code": "4468", "label": "Autres comptes d'associés - créditeurs", "printed_page": 59, "classe": 4},
    # 448. AUTRES CREANCIERS (printed p. 59)
    {"code": "4481", "label": "Dettes sur acquisition d'immobilisations", "printed_page": 59, "classe": 4},
    {"code": "4483", "label": "Dettes sur acquisitions de titres et valeurs de placement", "printed_page": 59, "classe": 4},
    {"code": "4484", "label": "Obligations échues à rembourser", "printed_page": 59, "classe": 4},
    {"code": "4485", "label": "Obligations, coupons à payer", "printed_page": 59, "classe": 4},
    {"code": "4487", "label": "Dettes rattachées aux autres créanciers", "printed_page": 59, "classe": 4},
    {"code": "4488", "label": "Divers créanciers", "printed_page": 59, "classe": 4},
    # 449. COMPTES DE REGULARISATION - PASSIF (printed p. 59)
    {"code": "4491", "label": "Produits constatés d'avance", "printed_page": 59, "classe": 4},
    {"code": "4493", "label": "Intérêts courus et non échus à payer", "printed_page": 59, "classe": 4},
    {"code": "4495", "label": "Comptes de répartition périodique des produits", "printed_page": 59, "classe": 4},
    {"code": "4497", "label": "Comptes transitoires ou d'attente - créditeurs", "printed_page": 59, "classe": 4},

    # 45. AUTRES PROVISIONS POUR RISQUES ET CHARGES
    # 450. AUTRES PROVISIONS POUR RISQUES ET CHARGES (printed p. 60)
    {"code": "4501", "label": "Provisions pour litiges", "printed_page": 60, "classe": 4},
    {"code": "4502", "label": "Provisions pour garanties données aux clients", "printed_page": 60, "classe": 4},
    {"code": "4505", "label": "Provisions pour amendes, doubles droits et pénalités", "printed_page": 60, "classe": 4},
    {"code": "4506", "label": "Provisions pour pertes de change", "printed_page": 60, "classe": 4},
    {"code": "4507", "label": "Provisions pour impôts", "printed_page": 60, "classe": 4},
    {"code": "4508", "label": "Autres provisions pour risques et charges", "printed_page": 60, "classe": 4},

    # 47. ECARTS DE CONVERSION - PASSIF (ELEMENTS CIRCULANTS)
    # 470. ECARTS DE CONVERSION - PASSIF (ELEMENTS CIRCULANTS) (printed p. 60)
    {"code": "4701", "label": "Augmentation des créances circulantes", "printed_page": 60, "classe": 4},
    {"code": "4702", "label": "Diminution des dettes circulantes", "printed_page": 60, "classe": 4},

    # =========================================================================
    # CLASSE 5 : COMPTES DE TRESORERIE (pages 38-39, printed 61-62)
    # =========================================================================
    # 51. TRESORERIE - ACTIF
    # 511. CHEQUES ET VALEURS A ENCAISSER (printed p. 61)
    {"code": "5111", "label": "Chèques à encaisser ou à l'encaissement", "printed_page": 61, "classe": 5},
    {"code": "51111", "label": "Chèques en portefeuille", "printed_page": 61, "classe": 5},
    {"code": "51112", "label": "Chèques à l'encaissement", "printed_page": 61, "classe": 5},
    {"code": "5113", "label": "Effets à encaisser ou à l'encaissement", "printed_page": 61, "classe": 5},
    {"code": "51131", "label": "Effets échus à encaisser", "printed_page": 61, "classe": 5},
    {"code": "51132", "label": "Effets à l'encaissement", "printed_page": 61, "classe": 5},
    {"code": "5115", "label": "Virements de fonds", "printed_page": 61, "classe": 5},
    {"code": "5118", "label": "Autres valeurs à encaisser", "printed_page": 61, "classe": 5},
    # 514. BANQUES, TRESORERIE GENERALE ET CHEQUES POSTAUX DEBITEURS (printed p. 61)
    {"code": "5141", "label": "Banques (soldes débiteurs)", "printed_page": 61, "classe": 5},
    {"code": "5143", "label": "Trésorerie Générale", "printed_page": 61, "classe": 5},
    {"code": "5146", "label": "Chèques postaux", "printed_page": 61, "classe": 5},
    {"code": "5148", "label": "Autres établissements financiers et assimilés (soldes débiteurs)", "printed_page": 61, "classe": 5},
    # 516. CAISSES, REGIES D'AVANCES ET ACCREDITIFS (printed p. 62)
    {"code": "5161", "label": "Caisses", "printed_page": 62, "classe": 5},
    {"code": "51611", "label": "Caisse centrale", "printed_page": 62, "classe": 5},
    {"code": "51613", "label": "Caisse (succursale ou agence A)", "printed_page": 62, "classe": 5},
    {"code": "51614", "label": "Caisse (succursale ou agence B)", "printed_page": 62, "classe": 5},
    {"code": "5165", "label": "Régies d'avances et accréditifs", "printed_page": 62, "classe": 5},

    # 55. TRESORERIE - PASSIF
    # 552. CREDITS D'ESCOMPTE (printed p. 62)
    {"code": "5520", "label": "Crédits d'escompte", "printed_page": 62, "classe": 5},
    # 553. CREDITS DE TRESORERIE (printed p. 62)
    {"code": "5530", "label": "Crédits de trésorerie", "printed_page": 62, "classe": 5},
    # 554. BANQUES (SOLDES CREDITEURS) (printed p. 62)
    {"code": "5541", "label": "Banques (soldes créditeurs)", "printed_page": 62, "classe": 5},
    {"code": "5548", "label": "Autres établissements financiers et assimilés (soldes créditeurs)", "printed_page": 62, "classe": 5},

    # 59. PROVISIONS POUR DEPRECIATION DES COMPTES DE TRESORERIE
    # 590. PROVISIONS POUR DEPRECIATION DES COMPTES DE TRESORERIE (printed p. 62)
    {"code": "5900", "label": "Provisions pour dépréciation des comptes de trésorerie", "printed_page": 62, "classe": 5},

    # =========================================================================
    # CLASSE 6 : COMPTES DE CHARGES (pages 40-54, printed 63-77)
    # =========================================================================
    # 61. CHARGES D'EXPLOITATION
    # 611. ACHATS REVENDUS DE MARCHANDISES (printed p. 63)
    {"code": "6111", "label": "Achats de marchandises \"groupe A\"", "printed_page": 63, "classe": 6},
    {"code": "6112", "label": "Achats de marchandises \"groupe B\"", "printed_page": 63, "classe": 6},
    {"code": "6114", "label": "Variation de stocks de marchandises", "printed_page": 63, "classe": 6},
    {"code": "6118", "label": "Achats revendus de marchandises des exercices antérieurs", "printed_page": 63, "classe": 6},
    {"code": "6119", "label": "Rabais, remises, et ristournes obtenus sur achats de marchandises", "printed_page": 63, "classe": 6},
    # 612. ACHATS CONSOMMES DE MATIERES ET DE FOURNITURES (printed p. 64-65)
    {"code": "6121", "label": "Achats de matières premières", "printed_page": 64, "classe": 6},
    {"code": "61211", "label": "Achats de matières premières A", "printed_page": 64, "classe": 6},
    {"code": "61212", "label": "Achats de matières premières B", "printed_page": 64, "classe": 6},
    {"code": "6122", "label": "Achats de matières et fournitures consommables", "printed_page": 64, "classe": 6},
    {"code": "61221", "label": "Achats de matières et fournitures A", "printed_page": 64, "classe": 6},
    {"code": "61222", "label": "Achats de matières et fournitures B", "printed_page": 64, "classe": 6},
    {"code": "61223", "label": "Achats de combustibles", "printed_page": 64, "classe": 6},
    {"code": "61224", "label": "Achats de produits d'entretien", "printed_page": 64, "classe": 6},
    {"code": "61225", "label": "Achats de fournitures d'atelier et d'usine", "printed_page": 64, "classe": 6},
    {"code": "61226", "label": "Achats de fournitures de magasin", "printed_page": 64, "classe": 6},
    {"code": "61227", "label": "Achats de fournitures de bureau", "printed_page": 64, "classe": 6},
    {"code": "6123", "label": "Achats d'emballages", "printed_page": 64, "classe": 6},
    {"code": "61231", "label": "Achats d'emballages perdus", "printed_page": 64, "classe": 6},
    {"code": "61232", "label": "Achats d'emballages récupérables non identifiables", "printed_page": 64, "classe": 6},
    {"code": "61233", "label": "Achats d'emballages à usage mixte", "printed_page": 64, "classe": 6},
    {"code": "6124", "label": "Variation des stocks de matières et fournitures", "printed_page": 64, "classe": 6},
    {"code": "61241", "label": "Variation des stocks de matières premières", "printed_page": 64, "classe": 6},
    {"code": "61242", "label": "Variation des stocks de matières et fournitures consommables", "printed_page": 64, "classe": 6},
    {"code": "61243", "label": "Variation des stocks des emballages", "printed_page": 64, "classe": 6},
    {"code": "6125", "label": "Achats non stockés de matières et de fournitures", "printed_page": 64, "classe": 6},
    {"code": "61251", "label": "Achats de fournitures non stockables (eau, électricité .....)", "printed_page": 64, "classe": 6},
    {"code": "61252", "label": "Achats de fournitures d'entretien", "printed_page": 64, "classe": 6},
    {"code": "61253", "label": "Achats de petit outillage et de petit équipement", "printed_page": 64, "classe": 6},
    {"code": "61254", "label": "Achats de fournitures de bureau", "printed_page": 64, "classe": 6},
    {"code": "6126", "label": "Achats de travaux , études et prestations de service", "printed_page": 65, "classe": 6},
    {"code": "61261", "label": "Achats des travaux", "printed_page": 65, "classe": 6},
    {"code": "61262", "label": "Achats des études", "printed_page": 65, "classe": 6},
    {"code": "61263", "label": "Achats des prestations de service", "printed_page": 65, "classe": 6},
    {"code": "6128", "label": "Achats de matières et de fournitures des exercices antérieurs", "printed_page": 65, "classe": 6},
    {"code": "6129", "label": "Rabais, remises et ristournes obtenus sur achats consommés de matières et fournitures", "printed_page": 65, "classe": 6},
    {"code": "61291", "label": "R.R.R obtenus sur achats de matières premières", "printed_page": 65, "classe": 6},
    {"code": "61292", "label": "R.R.R. obtenus sur achats de matières et fournitures consommables", "printed_page": 65, "classe": 6},
    {"code": "61293", "label": "R.R.R. obtenus sur achats des emballages", "printed_page": 65, "classe": 6},
    {"code": "61295", "label": "R.R.R. obtenus sur achats non stockés", "printed_page": 65, "classe": 6},
    {"code": "61296", "label": "R.R.R. obtenus sur achats de travaux, études et prestations de service", "printed_page": 65, "classe": 6},
    {"code": "61298", "label": "R.R.R. obtenus sur achats de matières et fournitures des exercices antérieurs", "printed_page": 65, "classe": 6},
    # 613/614. AUTRES CHARGES EXTERNES (printed p. 66-68)
    {"code": "6131", "label": "Locations et charges locatives", "printed_page": 66, "classe": 6},
    {"code": "61311", "label": "Location de terrains", "printed_page": 66, "classe": 6},
    {"code": "61312", "label": "Location de constructions", "printed_page": 66, "classe": 6},
    {"code": "61313", "label": "Location de matériel et d'outillage", "printed_page": 66, "classe": 6},
    {"code": "61314", "label": "Location de mobilier et matériel de bureau", "printed_page": 66, "classe": 6},
    {"code": "61315", "label": "Location de matériel informatique", "printed_page": 66, "classe": 6},
    {"code": "61316", "label": "Location de matériel de transport", "printed_page": 66, "classe": 6},
    {"code": "61317", "label": "Malis sur emballages rendus", "printed_page": 66, "classe": 6},
    {"code": "61318", "label": "Locations et charges locatives diverses", "printed_page": 66, "classe": 6},
    {"code": "6132", "label": "Redevances de crédit-bail", "printed_page": 66, "classe": 6},
    {"code": "61321", "label": "Redevances de crédit-bail - mobilier et matériel", "printed_page": 66, "classe": 6},
    {"code": "6133", "label": "Entretien et réparations", "printed_page": 66, "classe": 6},
    {"code": "61331", "label": "Entretien et Réparations des biens immobiliers", "printed_page": 66, "classe": 6},
    {"code": "61332", "label": "Entretien et réparations des biens mobiliers", "printed_page": 66, "classe": 6},
    {"code": "61335", "label": "Maintenance", "printed_page": 66, "classe": 6},
    {"code": "6134", "label": "Primes d'assurances", "printed_page": 66, "classe": 6},
    {"code": "61341", "label": "Assurances multirisques (vol, incendie, responsabilité civile....)", "printed_page": 66, "classe": 6},
    {"code": "61343", "label": "Assurances - Risques d'exploitation", "printed_page": 66, "classe": 6},
    {"code": "61345", "label": "Assurances - Matériel de transport", "printed_page": 66, "classe": 6},
    {"code": "61348", "label": "Autres assurances", "printed_page": 66, "classe": 6},
    {"code": "6135", "label": "Rémunérations du personnel extérieur à l'entreprise", "printed_page": 67, "classe": 6},
    {"code": "61351", "label": "Rémunérations du personnel occasionnel", "printed_page": 67, "classe": 6},
    {"code": "61352", "label": "Rémunérations du personnel intérimaire", "printed_page": 67, "classe": 6},
    {"code": "61353", "label": "Rémunérations du personnel détaché ou prêté à l'entreprise", "printed_page": 67, "classe": 6},
    {"code": "6136", "label": "Rémunérations d'intermédiaires et honoraires", "printed_page": 67, "classe": 6},
    {"code": "61361", "label": "Commissions et courtages", "printed_page": 67, "classe": 6},
    {"code": "61365", "label": "Honoraires", "printed_page": 67, "classe": 6},
    {"code": "61367", "label": "Frais d'actes et de contentieux", "printed_page": 67, "classe": 6},
    {"code": "6137", "label": "Redevances pour brevets marques, droits et valeurs similaires", "printed_page": 67, "classe": 6},
    {"code": "61371", "label": "Redevances pour brevets", "printed_page": 67, "classe": 6},
    {"code": "61378", "label": "Autres redevances", "printed_page": 67, "classe": 6},
    {"code": "6141", "label": "Etudes, recherches et documentation", "printed_page": 67, "classe": 6},
    {"code": "61411", "label": "Etudes générales", "printed_page": 67, "classe": 6},
    {"code": "61413", "label": "Recherches", "printed_page": 67, "classe": 6},
    {"code": "61415", "label": "Documentation générale", "printed_page": 67, "classe": 6},
    {"code": "61416", "label": "Documentation technique", "printed_page": 67, "classe": 6},
    {"code": "6142", "label": "Transports", "printed_page": 67, "classe": 6},
    {"code": "61421", "label": "Transports du personnel", "printed_page": 67, "classe": 6},
    {"code": "61425", "label": "Transports sur achats", "printed_page": 67, "classe": 6},
    {"code": "61426", "label": "Transports sur ventes", "printed_page": 67, "classe": 6},
    {"code": "61428", "label": "Autres transports", "printed_page": 67, "classe": 6},
    {"code": "6143", "label": "Déplacements, missions et réceptions", "printed_page": 67, "classe": 6},
    {"code": "61431", "label": "Voyages et déplacements", "printed_page": 67, "classe": 6},
    {"code": "61433", "label": "Frais de déménagement", "printed_page": 67, "classe": 6},
    {"code": "61435", "label": "Missions", "printed_page": 67, "classe": 6},
    {"code": "61436", "label": "Réceptions", "printed_page": 67, "classe": 6},
    {"code": "6144", "label": "Publicité, publications et relations publiques", "printed_page": 68, "classe": 6},
    {"code": "61441", "label": "Annonces et insertions", "printed_page": 68, "classe": 6},
    {"code": "61442", "label": "Echantillons, catalogues et imprimés publicitaires", "printed_page": 68, "classe": 6},
    {"code": "61443", "label": "Foires et expositions", "printed_page": 68, "classe": 6},
    {"code": "61444", "label": "Primes de publicité", "printed_page": 68, "classe": 6},
    {"code": "61446", "label": "Publications", "printed_page": 68, "classe": 6},
    {"code": "61447", "label": "Cadeaux à la clientèle", "printed_page": 68, "classe": 6},
    {"code": "61448", "label": "Autres charges de publicité et relations publiques", "printed_page": 68, "classe": 6},
    {"code": "6145", "label": "Frais postaux et frais de télécommunications", "printed_page": 68, "classe": 6},
    {"code": "61451", "label": "Frais postaux", "printed_page": 68, "classe": 6},
    {"code": "61455", "label": "Frais de téléphone", "printed_page": 68, "classe": 6},
    {"code": "61456", "label": "Frais de télex et de télégrammes", "printed_page": 68, "classe": 6},
    {"code": "6146", "label": "Cotisations et dons", "printed_page": 68, "classe": 6},
    {"code": "61461", "label": "Cotisations", "printed_page": 68, "classe": 6},
    {"code": "61462", "label": "Dons", "printed_page": 68, "classe": 6},
    {"code": "6147", "label": "Services bancaires", "printed_page": 68, "classe": 6},
    {"code": "61471", "label": "Frais d'achat et de vente des titres", "printed_page": 68, "classe": 6},
    {"code": "61472", "label": "Frais sur effets de commerce", "printed_page": 68, "classe": 6},
    {"code": "61473", "label": "Frais et commissions sur services bancaires", "printed_page": 68, "classe": 6},
    {"code": "6148", "label": "Autres charges externes des exercices antérieurs", "printed_page": 68, "classe": 6},
    {"code": "6149", "label": "Rabais, Remises et ristournes obtenus sur autres charges externes", "printed_page": 68, "classe": 6},
    # 616. IMPOTS ET TAXES (printed p. 69)
    {"code": "6161", "label": "Impôts et taxes directs", "printed_page": 69, "classe": 6},
    {"code": "61611", "label": "Taxe urbaine et taxe d'édilité", "printed_page": 69, "classe": 6},
    {"code": "61612", "label": "Patente", "printed_page": 69, "classe": 6},
    {"code": "61615", "label": "Taxes locales", "printed_page": 69, "classe": 6},
    {"code": "6165", "label": "Impôts et Taxes Indirectes", "printed_page": 69, "classe": 6},
    {"code": "6167", "label": "Impôts, taxes et droits assimilés", "printed_page": 69, "classe": 6},
    {"code": "61671", "label": "Droits d'enregistrement et de timbre", "printed_page": 69, "classe": 6},
    {"code": "61673", "label": "Taxes sur les véhicules", "printed_page": 69, "classe": 6},
    {"code": "61678", "label": "Autres impôts, taxes et droits assimilés", "printed_page": 69, "classe": 6},
    {"code": "6168", "label": "Impôts et taxes des exercices antérieurs", "printed_page": 69, "classe": 6},
    # 617. CHARGES DE PERSONNEL (printed p. 69-70)
    {"code": "6171", "label": "Rémunérations du personnel", "printed_page": 69, "classe": 6},
    {"code": "61711", "label": "Appointements et salaires", "printed_page": 69, "classe": 6},
    {"code": "61712", "label": "Primes et gratifications", "printed_page": 69, "classe": 6},
    {"code": "61713", "label": "Indemnités et avantages divers", "printed_page": 69, "classe": 6},
    {"code": "61714", "label": "Commissions au personnel", "printed_page": 69, "classe": 6},
    {"code": "61715", "label": "Rémunérations des administrateurs, gérants et associés", "printed_page": 69, "classe": 6},
    {"code": "6174", "label": "Charges sociales", "printed_page": 69, "classe": 6},
    {"code": "61741", "label": "Cotisations de sécurité sociale", "printed_page": 69, "classe": 6},
    {"code": "61742", "label": "Cotisations aux caisses de retraite", "printed_page": 69, "classe": 6},
    {"code": "61743", "label": "Cotisations aux mutuelles", "printed_page": 69, "classe": 6},
    {"code": "61744", "label": "Prestations familiales", "printed_page": 69, "classe": 6},
    {"code": "61745", "label": "Assurances accidents de travail", "printed_page": 69, "classe": 6},
    {"code": "6176", "label": "Charges sociales diverses", "printed_page": 70, "classe": 6},
    {"code": "61761", "label": "Assurances groupe", "printed_page": 70, "classe": 6},
    {"code": "61762", "label": "Prestations de retraites", "printed_page": 70, "classe": 6},
    {"code": "61763", "label": "Allocations aux oeuvres sociales", "printed_page": 70, "classe": 6},
    {"code": "61764", "label": "Habillement et vêtements de travail", "printed_page": 70, "classe": 6},
    {"code": "61765", "label": "Indemnités de préavis et de licenciement", "printed_page": 70, "classe": 6},
    {"code": "61766", "label": "Médecine de travail, pharmacie", "printed_page": 70, "classe": 6},
    {"code": "61768", "label": "Autres charges sociales diverses", "printed_page": 70, "classe": 6},
    {"code": "6177", "label": "Rémunération de l'exploitant", "printed_page": 70, "classe": 6},
    {"code": "61771", "label": "Appointements et salaires", "printed_page": 70, "classe": 6},
    {"code": "61774", "label": "Charges sociales sur appointements et salaires de l'exploitant", "printed_page": 70, "classe": 6},
    {"code": "6178", "label": "Charges de personnel des exercices antérieurs.", "printed_page": 70, "classe": 6},
    # 618. AUTRES CHARGES D'EXPLOITATION (printed p. 70)
    {"code": "6181", "label": "Jetons de présence", "printed_page": 70, "classe": 6},
    {"code": "6182", "label": "Pertes sur créances irrécouvrables", "printed_page": 70, "classe": 6},
    {"code": "6185", "label": "Pertes sur opérations faites en commun", "printed_page": 70, "classe": 6},
    {"code": "6186", "label": "Transfert de profits sur opérations faites en commun", "printed_page": 70, "classe": 6},
    {"code": "6188", "label": "Autres charges d'exploitation des exercices antérieurs", "printed_page": 70, "classe": 6},
    # 619. DOTATIONS D'EXPLOITATION (printed p. 70-72)
    {"code": "6191", "label": "Dotations d'exploitation aux amortissements de l'immobilisation en non-valeurs", "printed_page": 70, "classe": 6},
    {"code": "61911", "label": "D.E.A. des frais préliminaires", "printed_page": 70, "classe": 6},
    {"code": "61912", "label": "D.E.A. des charges à répartir", "printed_page": 70, "classe": 6},
    {"code": "6192", "label": "Dotations d'exploitation aux amortissements des immobilisations incorporelles", "printed_page": 71, "classe": 6},
    {"code": "61921", "label": "D.E.A. de l'immobilisations en recherche et développement", "printed_page": 71, "classe": 6},
    {"code": "61922", "label": "D.E.A. des brevets, marques, droits et valeurs similaires", "printed_page": 71, "classe": 6},
    {"code": "61923", "label": "D.E.A. du fonds commercial", "printed_page": 71, "classe": 6},
    {"code": "61928", "label": "D.E.A. des autres immobilisations incorporelles", "printed_page": 71, "classe": 6},
    {"code": "6193", "label": "Dotations d'exploitaion aux amortissements des immobilisations corporelles", "printed_page": 71, "classe": 6},
    {"code": "61931", "label": "D.E.A. des terrains", "printed_page": 71, "classe": 6},
    {"code": "61932", "label": "D.E.A. des constructions", "printed_page": 71, "classe": 6},
    {"code": "61933", "label": "D.E.A. des installations techniques, matériel et outillage", "printed_page": 71, "classe": 6},
    {"code": "61934", "label": "D.E.A. du matériel de transport", "printed_page": 71, "classe": 6},
    {"code": "61935", "label": "D.E.A. des mobilier, matériel de bureau et aménagements divers", "printed_page": 71, "classe": 6},
    {"code": "61938", "label": "D.E.A des autres immobilisations corporelles", "printed_page": 71, "classe": 6},
    {"code": "6194", "label": "Dotations d'exploitation aux provisions pour dépréciation des immobilisations", "printed_page": 71, "classe": 6},
    {"code": "61942", "label": "D.E.P. pour dépréciation des immobilisations incorporelles", "printed_page": 71, "classe": 6},
    {"code": "61943", "label": "D.E.P pour dépréciation des immobilisations corporelles", "printed_page": 71, "classe": 6},
    {"code": "6195", "label": "Dotations d'exploitation aux provisions pour risques et charges", "printed_page": 71, "classe": 6},
    {"code": "61955", "label": "D.E.P. pour risques et charges durables", "printed_page": 71, "classe": 6},
    {"code": "61957", "label": "D.E.P. pour risques et charges momentanés", "printed_page": 71, "classe": 6},
    {"code": "6196", "label": "Dotations d'exploitation aux provisions pour dépréciation de l'actif circulant", "printed_page": 72, "classe": 6},
    {"code": "61961", "label": "D.E.P. pour dépréciation des stocks", "printed_page": 72, "classe": 6},
    {"code": "61964", "label": "D.E.P. pour dépréciation des créances de l'actif circulant", "printed_page": 72, "classe": 6},
    {"code": "6198", "label": "Dotations d'exploitation des exercices antérieurs", "printed_page": 72, "classe": 6},
    {"code": "61981", "label": "D.E. aux amortissements des exercices antérieurs", "printed_page": 72, "classe": 6},
    {"code": "61984", "label": "D.E. aux provisions des exercices antérieurs", "printed_page": 72, "classe": 6},

    # 63. CHARGES FINANCIERES
    # 631. CHARGES D'INTERETS (printed p. 73)
    {"code": "6311", "label": "Intérêts des emprunts et dettes", "printed_page": 73, "classe": 6},
    {"code": "63111", "label": "Intérêts des emprunts", "printed_page": 73, "classe": 6},
    {"code": "63113", "label": "Intérêts des dettes rattachées à des participations", "printed_page": 73, "classe": 6},
    {"code": "63114", "label": "Intérêts des comptes courants et dépôts créditeurs", "printed_page": 73, "classe": 6},
    {"code": "63115", "label": "Intérêts bancaires et sur opérations de financement", "printed_page": 73, "classe": 6},
    {"code": "63118", "label": "Autres intérêts des emprunts et dettes", "printed_page": 73, "classe": 6},
    {"code": "6318", "label": "Charges d'intérêts des exercices antérieurs", "printed_page": 73, "classe": 6},
    # 633. PERTES DE CHANGE (printed p. 73)
    {"code": "6331", "label": "Pertes de change propres à l'exercice", "printed_page": 73, "classe": 6},
    {"code": "6338", "label": "Pertes de change des exercices antérieurs", "printed_page": 73, "classe": 6},
    # 638. AUTRES CHARGES FINANCIERES (printed p. 73-74)
    {"code": "6382", "label": "Pertes sur créances liées à des participations", "printed_page": 73, "classe": 6},
    {"code": "6385", "label": "Charges nettes sur cessions de titres et valeurs de placement", "printed_page": 73, "classe": 6},
    {"code": "6386", "label": "Escomptes accordés", "printed_page": 73, "classe": 6},
    {"code": "6388", "label": "Autres charges financières des exercices antérieurs", "printed_page": 74, "classe": 6},
    # 639. DOTATIONS FINANCIERES (printed p. 74)
    {"code": "6391", "label": "Dotations aux amortissements des primes de remboursement des obligations", "printed_page": 74, "classe": 6},
    {"code": "6392", "label": "Dotations aux provisions pour dépréciation des immobilisations financières", "printed_page": 74, "classe": 6},
    {"code": "6393", "label": "Dotations aux provisions pour risques et charges financiers", "printed_page": 74, "classe": 6},
    {"code": "6394", "label": "Dotations aux provisions pour dépréciation des titres et valeurs de placement", "printed_page": 74, "classe": 6},
    {"code": "6396", "label": "Dotations aux provisions pour dépréciation des comptes de trésorerie", "printed_page": 74, "classe": 6},
    {"code": "6398", "label": "Dotations financières des exercices antérieurs", "printed_page": 74, "classe": 6},

    # 65. CHARGES NON-COURANTES
    # 651. VALEURS NETTES D'AMORTISSEMENTS DES IMMOBILISATIONS CEDEES (printed p. 75)
    {"code": "6512", "label": "V.N.A des immobilisations incorporelles cédées", "printed_page": 75, "classe": 6},
    {"code": "6513", "label": "V.N.A des immobilisations corporelles cédées", "printed_page": 75, "classe": 6},
    {"code": "6514", "label": "V.N.A des immobilisations financières cédées (droits de propriété)", "printed_page": 75, "classe": 6},
    {"code": "6518", "label": "V.N.A des immobilisations cédées des exercices antérieurs", "printed_page": 75, "classe": 6},
    # 656. SUBVENTIONS ACCORDEES (printed p. 75)
    {"code": "6561", "label": "Subventions accordées de l'exercice", "printed_page": 75, "classe": 6},
    {"code": "6568", "label": "Subventions accordées des exercices antérieurs", "printed_page": 75, "classe": 6},
    # 658. AUTRES CHARGES NON COURANTES (printed p. 75-76)
    {"code": "6581", "label": "Pénalités sur marchés et dédits", "printed_page": 75, "classe": 6},
    {"code": "65811", "label": "Pénalités sur marchés", "printed_page": 75, "classe": 6},
    {"code": "65812", "label": "Dédits", "printed_page": 75, "classe": 6},
    {"code": "6582", "label": "Rappels d'impôts (autres qu'impôts sur les résultats)", "printed_page": 75, "classe": 6},
    {"code": "6583", "label": "Pénalités et amendes fiscales ou pénales", "printed_page": 75, "classe": 6},
    {"code": "65831", "label": "Pénalités et amendes fiscales", "printed_page": 75, "classe": 6},
    {"code": "65833", "label": "Pénalités et amendes pénales", "printed_page": 75, "classe": 6},
    {"code": "6585", "label": "Créances devenues irrécouvrables", "printed_page": 75, "classe": 6},
    {"code": "6586", "label": "Dons, libéralités et lots", "printed_page": 76, "classe": 6},
    {"code": "65861", "label": "Dons", "printed_page": 76, "classe": 6},
    {"code": "65862", "label": "Libéralités", "printed_page": 76, "classe": 6},
    {"code": "65863", "label": "Lots", "printed_page": 76, "classe": 6},
    {"code": "6588", "label": "Autres charges non courantes des exercices antérieurs", "printed_page": 76, "classe": 6},
    # 659. DOTATIONS NON COURANTES (printed p. 76-77)
    {"code": "6591", "label": "Dotations aux amortissements exceptionnels des immobilisations", "printed_page": 76, "classe": 6},
    {"code": "65911", "label": "D.A.E. de l'immobilisation en non-valeurs", "printed_page": 76, "classe": 6},
    {"code": "65912", "label": "D.A.E. des immobilisations incorporelles", "printed_page": 76, "classe": 6},
    {"code": "65913", "label": "D.A.E. des immobilisations corporelles", "printed_page": 76, "classe": 6},
    {"code": "6594", "label": "Dotations non courantes aux provisions réglementées", "printed_page": 76, "classe": 6},
    {"code": "65941", "label": "DNC pour amortissements dérogatoires", "printed_page": 76, "classe": 6},
    {"code": "65942", "label": "DNC pour plus-values en instance d'imposition", "printed_page": 76, "classe": 6},
    {"code": "65944", "label": "DNC pour investissements", "printed_page": 76, "classe": 6},
    {"code": "65945", "label": "DNC pour reconstitution de gisements", "printed_page": 76, "classe": 6},
    {"code": "65946", "label": "DNC pour acquisition et construction de logements", "printed_page": 76, "classe": 6},
    {"code": "6595", "label": "Dotations non courantes aux provisions pour risques et charges", "printed_page": 77, "classe": 6},
    {"code": "65955", "label": "DNC aux provisions pour risques et charges durables", "printed_page": 77, "classe": 6},
    {"code": "65957", "label": "DNC aux provisions pour risques et charges momentanés", "printed_page": 77, "classe": 6},
    {"code": "6596", "label": "Dotations non courantes aux provisions pour dépréciation", "printed_page": 77, "classe": 6},
    {"code": "65962", "label": "DNC aux provisions pour dépréciation de l'actif immobilisé", "printed_page": 77, "classe": 6},
    {"code": "65963", "label": "DNC aux provisions pour dépréciation de l'actif circulant", "printed_page": 77, "classe": 6},
    {"code": "6598", "label": "Dotations non courantes des exercices antérieurs", "printed_page": 77, "classe": 6},

    # 67. IMPOTS SUR LES RESULTATS
    # 670. IMPOTS SUR LES RESULTATS (printed p. 77)
    {"code": "6701", "label": "Impôts sur les bénéfices", "printed_page": 77, "classe": 6},
    {"code": "6705", "label": "Imposition minimale annuelle des sociétés", "printed_page": 77, "classe": 6},
    {"code": "6708", "label": "Rappels et dégrèvements des impôts sur les résultats", "printed_page": 77, "classe": 6},

    # =========================================================================
    # CLASSE 7 : COMPTES DE PRODUITS (pages 55-64, printed 79-88)
    # =========================================================================
    # 71. PRODUITS D'EXPLOITATION
    # 711. VENTES DE MARCHANDISES (printed p. 79)
    {"code": "7111", "label": "Ventes de marchandises au Maroc", "printed_page": 79, "classe": 7},
    {"code": "7113", "label": "Ventes de marchandises à l'étranger", "printed_page": 79, "classe": 7},
    {"code": "7118", "label": "Ventes de marchandises des exercices antérieurs", "printed_page": 79, "classe": 7},
    {"code": "7119", "label": "Rabais, remises et ristournes accordés par l'entreprise", "printed_page": 79, "classe": 7},
    # 712. VENTES DE BIENS ET SERVICES PRODUITS (printed p. 79-81)
    {"code": "7121", "label": "Ventes de biens produits au Maroc", "printed_page": 79, "classe": 7},
    {"code": "71211", "label": "Ventes de produits finis", "printed_page": 79, "classe": 7},
    {"code": "71212", "label": "Ventes de produits intermédiaires", "printed_page": 79, "classe": 7},
    {"code": "71217", "label": "Ventes de produits résiduels", "printed_page": 79, "classe": 7},
    {"code": "7122", "label": "Ventes de biens produits à l'étranger", "printed_page": 80, "classe": 7},
    {"code": "71221", "label": "Ventes de produits finis", "printed_page": 80, "classe": 7},
    {"code": "71222", "label": "Ventes de produits intermédiaires", "printed_page": 80, "classe": 7},
    {"code": "7124", "label": "Ventes de services produits au Maroc", "printed_page": 80, "classe": 7},
    {"code": "71241", "label": "Travaux", "printed_page": 80, "classe": 7},
    {"code": "71242", "label": "Etudes", "printed_page": 80, "classe": 7},
    {"code": "71243", "label": "Prestations de service", "printed_page": 80, "classe": 7},
    {"code": "7125", "label": "Ventes de services produits à l'étranger", "printed_page": 80, "classe": 7},
    {"code": "71251", "label": "Travaux", "printed_page": 80, "classe": 7},
    {"code": "71252", "label": "Etudes", "printed_page": 80, "classe": 7},
    {"code": "71253", "label": "Prestations de service", "printed_page": 80, "classe": 7},
    {"code": "7126", "label": "Redevances pour brevets, marques, droits et valeurs similaires", "printed_page": 80, "classe": 7},
    {"code": "7127", "label": "Ventes et produits accessoires", "printed_page": 80, "classe": 7},
    {"code": "71271", "label": "Locations diverses reçues", "printed_page": 80, "classe": 7},
    {"code": "71272", "label": "Commissions et courtages reçus", "printed_page": 80, "classe": 7},
    {"code": "71273", "label": "Produits de services exploités dans l'intérêt du personnel", "printed_page": 80, "classe": 7},
    {"code": "71275", "label": "Bonis sur reprises d'emballages consignés", "printed_page": 80, "classe": 7},
    {"code": "71276", "label": "Ports et frais accessoires facturés", "printed_page": 80, "classe": 7},
    {"code": "71278", "label": "Autres ventes et produits accessoires", "printed_page": 80, "classe": 7},
    {"code": "7128", "label": "Ventes de biens et services produits des exercices antérieurs", "printed_page": 80, "classe": 7},
    {"code": "7129", "label": "Rabais, Remises,et Ristournes accordés par l'entreprise", "printed_page": 81, "classe": 7},
    {"code": "71291", "label": "R.R.R. accordés sur ventes au Maroc des biens produits", "printed_page": 81, "classe": 7},
    {"code": "71292", "label": "R.R.R. accordés sur ventes à l'étranger des biens produits", "printed_page": 81, "classe": 7},
    {"code": "71294", "label": "R.R.R. accordés sur ventes au Maroc des services produits", "printed_page": 81, "classe": 7},
    {"code": "71295", "label": "R.R.R. accordés sur ventes à l'étranger des services produits", "printed_page": 81, "classe": 7},
    {"code": "71298", "label": "R.R.R. accordés sur ventes de biens et services produits des exercices antérieurs", "printed_page": 81, "classe": 7},
    # 713. VARIATION DES STOCKS DE PRODUITS (printed p. 81-82)
    {"code": "7131", "label": "Variation des stocks de produits en cours", "printed_page": 81, "classe": 7},
    {"code": "71311", "label": "Variation des stocks de Biens produits en cours", "printed_page": 81, "classe": 7},
    {"code": "71312", "label": "Variation des stocks de produits intermédiaires en cours", "printed_page": 81, "classe": 7},
    {"code": "71317", "label": "Variation des stocks de produits résiduels en cours", "printed_page": 81, "classe": 7},
    {"code": "7132", "label": "Variation des stocks de biens produits", "printed_page": 81, "classe": 7},
    {"code": "71321", "label": "Variation des stocks de produits finis", "printed_page": 81, "classe": 7},
    {"code": "71322", "label": "Variation des stocks de produits intermédiaires", "printed_page": 81, "classe": 7},
    {"code": "71327", "label": "Variation des stocks de produits résiduels", "printed_page": 81, "classe": 7},
    {"code": "7134", "label": "Variations des stocks de services en cours", "printed_page": 82, "classe": 7},
    {"code": "71341", "label": "Variation des stocks de travaux en cours", "printed_page": 82, "classe": 7},
    {"code": "71342", "label": "Variation des stocks d'études en cours", "printed_page": 82, "classe": 7},
    {"code": "71343", "label": "Variation des stocks de prestations en cours", "printed_page": 82, "classe": 7},
    # 714. IMMOBILISATIONS PRODUITES PAR L'ENTREPRISE POUR ELLE MEME (printed p. 82)
    {"code": "7141", "label": "Immobilisation en non-valeurs produite", "printed_page": 82, "classe": 7},
    {"code": "7142", "label": "Immobilisations incorporelles produites", "printed_page": 82, "classe": 7},
    {"code": "7143", "label": "Immobilisations corporelles produites", "printed_page": 82, "classe": 7},
    {"code": "7148", "label": "Immobilisations produites des exercices antérieurs.", "printed_page": 82, "classe": 7},
    # 716. SUBVENTIONS D'EXPLOITATION (printed p. 82)
    {"code": "7161", "label": "Subventions d'exploitation reçues de l'exercice", "printed_page": 82, "classe": 7},
    {"code": "7168", "label": "Subventions d'exploitation reçues des exercices antérieurs", "printed_page": 82, "classe": 7},
    # 718. AUTRES PRODUITS D'EXPLOITATION (printed p. 82)
    {"code": "7181", "label": "Jetons de présence reçus", "printed_page": 82, "classe": 7},
    {"code": "7182", "label": "Revenus des immeubles non affectés à l'exploitation", "printed_page": 82, "classe": 7},
    {"code": "7185", "label": "Profits sur opérations faites en commun", "printed_page": 82, "classe": 7},
    {"code": "7186", "label": "Transfert de pertes sur opérations faites en commun", "printed_page": 83, "classe": 7},
    {"code": "7188", "label": "Autres produits d'exploitation des exercices antérieurs", "printed_page": 83, "classe": 7},
    # 719. REPRISES D'EXPLOITATION; TRANSFERTS DE CHARGES (printed p. 83)
    {"code": "7191", "label": "Reprises sur amortissements de l'immobilisation en non-valeurs", "printed_page": 83, "classe": 7},
    {"code": "7192", "label": "Reprises sur amortissements des immobilisations incorporelles", "printed_page": 83, "classe": 7},
    {"code": "7193", "label": "Reprises sur amortissements des immobilisations corporelles", "printed_page": 83, "classe": 7},
    {"code": "7194", "label": "Reprises sur provisions pour dépréciation des immobilisations", "printed_page": 83, "classe": 7},
    {"code": "7195", "label": "Reprises sur provisions pour risques et charges", "printed_page": 83, "classe": 7},
    {"code": "7196", "label": "Reprises sur provisions pour dépréciation de l'actif circulant", "printed_page": 83, "classe": 7},
    {"code": "7197", "label": "Transferts de charges d'exploitation", "printed_page": 83, "classe": 7},
    {"code": "71971", "label": "T.C.E-achats de marchandises", "printed_page": 83, "classe": 7},
    {"code": "71972", "label": "T.C.E-achats consommés de matières et fournitures", "printed_page": 83, "classe": 7},
    {"code": "71973", "label": "T.C.E - Autres charges externes", "printed_page": 83, "classe": 7},
    {"code": "71975", "label": "T.C.E - Impôt et taxes", "printed_page": 83, "classe": 7},
    {"code": "71976", "label": "T.C.E - Charges du personnel", "printed_page": 83, "classe": 7},
    {"code": "71978", "label": "T.C.E - Autres charges d'exploitation", "printed_page": 83, "classe": 7},
    {"code": "7198", "label": "Reprises sur amortissements et provisions des exercices antérieurs", "printed_page": 83, "classe": 7},
    {"code": "71981", "label": "Reprises sur amortissements des exercices antérieurs", "printed_page": 83, "classe": 7},
    {"code": "71984", "label": "Reprises sur provisions des exercices antérieurs", "printed_page": 83, "classe": 7},

    # 73. PRODUITS FINANCIERS
    # 732. PRODUITS DES TITRES DE PARTICIPATION ET DES AUTRES TITRES IMMOBILISES (printed p. 84)
    {"code": "7321", "label": "Revenus des titres de participation", "printed_page": 84, "classe": 7},
    {"code": "7325", "label": "Revenus des titres immobilisés", "printed_page": 84, "classe": 7},
    {"code": "7328", "label": "Produits des titres de participation et des autres titres immobilisés des exercices antérieurs", "printed_page": 84, "classe": 7},
    # 733. GAINS DE CHANGE (printed p. 84)
    {"code": "7331", "label": "Gains de change propres à l'exercice", "printed_page": 84, "classe": 7},
    {"code": "7338", "label": "Gains de change des exercices antérieurs", "printed_page": 84, "classe": 7},
    # 738. INTERETS ET AUTRES PRODUITS FINANCIERS (printed p. 84)
    {"code": "7381", "label": "Intérêts et produits assimilés", "printed_page": 84, "classe": 7},
    {"code": "73811", "label": "Intérêts des prêts", "printed_page": 84, "classe": 7},
    {"code": "73813", "label": "Revenus des autres créances financières", "printed_page": 84, "classe": 7},
    {"code": "7383", "label": "Revenus des créances rattachées à des participations", "printed_page": 84, "classe": 7},
    {"code": "7384", "label": "Revenus des titres et valeurs de placement", "printed_page": 84, "classe": 7},
    {"code": "7385", "label": "Produits nets sur cessions de titres et valeurs de placement", "printed_page": 84, "classe": 7},
    {"code": "7386", "label": "Escomptes obtenus", "printed_page": 84, "classe": 7},
    {"code": "7388", "label": "Intérêts et autres produits financiers des exercices antérieurs", "printed_page": 84, "classe": 7},
    # 739. REPRISES FINANCIERES ; TRANSFERTS DE CHARGES (printed p. 85)
    {"code": "7391", "label": "Reprises sur amortissements des primes de remboursement des obligations", "printed_page": 85, "classe": 7},
    {"code": "7392", "label": "Reprises sur provisions pour dépréciation des immobilisations financières", "printed_page": 85, "classe": 7},
    {"code": "7393", "label": "Reprises sur provisions pour risques et charges financiers", "printed_page": 85, "classe": 7},
    {"code": "7394", "label": "Reprises sur provisions pour dépréciation des titres et valeurs de placement", "printed_page": 85, "classe": 7},
    {"code": "7396", "label": "Reprises sur provisions pour dépréciation des comptes de trésorerie", "printed_page": 85, "classe": 7},
    {"code": "7397", "label": "Transferts de charges financières", "printed_page": 85, "classe": 7},
    {"code": "73971", "label": "Transferts - charges d'intérêts", "printed_page": 85, "classe": 7},
    {"code": "73973", "label": "Transferts - pertes de change", "printed_page": 85, "classe": 7},
    {"code": "73978", "label": "Transferts autres charges financières", "printed_page": 85, "classe": 7},
    {"code": "7398", "label": "Reprises sur dotations financières des exercices antérieurs", "printed_page": 85, "classe": 7},

    # 75. PRODUITS NON COURANTES
    # 751. PRODUITS DES CESSIONS D'IMMOBILISATIONS (printed p. 86)
    {"code": "7512", "label": "P.C des immobilisations incorporelles cédées", "printed_page": 86, "classe": 7},
    {"code": "7513", "label": "P.C des immobilisations corporelles cédées", "printed_page": 86, "classe": 7},
    {"code": "7514", "label": "P.C des immobilisations financières (droits de propriété)", "printed_page": 86, "classe": 7},
    {"code": "7518", "label": "P.C des immobilisations des exercices antérieurs", "printed_page": 86, "classe": 7},
    # 756. SUBVENTIONS D'EQUILIBRE (printed p. 86)
    {"code": "7561", "label": "Subventions d'équilibre reçues de l'exercice", "printed_page": 86, "classe": 7},
    {"code": "7568", "label": "Subventions d'équilibre reçues des exercices antérieurs", "printed_page": 86, "classe": 7},
    # 757. REPRISES SUR SUBVENTIONS D'INVESTISSEMENT (printed p. 86)
    {"code": "7577", "label": "Reprises sur subventions d'investissement de l'exercice", "printed_page": 86, "classe": 7},
    {"code": "7578", "label": "Reprises sur subventions d'investissement des exercices antérieurs", "printed_page": 86, "classe": 7},
    # 758. AUTRES PRODUITS NON COURANTS (printed p. 86-87)
    {"code": "7581", "label": "Pénalités et dédits reçus", "printed_page": 86, "classe": 7},
    {"code": "75811", "label": "Pénalités reçues sur marchés", "printed_page": 86, "classe": 7},
    {"code": "75812", "label": "Dédits reçus", "printed_page": 86, "classe": 7},
    {"code": "7582", "label": "Dégrèvements d'impôts (autres qu'impôts sur les résultats)", "printed_page": 87, "classe": 7},
    {"code": "7585", "label": "Rentrées sur créances soldées", "printed_page": 87, "classe": 7},
    {"code": "7586", "label": "Dons, libéralités et lots reçus", "printed_page": 87, "classe": 7},
    {"code": "75861", "label": "Dons", "printed_page": 87, "classe": 7},
    {"code": "75862", "label": "Libéralités", "printed_page": 87, "classe": 7},
    {"code": "75863", "label": "Lots", "printed_page": 87, "classe": 7},
    {"code": "7588", "label": "Autres produits non courants des exercices antérieurs", "printed_page": 87, "classe": 7},
    # 759. REPRISES NON COURANTES ; TRANSFERTS DE CHARGES (printed p. 87-88)
    {"code": "7591", "label": "Reprises non courantes sur amortissements exceptionnels des immobilisations", "printed_page": 87, "classe": 7},
    {"code": "75911", "label": "R.A.E. de l'immobilisation en non valeurs", "printed_page": 87, "classe": 7},
    {"code": "75912", "label": "R.A.E. des immobilisations incorporelles", "printed_page": 87, "classe": 7},
    {"code": "75913", "label": "R.A.E des immobilisations corporelles", "printed_page": 87, "classe": 7},
    {"code": "7594", "label": "Reprises non courantes sur provisions réglementées", "printed_page": 87, "classe": 7},
    {"code": "75941", "label": "Reprises sur amortissements dérogatoires", "printed_page": 87, "classe": 7},
    {"code": "75942", "label": "Reprises sur plus-values en instance d'imposition", "printed_page": 87, "classe": 7},
    {"code": "75944", "label": "Reprises sur provisions pour investissements", "printed_page": 87, "classe": 7},
    {"code": "75945", "label": "Reprises sur provisions pour reconstitution de gisements", "printed_page": 87, "classe": 7},
    {"code": "75946", "label": "Reprises sur provisions pour acquisition et construction de logements", "printed_page": 88, "classe": 7},
    {"code": "7595", "label": "Reprises non courantes sur provisions pour risques et charges", "printed_page": 88, "classe": 7},
    {"code": "75955", "label": "Reprises sur provisions pour risques et charges durables", "printed_page": 88, "classe": 7},
    {"code": "75957", "label": "Reprises sur provisions pour risques et charges momentanés", "printed_page": 88, "classe": 7},
    {"code": "7596", "label": "Reprises non courantes sur provisions pour dépréciation", "printed_page": 88, "classe": 7},
    {"code": "75962", "label": "R.N.C. sur provisions pour dépréciation de l'actif immobilisé", "printed_page": 88, "classe": 7},
    {"code": "75963", "label": "R.N.C sur provisions pour dépréciation de l'actif circulant", "printed_page": 88, "classe": 7},
    {"code": "7597", "label": "Transferts de charges non courantes", "printed_page": 88, "classe": 7},
    {"code": "7598", "label": "Reprises non courantes des exercices antérieurs", "printed_page": 88, "classe": 7},

    # =========================================================================
    # CLASSE 8 : COMPTES DE RESULTATS (pages 65-67, printed 89-91)
    # =========================================================================
    # 81. RESULTAT D'EXPLOITATION (printed p. 89-90)
    {"code": "8100", "label": "Résultat d'exploitation", "printed_page": 89, "classe": 8},
    {"code": "8110", "label": "Marge brute", "printed_page": 89, "classe": 8},
    {"code": "8140", "label": "Valeur ajoutée", "printed_page": 89, "classe": 8},
    {"code": "8171", "label": "Excédent brut d'exploitation (créditeur)", "printed_page": 90, "classe": 8},
    {"code": "8179", "label": "Insuffisance brute d'exploitation (débiteur)", "printed_page": 90, "classe": 8},
    # 83. RESULTAT FINANCIER (printed p. 90)
    {"code": "8300", "label": "Résultat financier", "printed_page": 90, "classe": 8},
    # 84. RESULTAT COURANT (printed p. 90)
    {"code": "8400", "label": "Résultat courant", "printed_page": 90, "classe": 8},
    # 85. RESULTAT NON COURANT (printed p. 90)
    {"code": "8500", "label": "Résultat non courant", "printed_page": 90, "classe": 8},
    # 86. RESULTAT AVANT IMPOTS (printed p. 90)
    {"code": "8600", "label": "Résultat avant impôts", "printed_page": 90, "classe": 8},
    # 88. RESULTAT APRES IMPOTS (printed p. 91)
    {"code": "8800", "label": "Résultat après impôts", "printed_page": 91, "classe": 8},
]

data_dir = Path(__file__).resolve().parent / "data"
data_dir.mkdir(parents=True, exist_ok=True)
with (data_dir / "official_plan_cgnc.json").open("w", encoding="utf-8") as f:
    json.dump(OFFICIAL_PLAN, f, ensure_ascii=False, indent=2)

print(f"Total standard general-business accounts extracted: {len(OFFICIAL_PLAN)}")

