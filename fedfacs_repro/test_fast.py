"""The matrix-multiply layer4 must equal torchvision's layer4 (outputs and gradients)."""
import torch
import torch.nn.functional as F
from fl import init_head

def test_fast_equals_reference():
    dev = "cuda" if torch.cuda.is_available() else "cpu"
    torch.backends.cudnn.allow_tf32 = False  # cuDNN convs default to TF32; compare in true fp32
    h = init_head(0, dev)
    g = torch.Generator(device=dev).manual_seed(1)
    # perturb BN affine + convs so the test is not trivially at pretrained values
    with torch.no_grad():
        for p in h.parameters():
            p.add_(0.01 * torch.randn(p.shape, device=dev, generator=g))
    x = torch.randn(32, 256, 2, 2, device=dev, generator=g).relu()
    y = torch.randint(0, 10, (32,), device=dev, generator=g)
    f_ref, f_fast = h.feats_ref(x), h.feats(x)
    assert torch.allclose(f_ref, f_fast, atol=1e-4, rtol=1e-4), (f_ref - f_fast).abs().max()
    ps = list(h.parameters())
    g1 = torch.autograd.grad(F.cross_entropy(h.fc(f_ref), y), ps)
    g2 = torch.autograd.grad(F.cross_entropy(h.fc(f_fast), y), ps)
    worst = max(((a - b).abs().max() / (a.abs().max() + 1e-12)).item() for a, b in zip(g1, g2))
    assert worst < 1e-3, worst
    return float((f_ref - f_fast).abs().max()), worst

if __name__ == "__main__":
    print("max |feat diff|, worst relative grad diff:", test_fast_equals_reference())
    print("test_fast passed")
