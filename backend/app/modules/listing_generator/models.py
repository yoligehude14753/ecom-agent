from dataclasses import dataclass, field


@dataclass
class GeneratedListing:
    asin_reference: str
    marketplace: str
    language: str
    title: str
    bullet_points: list[str]          # exactly 5
    description: str
    search_terms: list[str]           # backend keywords, max 250 chars
    subject_matter: list[str]         # A+ content focus topics
    a_plus_draft: str                 # A+ content narrative draft
    seo_score: float                  # estimated SEO quality 0-10
    character_counts: dict            # {title, description, search_terms}
