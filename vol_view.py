import pandas as pd
import ast

def safe_convert_string_to_list(string):
    try:
        return ast.literal_eval(string)
    except (ValueError, SyntaxError):
        return [string] if string else []

def compare_pin_codes(pin1, pin2):
    num1 = int(str(pin1)[:3])
    num2 = int(str(pin2)[:3])
    difference = abs(num1 - num2)
    if difference >= 201:
        return 0
    elif 101 <= difference <= 200:
        return 1
    elif 51 <= difference <= 100:
        return 2
    elif 11 <= difference <= 50:
        return 3
    elif 0 <= difference <= 10:
        return 4

def calculate_match_score(person, job):
    shared_skills = set(person['Skills']).intersection(set(job['Skills Requirement']))
    shared_languages = set(person['Languages']).intersection(set(job['Language Requirement']))
    min_age, max_age = map(int, job['Age Range'].split('-'))
    if not shared_skills or not (min_age <= person['Age'] <= max_age) or len(shared_languages) == 0:
        return 0
    score = len(shared_languages) + (3 if job['Interest'].lower() in [interest.lower() for interest in person['Interests']] else 0) + len(shared_skills) * 2
    score += compare_pin_codes(person['Postal Code'], job['Postal Code'])
    return score

job_volunteer_openings = pd.read_csv('/content/jobs1.csv')
person_data = pd.read_csv('/content/people1.csv')

for column in ['Language Requirement', 'Skills Requirement', 'Skills', 'Languages', 'Interests']:
    if column in job_volunteer_openings:
        job_volunteer_openings[column] = job_volunteer_openings[column].apply(safe_convert_string_to_list)
    if column in person_data:
        person_data[column] = person_data[column].apply(safe_convert_string_to_list)

match_scores = []
for person_index, person in person_data.iterrows():
    for job_index, job in job_volunteer_openings.iterrows():
        score = calculate_match_score(person, job)
        match_scores.append({"Person Index": person_index, "Job Index": job_index, "Match Score": score})

match_scores_df = pd.DataFrame(match_scores)
top_matches = match_scores_df.sort_values(by=['Person Index', 'Match Score'], ascending=[True, False])
top_5_matches_per_person = top_matches.groupby('Person Index').head(5)

print(top_5_matches_per_person[['Person Index', 'Job Index', 'Match Score']])
