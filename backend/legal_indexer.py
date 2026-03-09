"""
Legal Research Indexer — Imigrai
Indexa fontes públicas de direito imigratório americano no MongoDB.

Fontes:
1. USCIS Policy Manual (policy-manual.uscis.gov)
2. CFR Título 8 (ecfr.gov)
3. AAO Decisions via Court Listener (courtlistener.com/api/)

Roda uma vez para indexar, depois incremental semanalmente.
"""

import asyncio
import hashlib
import logging
import os
import re
from datetime import datetime

import httpx
from bs4 import BeautifulSoup
from motor.motor_asyncio import AsyncIOMotorClient
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "osprey_immigration_db"
COLLECTION = "legal_knowledge"

# Modelo leve e eficiente — roda bem em VPS com 16GB RAM
MODEL_NAME = "all-MiniLM-L6-v2"

# ── FONTES ──────────────────────────────────────────────────────

USCIS_POLICY_VOLUMES = [
    {"vol": "1", "name": "General Policies and Procedures", "url": "https://www.uscis.gov/policy-manual/volume-1"},
    {"vol": "2", "name": "Nonimmigrants", "url": "https://www.uscis.gov/policy-manual/volume-2"},
    {"vol": "3", "name": "Protecting Immigrants", "url": "https://www.uscis.gov/policy-manual/volume-3"},
    {"vol": "6", "name": "Immigrants", "url": "https://www.uscis.gov/policy-manual/volume-6"},
    {"vol": "7", "name": "Adjustment of Status", "url": "https://www.uscis.gov/policy-manual/volume-7"},
    {"vol": "8", "name": "Admissibility", "url": "https://www.uscis.gov/policy-manual/volume-8"},
    {"vol": "10", "name": "Employment Authorization", "url": "https://www.uscis.gov/policy-manual/volume-10"},
    {"vol": "12", "name": "Citizenship & Naturalization", "url": "https://www.uscis.gov/policy-manual/volume-12"},
]

CFR_PARTS = [
    {"part": "214", "name": "Nonimmigrant Classes", "url": "https://www.ecfr.gov/current/title-8/chapter-I/subchapter-B/part-214"},
    {"part": "204", "name": "Immigrant Petitions", "url": "https://www.ecfr.gov/current/title-8/chapter-I/subchapter-B/part-204"},
    {"part": "245", "name": "Adjustment of Status", "url": "https://www.ecfr.gov/current/title-8/chapter-I/subchapter-B/part-245"},
    {"part": "248", "name": "Change of Nonimmigrant Status", "url": "https://www.ecfr.gov/current/title-8/chapter-I/subchapter-B/part-248"},
    {"part": "274a", "name": "Control of Employment of Aliens", "url": "https://www.ecfr.gov/current/title-8/chapter-I/subchapter-B/part-274a"},
]

COURT_LISTENER_AAO = "https://www.courtlistener.com/api/rest/v4/opinions/?court=aao&order_by=-date_filed&format=json&page_size=100"


