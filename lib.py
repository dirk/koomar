import re

"""General library with some helper functions. DRY'ness is always good."""
def is_private_message(line):
    line = line.strip().split()
    if not line[2].startswith('#'): return True
    return False
def is_public_message(line):
    return not is_private_message(line)
def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> [1, 2, [3,4], (5,6)]
    [1, 2, [3, 4], (5, 6)]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]"""
    result = []
    for el in x:
        #if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result
class Message:
    def __init__(self, message):
        a = message.split(' ', 3)
        self.type = a[1]
        matches = re.match(':([A-Za-z0-9_-]+)!', a[0])
        if matches:
            self.sender = matches.groups()[0]
        else:
            self.sender = None
        self.target = a[2]
        self.body = a[3][1:]
    def is_public(self):
        if self.target.startswith('#'): return True
        return False
    def is_private(self):
        if not self.is_public(): return True
        return False
    # Everything below here is horrendously ugly, but it works.
    def command(self, command):
        if self.is_public() and self.body.startswith(command):
            return self.body[(command.__len__()+1):].__str__().strip().split(' ')[0].__str__()
        else:
            return self.body.__str__().strip().split(' ')[0].__str__()
    def argv(self, command):
        if self.is_public() and self.body.startswith(command):
            try:
                return self.body[(command.__len__()+1):].__str__().strip().split(' ', 1)[1].__str__().strip()
            except IndexError:
                return False
        else:
            try:
                return self.body.__str__().strip().split(' ', 1)[1].__str__().strip()
            except IndexError:
                return False
        