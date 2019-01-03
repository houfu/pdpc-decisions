#  MIT License Copyright (c) 2019. Houfu Ang.

import re


def find_citation(source):
    """
    Helper function to locate the citation of a new decision. Uses the first citation (usually in the preface)
    as the citation of the document.
    :param source:
    :return: The citation or {None} if nothing was found.
    """
    match = re.search(r'(\[\d{4}]) (SGPDPC) (\[\d+])', source)
    if match:
        #  Grumble Grumble. Some decisions are incorrectly labelled, ie. [2018] SGPDPC [18]
        case_number = match.group(3)[1:-1]
        result = match.group(0)[0:14] + case_number
        return result
    else:
        match2 = re.search(r'\[\d{4}] SGPDPC \d+', source)
        if match2:
            return match2.group(0)
        else:
            return None
