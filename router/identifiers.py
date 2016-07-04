import json
import sys
import mmap
import os.path

repo_data = {}

def load(config):
    global repo_data

    for repo_name in config['repos']:
        print 'Loading identifiers for', repo_name
        index_path = config['repos'][repo_name]['index_path']

        f = open(os.path.join(index_path, 'identifiers'))
        mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
        f.close()

        repo_data[repo_name] = mm

def get_line(mm, pos):
    if mm[pos] == '\n':
        pos -= 1

    start = end = pos

    while start >= 0 and mm[start] != '\n':
        start -= 1
    start += 1

    size = mm.size()
    while end < size and mm[end] != '\n':
        end += 1

    return mm[start:end]

def bisect(mm, needle, upper_bound):
    first = 0
    count = mm.size()
    while count > 0:
        step = count / 2
        pos = first + step

        line = get_line(mm, pos)
        if line < needle or (upper_bound and line == needle):
            first = pos + 1
            count -= step + 1
        else:
            count = step

    return first

def lookup(tree_name, needle, complete):
    mm = repo_data[tree_name]

    first = bisect(mm, needle, False)
    last = bisect(mm, needle + '~', False)

    result = []
    mm.seek(first)
    while mm.tell() < last:
        line = mm.readline().strip()
        pieces = line.split(' ')
        suffix = pieces[0][len(needle):]
        if ':' in suffix or '.' in suffix or (complete and suffix):
            continue
        result.append(pieces[0:2])

    return result

if __name__ == '__main__':
    load(json.load(open(sys.argv[1])))
    print lookup(sys.argv[2], sys.argv[3])
