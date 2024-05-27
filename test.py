s = "aaaaabsjfdbdskskkkkkksalajschshska"
d = {}

for x in s:
    if x in d.keys():
        d[x] += 1
    else:
        d[x] = 1

print(d)
for k,v in d.items():
    print(f"{k}={v} times")