"""
Grad-CAM implementation for the MobileNetV2 classifier.

Hooks the last convolutional block, captures its activations and the
gradient of the predicted class w.r.t. those activations, and combines
them into a heatmap showing which pixels drove the prediction.

This module is imported both by a standalone notebook (for inspecting
training results) and by the backend's inference endpoint.
"""
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms

IMG_SIZE = 224
NORMALIZE = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])


class GradCAM:
    def __init__(self, model, target_layer):
        self.model = model
        self.target_layer = target_layer
        self.activations = None
        self.gradients = None

        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_full_backward_hook(self._save_gradient)

    def _save_activation(self, module, input, output):
        self.activations = output.detach()

    def _save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate(self, input_tensor: torch.Tensor, class_idx: int = None):
        """Returns a (H, W) heatmap in [0, 1] and the predicted class index."""
        self.model.zero_grad()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = output.argmax(dim=1).item()

        score = output[0, class_idx]
        score.backward()

        # Global-average-pool the gradients to get per-channel importance weights
        weights = self.gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * self.activations).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=(IMG_SIZE, IMG_SIZE), mode="bilinear", align_corners=False)

        cam = cam.squeeze().cpu().numpy()
        cam = (cam - cam.min()) / (cam.max() - cam.min() + 1e-8)

        confidence = F.softmax(output, dim=1)[0, class_idx].item()
        return cam, class_idx, confidence


def preprocess_image(image_path: Path) -> torch.Tensor:
    img = Image.open(image_path).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    tensor = transforms.ToTensor()(img)
    tensor = NORMALIZE(tensor)
    return tensor.unsqueeze(0)  # add batch dimension


def overlay_heatmap(image_path: Path, heatmap: np.ndarray, alpha: float = 0.45) -> Image.Image:
    """Blends the Grad-CAM heatmap onto the original image for display."""
    import matplotlib.cm as cm

    original = Image.open(image_path).convert("RGB").resize((IMG_SIZE, IMG_SIZE))
    colored = (cm.jet(heatmap)[:, :, :3] * 255).astype(np.uint8)
    colored_img = Image.fromarray(colored)
    return Image.blend(original, colored_img, alpha=alpha)
