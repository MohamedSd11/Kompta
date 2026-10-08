"""CGNC (Code Général de Normalisation Comptable) account roots shared by backend modules."""
from __future__ import annotations

CLIENTS_ROOT = "3421"
SUPPLIERS_ROOT = "4411"
CHARGES_CLASS = "6"
PRODUCTS_CLASS = "7"

TIER_ROOT_TYPES = {CLIENTS_ROOT: "Client", SUPPLIERS_ROOT: "Fournisseur"}
TIER_ROOTS = tuple(TIER_ROOT_TYPES)
