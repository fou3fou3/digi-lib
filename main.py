import os
import json

def load_config():
    return json.load(open("conf.json"))

def list_documents(documents_dir: str, file_types: list[str]):
    for item in os.listdir(documents_dir):
        if os.path.isfile(os.path.join(documents_dir, item)):
            if item.split(".")[-1] in file_types: yield documents_dir + "/" + item
        else:
            for document in list_documents(documents_dir + "/" + item, file_types):
                yield document

def get_doc_info(word: str, doc: str):
    doc_text = open(doc, 'r').read()
    return doc_text.count(word), len(doc_text.split())

def collect_basic_docs_info(query: str, documents: list[str]) -> tuple[dict[str, dict], float]:
    docs_info = {}
    avg_doc_len = 0

    for document in documents:
        document_text = open(document, 'r').read()
        doc_len = len(document_text.split())

        doc_word_freqs = {}

        for word in query.split():
            word_freq = document_text.count(word)
            doc_word_freqs[word] = word_freq

        docs_info[document] = {'doc_len': doc_len, 'doc_word_freqs': doc_word_freqs}
        avg_doc_len += doc_len

    avg_doc_len = avg_doc_len / len(documents)

    return docs_info, avg_doc_len

def calculate_words_idf(query: str, documents: list[str], docs_info: dict[str, dict]) -> dict[str, float]:
    query_words_idf = {}
    for word in query.split():
        docs_containing_word = 0
        for _, doc_info in docs_info.items():
            if doc_info['doc_word_freqs'][word] > 0:
                docs_containing_word += 1

        query_words_idf[word] = ((len(documents) - docs_containing_word + 0.5) / (docs_containing_word + 0.5)) + 1

    return query_words_idf

def calculate_word_bm(word_idf: float, word_freq: int, document_len: int, avg_doc_len: float):
    k1 = 1.5
    b = 0.75
    return (word_idf) * ((word_freq * (k1 + 1)) / (word_freq + (k1 * (1 - b + (b * (document_len / avg_doc_len))))))

def calculate_doc_bm(documents: list[str], query: str, query_words_idf: dict[str, float], docs_info: dict[str, dict], avg_doc_len: float):
    for doc in documents:
        bm_score = 0
        for word in query.split():
            bm_score += calculate_word_bm(query_words_idf[word], docs_info[doc]['doc_word_freqs'][word], docs_info[doc]['doc_len'], avg_doc_len)

        docs_info[doc]['bm_score'] = bm_score

def main(query: str = "hello there"):
    conf = load_config()

    documents = list(list_documents(conf["directory"], conf["file_types"]))

    docs_info, avg_doc_len = collect_basic_docs_info(query, documents)
    query_words_idf = calculate_words_idf(query, documents, docs_info)

    calculate_doc_bm(documents, query, query_words_idf, docs_info, avg_doc_len)

    print(json.dumps(docs_info, indent=4))

main()
