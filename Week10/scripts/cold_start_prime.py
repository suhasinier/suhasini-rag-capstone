
"""Pre-populate the Week 10 semantic cache with CBSE FAQ questions."""

from src.rag.qdrant_rag import ask_rag

seed_questions = [
    # Overall curriculum and scheme of studies
    "What is the CBSE scheme of studies for Class IX for 2026-27?",
    "What subjects are included in the CBSE Class IX curriculum?",
    "What are the compulsory subjects for Class IX students?",
    "What vocational education options are available to Class IX students?",

    # Mathematics
    "What topics are covered in the Class IX Mathematics syllabus?",
    "What are the main algebra topics in Class IX Mathematics?",
    "Which geometry topics are included in the Class IX syllabus?",
    "What does the Class IX Mathematics curriculum cover apart from algebra and geometry?",

    # Science
    "What topics are included in the Class IX Science syllabus?",
    "Which topics are covered in Class IX Physics?",
    "What topics are covered in Class IX Chemistry?",
    "What are the main topics in Class IX Biology?",

    # Social Science
    "What subjects are covered in Class IX Social Science?",
    "What topics are included in Class IX History?",
    "What topics are covered in Class IX Geography?",
    "What are the main areas covered in Class IX Political Science?",

    # English
    "What does the Class IX English Language and Literature syllabus include?",
    "What are the reading and writing components of Class IX English?",
    "What literature components are prescribed for Class IX English?",

    # CBSE Circular 70/2026
    "What changes were announced for the Class IX scheme of studies for 2026-27?",
    "Which components are excluded from Class IX for the 2026-27 academic year?",
    "What changes were announced regarding Environmental Education?",
    "Is vocational education still compulsory under the revised scheme?",
    "What assessment provisions apply to vocational education?",
]

for q in seed_questions:
    result = ask_rag(q)
    print(f"Primed: {q!r} (hit={result['cache_hit']})")

print(f"\nPriming completed. Questions processed: {len(seed_questions)}")
