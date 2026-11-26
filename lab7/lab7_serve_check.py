"""Lab #7 - functional case for the Cornac model server (cornac/serving/app.py).

Two sub-commands, both run from the repository root on the GitHub runner:

  python lab7/lab7_serve_check.py prepare
      Trains a small BPR model on the repository's own fixture tests/data.txt
      (10 users x 10 items, one interaction each) and saves it together with its
      training set, exactly like tests/cornac/serving/test_app.py does.
      Prints the saved model path (used as MODEL_PATH for the server).

  python lab7/lab7_serve_check.py check --url http://127.0.0.1:8080
      Sends real HTTP requests to the running server, prints them, writes
      lab7_evidence.json and checks:
        * invariants that must hold in BOTH versions (explicit remove_seen=false /
          remove_seen=true behave as documented, k is respected, status 200);
        * which default contract the running version satisfies:
            OLD contract: no remove_seen given -> seen items ARE returned
            NEW contract: no remove_seen given -> seen items are NOT returned
          Both are always reported; the run fails if the contract stated in
          EXPECTED_DEFAULT_REMOVE_SEEN below does not hold.
"""
import argparse
import json
import sys
import urllib.request

# The documented default of this version of the server (baseline: False,
# changed in Lab 7: seen items are hidden by default).
EXPECTED_DEFAULT_REMOVE_SEEN = True

DATA = "tests/data.txt"
UID = "930"  # user of the upstream serving test; has interacted with item 709


def read_interactions():
    rows = []
    with open(DATA) as f:
        for line in f:
            if line.strip():
                u, i, r, *_ = line.split()
                rows.append((u, i, float(r)))
    return rows


def prepare():
    from cornac.data import Dataset
    from cornac.models import BPR

    train_set = Dataset.from_uir(read_interactions(), seed=123)
    model = BPR(k=10, max_iter=100, learning_rate=0.01, lambda_reg=0.01, seed=123)
    model.fit(train_set)
    path = model.save(save_dir="lab7_model", save_trainset=True)
    print(path)


def get(url):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.status, json.loads(resp.read().decode())


def check(base_url):
    rows = read_interactions()
    all_items = sorted({i for _, i, _ in rows})
    seen = sorted({i for u, i, _ in rows if u == UID})

    requests = {
        "default_all": f"/recommend?uid={UID}&k=-1",
        "explicit_false": f"/recommend?uid={UID}&k=-1&remove_seen=false",
        "explicit_true": f"/recommend?uid={UID}&k=-1&remove_seen=true",
        "default_k5": f"/recommend?uid={UID}&k=5",
    }
    resp = {}
    for name, path in requests.items():
        status, body = get(base_url + path)
        resp[name] = {"request": "GET " + path, "status": status, **body}
        print(f"{name:15s} GET {path}\n{'':15s} -> {status} {json.dumps(body)}")

    default = resp["default_all"]["recommendations"]
    explicit_false = resp["explicit_false"]["recommendations"]
    explicit_true = resp["explicit_true"]["recommendations"]

    invariants = {
        "all requests return HTTP 200": all(r["status"] == 200 for r in resp.values()),
        "remove_seen=false returns every item, seen ones included":
            sorted(explicit_false) == all_items,
        "remove_seen=true returns no seen item":
            not set(explicit_true) & set(seen),
        "remove_seen=true = remove_seen=false minus seen items, same order":
            explicit_true == [i for i in explicit_false if i not in seen],
        "k=5 returns exactly 5 items": len(resp["default_k5"]["recommendations"]) == 5,
    }
    old_contract = (default == explicit_false
                    and resp["default_all"]["query"]["remove_seen"] is False)
    new_contract = (default == explicit_true
                    and resp["default_all"]["query"]["remove_seen"] is True
                    and not set(resp["default_k5"]["recommendations"]) & set(seen))

    print(f"\nuser {UID}: seen items {seen}, catalogue size {len(all_items)}")
    print(f"default request returned {len(default)} items, "
          f"seen item(s) included: {sorted(set(default) & set(seen))}")
    for name, ok in invariants.items():
        print(f"[{'PASS' if ok else 'FAIL'}] invariant: {name}")
    print(f"[{'HOLDS' if old_contract else 'no'}] OLD contract: default returns seen items")
    print(f"[{'HOLDS' if new_contract else 'no'}] NEW contract: default hides seen items")
    print(f"expected by this commit: {'NEW' if EXPECTED_DEFAULT_REMOVE_SEEN else 'OLD'} contract")

    evidence = {
        "uid": UID, "seen_items": seen, "catalogue_size": len(all_items),
        "responses": resp, "invariants": invariants,
        "old_contract_holds": old_contract, "new_contract_holds": new_contract,
        "expected_default_remove_seen": EXPECTED_DEFAULT_REMOVE_SEEN,
    }
    with open("lab7_evidence.json", "w") as f:
        json.dump(evidence, f, indent=2)

    expected_ok = new_contract if EXPECTED_DEFAULT_REMOVE_SEEN else old_contract
    if not (all(invariants.values()) and expected_ok):
        sys.exit("Lab7 check FAILED")
    print("Lab7 check passed")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["prepare", "check"])
    p.add_argument("--url", default="http://127.0.0.1:8080")
    a = p.parse_args()
    prepare() if a.cmd == "prepare" else check(a.url)
