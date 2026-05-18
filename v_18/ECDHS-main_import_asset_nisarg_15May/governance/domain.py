#!/usr/bin/python3

recs = [ "30", "31", "32" ]
#recs = [ "30" ]

if len(recs) > 1:
    domain = ["|"]
else:
    domain = []


for rec in recs:
    text = 'goal', '=', rec 
    domain.append(text)
