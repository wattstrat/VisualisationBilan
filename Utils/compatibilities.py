def merge_two_dicts(x, y):
    '''Given two dicts, merge them into a new dict as a shallow copy.'''
    z = x.copy()
    z.update(y)
    return z

def safe_list_get (l, idx, default):
    try:
        return l[idx]
    except IndexError:
        return default

flatten = lambda l: [item for sublist in l for item in sublist]
