import torch
from transformers import AutoModel
from app.core.factVerification.models.evidence_selection_model import EvidenceSelectionModel

# Load your model
model_name = "lukasellinger/evidence-selection-model"  # Replace with your model
model = AutoModel.from_pretrained(
    model_name,
    trust_remote_code=True,
    add_pooling_layer=False,
    safe_serialization=True
).to("cpu")

# Set the model to evaluation mode
model.eval()

# Initialize your custom EvidenceSelectionModel
evidence_model = EvidenceSelectionModel(model)

# Define dummy input data as per your example
input_ids = torch.tensor([[101, 3103, 2003, 9716, 1012, 102]])  # batch_size=1, sequence_length=6 (2D)
attention_mask = torch.tensor([[1, 1, 1, 1, 1, 1]])  # batch_size=1, sequence_length=6 (2D)
sentence_mask = torch.tensor([[[1, 1, 1, 1, 1, 1]]])  # batch_size=1, sequence_length=6, mask_dim=3 (3D)

# Set the model to evaluation mode
evidence_model.eval()

# Export the model to ONNX
torch.onnx.export(
    evidence_model,
    (input_ids, attention_mask, sentence_mask),  # Provide inputs, sentence_mask is 3D here
    "evidence_selection_model.onnx",  # Path to save the ONNX model
    input_names=["input_ids", "attention_mask", "sentence_mask"],  # Named inputs
    output_names=["sentence_embeddings"],  # Output name
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},  # dynamic batch and sequence length for 2D inputs
        "attention_mask": {0: "batch_size", 1: "sequence_length"},  # same for attention_mask
        "sentence_mask": {0: "batch_size", 1: "sequence_length", 2: "mask_dim"},  # 3D for sentence_mask
        "sentence_embeddings": {0: "batch_size"}  # Output can vary by batch size
    },
    opset_version=12,  # Make sure to use a compatible opset version
    do_constant_folding=True  # Optimize constants for faster inference
)