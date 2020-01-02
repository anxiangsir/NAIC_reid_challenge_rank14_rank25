import json
import pickle

import numpy as np
import torch
from sklearn import preprocessing
from rerank.rerank_kreciprocal import re_ranking
from sklearn.cluster import AgglomerativeClustering
NAME = "dgreid_b_003"


LABEL_DICT = {}


def process_info(info):
    feats, imgnames = info
    feats = preprocessing.normalize(feats)
    return feats, imgnames


def get_result(query_imgnames, query_feats, gallery_feats, gallery_imgnames):
    sim = np.dot(query_feats, gallery_feats.T)
    num_q, num_g = sim.shape
    indices = np.argsort(-sim, axis=1)

    clean_set = set()
    #
    for q_idx in range(num_q):
        order = indices[q_idx][:100]
        for gallery_index in order:
            clean_set.add(gallery_imgnames[gallery_index])
        else:
            continue

    temp_feat = np.zeros((len(clean_set), gallery_feats.shape[1]), dtype=np.float32)
    for idx, name in enumerate(clean_set):
        temp_feat[idx] = gallery_feats[gallery_imgnames.index(name)]

    print(temp_feat.shape)
    gallery_imgnames = list(clean_set)
    gallery_feats = temp_feat

    #
    query_feats = torch.from_numpy(query_feats)
    gallery_feats = torch.from_numpy(gallery_feats)
    sim = re_ranking(query_feats, gallery_feats, k1=10, k2=2, lambda_value=0.60)

    # sim = np.dot(query_feats, gallery_feats.T)
    num_q, num_g = sim.shape
    # indices = np.argsort(-sim, axis=1)
    indices = np.argsort(sim, axis=1)

    submission_key = {}
    for q_idx in range(num_q):
        order = indices[q_idx][:200]
        query_gallery = []
        for gallery_index in order:
            query_gallery.append(gallery_imgnames[gallery_index])
        submission_key[query_imgnames[q_idx]] = query_gallery

    return submission_key


def main():
    gallery_info = pickle.load(open('features/%s/gallery_feature.feat' % NAME, 'rb'))
    query_info = pickle.load(open('features/%s/query_feature.feat' % NAME, 'rb'))

    gallery_feats, gallery_imgnames = process_info(gallery_info)
    query_feats, query_imgnames = process_info(query_info)

    #
    chunk_size = 500
    #
    iter_num = len(query_imgnames) // chunk_size + 1
    #
    submission_key = {}
    #
    for i in range(iter_num):
        if i == iter_num - 1:
            _query_imgnames = query_imgnames[i * chunk_size:]
            _query_feats = query_feats[i * chunk_size:]
        else:
            _query_imgnames = query_imgnames[i * chunk_size: (i + 1) * chunk_size]
            _query_feats = query_feats[i * chunk_size: (i + 1) * chunk_size]

        # get
        _submission_key = get_result(_query_imgnames, _query_feats, gallery_feats, gallery_imgnames)
        # update
        submission_key.update(_submission_key)

    # cls = AgglomerativeClustering(
    #     n_clusters=None,
    #     linkage='average',
    #     affinity="cosine",
    #     distance_threshold=0.7
    # )
    #
    # cls.fit(query_feats)
    #
    # # generate label dict
    # for idx, _label in enumerate(cls.labels_):
    #     if _label not in LABEL_DICT:
    #         LABEL_DICT[_label] = [testA_query_img_names[idx]]
    #     else:
    #         assert isinstance(LABEL_DICT[_label], list)
    #         LABEL_DICT[_label].append(testA_query_img_names[idx])
    # #
    # print(len(set(cls.labels_)))

    # final
    submission_json = json.dumps(submission_key)
    print(type(submission_json))

    with open('rerank_%s.json' % NAME, 'w', encoding='utf-8') as f:
        f.write(submission_json)


if __name__ == '__main__':
    main()
