

import shap
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import numpy as np
from nltk import ngrams
from nltk.tokenize import word_tokenize
import re
import os
import csv
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.llms import LlamaCpp

all_user_ids_to_post_ids = {
    "19041": ["1ftvgt", "2j2t7i"],
    "19239": ["1wj80m"],
    "19788": ["36eh73", "3am642"],
    "48665": ["ev6tp"],
    "1523": ["3ejsiv"],
    "6939": ["17r00i", "3fuxue"],
    "6998": ["3c83gc"],
    "7302": ["3gcaik"],
    "10090": ["22l8w4", "2mb3ku"],
    "11388": ["2m9gm4"],
    "12559": ["2sq2me"],
    "14958": ["1shwnv"],
    "15807": ["l5jxp"],
    "18608": ["2v0w14"],
    "18639": ["2f7wj4"],
    "20277": ["3hy1hk", "3i9p8b"],
    "21653": ["16xkll"],
    "23080": ["1gceob", "1t7se3"],
    "23341": ["3dthkh"],
    "23400": ["1y298o"],
    "24003": ["2jo2q0"],
    "24331": ["2zienb"],
    "27262": ["2u5z30"],
    "29356": ["26nqsc"],
    "30179": ["2evvoo"],
    "34032": ["1otrx6"],
    "34464": ["35lq71"],
    "34502": ["12umtk"],
    "37770": ["3f9nd4", "3gk55c"],
    "38531": ["2qlffz"],
    "39656": ["30reha"],
    "39832": ["1xpagm", "2017wz"],
    "40671": ["357o7f"],
    "41651": ["2scmvs", "2u91iq"],
    "43030": ["2fwbqi"],
    "43328": ["2x08xn"],
    "44826": ["1k3agb"],
    "46267": ["2nmehc"],
    "49038": ["2gt6wk", "2hnma9"],
    "11360": ["2xrnry"],
    "13321": ["3ic4t8"],
    "14075": ["32b7zk", "33kh5m", "35ylua"],
    "16852": ["1631gw"],
    "16867": ["30xti7", "32jo2k"],
    "18321": ["21mm33", "241gpm"],
    "19250": ["3gizbj"],
    "21926": ["1ph5yt"],
    "28817": ["36xc3s", "383n1f", "3cq8kt"],
    "29142": ["38bc2o"],
    "31972": ["2iz5y7"],
    "33368": ["2f27hy"],
    "33824": ["33r8b6"],
    "34268": ["2z2q1f"],
    "37759": ["3152g6"],
    "46616": ["10llu1"],
    "46771": ["3896jf"],
    "24231": ["23tvqs"],
    "35822": ["24u2gv"],
    "44554": ["2jfo9n", "2onplv"],
    "47912": ["thn6n"],
    "3434": ["3h0z05"],
    "5916": ["280apu"],
    "8368": ["1azxoz"],
    "8547": ["39akaq"],
    "10940": ["2h4b4q"],
    "13753": ["2vcol2"],
    "14272": ["yaqxi"],
    "14302": ["2b3y50", "2booi6"],
    "14680": ["16d5de"],
    "15722": ["31dz04"],
    "16366": ["3dv1gk"],
    "16596": ["2rp5bb", "319ioh"],
    "16673": ["2uquru"],
    "17606": ["1tplbc"],
    "18616": ["xfyos"],
    "19510": ["3gx2sj"],
    "25320": ["2aqb2a", "2kvmof"],
    "27214": ["mxci8", "13c9hl", "1455fd"],
    "31509": ["2c7y41"],
    "31683": ["3gjkm6"],
    "32490": ["2h1vke"],
    "32714": ["35miyb"],
    "34078": ["2802g5"],
    "36117": ["1mjszi", "2d3de4"],
    "43263": ["25rnwu"],
    "43701": ["3hxe6j"],
    "44656": ["278mzu"],
    "44846": ["2yek5b"],
    "45909": ["2ng6fr"],
    "46258": ["1wb4qr", "2wsqbn"],
    "46530": ["20d48v"],
    "47012": ["37jcax"],
    "47614": ["pnkh4", "15j1ft"],
    "47899": ["19jxq1"],
    "50326": ["3akx6o"],
    "3058": ["3iagg6"],
    "3928": ["32i9nz"],
    "5224": ["2a7wms"],
    "14737": ["3fvr4l"],
    "17820": ["k76ov"],
    "19058": ["2zqq2c", "32o53l"],
    "19916": ["2e5zho"],
    "20007": ["1w6g6u"],
    "29501": ["1getay", "1gwlbb"],
    "30593": ["2uafbk"],
    "32858": ["2y7a6g", "3ci2ni"],
    "38515": ["1pl51l"],
    "42410": ["1zhg6p", "224i1n", "227n97"],
    "47251": ["2dq4gx"],
    "47572": ["2tfdb4", "3ff64x"],
    "50337": ["3f7iqw"],
    "51395": ["189w0w"],
    "123": ["2v6c9q", "3e8si7"],
    "3697": ["2ff664"],
    "5616": ["g7f7g"],
    "6303": ["20kbpj"],
    "6572": ["2xa7jl"],
    "243": ["2j44ow"],
    "777": ["1kpxiu"],
    "836": ["1d7nab", "1unus3"],
    "1270": ["2dv5mw"],
    "373": ["2xe7hp", "3bhds2", "3d2ttx"],
    "899": ["3h9o7o", "3hh29z"],
    "1264": ["vkxfb", "2nledl"],
    "2421": ["2il6xf"],
}