# ── CHUNKER ─────────────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list:
    """Divide texto em chunks com overlap para melhor contexto."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i : i + chunk_size])
        if len(chunk.strip()) > 100:
            chunks.append(chunk.strip())
        i += chunk_size - overlap
    return chunks


def clean_html(html: str) -> str:
    """Remove HTML e limpa espaços."""
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def doc_id(url: str, chunk_index: int) -> str:
    """ID único por chunk."""
    return hashlib.md5(f"{url}:{chunk_index}".encode()).hexdigest()


def extract_visa_types(text: str) -> list:
    """Detecta tipos de visto mencionados no chunk."""
    patterns = {
        "H-1B": r"\bH-?1B\b",
        "EB-1A": r"\bEB-?1A?\b|extraordinary ability",
        "EB-2 NIW": r"\bEB-?2\b.*\bNIW\b|national interest waiver",
        "O-1A": r"\bO-?1A?\b",
        "L-1A": r"\bL-?1A?\b",
        "I-130": r"\bI-?130\b",
        "I-485": r"\bI-?485\b",
        "I-765": r"\bI-?765\b",
        "F-1": r"\bF-?1\b",
        "B-2": r"\bB-?2\b",
    }
    found = []
    for visa, pattern in patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(visa)
    return found


# ── SCRAPERS ─────────────────────────────────────────────────────

async def scrape_uscis_policy(client: httpx.AsyncClient, volume: dict) -> list:
    """Scrape USCIS Policy Manual — um volume."""
    docs = []
    try:
        resp = await client.get(volume["url"], timeout=30)
        if resp.status_code != 200:
            logger.warning(f"Failed to fetch {volume['url']}: {resp.status_code}")
            return docs

        soup = BeautifulSoup(resp.text, "lxml")

        # Pegar links dos capítulos/partes dentro do volume
        links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/policy-manual/volume-" in href and href != volume["url"]:
                full_url = f"https://www.uscis.gov{href}" if href.startswith("/") else href
                if full_url not in links:
                    links.append(full_url)

        if not links:
            links = [volume["url"]]

        for link in links[:20]:
            try:
                page = await client.get(link, timeout=30)
                if page.status_code != 200:
                    continue

                text = clean_html(page.text)
                if len(text) < 200:
                    continue

                chunks = chunk_text(text)
                for i, chunk in enumerate(chunks):
                    docs.append(
                        {
                            "doc_id": doc_id(link, i),
                            "source": "uscis_policy_manual",
                            "volume": volume["vol"],
                            "volume_name": volume["name"],
                            "url": link,
                            "chunk_index": i,
                            "text": chunk,
                            "indexed_at": datetime.utcnow(),
                            "visa_types": extract_visa_types(chunk),
                        }
                    )

                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error scraping {link}: {e}")
                continue

        logger.info(f"Volume {volume['vol']}: {len(docs)} chunks")
    except Exception as e:
        logger.error(f"Error with volume {volume['vol']}: {e}")

    return docs


async def scrape_cfr(client: httpx.AsyncClient, part: dict) -> list:
    """Scrape eCFR Título 8 — HTML first, JSON fallback."""
    docs = []
    try:
        text = ""

        # Try HTML scraping first (more reliable)
        resp = await client.get(part["url"], timeout=45)
        if resp.status_code == 200:
            text = clean_html(resp.text)

        # If HTML too short, try JSON API
        if len(text) < 500:
            api_url = f"https://www.ecfr.gov/api/versioner/v1/full/current/title-8.json?part={part['part']}"
            resp = await client.get(api_url, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                text = extract_cfr_text(data)

        if len(text) < 200:
            logger.warning(f"CFR Part {part['part']}: insufficient content ({len(text)} chars)")
            return docs

        chunks = chunk_text(text)
        for i, chunk in enumerate(chunks):
            docs.append(
                {
                    "doc_id": doc_id(part["url"], i),
                    "source": "cfr_title_8",
                    "part": part["part"],
                    "part_name": part["name"],
                    "url": part["url"],
                    "chunk_index": i,
                    "text": chunk,
                    "indexed_at": datetime.utcnow(),
                    "visa_types": extract_visa_types(chunk),
                }
            )

        logger.info(f"CFR Part {part['part']}: {len(docs)} chunks")
    except Exception as e:
        logger.error(f"Error with CFR part {part['part']}: {e}")

    return docs


async def fetch_aao_decisions(client: httpx.AsyncClient, max_pages: int = 5) -> list:
    """Fetch AAO Decisions from USCIS and DOJ/EOIR sources."""
    docs = []

    # Source 1: USCIS AAO non-precedent decisions search page
    aao_urls = [
        "https://www.uscis.gov/administrative-appeals/aao-decisions/aao-non-precedent-decisions",
        "https://www.uscis.gov/administrative-appeals/aao-decisions",
        "https://www.uscis.gov/administrative-appeals",
    ]

    for url in aao_urls:
        try:
            resp = await client.get(url, timeout=30)
            if resp.status_code != 200:
                continue

            text = clean_html(resp.text)
            if len(text) < 200:
                continue

            chunks = chunk_text(text)
            for i, chunk in enumerate(chunks):
                docs.append(
                    {
                        "doc_id": doc_id(url, i),
                        "source": "aao_decisions",
                        "case_name": "USCIS AAO Guidance",
                        "date_filed": "",
                        "url": url,
                        "chunk_index": i,
                        "text": chunk,
                        "indexed_at": datetime.utcnow(),
                        "visa_types": extract_visa_types(chunk),
                    }
                )

            await asyncio.sleep(1)
        except Exception as e:
            logger.error(f"Error fetching AAO page {url}: {e}")

    # Source 2: Court Listener API (may require auth)
    try:
        resp = await client.get(COURT_LISTENER_AAO, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            for opinion in data.get("results", []):
                text = opinion.get("plain_text", "") or opinion.get(
                    "html_with_citations", ""
                )
                if not text:
                    continue
                if "<" in text:
                    text = clean_html(text)

                chunks = chunk_text(text)
                case_name = opinion.get("case_name", "AAO Decision")
                date_filed = opinion.get("date_filed", "")
                opinion_url = f"https://www.courtlistener.com{opinion.get('absolute_url', '')}"

                for i, chunk in enumerate(chunks):
                    docs.append(
                        {
                            "doc_id": doc_id(opinion_url, i),
                            "source": "aao_decisions",
                            "case_name": case_name,
                            "date_filed": date_filed,
                            "url": opinion_url,
                            "chunk_index": i,
                            "text": chunk,
                            "indexed_at": datetime.utcnow(),
                            "visa_types": extract_visa_types(chunk),
                        }
                    )
        else:
            logger.warning(f"Court Listener AAO: status {resp.status_code} (may need auth)")
    except Exception as e:
        logger.warning(f"Court Listener AAO failed: {e}")

    # Source 3: Key AAO precedent decisions (well-known cases)
    precedent_texts = [
        {
            "case_name": "Matter of Dhanasar (2016)",
            "url": "https://www.uscis.gov/sites/default/files/err/B5%20-%20Members%20of%20the%20Professions%20holding%20Advanced%20Degrees%20or%20Aliens%20of%20Exceptional%20Ability/Decisions_Issued_in_2016/DEC312016_01B5101.pdf",
            "text": (
                "Matter of Dhanasar, 26 I&N Dec. 884 (AAO 2016). The AAO established a new analytical framework "
                "for adjudicating national interest waiver (NIW) petitions under INA 203(b)(2)(B). The three-prong "
                "Dhanasar framework replaced the previous NYSDOT framework and requires: (1) The foreign national's "
                "proposed endeavor has both substantial merit and national importance; (2) The foreign national is "
                "well positioned to advance the proposed endeavor; and (3) On balance, it would be beneficial to the "
                "United States to waive the requirements of a job offer and thus of a labor certification. "
                "Prong 1 - Substantial Merit and National Importance: The endeavor's merit may be demonstrated in a "
                "range of areas such as business, entrepreneurialism, science, technology, culture, health, or education. "
                "National importance requires the endeavor to have implications beyond a specific locality. "
                "Prong 2 - Well Positioned: Factors include education, skills, knowledge, record of success, a plan "
                "or model for future activity, progress towards achieving the proposed endeavor, and interest from "
                "relevant individuals, organizations, or governmental entities. "
                "Prong 3 - Balancing: Even assuming the other statutory requirements are met, USCIS may determine "
                "that it is not in the national interest to waive the labor certification requirement."
            ),
        },
        {
            "case_name": "Kazarian v. USCIS (2010)",
            "url": "https://scholar.google.com/scholar_case?case=kazarian+v+uscis",
            "text": (
                "Kazarian v. USCIS, 596 F.3d 1115 (9th Cir. 2010). This landmark case established the two-step "
                "analytical framework for evaluating EB-1A extraordinary ability petitions. Step 1: USCIS determines "
                "if the evidence meets any of the regulatory criteria (at least 3 of 10). Step 2: USCIS conducts a "
                "final merits determination to evaluate whether the totality of the evidence demonstrates sustained "
                "national or international acclaim and extraordinary ability. The court held that meeting the minimum "
                "evidentiary criteria alone does not automatically establish eligibility; the petitioner must also "
                "demonstrate that the totality of the evidence shows the requisite extraordinary ability. "
                "The 10 criteria for EB-1A are: (1) Awards/prizes for excellence; (2) Membership in associations "
                "requiring outstanding achievements; (3) Published material about the alien; (4) Judging the work of "
                "others; (5) Original contributions of major significance; (6) Authorship of scholarly articles; "
                "(7) Display of work at exhibitions; (8) Leading/critical role in distinguished organizations; "
                "(9) High salary; (10) Commercial success in performing arts."
            ),
        },
        {
            "case_name": "Matter of New York State DOT (1998)",
            "url": "https://www.justice.gov/eoir/matter-new-york-state-department-transportation",
            "text": (
                "Matter of New York State Department of Transportation, 22 I&N Dec. 215 (Acting Assoc. Comm. 1998). "
                "This case established the original three-prong test for national interest waivers (NIW) before being "
                "superseded by Matter of Dhanasar in 2016. The NYSDOT framework required: (1) The alien seeks "
                "employment in an area of substantial intrinsic merit; (2) The proposed benefit is national in scope; "
                "and (3) The national interest would be adversely affected if a labor certification were required. "
                "While superseded by Dhanasar, understanding NYSDOT is important because older AAO decisions and "
                "some precedent may still reference this framework."
            ),
        },
    ]

    for p in precedent_texts:
        chunks = chunk_text(p["text"])
        for i, chunk in enumerate(chunks):
            docs.append(
                {
                    "doc_id": doc_id(p["url"], i),
                    "source": "aao_decisions",
                    "case_name": p["case_name"],
                    "date_filed": "",
                    "url": p["url"],
                    "chunk_index": i,
                    "text": chunk,
                    "indexed_at": datetime.utcnow(),
                    "visa_types": extract_visa_types(chunk),
                }
            )

    logger.info(f"AAO total: {len(docs)} chunks")
    return docs


def extract_cfr_text(data: dict) -> str:
    """Extrai texto recursivamente do JSON do eCFR."""
    texts = []

    def recurse(node):
        if isinstance(node, dict):
            if "text" in node:
                texts.append(node["text"])
            if "heading" in node:
                texts.append(node["heading"])
            for v in node.values():
                recurse(v)
        elif isinstance(node, list):
            for item in node:
                recurse(item)

    recurse(data)
    return " ".join(texts)


# ── EMBEDDINGS + INDEXAÇÃO ───────────────────────────────────────


async def index_documents(docs: list, model: SentenceTransformer, db):
    """Gera embeddings e insere no MongoDB."""
    if not docs:
        return 0

    texts = [d["text"] for d in docs]
    logger.info(f"Generating embeddings for {len(texts)} chunks...")
    embeddings = model.encode(texts, batch_size=32, show_progress_bar=True)

    for doc, embedding in zip(docs, embeddings):
        doc["embedding"] = embedding.tolist()

    inserted = 0
    for doc in docs:
        result = await db[COLLECTION].update_one(
            {"doc_id": doc["doc_id"]}, {"$set": doc}, upsert=True
        )
        if result.upserted_id:
            inserted += 1

    return inserted


# ── MAIN ─────────────────────────────────────────────────────────


async def run_indexer(sources: list = None):
    """
    Indexar fontes jurídicas.
    sources: ["policy_manual", "cfr", "aao"] ou None para todas
    """
    client_db = AsyncIOMotorClient(MONGO_URI)
    db = client_db[DB_NAME]

    await db[COLLECTION].create_index([("text", "text")])
    await db[COLLECTION].create_index([("source", 1)])
    await db[COLLECTION].create_index([("visa_types", 1)])
    await db[COLLECTION].create_index([("doc_id", 1)], unique=True)

    logger.info("Loading embedding model...")
    model = SentenceTransformer(MODEL_NAME)

    total = 0

    async with httpx.AsyncClient(
        headers={
            "User-Agent": "Imigrai Legal Research Bot/1.0 (immigration law research)"
        },
        follow_redirects=True,
    ) as http:

        if not sources or "policy_manual" in sources:
            logger.info("=== Indexing USCIS Policy Manual ===")
            for volume in USCIS_POLICY_VOLUMES:
                docs = await scrape_uscis_policy(http, volume)
                n = await index_documents(docs, model, db)
                total += n
                logger.info(f"Volume {volume['vol']}: +{n} new chunks")

        if not sources or "cfr" in sources:
            logger.info("=== Indexing CFR Title 8 ===")
            for part in CFR_PARTS:
                docs = await scrape_cfr(http, part)
                n = await index_documents(docs, model, db)
                total += n
                logger.info(f"CFR Part {part['part']}: +{n} new chunks")

        if not sources or "aao" in sources:
            logger.info("=== Indexing AAO Decisions ===")
            docs = await fetch_aao_decisions(http, max_pages=10)
            n = await index_documents(docs, model, db)
            total += n
            logger.info(f"AAO Decisions: +{n} new chunks")

    count = await db[COLLECTION].count_documents({})
    logger.info(f"=== INDEXING COMPLETE === Total in DB: {count} chunks (+{total} new)")
    return total


if __name__ == "__main__":
    import sys

    sources = sys.argv[1:] if len(sys.argv) > 1 else None
    asyncio.run(run_indexer(sources))
