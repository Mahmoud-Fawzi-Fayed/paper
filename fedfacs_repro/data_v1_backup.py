"""Datasets, frozen-backbone feature cache and federated partitions.

Design (all choices are ours and are documented in the manuscript, because the original
experiment's preprocessing was not recorded):
  * ResNet-18 with ImageNet weights; conv1 + layer1-3 frozen and run once in eval mode, so their output
    (256 x 2 x 2 for 28x28 and 32x32 inputs) is cached. Only layer4 + a new 10-way fc are trained in FL.
  * grayscale images are replicated to 3 channels; ImageNet mean/std normalisation; native resolution.
"""
import os
import numpy as np
import torch
from torchvision import datasets, models

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
CACHE = os.path.join(ROOT, "cache")
os.makedirs(CACHE, exist_ok=True)

MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
NUM_CLASSES = 10
N_VAL = 5000


def _raw(name):
    if name == "cifar10":
        tr, te = datasets.CIFAR10(DATA, True, download=True), datasets.CIFAR10(DATA, False, download=True)
        xtr, xte = np.asarray(tr.data), np.asarray(te.data)  # N,32,32,3
    else:
        cls = datasets.FashionMNIST if name == "fmnist" else datasets.MNIST
        tr, te = cls(DATA, True, download=True), cls(DATA, False, download=True)
        xtr, xte = tr.data.numpy(), te.data.numpy()  # N,28,28
    return xtr, np.asarray(tr.targets), xte, np.asarray(te.targets)


def _to_input(x):
    x = torch.from_numpy(np.ascontiguousarray(x)).float() / 255.0
    if x.ndim == 3:  # grayscale -> 3 channels
        x = x.unsqueeze(1).repeat(1, 3, 1, 1)
    else:
        x = x.permute(0, 3, 1, 2)
    return (x - MEAN) / STD


def build_stem():
    m = models.resnet18(weights=models.ResNet18_Weights.IMAGENET1K_V1)
    stem = torch.nn.Sequential(m.conv1, m.bn1, m.relu, m.maxpool, m.layer1, m.layer2, m.layer3)
    return stem.eval(), m


@torch.no_grad()
def _extract(stem, x, dev, bs=1000):
    out = []
    for i in range(0, len(x), bs):
        out.append(stem(_to_input(x[i:i + bs]).to(dev)).half().cpu())
    return torch.cat(out)


def features(name, dev="cuda"):
    path = os.path.join(CACHE, f"{name}_feats.pt")
    if os.path.exists(path):
        return torch.load(path)
    xtr, ytr, xte, yte = _raw(name)
    stem, _ = build_stem()
    stem = stem.to(dev)
    d = dict(xtr=_extract(stem, xtr, dev), ytr=torch.from_numpy(ytr).long(),
             xte=_extract(stem, xte, dev), yte=torch.from_numpy(yte).long())
    torch.save(d, path)
    return d


# ---------------------------------------------------------------- partitions
def dirichlet_partition(y, n_clients, alpha, rng, min_size=30, max_tries=2000):
    classes = np.unique(y)
    n = len(y)
    best = None
    for _ in range(max_tries):
        idx = [[] for _ in range(n_clients)]
        for c in classes:
            ids = np.where(y == c)[0]
            rng.shuffle(ids)
            p = rng.dirichlet(alpha * np.ones(n_clients))
            p = np.array([pj * (len(ij) < n / n_clients) for pj, ij in zip(p, idx)])  # NIID-bench balancing
            p = p / p.sum() if p.sum() > 0 else np.ones(n_clients) / n_clients
            cuts = (np.cumsum(p) * len(ids)).astype(int)[:-1]
            for j, part in enumerate(np.split(ids, cuts)):
                idx[j] += part.tolist()
        m = min(len(i) for i in idx)
        if best is None or m > best[0]:
            best = (m, idx)
        if m >= min_size:
            return [np.array(i) for i in idx]
    raise RuntimeError(f"could not reach min_size={min_size}; best min was {best[0]}")


def two_class_partition(y, n_clients, rng, per=2, min_size=30):
    classes = np.unique(y)
    held = [rng.choice(classes, per, replace=False) for _ in range(n_clients)]
    idx = [[] for _ in range(n_clients)]
    for c in classes:
        holders = [i for i in range(n_clients) if c in held[i]]
        if not holders:
            continue
        ids = np.where(y == c)[0]
        rng.shuffle(ids)
        for h, part in zip(holders, np.array_split(ids, len(holders))):
            idx[h] += part.tolist()
    if min(len(i) for i in idx) < min_size:
        raise RuntimeError("two-class partition produced a client below min_size")
    return [np.array(i) for i in idx]


def make_federation(name, scenario, n_clients, seed, dev="cuda", local_test_frac=0.2):
    """Returns a dict of GPU tensors and per-client index lists.

    scenario: 's1_0.1' | 's1_0.5' (Dirichlet alpha) | 's2' (two classes per client).
    Splits (all disjoint): server validation (N_VAL of the training set), per-client train /
    per-client local test (20%), and the official test set.
    """
    f = features(name)
    rng = np.random.default_rng(10_000 + seed)
    ytr = f["ytr"].numpy()
    perm = rng.permutation(len(ytr))
    val_ids, pool = perm[:N_VAL], perm[N_VAL:]
    ypool = ytr[pool]
    if scenario.startswith("s1_"):
        parts = dirichlet_partition(ypool, n_clients, float(scenario.split("_")[1]), rng)
    elif scenario == "s2":
        parts = two_class_partition(ypool, n_clients, rng)
    else:
        raise ValueError(scenario)
    tr_idx, lt_idx = [], []
    for p in parts:
        gid = pool[p]
        gid = gid[rng.permutation(len(gid))]
        k = max(10, int(round(local_test_frac * len(gid))))
        lt_idx.append(gid[:k])
        tr_idx.append(gid[k:])
    g = lambda a: torch.as_tensor(a).to(dev)
    return dict(
        X=f["xtr"].to(dev), Y=f["ytr"].to(dev),
        Xte=f["xte"].to(dev), Yte=f["yte"].to(dev),
        val=g(val_ids), tr=[g(i) for i in tr_idx], lt=[g(i) for i in lt_idx],
        n=np.array([len(i) for i in tr_idx]), n_clients=n_clients,
        class_hist=np.stack([np.bincount(ytr[i], minlength=NUM_CLASSES) for i in tr_idx]),
    )