def load_csv(path_data):
    csv.field_size_limit(131072 * 10)

    expert_posts_columns = ['post_id', 'user_id', 'timestamp', 'subreddit', 'post_title', 'post_body']
    expert_posts_columns_file_path = os.path.join(path_data, "expert_posts.csv")


    expert_posts= []

    with open(expert_posts_columns_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=expert_posts_columns)
        next(reader, None)

        for row in reader:
            expert_posts.append(row)

    expert_columns = ['user_id', 'label']
    expert_path = os.path.join(path_data, "expert.csv")


    expert = []

    with open(expert_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=expert_columns)
        next(reader, None)

        for row in reader:
            expert.append(row)
    return {
        'posts': expert_posts,
        'users': expert,
    }

def path_find(file, path_data):
    path_data_set = os.getcwd()
    path_data_set = os.path.join(path_data_set, file)
    path_data_set = os.path.join(path_data_set, path_data)
    return path_data_set

def clustering_data(expert_posts, expert_users):
    data=[]
    for user in expert_users:
        user_id=user['user_id']
        for post in expert_posts:
            if post['user_id']==user_id and post['subreddit']=='SuicideWatch':
                post['label']=user['label']
                data.append(post)
    return data

data_mapping_expert = load_csv(path_find('umd_reddit_suicidewatch_dataset_v2', 'expert'))
expert_posts=data_mapping_expert['posts']
expert_users=data_mapping_expert['users']
expert_users=[user for user in expert_users if not user.get('label', '') == '']
expert_users=[user for user in expert_users if not user.get('label', '') == 'a']
expert_posts=clustering_data(expert_posts,expert_users)
data=pd.DataFrame(expert_posts)                     #cei 209 de experti

def load_csv(path_data, test=None):
    csv.field_size_limit(131072 * 10)

    shared_task_columns = ['post_id', 'user_id', 'timestamp', 'subreddit', 'post_title', 'post_body']
    if test is None:
        shared_task_file_path = os.path.join(path_data, "shared_task_posts.csv")
    else:
        shared_task_file_path = os.path.join(path_data, "shared_task_posts_test.csv")

    shared_task_posts = []

    with open(shared_task_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=shared_task_columns)
        next(reader, None)

        for row in reader:
            shared_task_posts.append(row)

    crowd_columns = ['user_id', 'label']
    if test is None:
        crowd_file_path = os.path.join(path_data, "crowd_train.csv")
    else:
        crowd_file_path = os.path.join(path_data, "crowd_test.csv")

    crowd_train = []

    with open(crowd_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=crowd_columns)
        next(reader, None)

        for row in reader:
            crowd_train.append(row)

    task_A_columns = ['post_id', 'user_id', 'subreddit']
    if test is None:
        task_A_file_path = os.path.join(path_data, "task_A_train.posts.csv")
    else:
        task_A_file_path = os.path.join(path_data, "task_A_test.posts.csv")

    task_A_train = []

    with open(task_A_file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=task_A_columns)
        next(reader, None)

        for row in reader:
            task_A_train.append(row)

    return {
        'shared_task_posts': shared_task_posts,
        'crowd_train': crowd_train,
        'task_A_train': task_A_train
    }

