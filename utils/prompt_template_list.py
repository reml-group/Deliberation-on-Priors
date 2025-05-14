path_generation_template = "please generate relation paths that can help in reasoning to answer the question. The relation paths must start from the topic entities mentioned in the question. The question is: {question}, and the topic entities are: {start_entities}"

path_generation_response_template = "The helpful relation paths that start from the topic entities are: {relation_paths}"

path_selection_prompt = """
Based on the reasoning relation paths in Freebase, think step by step to select the most one relevant path to answer the question. 
#####
You will be given:
- Question: The question to be answered.
- Topic Entities: The main entities identified in the question.
- Memory: Paths have been selected and the feedback of the previous step.
- Reasoning Paths: A set of reasoning paths starting from the topic entities. 

#####
Here are some examples.
Example 1:
- Question: What sports team owned by George Steinbrenner did Deion Sanders play baseball for?, 
- Topic Entities: ['Baseball', 'Deion Sanders', 'George Steinbrenner'],
- Memory: [], 
- Reasoning Paths: ['Path 1: Baseball -> base.sportbase.sport.played_by_clubs -> Unknown Entity', 'Path 2: Deion Sanders -> sports.pro_athlete.teams -> Unknown Entity -> sports.sports_team_roster.team -> Unknown Entity', 'Path 3: Deion Sanders -> baseball.baseball_player.batting_stats -> Unknown Entity -> baseball.batting_statistics.team -> Unknown Entity', 'Path 4: George Steinbrenner -> sports.sports_team_owner.teams_owned -> Unknown Entity']

- Output: {{Path 2}} - This path starts from Deion Sanders, follows his professional athlete teams, and connects to a specific sports team. Since the question asks for the team he played baseball for, this path is the most relevant in identifying the correct team.

Example 2:
- Question: What movie was Charlie Hunnam in that was about human extinction?,
- Topic Entities: ['Human extinction', 'Charlie Hunnam'],
- Memory: [{{'selected_path': 'Charlie Hunnam -> film.actor.film -> Unknown Entity -> film.performance.film -> Unknown Entity', 'feedback': 'This path connects Charlie Hunnam to films he has acted in, but we need to find which movie is about human extinction.'}}],
- Reasoning Paths: ['Path 1: Human extinction -> film.film_subject.films -> Unknown Entity', 'Path 2: Charlie Hunnam -> film.actor.film -> Unknown Entity -> film.performance.film -> Unknown Entity', 'Path 3: Charlie Hunnam -> common.topic.notable_types -> Unknown Entity', 'Path 4: Charlie Hunnam -> tv.tv_actor.starring_roles -> Unknown Entity -> tv.regular_tv_appearance.character -> Unknown Entity']

- Output: {{Path 1}} - The previous selected path connected Charlie Hunnam to films he acted in but did not ensure the movie was about human extinction. This path directly connects "Human extinction" to relevant films, making it the best choice to identify the correct movie.

Example 3:
- Question: Which state with Colorado River that Larry Owens was born in?
- Topic Entities: ['Colorado River', 'Larry Owens'],
- Memory: [{{'selected_path': 'Colorado River -> location.location.partially_containedby -> Unknown Entity', 'feedback': 'This path connects Colorado River to a location, but we need to find the state Larry Owens was born in.'}}],
- Reasoning Paths: ['Path 1: Larry Owens -> people.person.spouse_s -> Unknown Entity -> people.sibling_relationship.sibling -> Unknown Entity']

- Output: {{no path}} - None of the available paths lead to information about the state where Larry Owens was born.

#####Input:
Question: {question},
Topic Entities: {topic_entities},
Memory: {memory},
Reasoning Paths: {paths}

#####Output:
"""
verification_prompt = """
Given a question and the associated retrieved knowledge triplets from Freebase, your task is to answer the question with these triplets and your knowledge.
#####
You will be given:
- Question: The question to be answered.
- Topic Entity: The main entity identified in the question.
- Constraints: The constraints extracted from the question that should be verified.
- Reasoning Paths: Paths starting from the topic entity (contains only relations).
- Knowledge Triplets: The instantiated reasoning paths in the form of triplets (entity, relation, entity).

Think step by step to answer the question:
- List all potential answers (**tail entities**) based on the knowledge triplets, ranking them by how likely they satisfy the question and constraints, and placing the most likely ones first. 
- Check if the answer satisfies the constraints and provide an explanation detailing the reasoning process and any missing knowledge needed for full verification.
Return a **JSON object** with the identified constraints.

#####
Here are some examples.
Example 1:
- Question: what is the name of justin bieber brother
- Topic Entity: ['Justin Bieber'],
- Constraints: [],
- Reasoning Path: ['Justin Bieber -> people.person.sibling_s -> Unknown Entity -> people.sibling_relationship.sibling -> Unknown Entity'],
- Knowledge Triplets: [[['Justin Bieber', 'people.person.sibling_s', 'm.0gxnnwp'], ['m.0gxnnwp', 'people.sibling_relationship.sibling', 'Jaxon Bieber']]]

- Output: {{"answer": ["Jaxon Bieber"], "sufficient": "Yes", "reason": "Based on the reasoning path, the answer is Jaxon Bieber, which is the sibling of Justin Bieber."}}

Example 2:
- Question: What year did the MLB franchise owned by Bill Neukom win the world series?
- Topic Entities: ['Bill Neukom'],
- Constraints: ['1. The MLB franchise is owned by Bill Neukom', '2. The year in which the franchise won the World Series'],
- Reasoning Path: ['Bill Neukom -> sports.sports_team_owner.teams_owned -> Unknown Entity -> sports.sports_team.championships -> Unknown Entity'],
- Knowledge Triplets: [[[['Bill Neukom', 'sports.sports_team_owner.teams_owned', 'San Francisco Giants'], ['San Francisco Giants', 'sports.sports_team.championships', '2010 World Series']], [['Bill Neukom', 'sports.sports_team_owner.teams_owned', 'San Francisco Giants'], ['San Francisco Giants', 'sports.sports_team.championships', '2014 World Series']], [['Bill Neukom', 'sports.sports_team_owner.teams_owned', 'San Francisco Giants'], ['San Francisco Giants', 'sports.sports_team.championships', '2012 World Series']]]]

- Output: {{"answer": ["2014 World Series", "2012 World Series", "2010 World Series"], "sufficient": "Yes", "reason": "The reasoning path connects Bill Neukom to the MLB franchise he owns and the events (tail entities) representing the years they won the World Series. Each tail entity like '2014 World Series' directly encodes the answer year, so they are valid answers."}}

Example 3:
- Question: what year did the seahawks win the superbowl
- Topic Entities: ['Seattle Seahawks'],
- Constraints: ['1. The answer should be a year', '2. The Seattle Seahawks won the Super Bowl in that year'],
- Reasoning Path: ['Seattle Seahawks -> sports.sports_team.championships -> Unknown Entity'],
- Knowledge Triplets: [[[['Seattle Seahawks', 'sports.sports_team.championships', '2014 NFC Championship Game']], [['Seattle Seahawks', 'sports.sports_team.championships', 'Super Bowl XLVIII']], [['Seattle Seahawks', 'sports.sports_team.championships', '2006 NFC Championship Game']]]]

- Output: {{"answer": ["Super Bowl XLVIII"], "sufficient": "Yes", "reason": "The answer 'Super Bowl XLVIII' is the tail entity in the reasoning path. It represents the event where the Seattle Seahawks won the Super Bowl, which occurred in 2014. Although the question asks for a year, the tail entity is used as a proxy to provide the required information."}}

Example 4:
- Question: What movie was Charlie Hunnam in that was about human extinction?,
- Topic Entities: ['Human extinction', 'Charlie Hunnam'],
- Constraints: ['1. The movie is a film Charlie Hunnam acted in.', '2. The movie is about human extinction.'],
- Reasoning Path: ['Charlie Hunnam -> film.actor.film -> Unknown Entity -> film.performance.film -> Unknown Entity'],
- Knowledge Triplets: [[[['Charlie Hunnam', 'film.actor.film', 'm.0jwksr'], ['m.0jwksr', 'film.performance.film', 'Cold Mountain']],[['Charlie Hunnam', 'film.actor.film', 'm.0jy_sj'], ['m.0jy_sj', 'film.performance.film', 'Green Street']],[['Charlie Hunnam', 'film.actor.film', 'm.046168c'], ['m.046168c', 'film.performance.film', 'Children of Men']]]]

- Output: {{"answer": ["Children of Men", "Green Street", "Cold Mountain"], "sufficient": "No", "reason": "The reasoning path connects Charlie Hunnam to films he has acted in, but we need to find which movie is about human extinction."}},

Now you need to output the results of the following input in JSON format.
#####Input:
Question: {question}, 
Topic entity: {topic_entities},
constraints = {constraints},
Reasoning Path: {path},
Knowledge Triplets: {triplets},

#####Output:
"""

