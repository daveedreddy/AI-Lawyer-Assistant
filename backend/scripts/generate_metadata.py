import os
import re
import json
import logging
import hashlib
import uuid
from pathlib import Path
from collections import Counter

# Initialize Logging Configuration for Enterprise Systems
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("metadata_pipeline.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Base Directory Configurations
BASE_DIR = Path(__file__).resolve().parent.parent
CHUNKED_DIR = BASE_DIR / "knowledge_base" / "processed" / "chunks"
METADATA_DIR = BASE_DIR / "knowledge_base" / "processed" / "metadata"
MANIFEST_FILE = METADATA_DIR / "metadata_manifest.json"

# Lightweight NLP Stopwords for Keyword Generation
STOPWORDS = {
    "shall", "which", "their", "there", "under", "where", "other", "these", "those", 
    "would", "could", "should", "about", "after", "before", "being", "having", "with", 
    "from", "into", "through", "during", "court", "act", "section", "article", "rule"
}

class LegalMetadataGenerator:
    """
    Core legal intelligence layer for chunk-level metadata enrichment.
    Extracts deep legal entities (Acts, Judgments, Sections, Citations) using 
    lightweight NLP and regex heuristics, assigning standalone context to every chunk.
    """
    def __init__(self):
        self.processing_version = "1.0.0"
        self.metadata_version = "1.0.0"
        
        METADATA_DIR.mkdir(parents=True, exist_ok=True)
        self.manifest = self.load_manifest()

    def load_manifest(self):
        """Loads the processing manifest for the metadata pipeline."""
        if MANIFEST_FILE.exists():
            try:
                with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to read metadata manifest file: {e}")
                return {}
        return {}

    def save_manifest(self):
        """Persists the metadata manifest to storage."""
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(self.manifest, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save metadata manifest file: {e}")

    def get_file_hash(self, file_path):
        """Generates a SHA-256 hash for the chunked JSON."""
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                buf = f.read()
                hasher.update(buf)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Hash generation failed for {file_path.name}: {e}")
            return None

    def generate_keywords(self, text, top_n=5):
        """Generates contextual keywords using lightweight term frequency (TF) analysis."""
        if not text:
            return []
        
        # Extract words longer than 4 characters, convert to lowercase
        words = re.findall(r'\b[a-zA-Z]{5,}\b', text.lower())
        filtered_words = [w for w in words if w not in STOPWORDS]
        
        # Count frequencies and return the most common terms
        counter = Counter(filtered_words)
        return [word for word, count in counter.most_common(top_n)]

    def extract_act_details(self, text, filename):
        """Extracts Act Name and Year from text or filename."""
        act_name = None
        act_year = None

        # Look for patterns like "The Indian Contract Act, 1872"
        act_match = re.search(r'(?i)(the\s+[a-zA-Z\s]+act)[\s,]*([12]\d{3})', text)
        if act_match:
            act_name = act_match.group(1).title().strip()
            act_year = int(act_match.group(2))
        else:
            # Fallback to filename parsing
            clean_name = filename.replace("_chunked.json", "").replace("_", " ")
            year_match = re.search(r'([12]\d{3})', clean_name)
            if year_match:
                act_year = int(year_match.group(1))
            act_name = clean_name.title()

        return act_name, act_year

    def extract_judgment_details(self, text):
        """Extracts highly specific metadata from judgment headers using regex heuristics."""
        details = {
            "court_name": None,
            "bench": None,
            "judge_names": [],
            "petitioner": None,
            "respondent": None,
            "case_title": None,
            "case_number": None,
            "citation": None,
            "judgment_date": None
        }

        if not text:
            return details

        # 1. Court Name
        court_match = re.search(r'(?i)(supreme court of india|high court of [a-zA-Z\s]+)', text)
        if court_match:
            details["court_name"] = court_match.group(1).title().strip()

        # 2. Case Number (Civil Appeal, Criminal Appeal, Writ Petition, Case No)
        case_no_match = re.search(r'(?i)(?:case\s+no\.|appeal\s+no\.|crl\.?\s*a\.?|civil\s+appeal(?:\s+no\.?)?|w\.?p\.?)\s*[:\-\s]*([A-Za-z0-9/.\-]+)', text)
        if case_no_match:
            details["case_number"] = case_no_match.group(0).strip()

        # 3. Citation (e.g., 2023 SCC 123 or AIR 2023 SC 45)
        citation_match = re.search(r'(?i)(\d{4}\s+(?:SCC|AIR|SCALE)\s+\d+)', text)
        if citation_match:
            details["citation"] = citation_match.group(1).upper()

        # 4. Date
        date_match = re.search(r'(?i)(?:dated|decided on|date of judgment)[\s:]*([0-9]{1,2}[/\-\sa-zA-Z]+[0-9]{4})', text)
        if date_match:
            details["judgment_date"] = date_match.group(1).strip()

        # 5. Bench / Coram
        bench_match = re.search(r'(?i)(?:bench|coram)\s*[:\-]\s*([a-zA-Z\s,\.]+)', text)
        if bench_match:
            details["bench"] = bench_match.group(1).strip().split('\n')[0]

        # 6. Judges
        judge_matches = re.findall(r'(?i)(?:hon\'?ble\s+mr\.\s+justice|before\s*:)\s*([a-zA-Z\s\.]+)', text)
        if judge_matches:
            details["judge_names"] = [j.strip() for j in judge_matches if len(j.strip()) > 3]

        # 7. Parties (Petitioner vs Respondent)
        vs_match = re.search(r'(?i)(.+?)\s+v(?:ersu)?s?\.?\s+(.+)', text)
        if vs_match:
            details["petitioner"] = vs_match.group(1).strip().split('\n')[-1].strip()
            details["respondent"] = vs_match.group(2).strip().split('\n')[0].strip()
            if len(details["petitioner"]) < 100 and len(details["respondent"]) < 100:
                details["case_title"] = f"{details['petitioner']} vs {details['respondent']}"
            else:
                details["petitioner"], details["respondent"] = None, None

        return details

    def extract_legal_entities(self, text):
        """Extracts granular legislative taxonomy from the chunk text."""
        def extract_unique(pattern):
            matches = re.findall(pattern, text)
            return list(dict.fromkeys([m.upper().strip() for m in matches])) if matches else None

        return {
            "part": extract_unique(r'(?i)\bpart\s+([IVXLCDM]+|\d+)\b'),
            "chapter": extract_unique(r'(?i)\bchapter\s+([IVXLCDM]+|\d+)\b'),
            "section": extract_unique(r'(?i)\b(?:section|sec\.)\s+(\d+[A-Z]?)\b'),
            "article": extract_unique(r'(?i)\b(?:article|art\.)\s+(\d+[A-Z]?)\b'),
            "rule": extract_unique(r'(?i)\brule\s+(\d+[A-Z]?)\b'),
            "schedule": extract_unique(r'(?i)\bschedule\s+([IVXLCDM]+|\d+)\b'),
            "clause": extract_unique(r'(?i)\bclause\s+(\d+[A-Z]?)\b'),
            "order": extract_unique(r'(?i)\border\s+([IVXLCDM]+|\d+)\b'),
            "appendix": extract_unique(r'(?i)\bappendix\s+([A-Z0-9]+)\b')
        }

    def process_all(self):
        """Orchestrates the metadata enrichment process, generating chunk-level vector payloads."""
        logger.info("Initializing Chunk-Level Legal Metadata Enrichment...")
        processed_count, skipped_count, failed_count = 0, 0, 0

        for root, _, files in os.walk(CHUNKED_DIR):
            for file in files:
                if not file.endswith(".json") or "manifest" in file.lower():
                    continue

                file_path = Path(root) / file
                relative_path = file_path.relative_to(CHUNKED_DIR)
                str_relative_path = str(relative_path)
                current_hash = self.get_file_hash(file_path)

                if str_relative_path in self.manifest and self.manifest[str_relative_path] == current_hash:
                    skipped_count += 1
                    continue

                logger.info(f"Enriching payload: {relative_path}")
                
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        payload = json.load(f)

                    # Determine Document Level Context from Paths
                    path_lower = str_relative_path.lower()
                    doc_type = "General Legal Document"
                    jurisdiction = "India"
                    
                    if "acts" in path_lower:
                        doc_type = "Act"
                    elif "judgments" in path_lower:
                        doc_type = "Judgment"
                    elif "constitution" in path_lower:
                        doc_type = "Constitution"
                    elif "faqs" in path_lower:
                        doc_type = "FAQ"

                    # Maintain Document-Level state for Judgments (Cascading metadata from Chunk 0)
                    doc_judgment_details = None
                    doc_act_name = None
                    doc_act_year = None

                    final_chunks = []
                    
                    # Verify chunked payload structure (handles dictionary containing list of chunks)
                    raw_chunks = payload.get("chunks", [])
                    if not raw_chunks:
                        logger.warning(f"No chunks found in {file}. Skipping.")
                        continue

                    for chunk_data in raw_chunks:
                        chunk_text = chunk_data.get("text", "")
                        chunk_index = chunk_data.get("chunk_index", 0)
                        
                        # Generate Unique ID for Vector DB compatibility
                        chunk_id = f"{payload.get('source_filename', 'doc')}_chunk_{chunk_index}_{uuid.uuid4().hex[:8]}"

                        # 1. Base Metadata Template
                        chunk_metadata = {
                            "document_type": doc_type,
                            "jurisdiction": jurisdiction,
                            "act_name": None,
                            "act_year": None,
                            "part": None,
                            "chapter": None,
                            "section": None,
                            "article": None,
                            "rule": None,
                            "schedule": None,
                            "clause": None,
                            "order": None,
                            "appendix": None,
                            "court_name": None,
                            "bench": None,
                            "judge_names": [],
                            "petitioner": None,
                            "respondent": None,
                            "case_title": None,
                            "case_number": None,
                            "citation": None,
                            "judgment_date": None,
                            "language": "English",
                            "keywords": self.generate_keywords(chunk_text),
                            "source_filename": payload.get("source_filename", file),
                            "relative_path": str_relative_path,
                            "source_format": payload.get("file_extension", ".txt").upper().replace(".", ""),
                            "processing_version": self.processing_version,
                            "metadata_version": self.metadata_version
                        }

                        # 2. Extract and Inject Document Specifics
                        if doc_type == "Act" or doc_type == "Constitution":
                            if not doc_act_name:
                                doc_act_name, doc_act_year = self.extract_act_details(chunk_text, file)
                                if doc_type == "Constitution":
                                    doc_act_name = "Constitution of India"
                            chunk_metadata["act_name"] = doc_act_name
                            chunk_metadata["act_year"] = doc_act_year

                        if doc_type == "Judgment":
                            if chunk_index == 0:
                                doc_judgment_details = self.extract_judgment_details(chunk_text)
                            
                            if doc_judgment_details:
                                for k, v in doc_judgment_details.items():
                                    chunk_metadata[k] = v

                        # 3. Extract Chunk Specific Legal Entities
                        entities = self.extract_legal_entities(chunk_text)
                        for k, v in entities.items():
                            chunk_metadata[k] = v

                        # 4. Finalize the ChromaDB compatible Chunk Object
                        final_chunks.append({
                            "chunk_id": chunk_id,
                            "text": chunk_text,
                            "metadata": chunk_metadata
                        })

                    # Output Array of perfectly formatted Chunks
                    output_folder = METADATA_DIR / relative_path.parent
                    output_folder.mkdir(parents=True, exist_ok=True)
                    output_filepath = output_folder / file.replace("_chunked.json", "_metadata.json")

                    with open(output_filepath, "w", encoding="utf-8") as out_f:
                        json.dump(final_chunks, out_f, indent=4, ensure_ascii=False)

                    self.manifest[str_relative_path] = current_hash
                    processed_count += 1
                    logger.info(f"Success: Processed {len(final_chunks)} fully enriched vectors for {file}")

                except Exception as e:
                    logger.error(f"Failed to process {file}: {e}")
                    failed_count += 1

        self.save_manifest()
        logger.info(f"Enrichment complete. Processed: {processed_count} | Skipped: {skipped_count} | Failed: {failed_count}")

if __name__ == "__main__":
    generator = LegalMetadataGenerator()
    generator.process_all()