import util


def extract_keywords(file_path):
    with util.Timer('extract_keywords', file_path):
        keywords = set()
        with open(file_path) as file:
            while True:
                line = file.readline()
                if not line:
                    break
                for word in line.split():
                    keywords.add(word)

        return list(keywords)

if __name__ == '__main__':
    file_paths = ['temp/user1', 'temp/anna', 'temp/aerondight', 'temp/regis',
                  'temp/geralt']

    for file_path in file_paths:
        keywords = extract_keywords(file_path)

        print(file_path+": {}".format(len(keywords)))