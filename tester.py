import csv
import os
import time

import main
import shutil
import config
import util
from temp.display_timings import display_timings
import inspect


# num_nodes = 28
# version = 'v1'
# graph = 'G1'

# timer_db_dest = 'temp/timer_db_' + graph + '_' + str(num_nodes) + '_' + version

def g1(consensus_algo, version, n_nodes):
    doc_id = 'doc1'
    user_name = 'yen'
    password = 'yen'
    iterations = 10
    util.Timer.clear()
    for i in range(iterations):
        main.request_phr(config.phr_gen_url, config.entries_url, doc_id,
                         user_name, password,
                         config.current_head_store_path + '_' + user_name)

    # Save the recording in a CSV file
    func_name = inspect.getframeinfo(inspect.currentframe()).function
    out_dir = 'temp/graph_recordings'
    # graph specific
    file_name = func_name + '_' + consensus_algo + '_' + version + '_200.csv'
    out_file_path = os.path.join(out_dir, file_name)
    if not os.path.exists(out_file_path):
        os.makedirs(out_dir, exist_ok=True)
        with open(out_file_path, 'w') as file:
            csv.writer(file).writerow([
                'Epoch Time(ns)',
                'Number of Nodes',
                'Avg(ms)',
                'Max(ms)',
                'Min(ms)'
            ])

    with open(out_file_path, 'a') as \
            results:
        # graph specific
        util.Timer.record_timings('request_phr', 'yen', 'doc1', file=results,
                                  entry_id=n_nodes)


def g2(consensus_algo, version, n_nodes):
    doc_id = 'doc1'
    user_name = 'yen'
    password = 'yen'
    iterations = 20

    # Note to get proper readings run g2 once and then comment it and run
    # again after the previous transactions have settled.
    if os.path.exists('temp/current_head_'+user_name):
        os.remove('temp/current_head_'+user_name)
    main.request_phr(config.phr_gen_url, config.entries_url, doc_id,
                     user_name, password,
                     config.current_head_store_path + '_' + user_name)

    util.Timer.clear()
    # time.sleep(n_nodes)
    w = "consciousness"
    for i in range(iterations):
        main.search(w, user_name)

    # Save the recording in a CSV file
    out_dir = 'temp/graph_recordings'
    # graph specific
    file_name = 'g2_' + consensus_algo + '_' + version + '.csv'
    out_file_path = os.path.join(out_dir, file_name)
    if not os.path.exists(out_file_path):
        os.makedirs(out_dir, exist_ok=True)
        with open(out_file_path, 'w') as file:
            csv.writer(file).writerow([
                'Epoch Time(ns)',
                'Number of Nodes',
                'Avg(ms)',
                'Max(ms)',
                'Min(ms)'
            ])

    with open(out_file_path, 'a') as \
            results:
        # graph specific
        util.Timer.record_timings('search', w, user_name, file=results,
                                  entry_id=n_nodes)


def g3(consensus_algo, version, idx):
    doc_id = 'doc1'
    user_names = ['ciri', 'yen', 'geralt', 'regis', 'dandelion', 'zoltan',
                  'vesemir', 'triss', 'lambert', 'eskel', 'anna', 'olgierd',
                  'gaunter', 'emhyr', 'unseen']
    n_keywords_list = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
                       1100,
                       1200, 1300, 1400, 1500]
    user_name = user_names[idx]
    n_keywords = n_keywords_list[idx]
    password = user_name
    iterations = 10
    util.Timer.clear()
    time.sleep(min(15, idx + 1))
    for i in range(iterations):
        main.request_phr(config.phr_gen_url, config.entries_url, doc_id,
                         user_name, password,
                         config.current_head_store_path + '_' + user_name)

    # Save the recording in a CSV file
    out_dir = 'temp/graph_recordings'
    # graph specific
    file_name = 'g3_' + consensus_algo + '_' + version + '_8.csv'
    out_file_path = os.path.join(out_dir, file_name)
    if not os.path.exists(out_file_path):
        os.makedirs(out_dir, exist_ok=True)
        with open(out_file_path, 'w') as file:
            csv.writer(file).writerow([
                'Epoch Time(ns)',
                'Number of Keywords',
                'Avg(ms)',
                'Max(ms)',
                'Min(ms)'
            ])

    with open(out_file_path, 'a') as results:
        # graph specific
        util.Timer.record_timings('request_phr', user_name, doc_id,
                                  file=results, entry_id=n_keywords)


