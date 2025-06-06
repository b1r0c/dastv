#!/usr/bin/env python3
# ordina_listone.py

import re
import sys
import os

# ---------------------------------------------------------------------------------
# 1) ORDINE FISSO DELLE CATEGORIE
# ---------------------------------------------------------------------------------
# Devono corrispondere esattamente (in minuscolo) a quanto vogliamo:
CATEGORIE_IN_ORDINE = [
    "rai",
    "mediaset",
    "discovery",
    "sky intrattenimento",
    "sky cinema",
    "sky sport",
    "sky calcio",
    "dazn",
    "eventi"
]

def trova_categoria(nome_canale: str) -> str:
    """
    Assegna a 'nome_canale' una delle 9 categorie, secondo la seguente logica:
      1) se contiene "rai" → "rai"
      2) se contiene "mediaset" o "canale 5"/"italia 1"/"rete 4" → "mediaset"
      3) se contiene "discovery" o "dmax"/"real time"/"top crime"/"food network"/"crime+ investigation"/"nove"/"hgtv" → "discovery"
      4) se contiene "sky cinema" → "sky cinema"
      5) se contiene "sky sport" ma NON "sky calcio" → "sky sport"
      6) se contiene "sky calcio" → "sky calcio"
      7) se inizia con "sky " (qualsiasi altro canale Sky) → "sky intrattenimento"
      8) se contiene "dazn" → "dazn"
      9) altrimenti → "eventi"
    """
    n = nome_canale.lower()

    if "rai" in n:
        return "rai"
    if "mediaset" in n or any(x in n for x in ["canale 5", "italia 1", "rete 4"]):
        return "mediaset"
    if ("discovery" in n or "dmax" in n or "real time" in n or 
        "top crime" in n or "food network" in n or 
        "crime+ investigation" in n or "nove" in n or "hgtv" in n):
        return "discovery"
    if "sky cinema" in n:
        return "sky cinema"
    if "sky sport" in n and "sky calcio" not in n:
        return "sky sport"
    if "sky calcio" in n:
        return "sky calcio"
    if n.startswith("sky "):
        return "sky intrattenimento"
    if "dazn" in n:
        return "dazn"
    return "eventi"

def estrai_nome_base(nome_completo: str) -> str:
    """
    Da "RAI 1 (V)", "RAI 1 (V) (2)", "RAI 1 (2)" restituisce "RAI 1".
    Si tronca tutto ciò che segue " (" (spazio-parentesi) se presente.
    """
    if " (" in nome_completo:
        return nome_completo.split(" (")[0].strip()
    return nome_completo.strip()

def ordina_listone(input_m3u: str = "listone.m3u8",
                   output_m3u: str = "listone_ordinato.m3u8") -> None:
    """
    Legge `input_m3u` riga per riga, estrae tutte le coppie (#EXTINF..., URL),
    applica deduplica (mantiene solo la prima occorrenza di ogni canale "base"),
    ordina secondo CATEGORIE_IN_ORDINE e il nome completo alfabeticamente,
    infine scrive `output_m3u`. Se `input_m3u` non esiste, esce con errore.
    """
    if not os.path.isfile(input_m3u):
        print(f"Errore: '{input_m3u}' non trovato.", file=sys.stderr)
        sys.exit(1)

    canali = []         # memorizza tuple (categoria, nome_completo, url)
    seen_base = set()   # per deduplica dei "canali base"

    with open(input_m3u, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.read().splitlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#EXTINF"):
            # Estraggo nome_completo (ciò che segue l'ultima virgola)
            parti = line.split(",")
            nome_completo = parti[-1].strip()

            # Estraggo "nome base" (eliminando eventuali suffissi tra parentesi)
            nome_base = estrai_nome_base(nome_completo).upper()

            # Se il nome_base è già visto, skippo questa coppia EXTINF+URL (deduplica)
            if nome_base in seen_base:
                i += 2
                continue
            seen_base.add(nome_base)

            # URL successivo (se esiste)
            url_canale = lines[i+1].strip() if (i+1) < len(lines) else ""

            # Assegno la categoria
            categoria = trova_categoria(nome_completo)

            # Aggiungo la tupla
            canali.append((categoria, nome_completo, url_canale))
            i += 2
        else:
            i += 1

    # Ordino: prima per indice di categoria, poi alfabeticamente per nome completo
    canali.sort(key=lambda x: (CATEGORIE_IN_ORDINE.index(x[0]), x[1].lower()))

    # Scrivo il file ordinato
    with open(output_m3u, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for _, nome, url in canali:
            f.write(f"#EXTINF:-1,{nome}\n")
            f.write(f"{url}\n")

    print(f"[OK] '{output_m3u}' creato con {len(canali)} canali unici.")

if __name__ == "__main__":
    ordina_listone()
