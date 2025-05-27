import sys
sys.path.append(
    '/Users/stellabullo/my_projects/health-projects/metaphor-tagger')


def tag_pain_description(description):
    from pain_descriptor_auto_tagger import process_text_batch  # delayed import
    input_data = [{"id": 1, "description": description}]
    results = process_text_batch(input_data)
    return results[0]