def g4(consensus_algo, version, idx):
    doc_id = 'doc1'
    user_names = ['ciri', 'yen', 'geralt', 'regis', 'dandelion', 'zoltan',
                  'vesemir', 'triss', 'lambert', 'eskel', 'anna', 'olgierd',
                  'gaunter', 'emhyr', 'unseen']
    n_keywords_list = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
                       1100, 1200, 1300, 1400, 1500]
    keywords = ['intensity', 'consciousness', 'greatest', 'interesting',
                'membership', 'endorsement', 'immunology', 'transit',
                'examinations', 'legislative', 'bulgaria', 'periodically',
                'gambling', 'invasion', 'expenditures']
    user_name = user_names[idx]
    keyword = keywords[idx]
    n_keywords = n_keywords_list[idx]
    password = user_name
    iterations = 10

    chd_path = config.current_head_store_path + '_' + user_name
    if os.path.exists(chd_path):
        os.remove(chd_path)

    util.Timer.clear()
    main.request_phr(config.phr_gen_url, config.entries_url, doc_id,
                     user_name, password, chd_path)

    time.sleep(min(15, idx + 1))
    for i in range(iterations):
        main.search(keyword, user_name)

    # Save the recording in a CSV file
    out_dir = 'temp/graph_recordings'
    # graph specific
    func_name = inspect.getframeinfo(inspect.currentframe()).function
    file_name = func_name + '_' + consensus_algo + '_' + version + '_8.csv'
    out_file_path = os.path.join(out_dir, file_name)
    if not os.path.exists(out_file_path):
        os.makedirs(out_dir, exist_ok=True)
        with open(out_file_path, 'w') as file:
            csv.writer(file).writerow([
                'Epoch Time(ns)',
                'Number of Keywords',
                'Avg(ms)',
                'Max(ms)',
                'Min(ms)'
            ])

    with open(out_file_path, 'a') as results:
        # graph specific
        util.Timer.record_timings('search', keyword, user_name, file=results,
                                  entry_id=n_keywords)


def g5():
    doc_id = 'doc1'
    user_name = 'yen'
    password = 'yen'
    iterations = 10
    for i in range(iterations):
        main.request_phr(config.phr_gen_url, config.entries_url, doc_id,
                         user_name, password,
                         config.current_head_store_path + '_' + user_name)


def g6():
    doc_id = 'doc1'
    user_names = ['ciri', 'yen', 'geralt', 'regis', 'dandelion', 'zoltan',
                  'vesemir', 'triss', 'lambert', 'eskel', 'anna', 'olgierd',
                  'gaunter', 'emhyr', 'unseen']
    user_name = user_names[6]
    password = user_name
    iterations = 10
    for i in range(iterations):
        main.request_phr(config.phr_gen_url, config.entries_url, doc_id,
                         user_name, password,
                         config.current_head_store_path + '_' + user_name)


if __name__ == '__main__':
    pass
    # g1('pbft', 'v1', 44)
    # g1('raft', 'v1', 40)

    # g2('pbft', 'v1', 32)
    g2('poet', 'v1', 24)
    # g2('raft', 'v1', 40)

    # g3('poet', 'v1', 3)
    # g3('pbft', 'v1', 14)
    # for i in range(0, 15):
    #     g3('raft', 'v1', i)
    #
    # time.sleep(20)
    #
    # for i in range(0, 15):
    #     # g4('pbft', 'v1', i)
    #     # g4('poet', 'v1', i)
    #     g4('raft', 'v1', i)
    #     time.sleep(2)

    # g5()
    # g6()
    # shutil.copy('temp/timer_db', timer_db_dest)
