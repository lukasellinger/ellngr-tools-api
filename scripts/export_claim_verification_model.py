import torch
from transformers import AutoModelForSequenceClassification
from torch import nn

from app.core.factVerification.models.claim_verification_model import ClaimVerificationModel

# Assuming model is already initialized
model_name = 'lukasellinger/claim-verification-model-top_last'  # Replace with your model name
model_raw = AutoModelForSequenceClassification.from_pretrained(model_name)
model = ClaimVerificationModel(model_raw)

# Example input for the model (input_ids and attention_mask)
input_ids = torch.tensor([[1, 4558, 340, 260, 2365, 260, 2365, 260, 2365, 6801, 261, 2,
                           4558, 340, 6801, 261, 2]])
attention_mask = torch.tensor([[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]])

# Export the model to ONNX
onnx_filename = "../onnx_models/claim_verification_model.onnx"
torch.onnx.export(
    model,  # The model to export
    (input_ids, attention_mask),  # Example inputs
    onnx_filename,  # Output filename
    input_names=["input_ids", "attention_mask"],  # Input names
    output_names=["logits"],  # Output name (the logits from the sequence classification model)
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "sequence_length"},
        # Batch size and sequence length as dynamic axes
        "attention_mask": {0: "batch_size", 1: "sequence_length"},
        "logits": {0: "batch_size"}  # Logits are batch-dependent
    },
    opset_version=12,  # ONNX opset version
    do_constant_folding=True  # Optimize constants for faster inference
)

print(f"Model successfully exported to {onnx_filename}")
