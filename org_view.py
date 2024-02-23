import pandas as pd
import ast

def safe_convert_string_to_list(string):
    try:
        return ast.literal_eval(string)
    except (ValueError, SyntaxError):
        return [string] if string and not isinstance(string, list) else []

def compare_pin_codes(pin1, pin2):
    num1 = int(str(pin1)[:3])
    num2 = int(str(pin2)[:3])
    difference = abs(num1 - num2)
    if difference >= 201:
        return 0
    elif difference <= 200:
        if difference >= 101:
            return 1
        elif difference >= 51:
            return 2
        elif difference >= 11:
            return 3
    return 4

def calculate_match_score(person, job):
    shared_skills = set(person['Skills']).intersection(set(job['Skills Requirement']))
    shared_languages = set(person['Languages']).intersection(set(job['Language Requirement']))
    min_age, max_age = map(int, job['Age Range'].split('-'))
    score = 0
    if shared_languages and shared_skills and (min_age <= person['Age'] <= max_age):
        score = len(shared_languages) + len(shared_skills) * 2
        if job['Interest'].lower() in [interest.lower() for interest in person['Interests']]:
            score += 3
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
for job_index, job in job_volunteer_openings.iterrows():
    for person_index, person in person_data.iterrows():
        score = calculate_match_score(person, job)
        match_scores.append({"Job Index": job_index, "Person Index": person_index, "Match Score": score})

match_scores_df = pd.DataFrame(match_scores)
top_prospects_by_job = pd.concat(
    [group.nlargest(job_volunteer_openings.loc[idx, 'No. of Open Positions'], 'Match Score') 
     for idx, group in match_scores_df.groupby('Job Index')]
)

print(top_prospects_by_job[['Job Index', 'Person Index', 'Match Score']])