constraint_extraction_prompt = """
You will be given a question. Your task is to identify and extract any constraints present in the question.

**Types of constraints to extract:**

1. Type Constraint:
   - The question specifies a required type or category for the answer.

2. Multi-Entity Constraint:
   - The question contains multiple entities and requires the answer to simultaneously satisfy conditions related to these entities.

3. Explicit Time Constraint:
   - The question clearly defines a specific time period or date to be referenced

4. Implicit Time Constraint:
   - The question implies a temporal frame that the answer should consider.

5. Order Constraint:
   - The question contains the sorting rule and requires the answer in a specific order.

**Instructions:**
- Extract only present constraints: Do not add constraints not explicitly or implicitly mentioned in the question.
-Output Format: Return a **List object** with the identified constraints. Each constraint type should either contain the relevant information or an empty string if not applicable.
#####
Here are some examples:
Example 1:
- Question: What country bordering France contains an airport that serves Nijmegen?
- Output: ["1. The answer should be a country", "2. The country borders France", "3. The country contains an airport that serves Nijmegen."]
Example 2:
- Question: Who was the 1996 coach of the team owned by Jerry Jones?
- Output: ["1. The team is owned by Jerry Jones", "2. The person was the coach in 1996"]
Example 3:
- Question: what did james k polk do before he was president
- Output: ["1. The question implies the time before James K. Polk was president"]
Example 4:
- Question: What was the last World Series won by the team whose mascot is Lou Seal?
- Output: ["1. The team is the one whose mascot is Lou Seal", "2. The answer should be a World Series", "3. The World Series is the last one won by the team"]
Example 5:
- Question: What genre is the movie Titanic?
- Output: ["1. The answer should be a genre of the movie"]
#####
Input question: {question}
Output:
"""
llm_only_answering_prompt = """
You are tasked with answering a knowledge graph question based on Freebase.
You will be given:
- Question: The question to be answered.
- Constraints: The constraints extracted from the question that should be verified.

### Your Task:
1. Carefully think through the question and constraints.
2. Infer the correct Freebase entity or entities that answer the question based on the provided information.
3. Clearly explain your reasoning process step by step before providing the final answer.
4. Return the answer as a **list of Freebase entity names** (not IDs).
#####Input:
Question: {question}, 
constraints = {constraints}

#####Output:
"""
