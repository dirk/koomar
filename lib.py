import re

"""General library with some helper functions. DRY'ness is always good."""
def flatten(x):
    """flatten(sequence) -> list

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables)."""
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
        self.body = a[3][1:].strip()
    def is_public(self):
        if self.target.startswith('#'): return True
        return False
    def is_private(self):
        if not self.is_public(): return True
        return False
    def is_command(self, command, exceptions):
        if self.is_public() and self.body.startswith(command):
            return True
        elif self.is_private() and not (self.sender == None or exceptions.__contains__(self.sender)):
            return True
        else:
            return False
    # Everything below here is horrendously ugly, but it works.
    def command(self, command):
        """Get the command that is issued to koomar."""
        if self.is_public() and self.body.startswith(command):
            return self.body[(command.__len__()+1):].split(' ')[0].strip()
        elif self.is_private():
            return self.body.split(' ')[0].strip()
        else:
            return False
    def argv(self, command):
        """Get the arguments (Everything passed after the command)."""
        # Currently kind of redundant, some cleanup may be necessary.
        if self.is_public() and self.body.startswith(command):
            try:
                return self.body[(command.__len__()+1):].split(' ', 1)[1].strip()
            except IndexError:
                return False
        elif self.is_private():
            try:
                return self.body.split(' ', 1)[1].strip()
            except IndexError:
                return False
        else:
            return False
        