def clustering_data(task_A_data, crowd_data, shared_task_posts_data):
    for task in task_A_data:
        for shared_task in shared_task_posts_data:
            if task['post_id'] == shared_task['post_id']:
                task['timestamp'] = shared_task['timestamp']
                task['subreddit'] = shared_task['subreddit']
                task['post_title'] = shared_task['post_title']
                task['post_body'] = shared_task['post_body']
                break
        for crowd in crowd_data:
            if task['user_id'] == crowd['user_id']:
                task['label'] = crowd['label']
                break
    return task_A_data

def path_find(file, path_data, path_train):
    path_data_set = os.getcwd()
    path_data_set = os.path.join(path_data_set, file)
    path_data_set = os.path.join(path_data_set, path_data)
    path_data_set = os.path.join(path_data_set, path_train)
    return path_data_set

data_mapping_test = load_csv(path_find('umd_reddit_suicidewatch_dataset_v2', 'crowd', 'test'), 'test')
shared_test_posts_data = data_mapping_test['shared_task_posts']
crowd_test_data = data_mapping_test['crowd_train']
task_A_test_data = data_mapping_test['task_A_train']
data_test = clustering_data(task_A_test_data, crowd_test_data, shared_test_posts_data)
df_test = pd.DataFrame(data_test)

mapare = {"a": 1, "b": -1, "c": -1, "d": -1}
df_test['label'] = df_test['label'].apply(lambda x: mapare[x])
data['label'] = data['label'].apply(lambda x: mapare[x])

tfidf_vectorizer = TfidfVectorizer(**{
    'min_df': 1,
    'max_features': None,
    'strip_accents': 'unicode',
    'analyzer': 'word',
    'token_pattern': r'\b[^\d\W]+\b',
    'ngram_range': (2, 4),
    'use_idf': True,
    'smooth_idf': True,
    'sublinear_tf': True,
    # 'vocabulary': all_keywords,
    # 'stop_words': stop_words#,
})

test_features = tfidf_vectorizer.fit_transform(df_test['post_title'] + df_test['post_body'])

model = LogisticRegression(class_weight='balanced')
model.fit(test_features, df_test['label'])

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm_model = LlamaCpp(
    model_path="openhermes-2.5-mistral-7b.Q4_K_M.gguf",
    temperature=0.75,
    max_tokens=2000,
    top_p=1,
    n_ctx=32000,
    callback_manager=callback_manager,
    verbose=True,
)


def verify_unique_strings(strings):
    unique_strings = []

    for string in strings:
        string_copy = string
        tokens = word_tokenize(string_copy)
        substrings = [' '.join(gram) for gram in ngrams(tokens, 3) if all(len(word) >= 3 for word in gram)]

        is_unique = all(
            all(sub not in other_string and other_string not in sub for other_string in unique_strings) for sub in
            substrings)

        if is_unique:
            unique_strings.append(string)

    return unique_strings


def extract_sentence_with_feature(post_body, feature):
    post_body_copy = post_body
    post_body_copy = clean_sentence(post_body_copy)
    tokens = word_tokenize(post_body_copy)
    sentences = [sentence.strip() for sentence in re.split(r'[.!?]', post_body_copy) if
                 feature in sentence]
    return sentences


def clean_sentence(sentence):
    cleaned_sentence = re.sub(r'[^A-Za-z0-9\s.,\'"!?-_[]()]', '', sentence)
    return cleaned_sentence


