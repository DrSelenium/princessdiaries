from flask import Flask, request
import sys
import os

app = Flask(__name__)

@app.route('/princess-diaries', methods=['POST'])
def princess_diaries():
    data = request.json
    tasks = data['tasks']
    subway = data['subway']
    starting_station = data['starting_station']

    # Find all unique stations and determine nv
    all_stations = set([starting_station])
    for t in tasks:
        all_stations.add(t['station'])
    for r in subway:
        all_stations.add(r['connection'][0])
        all_stations.add(r['connection'][1])
    nv = max(all_stations) + 1 if all_stations else 1

    inf = float('inf')
    dist = [[inf] * nv for _ in range(nv)]
    for i in range(nv):
        dist[i][i] = 0
    for r in subway:
        u, v = r['connection']
        fee = r['fee']
        dist[u][v] = min(dist[u][v], fee)
        dist[v][u] = min(dist[v][u], fee)

    # Floyd-Warshall
    for k in range(nv):
        for i in range(nv):
            for j in range(nv):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]

    # Sort tasks by start time
    tasks_sorted = sorted(tasks, key=lambda x: x['start'])
    m = len(tasks_sorted)
    if m == 0:
        return {"max_score": 0, "min_fee": 0, "schedule": []}

    starts = [t['start'] for t in tasks_sorted]
    ends = [t['end'] for t in tasks_sorted]
    scores = [t['score'] for t in tasks_sorted]
    stations_list = [t['station'] for t in tasks_sorted]
    names = [t['name'] for t in tasks_sorted]

    dp_score = [0] * m
    dp_cost = [inf] * m
    prev = [-1] * m

    for i in range(m):
        dp_score[i] = scores[i]
        dp_cost[i] = dist[starting_station][stations_list[i]]
        prev[i] = -1
        for j in range(i):
            if ends[j] <= starts[i]:
                cand_score = dp_score[j] + scores[i]
                cand_cost = dp_cost[j] + dist[stations_list[j]][stations_list[i]]
                if cand_score > dp_score[i] or (cand_score == dp_score[i] and cand_cost < dp_cost[i]):
                    dp_score[i] = cand_score
                    dp_cost[i] = cand_cost
                    prev[i] = j

    max_score = max(dp_score) if dp_score else 0

    min_fee = inf
    best_end = -1
    for i in range(m):
        if dp_score[i] == max_score:
            this_fee = dp_cost[i] + dist[stations_list[i]][starting_station]
            if this_fee < min_fee:
                min_fee = this_fee
                best_end = i

    if best_end == -1:
        return {"max_score": 0, "min_fee": 0, "schedule": []}

    # Recover schedule
    sch = []
    cur = best_end
    while cur != -1:
        sch.append(names[cur])
        cur = prev[cur]
    sch.reverse()

    return {"max_score": max_score, "min_fee": int(min_fee), "schedule": sch}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)