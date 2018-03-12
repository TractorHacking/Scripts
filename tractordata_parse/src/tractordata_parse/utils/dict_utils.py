import itertools

def squashKeys(d, hashfn):
  newdict = dict()
  for basekey, matching_ids in itertools.groupby(d.keys(), hashfn):
    matchlist = newdict.setdefault(basekey, [])
    # want to do something clever with this but all I'm getting is sadness
#    newdict[basekey] = functools.reduce(lambda l, i: l.extend(d[i]) , matching_ids, matchlist)
    for thing in matching_ids:
      matchlist.extend(d[thing])
  return newdict
