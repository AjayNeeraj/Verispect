import httpx

endpoints = ['/api/metrics', '/api/logs', '/api/drift-events', '/api/drift-timeline', '/api/compliance-summary']
for e in endpoints:
    try:
        r = httpx.get(f'http://localhost:8000{e}')
        data = r.json()
        if isinstance(data, list):
            print(f'{e}: {r.status_code} — {len(data)} items')
        else:
            print(f'{e}: {r.status_code} — {data}')
    except Exception as ex:
        print(f'{e}: ERROR — {ex}')