def get_summarized_evidence(post_id, shap_values, dataset, ft_names):
    matching_rows = dataset[dataset['post_id'] == post_id]

    if not matching_rows.empty:
        post_index = matching_rows.index[0]

        if post_index < len(shap_values):
            post_shap_values = shap_values[post_index]
            top_feature_indices = np.argsort(post_shap_values)[:50]
            top_features = ft_names[top_feature_indices]
            unique_top_features = verify_unique_strings(top_features)

            summarized_evidence = []
            post_body = dataset.loc[post_index, 'post_body']

            for feature in unique_top_features:
                sentences = extract_sentence_with_feature(post_body, feature)
                summarized_evidence.extend(sentences)

            summarized_evidence = list(set(summarized_evidence))

            return summarized_evidence
    else:
        return []


def verify_top_features_existence(unique_top_features, post_body):
    verified_top_features = []

    for feature in unique_top_features:
        if feature.lower() in post_body.lower():
            verified_top_features.append(feature)

    return verified_top_features

def get_highlights(post_id, shap_values, dataset, ft_names):
    matching_rows = dataset[dataset['post_id'] == post_id]

    if not matching_rows.empty:
        post_index = matching_rows.index[0]

        if post_index < len(shap_values):
            post_shap_values = shap_values[post_index]
            top_feature_indices = np.argsort(post_shap_values)[:50]
            top_features = ft_names[top_feature_indices]
            unique_top_features = verify_unique_strings(top_features)

            highlights = []
            post_body = dataset.loc[post_index, 'post_body']

            for feature in unique_top_features:
                sentences = extract_sentence_with_feature(post_body, feature)
                highlights.extend(sentences)

            highlights = list(set(highlights))

            return highlights
    else:
        return []

def generate_json_output(user_id, post_id, shap_values, dataset, ft_names, llm_model):

    user_data = {
        "summarized_evidence": "",
        "posts": [
            {
                "post_id": post_id,
                "highlights": ""
            }
        ],
        "optional": [
            []
        ]
    }

    return {user_id: user_data}


new_data = tfidf_vectorizer.transform(data['post_title'] + data['post_body']).toarray()
explainer_new = shap.LinearExplainer(model, new_data, feature_dependence="independent")
shap_values_new = explainer_new.shap_values(new_data)

feature_names_new = np.array(tfidf_vectorizer.get_feature_names_out())

output_data_new = {}

for user_id, user_posts in data.head(2).groupby('user_id'):
    user_data = {
        "summarized_evidence": "",
        "posts": [],
        "optional": [[]]
    }

    text = ""

    for index, row in user_posts.iterrows():
        post_id = row['post_id']

        extracted_sentences = get_summarized_evidence(post_id, shap_values_new, data, feature_names_new)

        text += ". ".join(extracted_sentences) + " " if extracted_sentences else ""

        user_data["posts"].append({
            "post_id": post_id,
            "highlights": get_highlights(post_id, shap_values_new, data, feature_names_new)
        })

    question = f"You are a licensed psychologist and expert therapist evaluating a case. Analyze the following text and make a professional summary of the content explaining why the individual has suicidal thoughts. The text is as follows: {text}"
    llm_result = llm_model(' '.join(question.split(' ')[:300]))

    find = llm_result.find("\n\n")
    if find != -1:
        llm_result = llm_result[find + 2:]
    llm_result = llm_result.replace("\n\n", '')

    user_data["summarized_evidence"] = llm_result
    output_data_new[user_id] = user_data

users_to_keep = set(all_user_ids_to_post_ids.keys())

users_to_delete = [user_id for user_id in output_data_new.keys() if user_id not in users_to_keep]

for user_id in users_to_delete:
    del output_data_new[user_id]

output_file_path_new = 'submissionTest2.json'
with open(output_file_path_new, 'w', encoding='utf-8') as json_file:
    json.dump(output_data_new, json_file, indent=2, ensure_ascii=False)

print(f"Output saved to {output_file_path_new}")

output_file_path_new = 'submissionTest2.json'

with open(output_file_path_new, 'r', encoding='utf-8') as json_file:
    json_data = json.load(json_file)
print(json.dumps(json_data, indent=2)[:10000])


