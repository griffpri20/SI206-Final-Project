    for movie in [m1, m2, m3]:
        cur.execute('''
                    SELECT q, time_posted, views, likes, comments
                    FROM YouTubeData
                    WHERE time_posted <> 'N/A'
                    AND views <>'N/A'
                    AND likes <> 'N/A'
                    AND comments <> 'N/A'
                    AND q = ?
                    ORDER BY time_posted''', (movie,))


    d = dict()
    for x in cur:
        year = x[-1].split()[0].split('-')[0]
        if x[0] == movie and year == '2018':
            count = int(x[1]) + int(x[2])
            month = int(x[-1].split('-')[1])
            if month not in d:
                d[month] = count
            else:
                d[month] = d[month] + count
    temp = [(x[0], x[1]) for x in sorted(d.items(), key = lambda y: y[0])]
    xlist = []
    ylist = []
    for x in temp:
        xlist.append(x[0])
        ylist.append(x[1])
    ax.plot(xlist, ylist, color, label=movie)


    if len(sort) > 10:
        for y in range(10, len(sort)):
            sort.remove(sort[10])
