from models import Professor
from rmp import get_professor_info  # your existing scraper

def get_or_create_professor(name, university="University of California Santa Cruz"):
    professor = Professor.objects.filter(name__iexact=name, university__iexact=university).first()
    if professor:
        return professor
    
    scraped_data = get_professor_info(name, university)
    if not scraped_data:
        return None

    professor = Professor.objects.create(
        name=scraped_data["name"],
        university=scraped_data["university"],
        rating=scraped_data["rating"],
        difficulty=scraped_data["difficulty"],
        take_again=scraped_data["take_again"],
        tags=scraped_data["tags"]
    )
    return professor
