"""General library with some helper functions. DRY'ness is always good."""
def is_private_message(line):
    line = line.strip().split()
    if not line[2].startswith('#'): return True
    return False
def is_public_message(line):
    return not is_private_message(line)